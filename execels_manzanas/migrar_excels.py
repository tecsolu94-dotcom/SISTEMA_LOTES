import os
import pandas as pd

def leer_archivos_excel():
    carpeta = 'excels_manzanas'
    
    # 1. Obtenemos la lista de todos los archivos en la carpeta
    archivos = [f for f in os.listdir(carpeta) if f.endswith('.xlsx') or f.endswith('.xls')]
    
    print(f"Se encontraron {len(archivos)} archivos de manzanas. Iniciando lectura...\n")
    
    for archivo in archivos:
        ruta_completa = os.path.join(carpeta, archivo)
        
        # Extraemos el nombre de la manzana desde el nombre del archivo (Ej: "Manzana_A.xlsx" -> "A")
        # Esto asume que el nombre del archivo tiene la letra de la manzana
        nombre_manzana = archivo.replace('.xlsx', '').replace('.xls', '')
        print(f"--- Procesando: {nombre_manzana} ---")
        
        try:
            # 2. Leer el Excel
            # Usamos header=None porque me mencionaste que el formato tiene colores y celdas combinadas, 
            # no una tabla perfecta. Así capturamos todo crudo primero.
            df = pd.read_excel(ruta_completa, header=None)
            
            # 3. Mostrar un resumen de lo que encontró en ese archivo
            filas, columnas = df.shape
            print(f"   Contiene {filas} filas de datos.")
            
            # Aquí imprimimos las primeras 3 filas para ver cómo viene la data real
            # y así programar la limpieza exacta
            print(df.head(3))
            print("-" * 30)
            
        except Exception as e:
            print(f"Error al leer {archivo}: {e}")

if __name__ == "__main__":
    leer_archivos_excel()