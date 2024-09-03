from rest_framework import serializers
from django.contrib.auth.models import User,Permission
from parametros.models import Transaccion,Tarifario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class TransaccionSerializer(serializers.ModelSerializer):
    nombre_regional=serializers.SerializerMethodField()
    nombre_reten=serializers.SerializerMethodField()
    nombre_categoria=serializers.SerializerMethodField()
    nombre_ruta=serializers.SerializerMethodField()
    nombre_recaudador=serializers.SerializerMethodField()
    class Meta:
        model=Transaccion
        fields='__all__'

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

class TarifariosTransaccionSerializer(serializers.ModelSerializer):
    nombre_categoria= serializers.SerializerMethodField()
    class Meta:
        model=Tarifario
        fields=('id_tarifario','nombre_categoria','importe')
    def get_nombre_categoria(self,tarifario):
        categoria=tarifario.id_categoria
        return categoria.nombre_categoria if categoria else None
