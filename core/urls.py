"""
URL configuration for core project.
"""

from django.contrib import admin
from django.urls import path

# Agrupamos TODAS las funciones en una sola importación limpia desde tu aplicación
from gestion_lotes.views import (
    vista_mapa, 
    buscar_propietario_lotes, 
    actualizar_lote, 
    descargar_excel_lotes,
    vista_impresion_manzana
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', vista_mapa, name='mapa'),
    path('api/buscar-propietario/', buscar_propietario_lotes, name='buscar_propietario'),
    path('api/actualizar-lote/', actualizar_lote, name='actualizar_lote'),
    path('api/descargar-excel/', descargar_excel_lotes, name='descargar_excel'),
    path('imprimir-manzana/', vista_impresion_manzana, name='imprimir_manzana')
]