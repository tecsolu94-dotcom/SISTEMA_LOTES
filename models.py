from django.db import models

class Propietario(models.Model):
    nombres = models.CharField(max_length=200)
    dni = models.CharField(max_length=15, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    
    # Aquí el administrador podrá escribir todo el historial o situación del dueño
    comentarios = models.TextField(null=True, blank=True) 

    def __str__(self):
        return self.nombres

class Manzana(models.Model):
    nombre = models.CharField(max_length=10, unique=True) 
    
    def __str__(self):
        return f"Manzana {self.nombre}"

class Lote(models.Model):
    ESTADOS_LEGAL = (
        ('LIBRE', 'Libre'),
        ('OCUPADO', 'Ocupado'),
        ('REGULARIZANDO', 'En Regularización'),
    )
    ESTADOS_PAGO = (
        ('PAGADO', 'Pagado'),
        ('DEUDA', 'Con Deuda'),
    )
    
    manzana = models.ForeignKey(Manzana, on_delete=models.CASCADE, related_name='lotes')
    numero = models.CharField(max_length=10)
    propietario = models.ForeignKey(Propietario, on_delete=models.SET_NULL, null=True, blank=True)
    
    estado_legal = models.CharField(max_length=20, choices=ESTADOS_LEGAL, default='LIBRE')
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='DEUDA')
    coordenadas_mapa = models.JSONField(null=True, blank=True) 

    def __str__(self):
        return f"Lote {self.numero} - Mz {self.manzana.nombre}"