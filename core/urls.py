"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path
from gestion_lotes.views import descargar_excel_lotes, vista_mapa, buscar_propietario_lotes, actualizar_lote
# Aquí le decimos a Django exactamente dónde están tus funciones
from gestion_lotes.views import vista_mapa, buscar_propietario_lotes
from gestion_lotes.views import vista_mapa, buscar_propietario_lotes, actualizar_lote, descargar_excel_lotes
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', vista_mapa, name='mapa'),
    # Y aquí usamos la función directamente
    path('api/buscar-propietario/', buscar_propietario_lotes, name='buscar_propietario'),
    path('api/actualizar-lote/', actualizar_lote, name='actualizar_lote'),
    path('api/descargar-excel/', descargar_excel_lotes, name='descargar_excel'),
]