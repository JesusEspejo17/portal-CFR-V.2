from django.db import models

from user.models import User
from django.forms import model_to_dict
from datetime import date


# Create your models here.

#Dimensiones
class Dimensiones(models.Model):
    nombre = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)
    descripcion = models.CharField(max_length=150)
    def __str__(self):
        return self.id

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Producto
class OITM(models.Model):
    ItemCode = models.CharField(max_length=150, primary_key=True)
    ItemName = models.CharField(max_length=150)
    PriceUnit = models.FloatField(default=0.0)
    TypeProduct = models.CharField(max_length=1, null=False)
    idAlmacen = models.CharField(null=True, blank=True)


    def __str__(self):
        return self.ItemCode

    class Meta:
        verbose_name = 'OITM'

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Socio de negocios (proveedor)
class OCRD(models.Model):
    CardCode = models.CharField(max_length=150, primary_key=True)
    CardName = models.CharField(max_length=150)
    CardType = models.CharField(max_length=10)

    def __str__(self):
        return self.CardCode

    class Meta:
        verbose_name = 'OCRD'

    def toJSON(self):
        item = model_to_dict(self)
        return item

    
#Validaciones
class Validaciones(models.Model):
    codValidador = models.CharField(max_length=150)
    codReqUser = models.CharField(max_length=150)
    fecha = models.DateField()
    estado = models.CharField(max_length=150)

    def __str__(self):
        return f'Aprobación de {self.codReqUser} por {self.codValidador}'

    class Meta:
        verbose_name = 'Aprobación'
        verbose_name_plural = 'Aprobaciones'

    def toJSON(self):
        item = {
            'id': self.pk,
            'codValidador': self.codValidador,
            'codReqUser': self.codReqUser,
            'fecha': self.fecha,
            'estado': self.estado,
        }
        return item

#Unidad de medida
class OUOM(models.Model):
    Code = models.CharField(max_length=150, primary_key=True)
    Name = models.CharField(max_length=150)

    def __str__(self):
        return self.Code

    class Meta:
        verbose_name = 'OUOM'

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Departamento
class Departamento(models.Model):
    Code = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=150)
    def __str__(self):
        return self.Name

    class Meta:
        verbose_name = 'Departamento'

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Impuestos
class OSTA(models.Model):
    Code = models.CharField(max_length=150, primary_key=True)
    Name = models.CharField(max_length=150)
    Rate = models.FloatField(default=0.0)
    Type = models.IntegerField(null=False)

    def __str__(self):
        return self.Code
    
    def get_impuesto_name(self):
        full_impuesto = "%s - %s" % (self.Name, self.Code)
        return full_impuesto
    
    def extract_id(cad):
        cad.split()
        return cad[3]

    class Meta:
        verbose_name = 'OSTA'

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Almacen
class OWHS(models.Model):
    WhsCode = models.CharField(max_length=150, primary_key=True)
    WhsName = models.CharField(max_length=150)

    def __str__(self):
        return self.WhsCode

    class Meta:
        verbose_name = 'OWHS'

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Almacén x Producto
class OWHS_OITM(models.Model):
    id = models.IntegerField(primary_key=True)
    WhsCod = models.ForeignKey(OWHS, on_delete=models.CASCADE, verbose_name='WhsCod')
    ItemCod = models.ForeignKey(OITM, on_delete=models.CASCADE, verbose_name='ItemCod')
    EnStock = models.IntegerField()
    Comprometido = models.IntegerField()
    Pedido = models.IntegerField()
    Disponible = models.IntegerField() 
    def __str__(self):
        return self.id

    class Meta:
        verbose_name = 'OWHS'

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Usuario de cuenta mayor
class OACT(models.Model):
    AcctCode = models.CharField(max_length=150, primary_key=True)
    AcctName = models.CharField(max_length=150)
    CurrTotal = models.FloatField(default=0.0, null=False)

    def __str__(self):
        return self.AcctCode

    class Meta:
        verbose_name = 'OACT'

    def toJSON(self):
        item = model_to_dict(self)
        return item

#Moneda
class Moneda(models.Model):
    idMoneda = models.IntegerField(primary_key=True)
    MonedaAbrev = models.CharField(max_length=150, null=False, blank=False)
    CambioSoles = models.FloatField(default=0.0, null=False, blank=False)
    TCDate = models.DateField()

    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
    
    def toJSON(self):
        item = model_to_dict(self)
        return item

