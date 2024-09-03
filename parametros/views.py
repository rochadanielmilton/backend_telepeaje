from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework import generics

from rest_framework.views import APIView
from rest_framework.response import Response
#from django.http import JsonResponse
from .models import Regionales,Retenes,CategoriaVehiculo,Tarifario,Rutas,Cargo,EntidadFinanciera,Localidad, CuentasBancarias,AuthUser

from .serializers import *
from django.views.generic import TemplateView, View, UpdateView, FormView,ListView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
#--------------------------REGIONALES------------------------------------
class RegionalesViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset=Regionales.objects.filter(baja=0)
    serializer_class=RegionalesSerializer
 
class BajaRegionalView(generics.UpdateAPIView):
    queryset = Regionales.objects.filter(baja=0)
    serializer_class = RegionalesSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.nombre_regional} fue dada de baja.'})
    
#------------------CATEGORIAS DE VEHICULOS--------------------------------------   

class CategoriasViewSet(viewsets.ModelViewSet):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
    queryset=CategoriaVehiculo.objects.filter(baja=0).order_by('-id_categoria')
    serializer_class=CategoriasSerializer
    
class BajaCategoriaView(generics.UpdateAPIView):
    queryset = CategoriaVehiculo.objects.filter(baja=0).order_by('id_categoria')
    serializer_class = CategoriasSerializer
    
    def update(self, *args, **kwargs):
        print("MMMMMMMMMMMMMMMMMMMMMMMMMMMM")
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.nombre_categoria} fue dada de baja.'})
    
@api_view(['POST'])
def upload_image(request):
    imagen = request.FILES.get('file')
    if imagen:
        # Genera un nombre único para el archivo
        nombre_imagen = default_storage.get_available_name(imagen.name)
        # Guarda el archivo en la carpeta media
        default_storage.save(nombre_imagen, ContentFile(imagen.read()))
        # Devuelve la URL del archivo cargado
        url = default_storage.url(nombre_imagen)
        return Response({'url': url})
    return Response({'error': 'No se ha proporcionado ningún archivo.'}) 
   
#-------------------TARIFARIOS-----------------------------------------------------

class TarifariosViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset=Tarifario.objects.filter(baja=0).order_by('-id_tarifario')
    def get_serializer_class(self):       
        return TarifariosSerializer
        
class BajaTarifarioView(generics.UpdateAPIView):
    queryset = Tarifario.objects.filter(baja=0).order_by('id_tarifario')
    serializer_class = TarifariosSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.id_tarifario} fue dada de baja.'})
    
#---------------------------------RUTAS-----------------------------------------

class RutasViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset=Rutas.objects.filter(baja=0).order_by('-id_ruta')
    def get_serializer_class(self):       
        return RutasSerializer

class BajaRutaView(generics.UpdateAPIView):
    queryset = Rutas.objects.filter(baja=0).order_by('id_ruta')
    serializer_class = RutasSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.nombre} fue dada de baja.'})
    
#---------------------------------CARGOS-----------------------------------------

class CargosViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset=Cargo.objects.filter(baja=0).order_by('-id')
    serializer_class=CargosSerializer
    
class BajaCargoView(generics.UpdateAPIView):
    queryset = Cargo.objects.filter(baja=0).order_by('id')
    serializer_class = CargosSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.descripcion} fue dada de baja.'})

#---------------------------------ENTIDAD FINANCIERA----------------------------------

class EntidadFinancieraViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = EntidadFinanciera.objects.filter(baja=0).order_by('-id_entidad')
    def get_serializer_class(self):       
        return EntidadFinancieraSerializer  # Para la acción de listado



class BajaEntidadFinancieraView(generics.UpdateAPIView):
    queryset = EntidadFinanciera.objects.filter(baja=0).order_by('id_entidad')
    serializer_class = EntidadFinancieraSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.nombre_entidad} fue dada de baja.'})   
#---------------------------------LOCALIDAD-----------------------------------------

class LocalidadViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset=Localidad.objects.filter(baja=0).order_by('-id_localidad')
    def get_serializer_class(self):
        return LocalidadSerializer
    
class BajaLocalidadView(generics.UpdateAPIView):
    queryset = Localidad.objects.filter(baja=0).order_by('id_localidad')
    serializer_class = LocalidadSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.nombre_localidad} fue dada de baja.'})

#---------------------------------RETENES-----------------------------------------

#class RetenesAPIView(APIView):
    #def get(self, request, *args, **kwargs):
         #Obtén la lista de retenes
        #lista_retenes = Retenes.objects.filter(baja=0).order_by('id_reten')
        #retenes_data = RetenesSerializer(lista_retenes, many=True).data

        #regionales = Regionales.objects.all()
        #rutas = Rutas.objects.all()
        #regionales_data = [{'id_regional': regional.id_regional, 'nombre_regional': regional.nombre_regional} for regional in regionales]
        #rutas_data = [{'id_ruta': ruta.id_ruta, 'nombre_ruta': ruta.nombre} for ruta in rutas]

        #response_data = {
         #   'retenes': retenes_data,
         #   'regionales': regionales_data,
         #   'rutas': rutas_data,
        #}
        
      #  return Response(response_data)


class RetenesViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset=Retenes.objects.filter(baja=0).order_by('-id_reten')
    def get_serializer_class(self):
        return RetenesSerializer    

class BajaRetenesView(generics.UpdateAPIView):
    queryset = Retenes.objects.filter(baja=0).order_by('id_reten')
    serializer_class = LocalidadSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.nombre_reten} fue dada de baja.'})
    
#---------------------------------------LISTAS PARA SELECTS-------------------------------
       
@api_view(['GET']) 
def ListaRegionales(request):
    lista_regionales=Regionales.objects.filter(baja=0).values('id','nombre_regional')
    regionales_data=[{'id_regional':item['id'],'nombre_regional':item['nombre_regional']} for item in lista_regionales]
    data=regionales_data
    return Response(data)

@api_view(['GET']) 
def ListaRetenes(request):
    lista_retenes=Retenes.objects.filter(baja=0).values('id_reten','nombre_reten','id_regional','id_ruta','id_tipo_reten','localidad_id')
    retenes_data=[{'id_reten':item['id_reten'],'nombre_reten':item['nombre_reten'],'id_regional':item['id_regional'],
                   'id_ruta':item['id_ruta'],'id_tipo_reten':item['id_tipo_reten'],'localidad_id':item['localidad_id']} for item in lista_retenes]
    data=retenes_data
    return Response(data)
@api_view(['GET'])
def ListaRutas(request):
    lista_rutas=Rutas.objects.filter(baja=0).values('id_ruta','nombre','id_regional')
    rutas_data=[{'id_ruta':item['id_ruta'],'nombre':item['nombre'],'id_regional':item['id_regional']} for item in lista_rutas]
    data=rutas_data
    return Response(data)
@api_view(['GET'])
def ListaCategorias(request):
    lista_categoria=CategoriaVehiculo.objects.filter(baja=0).values('id_categoria','nombre_categoria')
    categoria_data=[{'id_categoria':item['id_categoria'],'nombre_categoria':item['nombre_categoria']} for item in lista_categoria]
    data=categoria_data
    return Response(data)
@api_view(['GET'])
def ListaLocalidades(request):
    lista_localidades=Localidad.objects.filter(baja=0).values('id_localidad','nombre_localidad','id_regional')
    localidades_data=[{'id_localidad':item['id_localidad'],'nombre_localidad':item['nombre_localidad'],'id_regional':item['id_regional']} for item in lista_localidades]
    data=localidades_data
    return Response(data)

#-------------------------------LISTAS FILTRADAS DADO UN REGIONAL-------------------------------

@api_view(['GET'])
def ListaLocalidadesDeRegional(request,id_regional):
    lista_localidades=Localidad.objects.filter(baja=0,id_regional=id_regional).values('id_localidad','nombre_localidad','id_regional')
    localidades_data=[{'id_localidad':item['id_localidad'],'nombre_localidad':item['nombre_localidad'],'id_regional':item['id_regional']} for item in lista_localidades]
    data=localidades_data
    return Response(data)

@api_view(['GET'])
def ListaRutasDeRegional(request,id_regional):
    lista_rutas=Rutas.objects.filter(baja=0,id_regional=id_regional).values('id_ruta','nombre','id_regional')
    rutas_data=[{'id_ruta':item['id_ruta'],'nombre':item['nombre'],'id_regional':item['id_regional']} for item in lista_rutas]
    data=rutas_data
    return Response(data)

@api_view(['GET']) 
def ListaRetenesDeRegional(request,id_regional):
    lista_retenes=Retenes.objects.filter(baja=0,id_regional=id_regional).values('id_reten','nombre_reten','id_regional','id_ruta','id_tipo_reten','localidad_id')
    retenes_data=[{'id_reten':item['id_reten'],'nombre_reten':item['nombre_reten'],'id_regional':item['id_regional'],
                   'id_ruta':item['id_ruta'],'id_tipo_reten':item['id_tipo_reten'],'localidad_id':item['localidad_id']} for item in lista_retenes]
    data=retenes_data
    return Response(data)

@api_view(['GET']) 
def ListaUsuariosDeRegional(request,id_regional):
    lista_usuarios=AuthUser.objects.filter(is_active=True,id_regional=id_regional).values('id','username','id_regional')
    usuarios_data=[{'id_usuario':item['id'],'usuario':item['username'],'id_regional':item['id_regional']} for item in lista_usuarios]
    data=usuarios_data
    return Response(data)   




class CuentasBancariasViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset=CuentasBancarias.objects.all().order_by('-id_cuentas')
    def get_serializer_class(self):       
        return CuentasBancariasSerializer
    

class TurnosViewSet(viewsets.ModelViewSet):
    queryset=Turnos.objects.all()
    serializer_class=TurnosSerializer
