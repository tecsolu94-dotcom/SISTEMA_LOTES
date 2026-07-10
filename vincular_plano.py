import ezdxf
from shapely.geometry import Point, Polygon
import json

def obtener_punto_real(entidad):
    if entidad.dxftype() == 'MTEXT':
        return Point(entidad.dxf.insert[0], entidad.dxf.insert[1])
    else:
        if hasattr(entidad.dxf, 'align_point') and (entidad.dxf.halign != 0 or entidad.dxf.valign != 0):
            return Point(entidad.dxf.align_point[0], entidad.dxf.align_point[1])
        else:
            return Point(entidad.dxf.insert[0], entidad.dxf.insert[1])

def procesar_plano():
    print("Iniciando Fase 2: Escáner Maestro por Redes de Manzanas unificadas...")
    doc = ezdxf.readfile("bloque nuevo.dxf")
    msp = doc.modelspace()

    # 1. Extraer Manzanas
    manzanas = []
    for e in msp.query('TEXT MTEXT[layer=="ID MANZANAS"]'):
        t = e.plain_text() if e.dxftype() == 'MTEXT' else e.dxf.text
        manzanas.append({'texto': t.strip().upper(), 'punto': obtener_punto_real(e)})

    # 2. Extraer Lotes Comerciales
    textos_lotes = []
    for e in msp.query('TEXT MTEXT[layer=="ID LOTESS"]'):
        t = e.plain_text() if e.dxftype() == 'MTEXT' else e.dxf.text
        if t.strip().isdigit():
            textos_lotes.append({'texto': str(int(t.strip())), 'punto': obtener_punto_real(e), 'asignado': False})
            
    for e in msp.query('INSERT[layer=="ID LOTESS"]'):
        if e.has_attrib:
            for attr in e.attribs:
                t = attr.dxf.text.strip()
                if t.isdigit():
                    textos_lotes.append({'texto': str(int(t)), 'punto': obtener_punto_real(attr), 'asignado': False})

    # 3. Extraer Áreas Especiales
    textos_areas = []
    for e in msp.query('TEXT MTEXT[layer=="ID AREAS_ESPECIALES"]'):
        t = e.plain_text() if e.dxftype() == 'MTEXT' else e.dxf.text
        t = t.strip().upper()
        if t and "M2" not in t and "AREA" not in t:
            textos_areas.append({'texto': t, 'punto': obtener_punto_real(e), 'asignado': False})
            
    for e in msp.query('INSERT[layer=="ID AREAS_ESPECIALES"]'):
        if e.has_attrib:
            for attr in e.attribs:
                t = attr.dxf.text.strip().upper()
                if t and not t.isdigit() and "M2" not in t and "AREA" not in t:
                    textos_areas.append({'texto': t, 'punto': obtener_punto_real(attr), 'asignado': False})

    print(f"-> Detectadas {len(manzanas)} manzanas en el plano.")
    print(f"-> Identificadores de lotes cargados: {len(textos_lotes)}")

    # 4. Cargar Polígonos de Lotes Crudos
    lotes_con_geometria = []
    for entity in msp.query('LWPOLYLINE[layer=="POLIGONOS_LOTES"]'):
        puntos = [(p[0], p[1]) for p in entity.get_points('xy')]
        if len(puntos) >= 3:
            poly = Polygon(puntos)
            lotes_con_geometria.append({
                'polygon': poly,
                'puntos': puntos,
                'numero': None,
                'manzana': None
            })

    # --- AQUÍ ESTÁ LA MAGIA: AGRUPACIÓN POR CERCANÍA FÍSICA (EVITA EL SALTO DE CALLE) ---
    print("Agrupando terrenos en manzanas físicas contiguas...")
    num_lotes = len(lotes_con_geometria)
    visitados = [False] * num_lotes
    clusters = []

    for i in range(num_lotes):
        if not visitados[i]:
            cluster = []
            queue = [i]
            visitados[i] = True
            while queue:
                curr_idx = queue.pop(0)
                curr_lote = lotes_con_geometria[curr_idx]
                cluster.append(curr_lote)
                
                curr_centroid = curr_lote['polygon'].centroid
                for j in range(num_lotes):
                    if not visitados[j]:
                        other_lote = lotes_con_geometria[j]
                        # Filtro rápido por cercanía de centros para optimizar velocidad
                        if curr_centroid.distance(other_lote['polygon'].centroid) < 45.0:
                            # Si los lotes se tocan o están pegados (distancia < 2 unidades métricas)
                            if curr_lote['polygon'].distance(other_lote['polygon']) < 2.0:
                                visitados[j] = True
                                queue.append(j)
            clusters.append(cluster)

    # Identificar colectivamente la manzana correcta para cada isla de lotes
    for cluster in clusters:
        mejor_mz = "DESCONOCIDA"
        min_dist_global = float('inf')
        for m in manzanas:
            for lote in cluster:
                d = lote['polygon'].centroid.distance(m['punto'])
                if d < min_dist_global:
                    min_dist_global = d
                    mejor_mz = m['texto']
        for lote in cluster:
            lote['manzana'] = mejor_mz

    # 5. Tu lógica original de vinculación estricta y limpia
    print("Procesando geometría de Lotes...")
    elementos_mapeados = []
    lotes_huerfanos = 0
    areas_huerfanas = 0

    for p in lotes_con_geometria:
        candidatos = []
        for t in textos_lotes:
            if t['asignado']:
                continue
            if p['polygon'].contains(t['punto']):
                candidatos.append((0, t))
            elif p['polygon'].distance(t['punto']) < 0.5:
                candidatos.append((p['polygon'].distance(t['punto']), t))
        
        if candidatos:
            candidatos.sort(key=lambda x: x[0])
            mejor_match = candidatos[0][1]
            mejor_match['asignado'] = True
            p['numero'] = mejor_match['texto']
            
            elementos_mapeados.append({
                'tipo': 'LOTE', 'manzana': p['manzana'], 'numero': p['numero'], 'coordenadas': p['puntos']
            })
        else:
            lotes_huerfanos += 1

    print("Procesando geometría de Áreas Especiales...")
    for entity in msp.query('LWPOLYLINE[layer=="AREAS_ESPECIALES"]'):
        puntos = [(p[0], p[1]) for p in entity.get_points('xy')]
        if len(puntos) >= 3:
            poly = Polygon(puntos)
            candidatos = []
            
            for t in textos_areas:
                if t['asignado']:
                    continue
                if poly.contains(t['punto']):
                    candidatos.append((0, t))
                elif poly.distance(t['punto']) < 0.5:
                    candidatos.append((poly.distance(t['punto']), t))
            
            if candidatos:
                candidatos.sort(key=lambda x: x[0])
                mejor_match = candidatos[0][1]
                mejor_match['asignado'] = True
                encontrado = mejor_match['texto']
                
                nombre_mz = min(manzanas, key=lambda m: poly.centroid.distance(m['punto']))['texto'] if manzanas else "GENERAL"
                elementos_mapeados.append({
                    'tipo': 'AREA_ESPECIAL', 'manzana': nombre_mz, 'numero': encontrado, 'coordenadas': puntos
                })
            else:
                areas_huerfanas += 1

    with open('coordenadas_finales.json', 'w', encoding='utf-8') as f:
        json.dump(elementos_mapeados, f, ensure_ascii=False, indent=4)
    
    print("-" * 50)
    print(f"⚠️ Polígonos de venta que quedaron vacíos legítimamente: {lotes_huerfanos}")
    print(f"✅ ¡Sincronización limpia! Se exportaron {len(elementos_mapeados)} polígonos sin duplicados.")

if __name__ == '__main__':
    procesar_plano()