#Solicitud de Compra
class OPRQ(models.Model):
    DocEntry = models.AutoField(primary_key=True, null=False)
    DocNum = models.IntegerField()
    Serie = models.IntegerField(null=True)
    ReqIdUser = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ReqIdUser')
    ReqCode = models.CharField(max_length=150, unique=False, verbose_name='ReqCode')
    ReqType = models.IntegerField()
    Department = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True)
    DocStatus = models.CharField(max_length=10, verbose_name='DocStatus')
    DocType = models.CharField(max_length=10, verbose_name='DocType')
    DocDate = models.DateField(verbose_name='DocDate')
    DocDueDate = models.DateField(verbose_name='DocDueDate')
    ReqDate = models.DateField(verbose_name='ReqDate', null=True)
    SystemDate = models.DateField(verbose_name='SystemDate', null=True)
    TaxCode = models.ForeignKey(OSTA, on_delete=models.CASCADE, max_length=150, null=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.CASCADE, max_length=150, null=True)
    Comments = models.CharField(max_length=150)
    Total = models.FloatField(verbose_name='Total')
    TotalImp = models.FloatField(verbose_name='TotalImpuestos')
    DocNumSAP = models.IntegerField(null=True)
    TipoDoc = models.CharField(max_length=10, verbose_name='TipoDocumentos', default='SOL')

    def __str__(self):
        return self.DocEntry
    
    class Meta:
        verbose_name = 'OPRQ'

    def toJSON(self):
        item = model_to_dict(self)
        item['DocEntry'] = format(self.DocEntry, '05d')
        item['Total'] = format(self.Total, ' .2f')
        item['TotalImp'] = format(self.TotalImp, '.2f')
        item['ReqIdUser'] = self.ReqIdUser.first_name +' '+ self.ReqIdUser.last_name if self.ReqIdUser else ''
        item['Department'] = self.Department.Name if self.Department else ''
        item['TaxCode'] = self.TaxCode.Code if self.TaxCode else ''
        item['moneda'] = self.moneda.MonedaAbrev if self.moneda else ''
        item['DocDate'] = self.DocDate.strftime('%d-%m-%Y') if self.DocDate else None
        item['DocDueDate'] = self.DocDueDate.strftime('%d-%m-%Y') if self.DocDueDate else None
        item['ReqDate'] = self.ReqDate.strftime('%d-%m-%Y') if self.ReqDate else None
        item['SystemDate'] = self.SystemDate.strftime('%d-%m-%Y') if self.SystemDate else None
        if self.DocStatus == 'P':
            item['seleccionable'] = True
        else:
            item['seleccionable'] = False 
        return item

#Detalle de compra
class PRQ1(models.Model):
    Code = models.AutoField(primary_key=True)
    NumDoc = models.ForeignKey(OPRQ, on_delete=models.CASCADE, max_length=150)
    ItemCode = models.ForeignKey(OITM, on_delete=models.CASCADE, max_length=150)
    LineVendor = models.ForeignKey(OCRD, on_delete=models.CASCADE, max_length=150)
    Currency = models.ForeignKey(Moneda, on_delete=models.CASCADE, null=True)
    Description = models.TextField()
    Quantity = models.IntegerField()
    UnidadMedida = models.ForeignKey(OUOM, on_delete=models.CASCADE, max_length=150)
    Almacen = models.ForeignKey(OWHS, on_delete=models.CASCADE, max_length=150)
    CuentaMayor = models.ForeignKey(OACT, on_delete=models.CASCADE, max_length=150)
    total = models.FloatField(default=0.0, null=False)
    idDimension = models.ForeignKey(Dimensiones, on_delete=models.CASCADE, blank=True, null=True)
    LineStatus = models.CharField(max_length=1, default='P',null=True, blank=True)
    Precio = models.FloatField(default=0.0, null=False)
    LineCount = models.IntegerField(default=0)
    LineCount_Indexado = models.IntegerField(null=True, blank=True)
    Quantity_rest = models.IntegerField(null=True, blank=True)  # Quitar el default
    total_rest = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.Code

    class Meta:
        verbose_name = 'PRQ1'
        
    def save(self, *args, **kwargs):
        # Si es un nuevo registro, inicializar Quantity_rest
        if not self.pk:  # si es una nueva instancia
            self.Quantity_rest = int(self.Quantity)  # Convertir a int
        
        # Validación para que Quantity_rest no sea negativo
        if int(self.Quantity_rest) < 0:  # Convertir a int
            raise ValueError("La cantidad restante no puede ser negativa")

        # Cálculo automático de total_rest
        self.total_rest = float(self.Precio) * float(self.Quantity_rest)  # Convertir a float

        # Código existente para LineCount
        if not self.pk:
            ultimo_line_count = PRQ1.objects.filter(NumDoc=self.NumDoc).order_by('-LineCount').first()
            if ultimo_line_count:
                self.LineCount = ultimo_line_count.LineCount + 1
            else:
                self.LineCount = 0

        super(PRQ1, self).save(*args, **kwargs)

    def toJSON(self):
        item = model_to_dict(self)
        return item


