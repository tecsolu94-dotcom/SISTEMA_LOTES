import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from gestion_lotes.models import Manzana, Lote

def acoplar_geometria():
    print("Abriendo 'coordenadas_finales.json'...")
    with open('coordenadas_finales.json', 'r', encoding='utf-8') as f:
        geometrias = json.load(f)
        
    print(f"Sincronizando {len(geometrias)} geometrías con la base de datos...")
    
    lotes_actualizados = 0
    lotes_nuevos = 0
    areas_especiales = 0
    
    for geo in geometrias:
        nombre_mz = geo['manzana']
        num_identificador = geo['numero']
        coordenadas = geo['coordenadas']
        tipo = geo['tipo']
        
        manzana_obj, _ = Manzana.objects.get_or_create(nombre=nombre_mz)
        
        if tipo == 'LOTE':
            lote_obj, creado = Lote.objects.get_or_create(
                manzana=manzana_obj,
                numero=num_identificador,
                defaults={
                    'estado_legal': 'LIBRE',
                    'estado_pago': 'PAGADO',
                    'coordenadas_mapa': coordenadas
                }
            )
            if not creado:
                lote_obj.coordenadas_mapa = coordenadas
                lote_obj.save()
                lotes_actualizados += 1
            else:
                lote_obj.coordenadas_mapa = coordenadas
                lote_obj.save()
                lotes_nuevos += 1
                
        elif tipo == 'AREA_ESPECIAL':
            # Registra el parque y bloquea su estado legal
            lote_obj, creado = Lote.objects.get_or_create(
                manzana=manzana_obj,
                numero=num_identificador,
                defaults={
                    'estado_legal': 'AREA_COMUN',
                    'estado_pago': 'NO_APLICA',
                    'coordenadas_mapa': coordenadas
                }
            )
            lote_obj.coordenadas_mapa = coordenadas
            lote_obj.estado_legal = 'AREA_COMUN'
            lote_obj.save()
            areas_especiales += 1

    print("-" * 50)
    print("¡Sincronización completa!")
    print(f"-> Lotes actualizados con coordenadas: {lotes_actualizados}")
    print(f"-> Nuevos lotes añadidos al sistema: {lotes_nuevos}")
    print(f"-> Áreas Especiales (Parques) protegidas: {areas_especiales}")

if __name__ == "__main__":
    acoplar_geometria()