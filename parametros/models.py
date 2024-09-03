from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from datetime import datetime
from django.core.validators import *
from django.utils import timezone

class Almacen(models.Model):
    id_almacen = models.AutoField(primary_key=True)
    fecha_creacion = models.DateField(blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    nombre_alamacen = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'almacen'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)
    baja = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_group'
    def __str__(self):
        return self.name

class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)

class AuthUser(AbstractBaseUser):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False, blank=True, null=True)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=False, blank=True, null=True)
    date_joined = models.DateTimeField(default=datetime.now)
    ci = models.IntegerField(blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    celular = models.IntegerField(blank=True, null=True)
    id_cargo = models.ForeignKey(
        'Cargo', models.DO_NOTHING, db_column='id_cargo', blank=True, null=True)
    id_regional = models.ForeignKey(
        'Regionales', models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    id_grupo = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        managed = False
        db_table = 'auth_user'
    def __str__(self):
        return self.username
    
class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)



class CajaCarril(models.Model):
    id = models.SmallAutoField(primary_key=True)
    id_disloque = models.ForeignKey('Disloque', models.DO_NOTHING, db_column='id_disloque')
    id_recaudador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_recaudador')
    id_reten = models.ForeignKey('Retenes', models.DO_NOTHING, db_column='id_reten', blank=True, null=True)
    numero_carril = models.IntegerField()
    fecha_apertura = models.DateTimeField()
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    encargado_apertura = models.CharField(max_length=100)
    observacion = models.CharField(max_length=255, blank=True, null=True)    
    total_apertura = models.DecimalField(max_digits=10, decimal_places=2)
    total_cierre_sistema = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)    
    total_cierre_recaudador = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    turno = models.CharField(max_length=30, blank=True, null=True)
    fecha_operaciones = models.DateField(blank=True, null=True)    
    anio = models.CharField(max_length=10, blank=True, null=True)
    mes = models.CharField(max_length=15, blank=True, null=True)
    dia = models.CharField(max_length=15, blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    estado = models.CharField(max_length=50)
    id_turno = models.SmallIntegerField(blank=True, null=True)
    consolidado = models.CharField(max_length=20, blank=True, null=True)
    descripcion_de_observacion = models.CharField(max_length=255, blank=True, null=True)
    excedente = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_comment='exedente de recaudacion')

    class Meta:
        managed = False
        db_table = 'caja_carril'


class Cargo(models.Model):
    descripcion = models.CharField(max_length=80)
    estado = models.CharField(max_length=20)
    baja = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    nombre_cargo = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cargo'

    def __str__(self):
        return self.descripcion

class Carril(models.Model):
    id_carril = models.AutoField(primary_key=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    ruta = models.CharField(max_length=50)
    baja = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'carril'


class CategoriaVehiculo(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)
    estado = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=80, blank=True, null=True)
    imagen = models.ImageField('imageret', upload_to='ImgCategoriaV/', default="ImgCategoriaV/modelo.png")
    baja = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categoria_vehiculo'