class Series(models.Model):
    Nombre = models.CharField(max_length=150, primary_key=True)
    PrimerNumero = models.IntegerField(null=False)
    NumeroSiguiente = models.IntegerField()
    UltimoNumero = models.IntegerField()
    CodigoSerie = models.IntegerField(default=75)
    DocType = models.CharField(max_length=10, verbose_name='DocType')

    def __str__(self):
        return self.Nombre

    class Meta:
        verbose_name = 'Series'
        

# ORDEN DE COMPRA
class Orden_Compra(models.Model):
    NumDoc = models.ForeignKey(OPRQ, on_delete=models.CASCADE, verbose_name="Número de Documento", null=True, blank=True) 
    Solicitante = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Solicitante")
    SystemDate = models.DateField(verbose_name='SystemDate', null=True, default=date.today)  # Asignando la fecha actual
    Serie = models.ForeignKey('series', on_delete=models.SET_NULL, null=True, verbose_name="Serie")
    DocDate = models.DateField(verbose_name='DocDate')
    DocDueDate = models.DateField(verbose_name='DocDueDate')
    ReqDate = models.DateField(verbose_name='RequestDate', null=True)
    ItemCode = models.CharField(max_length=150, null=True, blank=True, verbose_name="Código del ítem")
    ItemDescription = models.TextField(verbose_name="Descripción del ítem")
    Moneda = models.ForeignKey('moneda', on_delete=models.SET_NULL, null=True, verbose_name="Moneda")
    Quantity = models.IntegerField(verbose_name="Cantidad")
    PrecioUnitario = models.FloatField(verbose_name="Precio unitario")
    Total = models.FloatField(verbose_name="Total")
    Impuesto = models.ForeignKey('osta', on_delete=models.SET_NULL, null=True, verbose_name="Impuestos")
    Almacen = models.ForeignKey('owhs', on_delete=models.SET_NULL, null=True, verbose_name="Almacén")
    Dimension = models.ForeignKey('dimensiones', on_delete=models.SET_NULL, null=True, verbose_name="Dimensión")
    DocNumSAPoc = models.IntegerField(null=True, verbose_name="DocNumSAP Orden Compra")
    
    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"

    def __str__(self):
        return f"Orden {self.id} - {self.Solicitante.username}"

    
#ORDEN COMPRA CABECERA
class OCC(models.Model):
    DocEntryOC = models.AutoField(primary_key=True)
    DocNumOC = models.IntegerField(unique=True)
    SerieOC = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True)
    SolicitanteOC = models.ForeignKey(User, on_delete=models.CASCADE)
    DocTypeOC = models.CharField(max_length=10, default='OC')
    DocDateOC = models.DateField()
    DocDueDateOC = models.DateField()
    SystemDateOC = models.DateField(auto_now_add=True)
    ProveedorOC = models.ForeignKey(OCRD, on_delete=models.CASCADE)
    MonedaOC = models.ForeignKey(Moneda, on_delete=models.SET_NULL, null=True)
    TaxCodeOC = models.ForeignKey(OSTA, on_delete=models.SET_NULL, null=True)
    TotalOC = models.FloatField()
    TotalImpuestosOC = models.FloatField()
    CommentsOC = models.TextField(null=True, blank=True)
    DocNumSAPOC =  models.IntegerField(null=True, verbose_name="DocNumSAPOC")

    def __str__(self):
        return f"OC {self.DocNumOC}"
    
    def toJSON(self):
        return {
            'DocEntryOC': self.DocEntryOC,
            'DocNumOC': self.DocNumOC,
            'SerieOC': self.SerieOC.Nombre if self.SerieOC else None,  # Asegúrate de que 'name' sea un atributo válido
            'SolicitanteOC': self.SolicitanteOC.username,  # O el atributo que desees mostrar
            'DocTypeOC': self.DocTypeOC,
            'DocDateOC': self.DocDateOC.strftime('%d-%m-%Y'),  # Formato de fecha ISO
            'DocDueDateOC': self.DocDueDateOC.strftime('%d-%m-%Y'),
            'SystemDateOC': self.SystemDateOC.strftime('%d-%m-%Y'),
            'ProveedorOC': self.ProveedorOC.CardName if self.ProveedorOC else None,  # Asegúrate de que 'name' sea un atributo válido
            'MonedaOC': self.MonedaOC.MonedaAbrev if self.MonedaOC else None,  # Asegúrate de que 'name' sea un atributo válido
            'TaxCodeOC': self.TaxCodeOC.Code if self.TaxCodeOC else None,  # Asegúrate de que 'code' sea un atributo válido
            'TotalOC': self.TotalOC,
            'TotalImpuestosOC': self.TotalImpuestosOC,
            'CommentsOC': self.CommentsOC,
            'DocNumSAPOC': self.DocNumSAPOC,
        }

