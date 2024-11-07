from django.db import models

from user.models import User
from django.forms import model_to_dict

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
    def __str__(self):
        return self.Code

    class Meta:
        verbose_name = 'PRQ1'

    def toJSON(self):
        item = model_to_dict(self)
        return item


class Series(models.Model):
    Nombre = models.CharField(max_length=150, primary_key=True)
    PrimerNumero = models.IntegerField(null=False)
    NumeroSiguiente = models.IntegerField()
    UltimoNumero = models.IntegerField()
    CodigoSerie = models.IntegerField(default=75)

    def __str__(self):
        return self.Nombre

    class Meta:
        verbose_name = 'Series'