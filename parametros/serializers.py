from rest_framework import serializers
from .models import Regionales, Retenes,CategoriaVehiculo,Tarifario,Rutas,Cargo,EntidadFinanciera,Localidad, CuentasBancarias, Turnos


class RegionalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regionales
        fields = '__all__'
        
class RetenesSerializer(serializers.ModelSerializer):
    nombre_regional = serializers.SerializerMethodField()
    nombre_ruta = serializers.SerializerMethodField()
    class Meta:
        model = Retenes
        fields = '__all__'
    def get_nombre_regional(self, retenes):
        # Obtén el nombre de la regional a partir de la entidad financiera
        regional = retenes.id_regional  # Supongamos que este es el campo que almacena la clave foránea
        return regional.nombre_regional if regional else None
    def get_nombre_ruta(self, retenes):
        # Obtén el nombre de la regional a partir de la entidad financiera
        rutas = retenes.id_ruta  # Supongamos que este es el campo que almacena la clave foránea
        return rutas.nombre if rutas else None

class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaVehiculo
        fields = '__all__'

class TarifariosSerializer(serializers.ModelSerializer):
    nombre_categoria = serializers.SerializerMethodField()
    nombre_regional = serializers.SerializerMethodField()
    nombre_reten = serializers.SerializerMethodField()

    class Meta:
        model = Tarifario
        fields = '__all__'

    def get_nombre_categoria(self, tarifario):
        # Obtén el nombre de la regional a partir de la entidad financiera
        categoria = tarifario.id_categoria  # Supongamos que este es el campo que almacena la clave foránea
        return categoria.nombre_categoria if categoria else None
    
    def get_nombre_regional(self, tarifario):       
        regional = tarifario.id_regional
        return regional.nombre_regional if regional else None
    
    def get_nombre_reten(self, tarifario):        
        reten = tarifario.id_reten
        return reten.nombre_reten if reten else None
    
class RutasSerializer(serializers.ModelSerializer):
    nombre_regional = serializers.SerializerMethodField()
    class Meta:
        model = Rutas
        fields = '__all__'
    def get_nombre_regional(self, ruta):       
        regional = ruta.id_regional
        return regional.nombre_regional if regional else None

class CargosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'

class EntidadFinancieraSerializer(serializers.ModelSerializer):
    nombre_regional = serializers.SerializerMethodField()
    class Meta:
        model = EntidadFinanciera
        fields = '__all__'

    def get_nombre_regional(self, entidad_financiera):
        # Obtén el nombre de la regional a partir de la entidad financiera
        regional = entidad_financiera.id_regional  # Supongamos que este es el campo que almacena la clave foránea
        return regional.nombre_regional if regional else None

class LocalidadSerializer(serializers.ModelSerializer):
    nombre_regional = serializers.SerializerMethodField()
    class Meta:
        model = Localidad
        fields = '__all__'
    def get_nombre_regional(self, localidad):
        # Obtén el nombre de la regional a partir de la entidad financiera
        regional = localidad.id_regional  # Supongamos que este es el campo que almacena la clave foránea
        return regional.nombre_regional if regional else None

class CuentasBancariasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentasBancarias
        fields = '__all__'


class TurnosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turnos
        fields = '__all__'        