#ORDEN COMPRA DETALLE
class OCD1(models.Model):
    CodeOCD = models.AutoField(primary_key=True)
    NumDocOCD = models.ForeignKey(OCC, on_delete=models.CASCADE, related_name='detalles_oc')
    ItemCodeOCD = models.ForeignKey(OITM, on_delete=models.CASCADE)
    LineVendorOCD = models.ForeignKey(OCRD, on_delete=models.CASCADE)
    DescriptionOCD = models.TextField()
    QuantityOCD = models.IntegerField()
    UnidadMedidaOCD = models.ForeignKey(OUOM, on_delete=models.CASCADE)
    AlmacenOCD = models.ForeignKey(OWHS, on_delete=models.CASCADE)
    CuentaMayorOCD = models.ForeignKey(OACT, on_delete=models.CASCADE)
    PrecioOCD = models.FloatField()
    TotalOCD = models.FloatField()
    LineStatusOCD = models.CharField(max_length=1, default='C', null=True, blank=True)
    DimensionOCD = models.ForeignKey(Dimensiones, on_delete=models.SET_NULL, null=True)
    DocNumSAPOCD = models.IntegerField(null=True)
    BaseEntryOCD = models.IntegerField(null=True)
    BaseLineOCD = models.IntegerField(null=True)
    DocEntryOCD = models.IntegerField(null=True) 

    def __str__(self):
        return f"Detalle OC {self.NumDocOCD.DocNumOC} - {self.ItemCodeOCD.ItemCode}"

    class Meta:
        verbose_name = "Detalle de Orden de Compra"
        
    def save(self, *args, **kwargs):
        if self.TotalOCD != self.PrecioOCD * self.QuantityOCD:
            self.TotalOCD = self.PrecioOCD * self.QuantityOCD
        super().save(*args, **kwargs)
        
    def toJSON(self):
        return {
            'CodeOCD': self.CodeOCD,
            'NumDocOCD': self.NumDocOCD.DocNumOC,  # Asumiendo que quieres mostrar el número de la OC
            'ItemCodeOCD': self.ItemCodeOCD.ItemCode,  # Asumiendo que quieres mostrar el código del ítem
            'LineVendorOCD': self.LineVendorOCD.CardName if self.LineVendorOCD else None,  # Nombre del proveedor
            'DescriptionOCD': self.DescriptionOCD,
            'QuantityOCD': self.QuantityOCD,
            'UnidadMedidaOCD': self.UnidadMedidaOCD.Name if self.UnidadMedidaOCD else None,  # Nombre de la unidad de medida
            'AlmacenOCD': self.AlmacenOCD.WhsName if self.AlmacenOCD else None,  # Nombre del almacén
            'CuentaMayorOCD': self.CuentaMayorOCD.AcctName if self.CuentaMayorOCD else None,  # Nombre de la cuenta mayor
            'PrecioOCD': format(self.PrecioOCD, '.2f'),  # Formato de precio
            'TotalOCD': format(self.TotalOCD, '.2f'),  # Formato de total
            'LineStatusOCD': self.LineStatusOCD,
            'DimensionOCD': self.DimensionOCD.nombre if self.DimensionOCD else None,  # Nombre de la dimensión
            'DocNumSAPOCD': self.DocNumSAPOCD,
            'BaseEntryOCD': self.BaseEntryOCD,
            'BaseLineOCD': self.BaseLineOCD,
            'DocEntryOCD': self.DocEntryOCD,
        }
