from rest_framework import serializers
from parametros.models import PuntoEmpadronamiento
from parametros.models import Cuenta, EntidadPersona, EntidadEmpresa, EntidadContrato, Depositos, Tags, Vehiculo

class PuntoEmpadronamientoSerializer(serializers.ModelSerializer):
    nombre_regional = serializers.CharField(source='id_regional.nombre_regional', read_only=True)

    class Meta:
        model = PuntoEmpadronamiento
        fields = '__all__'


class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = '__all__'  # O lista los campos que desees serializar

class CuentaDetalleSerializer(serializers.Serializer):
    tipo = serializers.CharField(max_length=30)
    saldo = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    estado = serializers.CharField(max_length=30)



class EntidadPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntidadPersona
        fields = '__all__'  # O lista los campos que desees serializar


class EntidadEmpresaSerializer(serializers.ModelSerializer):
    nombre_regional = serializers.SerializerMethodField()
    class Meta:
        model = EntidadEmpresa
        fields = '__all__'  # O lista los campos que desees serializar
    def get_nombre_regional(self, entidad_empresa):
        # Obtén el nombre de la regional a partir de la entidad financiera
        regional = entidad_empresa.id_regional  # Supongamos que este es el campo que almacena la clave foránea
        return regional.nombre_regional if regional else None  



class EntidadContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntidadContrato
        fields = '__all__'  # O lista los campos que desees serializar



class DepositosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depositos
        fields = '__all__'  # O lista los campos que desees serializar



class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'  # O lista los campos que desees serializar


class VehiculoSerializer(serializers.ModelSerializer):
    nombre_categoria = serializers.SerializerMethodField()
    class Meta:
        model = Vehiculo
        fields = '__all__'  # O lista los campos que desees serializar
    def get_nombre_categoria(self, vehiculo):
        # Obtén el nombre de la regional a partir de la entidad financiera
        categoria = vehiculo.id_categoria  # Supongamos que este es el campo que almacena la clave foránea
        return categoria.nombre_categoria if categoria else None       

class VehiculoDetalleSerializer(serializers.Serializer): 
    placa = serializers.CharField(max_length=20)
    marca = serializers.CharField(max_length=50)
    tipo = serializers.CharField(max_length=20)
    clase = serializers.CharField(max_length=20)
    modelo = serializers.IntegerField()
    color = serializers.CharField(max_length=30)
    cilindrada = serializers.IntegerField()
    cap_carga = serializers.CharField(max_length=50)
    nro_ejes = serializers.IntegerField()
    baja = serializers.IntegerField()
    id_usuario = serializers.IntegerField()
    id_cuenta = serializers.IntegerField()
    id_categoria = serializers.IntegerField()

    
