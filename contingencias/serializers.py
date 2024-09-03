from rest_framework import serializers
from parametros.models import Contingencias,TipoContingencia


class ContingenciasSerializer(serializers.ModelSerializer):
    nombre_regional = serializers.SerializerMethodField()
    nombre_ruta = serializers.SerializerMethodField()
    tipo_contingencia =serializers.SerializerMethodField()

    class Meta:
        model = Contingencias
        fields = '__all__'
    def get_nombre_regional(self, usuario):
         # Obtén el nombre de la regional a partir de la entidad financiera
         regional = usuario.id_regional  # Supongamos que este es el campo que almacena la clave foránea
         return regional.nombre_regional if regional else None     
    def get_nombre_ruta(self, usuario):
         # Obtén el nombre de la regional a partir de la entidad financiera
         ruta = usuario.id_ruta  # Supongamos que este es el campo que almacena la clave foránea
         return ruta.nombre if ruta else None 
    def get_tipo_contingencia(self, usuario):
         # Obtén el nombre de la regional a partir de la entidad financiera
         tipo = usuario.id_tipo_contingencia  # Supongamos que este es el campo que almacena la clave foránea
         return tipo.tipo if tipo else None  
