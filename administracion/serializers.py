from rest_framework import serializers
from django.contrib.auth.models import User,Permission
from parametros.models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class AuthUserSerializer(serializers.ModelSerializer):
#     nombre_cargo = serializers.SerializerMethodField()
#     nombre_regional = serializers.SerializerMethodField()
#     class Meta:
#         model = AuthUser
#         exclude = ['id_cargo','id_regional']

#     def get_nombre_regional(self, usuario):
#         # Obtén el nombre de la regional a partir de la entidad financiera
#         regional = usuario.id_regional  # Supongamos que este es el campo que almacena la clave foránea
#         return regional.nombre_regional if regional else None
#     def get_nombre_cargo(self, usuario):
#         # Obtén el nombre de la regional a partir de la entidad financiera
#         cargo = usuario.id_cargo  # Supongamos que este es el campo que almacena la clave foránea
#         return cargo.descripcion if cargo else None 

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass
class EmptySerializer(serializers.Serializer):
    pass
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields=('username','email','first_name','last_name')
#-------------------------SERIALIZADORES PARA GESTION DE USUARIOS--------

class AuthUserSerializer(serializers.ModelSerializer):
    nombre_cargo = serializers.SerializerMethodField()
    nombre_regional = serializers.SerializerMethodField()
    #id_grupo = serializers.SerializerMethodField()
    class Meta:
        model = AuthUser
        fields = ('id', 'username', 'username', 'first_name', 'last_name', 'email', 'password', 'ci', 'celular', 'direccion', 'id_regional', 'nombre_regional', 'id_cargo', 'nombre_cargo', 'is_active', 'is_staff', 'password', 'id_grupo')
        extra_kwargs = {'password': {'write_only': True, 'required':False}}

    #def get_id_grupo(self, obj):
        #return list(obj.groups.values_list('name', flat=True))
    
    def get_nombre_regional(self, usuario):
         # Obtén el nombre de la regional a partir de la entidad financiera
         regional = usuario.id_regional  # Supongamos que este es el campo que almacena la clave foránea
         return regional.nombre_regional if regional else None   
    def get_nombre_cargo(self, usuario):
         # Obtén el nombre de la regional a partir de la entidad financiera
         cargo = usuario.id_cargo  # Supongamos que este es el campo que almacena la clave foránea
         return cargo.descripcion if cargo else None  
    
    def create(self, validated_data):
        print(validated_data, 456464646)
        user = AuthUser(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            ci=validated_data['ci'],
            celular=validated_data['celular'],
            direccion=validated_data['direccion'],
            id_regional=validated_data['id_regional'],
            id_cargo=validated_data['id_cargo'],
            is_staff=validated_data['is_staff'],
            email=validated_data['email'],
            is_active=validated_data['is_active'],
            id_grupo=validated_data['id_grupo'],
        )
        user.set_password(validated_data['password'])
        user.save()
        AuthUserGroups.objects.create(user_id=user.id, group_id=user.id_grupo)
        return user
    
class GroupIdSerializer(serializers.Serializer):
    grupo_id = serializers.IntegerField()


#-----------------------------------------------------------------------------
#---------------------------SERIALIZADORES PARA USUARIOS Y GRUPOS-------------
class AuthGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthGroup
        fields = '__all__'


class AuthUserGroupsSerializer(serializers.ModelSerializer):
    class Meta:
            model = AuthUserGroups
            fields = '__all__' 

class AuthPermissionSerializer(serializers.ModelSerializer):
    nombre_content_type = serializers.SerializerMethodField()
    class Meta:
            model = AuthPermission
            fields = '__all__' 

    def get_nombre_content_type(self, auth_permission):
        content_type = auth_permission.content_type  # Supongamos que este es el campo que almacena la clave foránea
        return content_type.model if content_type else None



class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
            model = DjangoContentType
            fields = '__all__' 


class AuthGroupPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
            model = AuthGroupPermissions
            fields = '__all__' 
            from django.contrib.auth.models import Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'content_type')
#----------------------------------------------------------------------------
#----------------------------SERIALIZADORES DISLOQUE-------------------------
class DisloqueSerializer(serializers.ModelSerializer):
    nombre_regional=serializers.SerializerMethodField()
    class Meta:
        model = Disloque
        fields = '__all__'
    def get_nombre_regional(self, disloque):
        regional=disloque.id_regional
        return regional.nombre_regional if regional else None

class DisloqueDetalleSerializer(serializers.Serializer):    
    regional_id = serializers.IntegerField()
    fecha_ini = serializers.DateField()
    fecha_fin = serializers.DateField()
    reten_id = serializers.IntegerField()
    recaudadores_seleccionados = serializers.ListField(child=serializers.IntegerField())
    
class DisloqueDetalleVistaSerializer(serializers.ModelSerializer):
    nombre_regional=serializers.SerializerMethodField()
    nombre_reten= serializers.SerializerMethodField()
    nombre_recaudador = serializers.SerializerMethodField()
    class Meta:
        model = DisloqueDetalle
        fields = '__all__'
    def get_nombre_regional(self, disloqueDetalle):
        regional=disloqueDetalle.id_regional
        return regional.nombre_regional if regional else None
    def get_nombre_reten(self, disloqueDetalle):
        reten = disloqueDetalle.id_reten
        return reten.nombre_reten if reten else None
    def get_nombre_recaudador(self, disloqueDetalle):
        recaudador = disloqueDetalle.id_recaudador
        return recaudador.username if recaudador else  None

class UsuariosLibresSerializer(serializers.Serializer):
    id_regional = serializers.IntegerField()
    fecha_ini = serializers.DateField()
    
class RetenesNoDisloqueSerializer(serializers.Serializer):
    id_regional = serializers.IntegerField()
    fecha_ini = serializers.DateField()
#--------------------------------------------------------------------------
#----------------------------SERIALIZADOR PARA CAJA CARRIL-----------------
class CajaCarrilSerializer(serializers.ModelSerializer):
    nombre_recaudador=serializers.SerializerMethodField()
    nombre_reten=serializers.SerializerMethodField()
    nombre_regional=serializers.SerializerMethodField()
    turno=serializers.SerializerMethodField()
    class Meta:
        model = CajaCarril
        fields = '__all__'
    def get_nombre_recaudador(self, caja_carril):
        usuario = caja_carril.id_recaudador  # Supongamos que este es el campo que almacena la clave foránea
        return usuario.username if usuario else None
    def get_nombre_reten(self, caja_carril):
        reten=caja_carril.id_reten
        return reten.nombre_reten if reten else None
    def get_nombre_regional(self,caja_carril):
        disloque=caja_carril.id_disloque
        return disloque.id_regional.nombre_regional if disloque else None
    def get_turno(self,caja_carril):
        turno=Turnos.objects.get(id_turno=caja_carril.id_turno)
        return turno.nombre if turno else None

class CierreCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CierreCaja
        fields = '__all__'

class CierreCajaTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CierreCajaTags
        fields = '__all__'
        
class RetenesSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Retenes
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Menu
        fields = '__all__'        

class MenuGroupSerializer(serializers.ModelSerializer):    
    nombre_menu = serializers.SerializerMethodField()
    nombre_grupo = serializers.SerializerMethodField()
    class Meta:
        model = MenuGroup
        fields = '__all__'
    def get_nombre_menu(self, menugroup):
        menu = menugroup.id_menu  
        return menu.nombre if menu else None          
    def get_nombre_grupo(self, menugroup):
        group = menugroup.id_group  
        return group.name if group else None
class TurnosSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Turnos
        fields = '__all__'                    