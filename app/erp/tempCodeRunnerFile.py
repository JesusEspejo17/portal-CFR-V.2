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
    DocType = models.CharField(max_length=10, verbose_name='DocType')

    def __str__(self):
        return self.Nombre

    class Meta:
        verbose_name = 'Series'