class Ciclo(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    fecha_inicio = models.DateField(blank=True, null=True, db_comment='fecha inicio del turno')
    fecha_fin = models.DateField(blank=True, null=True, db_comment='fecha fin del turno')
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    id_reten = models.ForeignKey('Retenes', models.DO_NOTHING, db_column='id_reten', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    finalizado = models.BooleanField(blank=True, null=True, db_comment='indica que el ciclo a finalizado')
    id_carril = models.SmallIntegerField(blank=True, null=True)
    tipo_carril = models.CharField(max_length=4, blank=True, null=True)
    timestamp_ciclo = models.DateTimeField(blank=True, null=True)
    estado_via = models.CharField(max_length=3, blank=True, null=True)
    estado_ciclo = models.CharField(max_length=3, blank=True, null=True)
    id_recaudador = models.SmallIntegerField(blank=True, null=True)
    rev_estado = models.CharField(max_length=3, blank=True, null=True)
    id_revisor = models.IntegerField(blank=True, null=True)
    id_revisor2 = models.SmallIntegerField(blank=True, null=True)
    anormal = models.BooleanField(blank=True, null=True)
    turnoasociado = models.BooleanField(blank=True, null=True)
    id_turno = models.ForeignKey('Turnos', models.DO_NOTHING, db_column='id_turno', blank=True, null=True)
    timestamp_turno = models.DateTimeField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True, db_comment='hora iniciado del turno')
    hora_fin = models.TimeField(blank=True, null=True, db_comment='hora finalizado del turno')

    class Meta:
        managed = False
        db_table = 'ciclo'


class Colores(models.Model):
    id_color = models.AutoField(primary_key=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'colores'

class TipoContingencia(models.Model):
    tipo = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_contingencia'

class Contingencias(models.Model):
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    id_ruta = models.ForeignKey('Rutas', models.DO_NOTHING, db_column='id_ruta', blank=True, null=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    id_tipo_contingencia = models.ForeignKey('TipoContingencia', models.DO_NOTHING, db_column='id_tipo_contingencia', blank=True, null=True)
    fecha_ini = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    hora_ini = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    foto1 = models.ImageField('imageret', upload_to='ImgContingencias/', default=None)
    foto2 = models.ImageField('imageret', upload_to='ImgContingencias/', default=None)
    foto3 = models.ImageField('imageret', upload_to='ImgContingencias/', default=None)
    foto4 = models.ImageField('imageret', upload_to='ImgContingencias/', default=None)
    punto_contingencia = models.CharField(max_length=100)
    resumen_hecho = models.CharField(max_length=40, blank=True, null=True)
    estado = models.CharField(max_length=20)
    baja = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'contingencias'
    def __str__(self):
        return self.resumen_hecho
    
class Cuenta(models.Model):
    id_cuenta = models.IntegerField(primary_key=True)
    tipo = models.CharField(max_length=30)
    saldo = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_inicio = models.DateField()
    estado = models.CharField(max_length=30)
    baja = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    fecha_fin = models.DateField(blank=True, null=True)
    nombre_entidad = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cuenta'


class CuentasBancarias(models.Model):
    id_cuentas = models.AutoField(primary_key=True)
    numero_cuenta = models.CharField(max_length=150, blank=True, null=True)
    nombre_banco = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cuentas_bancarias'


class DepositoDetalle(models.Model):
    id_deposito_detalle = models.IntegerField(primary_key=True)
    id_deposito = models.ForeignKey('EntidadDepositos', models.DO_NOTHING, db_column='id_deposito', blank=True, null=True)
    nombre = models.CharField(max_length=30)
    appaterno = models.CharField(max_length=30)
    apmaterno = models.CharField(max_length=30)
    ci = models.IntegerField()
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    tipo_moneda = models.CharField(max_length=20)
    cuenta_origen = models.IntegerField(blank=True, null=True)
    cuenta_destino = models.IntegerField(blank=True, null=True)
    fecha = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'deposito_detalle'


class Depositos(models.Model):
    id = models.SmallAutoField(primary_key=True)
    nombre_cuenta = models.CharField(max_length=150, blank=True, null=True)
    nombre_depositante = models.CharField(max_length=100, blank=True, null=True)
    celular = models.IntegerField(blank=True, null=True)
    monto_depositado = models.FloatField(blank=True, null=True)
    comprobante_deposito = models.FileField(
        upload_to="depositos/", default="depositos/archivoBlanco.pdf", blank=True)
    fecha_deposito = models.DateTimeField(blank=True, null=True)
    tipo_pago = models.CharField(max_length=50, blank=True, null=True)
    cuenta_bancaria = models.BigIntegerField(blank=True, null=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    id_cuenta = models.ForeignKey(Cuenta, models.DO_NOTHING, db_column='id_cuenta', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'depositos'


class DetalleLicitacion(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    licitacion = models.ForeignKey('Licitaciones', models.DO_NOTHING, blank=True, null=True)
    valor = models.ForeignKey('Valores', models.DO_NOTHING, blank=True, null=True)
    color = models.ForeignKey(Colores, models.DO_NOTHING, blank=True, null=True)
    boletos_del = models.CharField(max_length=255)
    boletos_al = models.CharField(max_length=255, blank=True, null=True)
    cantidad_solicitada = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=255, blank=True, null=True)
    fecha_entrega = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detalle_licitacion'


class Disloque(models.Model):
    id = models.SmallAutoField(primary_key=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_creacion = models.DateField()
    estado = models.CharField(max_length=30)
    responsable_disloque = models.CharField(max_length=100, blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disloque'


class DisloqueDetalle(models.Model):
    #numero_disloque = models.ForeignKey(Disloque, models.DO_NOTHING, db_column='numero_disloque')
    numero_disloque=models.IntegerField(blank=True, null=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional')
    id_reten = models.ForeignKey('Retenes', models.DO_NOTHING, db_column='id_reten')
    id_recaudador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_recaudador')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_creacion = models.DateField()
    estado = models.CharField(max_length=30)
    responsable_disloque = models.CharField(max_length=100, blank=True, null=True)
    responsable_reten = models.CharField(max_length=20, blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disloque_detalle'


class DistanciaRetenReten(models.Model):
    id_distancia = models.AutoField(primary_key=True)
    reten_origen = models.CharField(max_length=40, blank=True, null=True)
    reten_destino = models.CharField(max_length=40, blank=True, null=True)
    distancia_reten_reten = models.CharField(max_length=30, blank=True, null=True)
    ciudad_origen = models.CharField(max_length=40, blank=True, null=True)
    cuidad_destino = models.CharField(max_length=40, blank=True, null=True)
    distancia_ciudad_cuidad = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'distancia_reten_reten'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EntidadContrato(models.Model):
    id_contrato = models.AutoField(primary_key=True)
    id_entidad_empresa = models.ForeignKey('EntidadEmpresa', models.DO_NOTHING, db_column='id_entidad_empresa', blank=True, null=True)
    id_entidad_persona = models.ForeignKey('EntidadPersona', models.DO_NOTHING, db_column='id_entidad_persona', blank=True, null=True)
    doc_contrato = models.FileField(
        upload_to="contratosDocs/", default="contratosDocs/archivoBlanco.pdf", blank=True)
    fecha_ini_contrato = models.DateField()
    fecha_fin_contrato = models.DateField()
    baja_contrato = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_seguimiento = models.ForeignKey('Seguimiento', models.DO_NOTHING, db_column='id_seguimiento', blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'entidad_contrato'


class EntidadDepositos(models.Model):
    id_deposito = models.AutoField(primary_key=True)
    id_cuenta = models.ForeignKey(Cuenta, models.DO_NOTHING, db_column='id_cuenta', blank=True, null=True)
    tipo_deposito = models.CharField(max_length=30)
    monto_deposito = models.FloatField()
    fecha_deposito = models.DateField()
    hora_deposito = models.TimeField()
    comprobante_deposito = models.CharField(max_length=50)
    estado = models.CharField(max_length=30)
    baja = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'entidad_depositos'


class EntidadEmpresa(models.Model):
    id_entidad_empresa = models.AutoField(primary_key=True)
    id_punto_empadronamiento = models.ForeignKey('PuntoEmpadronamiento', models.DO_NOTHING, db_column='id_punto_empadronamiento', blank=True, null=True)
    id_cuenta = models.ForeignKey(Cuenta, models.DO_NOTHING, db_column='id_cuenta', blank=True, null=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional')
    razon_social = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=150)
    sector = models.CharField(max_length=200)
    tipo_empresa = models.CharField(max_length=100)
    correo = models.CharField(max_length=50)
    interno_1 = models.IntegerField(blank=True, null=True)
    interno_2 = models.IntegerField(blank=True, null=True)
    telefono = models.IntegerField(blank=True, null=True)
    celular = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    nit = models.BigIntegerField(blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entidad_empresa'


class EntidadFinanciera(models.Model):
    id_entidad = models.AutoField(primary_key=True)
    nombre_entidad = models.CharField(max_length=100)
    acronimo_entidad = models.CharField(max_length=20)
    direccion = models.CharField(max_length=20)
    telefono = models.IntegerField(blank=True, null=True)
    celular = models.IntegerField()
    rubro = models.CharField(max_length=50)
    baja = models.CharField(max_length=20)
    estado = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entidad_financiera'


class EntidadPersona(models.Model):
    id_entidad_persona = models.AutoField(primary_key=True)
    id_cuenta = models.ForeignKey(Cuenta, models.DO_NOTHING, db_column='id_cuenta', blank=True, null=True)
    id_punto_empadronamiento = models.ForeignKey('PuntoEmpadronamiento', models.DO_NOTHING, db_column='id_punto_empadronamiento', blank=True, null=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional')
    nombre = models.CharField(max_length=30)
    ap_paterno = models.CharField(max_length=20)
    ap_materno = models.CharField(max_length=20, blank=True, null=True)
    ci_persona = models.IntegerField()
    direccion = models.CharField(max_length=100)
    celular = models.IntegerField()
    telefono = models.IntegerField(blank=True, null=True)
    ciudad = models.CharField(max_length=30)
    correo = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    baja = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entidad_persona'


class EntregaDetalle(models.Model):
    id_entregadetalle = models.AutoField(primary_key=True)
    detalle_licitacion = models.ForeignKey(DetalleLicitacion, models.DO_NOTHING, blank=True, null=True)
    fecha_remision = models.DateField(blank=True, null=True)
    cantidad_recibida = models.IntegerField(blank=True, null=True)
    saldo_pendiente = models.IntegerField(blank=True, null=True)
    recibir_boleto_del = models.IntegerField(blank=True, null=True)
    recibir_boleto_al = models.IntegerField(blank=True, null=True)
    almacen = models.ForeignKey(Almacen, models.DO_NOTHING, blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entrega_detalle'


class Imprentas(models.Model):
    id_imprenta = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    telefono = models.IntegerField(blank=True, null=True)
    celular = models.IntegerField(blank=True, null=True)
    persona_contacto = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    baja = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'imprentas'


class LicitacionEntrega(models.Model):
    id_entregal = models.AutoField(primary_key=True)
    detalle_licitacion = models.ForeignKey(DetalleLicitacion, models.DO_NOTHING, blank=True, null=True)
    almacen = models.ForeignKey(Almacen, models.DO_NOTHING, blank=True, null=True)
    fecha_entregal = models.DateField(blank=True, null=True)
    recibir_boleto_del = models.IntegerField(blank=True, null=True)
    recibir_boleto_al = models.IntegerField(blank=True, null=True)
    observacionl = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'licitacion_entrega'


class Licitaciones(models.Model):
    id_licitaciones = models.AutoField(primary_key=True)
    imprenta = models.ForeignKey(Imprentas, models.DO_NOTHING, blank=True, null=True)
    nro_contrato = models.CharField(max_length=255)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    fechacreacion = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'licitaciones'


class Localidad(models.Model):
    id_localidad = models.AutoField(primary_key=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    estado = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    baja = models.IntegerField(blank=True, null=True)
    nombre_localidad = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'localidad'


class ParametrosDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    uploadedfile = models.CharField(db_column='uploadedFile', max_length=100)  # Field name made lowercase.
    datetimeofupload = models.DateTimeField(db_column='dateTimeOfUpload')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'parametros_document'


class ParametrosGenerales(models.Model):
    id_parametros = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    direccion = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.IntegerField()
    celular = models.IntegerField(blank=True, null=True)
    regional = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'parametros_generales'


class PuntoEmpadronamiento(models.Model):
    id_punto_empadronamiento = models.AutoField(primary_key=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional')
    direccion = models.CharField(max_length=70)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    baja = models.IntegerField(blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'punto_empadronamiento'


class RecargaSaldo(models.Model):
    nombre_cuenta = models.CharField(max_length=150, blank=True, null=True)
    nombre_depositante = models.CharField(max_length=150, blank=True, null=True)
    celular = models.TextField(blank=True, null=True)  # This field type is a guess.
    monto_depositado = models.FloatField(blank=True, null=True)
    comprobante_deposito = models.CharField(max_length=200, blank=True, null=True)
    fecha_deposito = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recarga_saldo'


class Regionales(models.Model):
    nombre_regional = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=80, blank=True, null=True)
    estado = models.CharField(max_length=20)
    telefono = models.IntegerField()
    direccion = models.CharField(max_length=100)
    baja = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'regionales'
    def __str__(self):
     return self.nombre_regional


class Retenes(models.Model):
    id_reten = models.AutoField(primary_key=True)
    id_regional = models.ForeignKey(Regionales, models.DO_NOTHING, db_column='id_regional')
    nombre_reten = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    hubicacion = models.CharField(max_length=100, blank=True, null=True)
    doc_creacion = models.CharField(max_length=100, blank=True, null=True)
    tiene_antena = models.CharField(max_length=20, blank=True, null=True)
    doc_resolucion = models.CharField(max_length=100, blank=True, null=True)
    latitud = models.CharField(max_length=100, blank=True, null=True)
    longitud = models.CharField(max_length=100, blank=True, null=True)
    compartido_regional = models.CharField(max_length=50, blank=True, null=True)
    convenio_abc = models.CharField(max_length=50, blank=True, null=True)
    baja = models.SmallIntegerField()
    nombre_creacion = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    id_tipo_reten = models.ForeignKey('TipoReten', models.DO_NOTHING, db_column='id_tipo_reten', blank=True, null=True)
    id_ruta = models.ForeignKey('Rutas', models.DO_NOTHING, db_column='id_ruta', blank=True, null=True)
    num_carril = models.IntegerField(blank=True, null=True)
    localidad = models.ForeignKey(Localidad, models.DO_NOTHING, blank=True, null=True)
    regionalcompartida = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'retenes'


class RutaReten(models.Model):
    id_ruta = models.SmallIntegerField(primary_key=True)
    id_regional = models.SmallIntegerField()
    id_reten = models.SmallIntegerField()
    baja = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ruta_reten'
        unique_together = (('id_ruta', 'id_regional', 'id_reten'),)


class Rutas(models.Model):
    id_ruta = models.AutoField(primary_key=True)
    id_regional = models.ForeignKey(Regionales, models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    nombre = models.CharField(max_length=30)
    estado = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    punto_inicio = models.CharField(max_length=150, blank=True, null=True)
    punto_fin = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rutas'


class Seguimiento(models.Model):
    id_persona = models.ForeignKey(EntidadPersona, models.DO_NOTHING, db_column='id_persona', blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    id_entidad_empresa = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seguimiento'


class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    cod_tag = models.CharField(unique=True, max_length=200)
    asignado = models.CharField(max_length=20)
    id_cuenta = models.IntegerField(blank=True, null=True)
    nombre_entidad = models.CharField(max_length=150, blank=True, null=True)
    placa = models.CharField(max_length=30, blank=True, null=True)
    estado = models.CharField(max_length=30, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tags'


class Tarifario(models.Model):
    id_tarifario = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(CategoriaVehiculo, models.DO_NOTHING, db_column='id_categoria')
    id_regional = models.ForeignKey(Regionales, models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    id_reten = models.ForeignKey(Retenes, models.DO_NOTHING, db_column='id_reten', blank=True, null=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    reten_origen = models.CharField(max_length=80, blank=True, null=True)
    reten_destino = models.CharField(max_length=80, blank=True, null=True)
    localidad_origen = models.CharField(max_length=100, blank=True, null=True)
    localidad_destino = models.CharField(max_length=100, blank=True, null=True)
    rutas = models.CharField(max_length=50, blank=True, null=True)
    sentido = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tarifario'


class TipoReten(models.Model):
    descripcion = models.CharField(max_length=50, blank=True, null=True)
    baja = models.SmallIntegerField()
    fecha = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_reten'


class Transaccion(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    id_ciclo = models.ForeignKey(Ciclo, models.DO_NOTHING, db_column='id_ciclo', blank=True, null=True)
    id_cuenta = models.ForeignKey(Cuenta, models.DO_NOTHING, db_column='id_cuenta', blank=True, null=True)
    id_regional = models.ForeignKey(Regionales, models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    id_reten = models.ForeignKey(Retenes, models.DO_NOTHING, db_column='id_reten', blank=True, null=True)
    id_carril = models.SmallIntegerField(blank=True, null=True)
    tipo_carril = models.CharField(max_length=70, blank=True, null=True)
    id_categoria = models.ForeignKey(CategoriaVehiculo, models.DO_NOTHING, db_column='id_categoria', blank=True, null=True)
    id_ruta = models.ForeignKey(Rutas, models.DO_NOTHING, db_column='id_ruta', blank=True, null=True)
    localidad_inicio = models.CharField(max_length=100, blank=True, null=True)
    localidad_fin = models.CharField(max_length=100, blank=True, null=True)
    importe_recaudador = models.DecimalField(max_digits=10, decimal_places=2)
    importe_telepeaje = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    importe_revision = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tipo_recibo = models.CharField(max_length=100, blank=True, null=True)
    tipo_pago = models.CharField(max_length=100, blank=True, null=True)
    nombre_revisor = models.CharField(max_length=100, blank=True, null=True)
    comentario_revisor = models.CharField(max_length=255, blank=True, null=True)
    id_recaudador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_recaudador', blank=True, null=True)
    id_turno = models.CharField(max_length=100, blank=True, null=True)
    id_grupo_exento = models.SmallIntegerField(blank=True, null=True)
    placa = models.CharField(max_length=255, blank=True, null=True)
    numero_ejes_inicio = models.SmallIntegerField(blank=True, null=True)
    numero_ejes_salida = models.SmallIntegerField(blank=True, null=True)
    ancho_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    alto_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    numero_remolques = models.SmallIntegerField(blank=True, null=True)
    clase_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    imagen_frontal = models.ImageField('imageret', upload_to='ImgVehiculos/', default="")
    imagen_lateral = models.ImageField('imageret', upload_to='ImgVehiculos/', default="")
    #imagen_frontal = models.CharField(max_length=100, blank=True, null=True)
    #imagen_lateral = models.CharField(max_length=100, blank=True, null=True)
    tag_leido = models.CharField(max_length=100, blank=True, null=True)
    id_denuncia = models.SmallIntegerField(blank=True, null=True)
    mensaje_panel = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_caja_carril = models.ForeignKey(CajaCarril, models.DO_NOTHING, db_column='id_caja_carril', blank=True, null=True)
    anio = models.SmallIntegerField(blank=True, null=True)
    mes = models.SmallIntegerField(blank=True, null=True)
    dia = models.SmallIntegerField(blank=True, null=True)
    sis_dist_12ejes = models.IntegerField(blank=True, null=True)
    sis_nro_llantasdobles = models.IntegerField(blank=True, null=True)
    sis_nro_llantasdobles2 = models.IntegerField(blank=True, null=True)
    sis_motocicleta = models.BooleanField(blank=True, null=True)
    rev_categoria = models.IntegerField(blank=True, null=True)
    rev_placa = models.CharField(blank=True, null=True)
    rev_revision_estado = models.CharField(blank=True, null=True)
    rev_estado = models.CharField(blank=True, null=True)
    id_revisor = models.IntegerField(blank=True, null=True)
    codigo_boleto = models.CharField(blank=True, null=True)
    saldo_restante = models.DecimalField(max_digits=10, decimal_places=2)
    numero_roseta = models.CharField(max_length=100, blank=True, null=True)
  
    class Meta:
        managed = False
        db_table = 'transaccion'


class UsuarioLog(models.Model):
    id_usuario = models.IntegerField()
    user_name = models.CharField(max_length=100)
    tabla = models.CharField(max_length=70)
    accion = models.CharField(max_length=100)
    ip = models.CharField(max_length=100, blank=True, null=True)
    fecha_hora = models.DateTimeField()
    id_operacion = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'usuario_log'


class Valores(models.Model):
    id_valor = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    observacion = models.CharField(max_length=200, blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'valores'


class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    placa = models.CharField(max_length=20)
    marca = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    clase = models.CharField(max_length=50)
    modelo = models.IntegerField()
    color = models.CharField(max_length=30)
    cilindrada = models.IntegerField()
    cap_carga = models.CharField(max_length=50, blank=True, null=True)
    nro_ejes = models.IntegerField(blank=True, null=True)
    imagen_fronal_vehiculo = models.ImageField(
        'imageret', upload_to='ImgVehiculos/', default="ImgCategoriaV/modelo.png")
    imagen_lateral_vehiculo = models.ImageField('imageret', upload_to='ImgVehiculos/', default="ImgCategoriaV/modelo.png")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    baja = models.IntegerField(blank=True, null=True)
    id_cuenta = models.ForeignKey(
        Cuenta, models.DO_NOTHING, db_column='id_cuenta', blank=True, null=True)
    id_categoria = models.ForeignKey(
        CategoriaVehiculo, models.DO_NOTHING, db_column='id_categoria', blank=True, null=True)
    tag = models.CharField(max_length=200, blank=True, null=True)
    numero_roceta = models.CharField(max_length=100, blank=True, null=True, db_comment='numero de roceta con la que cuenta el vehiculo')
    estado = models.CharField(max_length=20,default='habilitado',blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vehiculo'

class EntregaDetalleAcumulado(models.Model):
    id_edacumulado = models.AutoField(primary_key=True)
    nroentrega = models.IntegerField(blank=True, null=True)
    entrega_detalle = models.ForeignKey(EntregaDetalle, models.DO_NOTHING, blank=True, null=True)
    recibir_boleto_deld = models.IntegerField(blank=True, null=True)
    recibir_boleto_ald = models.IntegerField(blank=True, null=True)
    cantidad_recibida = models.IntegerField(blank=True, null=True)
    saldopendiente = models.IntegerField(blank=True, null=True)
    fecha_entregal = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entrega_detalle_acumulado'
class CierreCaja(models.Model):
    id_recaudador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_recaudador', blank=True, null=True)
    id_caja_carril = models.ForeignKey(CajaCarril, models.DO_NOTHING, db_column='id_caja_carril', blank=True, null=True)
    id_regional = models.ForeignKey('Regionales', models.DO_NOTHING, db_column='id_regional', blank=True, null=True)
    id_reten = models.ForeignKey('Retenes', models.DO_NOTHING, db_column='id_reten', blank=True, null=True)
    carril = models.SmallIntegerField(blank=True, null=True)
    turno = models.CharField(max_length=40, blank=True, null=True)
    nombre_categoria = models.CharField(max_length=100, blank=True, null=True)
    importe_categoria=models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    cantidad_transacciones = models.SmallIntegerField(blank=True, null=True)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    fecha_operaciones = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cierre_caja'
class CierreCajaTags(models.Model):
    id_recaudador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_recaudador', blank=True, null=True)
    id_caja_carril = models.ForeignKey(CajaCarril, models.DO_NOTHING, db_column='id_caja_carril', blank=True, null=True)
    regional = models.CharField(max_length=20, blank=True, null=True)
    reten = models.CharField(max_length=30, blank=True, null=True)
    carril = models.SmallIntegerField(blank=True, null=True)
    turno = models.CharField(max_length=40, blank=True, null=True)
    nombre_categoria = models.CharField(max_length=100, blank=True, null=True)
    cantidad_transacciones = models.SmallIntegerField(blank=True, null=True)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    importe_categoria = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fecha_operaciones = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cierre_caja_tags'

class Meses(models.Model):
    mes = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'meses'
    def __str__(self):
        return self.mes
    
class Menu(models.Model):
    id_menu =models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    ruta = models.CharField(max_length=255, blank=True, null=True)
    icono = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    fid_menu = models.IntegerField(blank=True, null=True)
    es_menu = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu'

class MenuGroup(models.Model):
    id_group = models.ForeignKey(AuthGroup, models.DO_NOTHING, db_column='id_group', blank=True, null=True)
    id_menu =models.ForeignKey(Menu, models.DO_NOTHING, db_column='id_menu', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu_group'        

class ReceptorDatos(models.Model):
    tag_leido = models.CharField(max_length=100, blank=True, null=True, db_comment='codigo recibido de los dispositivos')
    placa = models.CharField(max_length=20, blank=True, null=True)
    numero_ejes_inicio = models.SmallIntegerField(blank=True, null=True)
    numero_ejes_salida = models.SmallIntegerField(blank=True, null=True)
    ancho_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    alto_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    numero_remolques = models.SmallIntegerField(blank=True, null=True)
    clase_vehiculo = models.CharField(max_length=100, blank=True, null=True)
    imagen_frontal = models.CharField(max_length=100, blank=True, null=True)
    imagen_lateral = models.CharField(max_length=100, blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    tipo = models.SmallIntegerField(blank=True, null=True, db_comment='si es tag o roceta')

    class Meta:
        managed = False
        db_table = 'receptor_datos'

class Turnos(models.Model):
    id_turno =models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=32, blank=True, null=True)
    horainicio = models.CharField(max_length=6, blank=True, null=True)
    grupo_turno = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'turnos'        

class IntentosCierre(models.Model):
    id_caja_carril = models.SmallIntegerField(blank=True, null=True)
    intentos_cierre = models.SmallIntegerField(blank=True, null=True)
    id_recaudador = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'intentos_cierre'

class DeudaRecaudador(models.Model):
    fecha = models.DateField(blank=True, null=True)
    reten = models.CharField(max_length=50, blank=True, null=True)
    turno = models.CharField(max_length=40, blank=True, null=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nombre_usuario = models.CharField(max_length=100, blank=True, null=True)
    regional = models.CharField(max_length=40, blank=True, null=True)
    id_caja_carril = models.ForeignKey(CajaCarril, models.DO_NOTHING, db_column='id_caja_carril', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deuda_recaudador'

class Monitor(models.Model):
    id_categoria = models.SmallIntegerField(blank=True, null=True)
    nombre_categoria = models.CharField(max_length=100, blank=True, null=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cantidad = models.SmallIntegerField(blank=True, null=True)
    importe_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'monitor'


class MonitorTotal(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_operaciones = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'monitor_total'

class CicloTransacciones(models.Model):
    cantidad = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ciclo_transacciones'