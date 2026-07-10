from django.shortcuts import render
from .models import Lote
import json
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Lote, Propietario, Manzana
def vista_mapa(request):
    # Traemos todos los lotes optimizando la consulta con select_related
    lotes_db = Lote.objects.select_related('manzana', 'propietario').all()
    
    lotes_lista = []
    for lote in lotes_db:
        # Solo procesamos los lotes que tengan coordenadas válidas
        if lote.coordenadas_mapa:
            lotes_lista.append({
                'manzana': lote.manzana.nombre,
                'numero': lote.numero,
                'estado': lote.estado_legal,
                'propietario': lote.propietario.nombres if lote.propietario else "Disponible",
                'coordenadas': lote.coordenadas_mapa
            })
            
    # Convertimos la lista a un string JSON seguro para JavaScript
    lotes_json = json.dumps(lotes_lista, ensure_ascii=False)
    
    return render(request, 'gestion_lotes/mapa.html', {'lotes_json': lotes_json})
from django.http import JsonResponse
from django.db.models import Q
from .models import Propietario, Lote

def buscar_propietario_lotes(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'error': 'Término de búsqueda vacío'}, status=400)

    # Buscamos coincidencias ignorando mayúsculas/minúsculas en Nombre o DNI
    propietarios = Propietario.objects.filter(
        Q(nombres__icontains=query) | Q(dni__icontains=query)
    )

    if not propietarios.exists():
        return JsonResponse({'resultados': [], 'mensaje': 'No se encontraron registros.'})

    resultados_json = []
    
    for prop in propietarios:
        # Extraemos todos los lotes que le pertenecen a esta persona
        lotes_asociados = Lote.objects.filter(propietario=prop)
        
        datos_lotes = []
        for lote in lotes_asociados:
            datos_lotes.append({
                'manzana': lote.manzana.nombre,
                'numero': lote.numero,
                'estado_legal': lote.estado_legal,
                'estado_pago': lote.estado_pago,
                'coordenadas': lote.coordenadas_mapa
            })
            
        resultados_json.append({
            'propietario_id': prop.id,
            'nombres': prop.nombres,
            'dni': prop.dni,
            'telefono': prop.telefono,
            'total_lotes': lotes_asociados.count(),
            'lotes': datos_lotes
        })

    return JsonResponse({'resultados': resultados_json})
@csrf_exempt # Desactivamos temporalmente el token de seguridad para facilitar la conexión con JS
def actualizar_lote(request):
    if request.method == 'POST':
        try:
            # Recibimos los datos que nos enviará el mapa
            data = json.loads(request.body)
            mz_nombre = data.get('manzana')
            lote_numero = data.get('numero')
            
            nombres = data.get('nombres', '').strip()
            dni = data.get('dni', '').strip()
            estado_legal = data.get('estado_legal', 'OCUPADO')

            # 1. Buscamos el lote exacto en la base de datos
            lote = Lote.objects.get(manzana__nombre=mz_nombre, numero=lote_numero)

            if nombres:
                # 2. Si nos envían un nombre, creamos al propietario o lo actualizamos si ya existe por su DNI
                if dni:
                    propietario, created = Propietario.objects.get_or_create(
                        dni=dni, 
                        defaults={'nombres': nombres}
                    )
                    # Si ya existía pero le cambiaron el nombre, lo actualizamos
                    if not created and propietario.nombres != nombres:
                        propietario.nombres = nombres
                        propietario.save()
                else:
                    # Si no tiene DNI, solo lo creamos por nombre
                    propietario = Propietario.objects.create(nombres=nombres)

                # 3. Asignamos el dueño al lote y lo marcamos como ocupado
                lote.propietario = propietario
                lote.estado_legal = estado_legal
            
            lote.save()

            return JsonResponse({
                'status': 'success', 
                'message': f'Lote {lote_numero} de la Mz {mz_nombre} actualizado correctamente.'
            })

        except Lote.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Lote no encontrado en la base de datos.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
import csv
from django.http import HttpResponse

def descargar_excel_lotes(request):
    # Creamos la respuesta HTTP indicando que es un archivo descargable (CSV compatible con Excel)
    # Usamos utf-8-sig para que Excel reconozca las tildes y las "Ñ" correctamente
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Reporte_VILLTECC_Lotes.csv"'

    writer = csv.writer(response, delimiter=';') # El punto y coma separa las columnas en Excel
    
    # 1. Escribimos la cabecera (La primera fila del Excel)
    writer.writerow(['Manzana', 'Numero de Lote', 'Estado Legal', 'Estado Pago', 'Propietario', 'DNI Propietario'])

    # 2. Traemos todos los lotes ordenados por Manzana y luego por Número
    lotes = Lote.objects.all().order_by('manzana__nombre', 'numero')

    # 3. Llenamos las filas una por una
    for lote in lotes:
        nombre_propietario = lote.propietario.nombres if lote.propietario else 'Sin Propietario'
        dni_propietario = lote.propietario.dni if lote.propietario and lote.propietario.dni else 'N/A'
        
        writer.writerow([
            lote.manzana.nombre,
            lote.numero,
            lote.estado_legal,
            lote.estado_pago,
            nombre_propietario,
            dni_propietario
        ])

    return response