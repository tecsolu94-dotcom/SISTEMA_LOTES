import ezdxf

def escanear_capas():
    doc = ezdxf.readfile("bloque nuevo.dxf")
    msp = doc.modelspace()

    print("--- RADIOGRAFÍA DEL PLANO ---")
    
    # 1. Buscar en qué capas hay textos realmente
    capas_texto = {}
    for entity in msp.query('TEXT MTEXT'):
        capa = entity.dxf.layer
        capas_texto[capa] = capas_texto.get(capa, 0) + 1

    print("\nTextos encontrados por capa:")
    if not capas_texto:
        print("  ¡No se encontró ningún texto (TEXT/MTEXT) en todo el dibujo!")
    else:
        for capa, cantidad in capas_texto.items():
            print(f"  - Capa '{capa}': {cantidad} textos")
            
    # 2. Buscar si los números están guardados como Bloques (INSERT)
    capas_bloques = {}
    for entity in msp.query('INSERT'):
        capa = entity.dxf.layer
        capas_bloques[capa] = capas_bloques.get(capa, 0) + 1
        
    print("\nBloques encontrados por capa:")
    if not capas_bloques:
        print("  No hay bloques en el dibujo.")
    else:
        for capa, cantidad in capas_bloques.items():
            print(f"  - Capa '{capa}': {cantidad} bloques")

if __name__ == '__main__':
    escanear_capas()