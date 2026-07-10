import os
import django
import json

# 1. Conectamos el script con el núcleo de tu proyecto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Ahora sí podemos importar los modelos de tu aplicación
from gestion_lotes.models import Manzana, Propietario, Lote

def poblar_base_de_datos():
    print("Abriendo la bóveda de datos (JSON)...")
    with open('datos_limpios.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)
        
    print(f"Iniciando la inyección de {len(datos)} lotes en Django. Por favor espera...")
    
    for item in datos:
        nombre_mz = item['manzana']
        num_lote = item['lote']
        nombre_prop = item['propietario']
        
        # 2. Busca la manzana, si no existe, la crea automáticamente
        manzana_obj, _ = Manzana.objects.get_or_create(nombre=nombre_mz)
        
        # 3. Busca al propietario, si no existe, lo crea
        propietario_obj, _ = Propietario.objects.get_or_create(nombres=nombre_prop)
        
        # 4. Asigna el lote a la manzana y al propietario
        Lote.objects.get_or_create(
            manzana=manzana_obj,
            numero=num_lote,
            defaults={
                'propietario': propietario_obj,
                'estado_legal': 'OCUPADO' # Como vienen del Excel, asumimos que tienen dueño
            }
        )
        
    print("¡Misión Cumplida! La base de datos está completamente poblada.")

if __name__ == "__main__":
    poblar_base_de_datos()