from rest_framework import serializers
from parametros.models import CategoriaVehiculo,Tarifario,Regionales,Retenes,AuthUser,Meses,Transaccion,Monitor

class CategoriaTransaccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoriaVehiculo
        fields = ('id_categoria','nombre_categoria')

class TarifarioTransaccionSerializer(serializers.ModelSerializer):
    id_categoria=serializers.SerializerMethodField()
    nombre_categoria=serializers.SerializerMethodField()
    class Meta:
        model =Tarifario
        fields = ('id_tarifario','id_categoria','importe','localidad_origen','localidad_destino','nombre_categoria')
    def get_id_categoria(self,tarifario):
        categoria= tarifario.id_categoria
        return categoria.id_categoria if categoria else None 
    def get_nombre_categoria(self, tarifario):
        categoria=tarifario.id_categoria
        return categoria.nombre_categoria if categoria else None  
class RegionalesReportesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Regionales
        fields=('id','nombre_regional')

class RetenesReportesSerializer(serializers.ModelSerializer):
    class Meta:
        model= Retenes
        fields=('id_reten','id_regional','nombre_reten') 
        
class UsuariosReportesSerializer(serializers.ModelSerializer):
    class Meta:
        model= AuthUser
        fields=('id','username') 
class MesesReportesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Meses
        fields='__all__'

class Transaciones_Tag_Serializer(serializers.ModelSerializer):
    nombre_regional=serializers.SerializerMethodField()
    nombre_reten=serializers.SerializerMethodField()
    class Meta:
        model=Transaccion
        fields=('id','id_cuenta','id_regional','id_reten','id_carril','tipo_carril','id_ruta','localidad_inicio','localidad_fin','importe_telepeaje','tipo_pago','fecha','saldo_restante','nombre_regional','nombre_reten')
    def get_nombre_regional(self,transaccion):
        regional=transaccion.id_regional
        return regional.nombre_regional if regional else None
    def get_nombre_reten(self,transaccion):
        reten=transaccion.id_reten
        return reten.nombre_reten if reten else None
class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Monitor
        fields='__all__'

class TransaccionSerializer(serializers.ModelSerializer):
    nombre_regional=serializers.SerializerMethodField()
    nombre_reten=serializers.SerializerMethodField()
    nombre_categoria=serializers.SerializerMethodField()
    nombre_ruta=serializers.SerializerMethodField()
    nombre_recaudador=serializers.SerializerMethodField()
    class Meta:
        model=Transaccion
        fields=('codigo_boleto','nombre_regional','nombre_reten','nombre_categoria','nombre_ruta','nombre_recaudador','id_carril','localidad_inicio','localidad_fin','importe_recaudador','fecha')

    def get_nombre_regional(self,transaccion):
        regional=transaccion.id_regional
        return regional.nombre_regional if regional else None
    def get_nombre_reten(self,transaccion):
        reten=transaccion.id_reten
        return reten.nombre_reten if reten else None
    def get_nombre_categoria(self,transaccion):
        categoria=transaccion.id_categoria
        return categoria.nombre_categoria if categoria else None
    def get_nombre_ruta(self, transaccion):
        ruta=transaccion.id_ruta
        return ruta.nombre if ruta else None
    def get_nombre_recaudador(self,transaccion):
        recaudador=transaccion.id_recaudador
        return recaudador.username if recaudador else None