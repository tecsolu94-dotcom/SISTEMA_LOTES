from django.contrib import admin
from .models import Lote, Manzana, Propietario

# 1. 🔍 CONFIGURACIÓN AVANZADA PARA LOTES
class LoteAdmin(admin.ModelAdmin):
    # Campos por los que puedes escribir en la barra de búsqueda superior
    search_fields = ['numero', 'manzana__nombre', 'propietario__nombres', 'propietario__dni']
    
    # Columnas que se verán ordenadas en la tabla principal
    list_display = ('__str__', 'estado_legal', 'estado_pago', 'propietario')
    
    # Filtros rápidos en una columna a la derecha
    list_filter = ('estado_legal', 'estado_pago', 'manzana')

# 2. 🔍 CONFIGURACIÓN AVANZADA PARA PROPIETARIOS
class PropietarioAdmin(admin.ModelAdmin):
    # Te permite buscar clientes escribiendo su Nombre, DNI o Teléfono
    search_fields = ['nombres', 'dni', 'telefono']
    
    # Muestra los datos más importantes en forma de lista tabulada
    list_display = ('nombres', 'dni', 'telefono')

# 3. 🔍 CONFIGURACIÓN AVANZADA PARA MANZANAS
class ManzanaAdmin(admin.ModelAdmin):
    # Te permite buscar una manzana escribiendo su letra/nombre directamente
    search_fields = ['nombre']
    list_display = ('nombre',)


# --- REGISTRO SEGURO DE MODELOS ---
# Usamos este bloque para limpiar cualquier registro previo y evitar el error "AlreadyRegistered"
try:
    admin.site.unregister(Lote)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Manzana)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Propietario)
except admin.sites.NotRegistered:
    pass
class LoteAdmin(admin.ModelAdmin):
    search_fields = ['numero', 'manzana__nombre', 'propietario__nombres', 'propietario__dni']
    list_display = ('__str__', 'estado_legal', 'estado_pago', 'propietario')
    list_filter = ('estado_legal', 'estado_pago', 'manzana')
    
    # ⚡ LA MAGIA: Transforma el desplegable en un buscador inteligente
    autocomplete_fields = ['propietario']
# Registramos los tres modelos con sus respectivos buscadores y filtros avanzados
admin.site.register(Lote, LoteAdmin)
admin.site.register(Manzana, ManzanaAdmin)
admin.site.register(Propietario, PropietarioAdmin)