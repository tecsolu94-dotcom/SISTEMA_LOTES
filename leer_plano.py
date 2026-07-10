import ezdxf

def analizar_plano():
    try:
        # 1. Cargar el archivo DXF
        doc = ezdxf.readfile("bloque nuevo.dxf")
        msp = doc.modelspace()
        
        # 2. Buscar las polilíneas (los lotes cerrados)
        lotes = msp.query('LWPOLYLINE')
        
        print("\n--- ANÁLISIS DEL PLANO ---")
        print(f"¡Éxito! Se han encontrado {len(lotes)} lotes dibujados en el plano.")
        
        # 3. Extraer las coordenadas del primer lote como prueba
        if len(lotes) > 0:
            primer_lote = lotes[0]
            puntos = primer_lote.get_points('xy')
            print("\nCoordenadas X,Y de los vértices del primer lote:")
            for i, punto in enumerate(puntos):
                print(f"Vértice {i+1}: {punto}")
                
    except Exception as e:
        print("Hubo un error al leer el archivo:", e)

if __name__ == "__main__":
    analizar_plano()