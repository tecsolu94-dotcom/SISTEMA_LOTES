import os
import pandas as pd
import re
import json # <- Importamos la librería para crear el archivo

def limpiar_y_migrar():
    carpeta = 'execels_manzanas'
    archivos = [f for f in os.listdir(carpeta) if f.endswith('.xlsx') or f.endswith('.xls')]
    
    print(f"Iniciando limpieza de {len(archivos)} manzanas...\n")
    
    datos_totales = [] # <- Aquí guardaremos toda la data limpia
    
    for archivo in archivos:
        ruta_completa = os.path.join(carpeta, archivo)
        # Limpiamos la palabra "MANZANA" para que solo quede la letra (Ej: "X1", "Y")
        nombre_manzana = archivo.replace('.xlsx', '').replace('.xls', '').replace('MANZANA ', '').strip()
        
        try:
            df = pd.read_excel(ruta_completa, header=None)
            df_limpio = df.dropna(subset=[1])
            df_limpio = df_limpio[~df_limpio[1].astype(str).str.contains('MANZANA', na=False, case=False)]

            for index, fila in df_limpio.iterrows():
                nombre_propietario = str(fila[1]).strip()
                lotes_crudos = str(fila[2]).strip()
                
                if lotes_crudos.lower() == 'nan':
                    continue
                    
                if lotes_crudos.endswith('.0'):
                    lotes_crudos = lotes_crudos[:-2]
                    
                lotes_limpios = lotes_crudos.replace('_', '-').replace(' ', '')
                lista_lotes = [lote for lote in re.split(r'-+', lotes_limpios) if lote]
                
                # <- Agregamos cada lote por separado a nuestra lista final
                for lote in lista_lotes:
                    datos_totales.append({
                        "manzana": nombre_manzana,
                        "lote": lote,
                        "propietario": nombre_propietario
                    })

        except Exception as e:
            print(f"Error en {archivo}: {e}")
            
    # <- Creamos el archivo JSON con toda la información
    with open('datos_limpios.json', 'w', encoding='utf-8') as f:
        json.dump(datos_totales, f, ensure_ascii=False, indent=4)
        
    print("-" * 50)
    print(f"¡Éxito! Se han extraído {len(datos_totales)} lotes en total.")
    print("Toda la información se guardó en 'datos_limpios.json'")

if __name__ == "__main__":
    limpiar_y_migrar()