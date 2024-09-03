from datetime import datetime
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
#from parametros.models import PuntoEmpadronamiento, Cuenta,Retenes, Vehiculo, AuthUser, UsuarioLog
#from .serializers import PuntoEmpadronamientoSerializer, CuentaSerializer
from parametros.models import *
from .serializers import *
from parametros.serializers import CategoriasSerializer, TarifariosSerializer, CuentasBancariasSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view,permission_classes
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.http import Http404




# Create your views here.
class PuntoEmpadronamientoViewSet(viewsets.ModelViewSet):
    queryset = PuntoEmpadronamiento.objects.filter(baja=0).order_by('-id_punto_empadronamiento')
    serializer_class = PuntoEmpadronamientoSerializer


class BajaPuntoEmpadronamientolView(generics.UpdateAPIView):
    queryset = PuntoEmpadronamiento.objects.all()
    serializer_class = PuntoEmpadronamientoSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'El punto de empadronamiento {instance.descripcion} fue dada de baja.'})



#class MostrarPuntoEmpadronamientoAPIView(APIView):
    #def get(self, request, *args, **kwargs):        
        #lista_pempadronamiento = PuntoEmpadronamiento.objects.filter(baja=0).order_by('id_punto_empadronamiento')
        #pempadronamiento_data = PuntoEmpadronamientoSerializer(lista_pempadronamiento, many=True).data
        #data = {
            #'pempadronamiento': pempadronamiento_data,
        #}
        #return Response(data)

    


class CuentaViewSet(viewsets.ModelViewSet):
    queryset = Cuenta.objects.filter(baja=0).order_by('-id_cuenta')
    serializer_class = CuentaSerializer

class RegistrarCuentaViewSet(viewsets.ViewSet):
   
    def create(self, request):
        ultimo_id = Cuenta.objects.last()
        id = ultimo_id.id_cuenta + 1 if ultimo_id else 1
        
        serializer = CuentaDetalleSerializer(data=request.data)
        
        if serializer.is_valid(): 
            data = serializer.validated_data
            id_cuenta = id
            tipo = data['tipo']
            saldo = data.get('saldo', 0.00)  # Usa 0.00 como valor predeterminado si saldo no se proporciona
            fecha_inicio = data['fecha_inicio']
            fecha_fin = data['fecha_fin']
            estado = data['estado']
            baja = 0
            
            nueva_cuenta = Cuenta.objects.create(
                id_cuenta=id_cuenta, 
                tipo=tipo, 
                saldo=saldo, 
                fecha_inicio=fecha_inicio, 
                estado=estado,
                baja=baja, 
                fecha_fin=fecha_fin
            )

            if tipo == "empresa":
                return Response({'AgregarEmpresa': id_cuenta, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})
            else:
                return Response({'AgregarPersonaConvenio': id_cuenta, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})
        else:
            return Response({'message': 'error'}, status=400)



class CancelarRegistroNuevaCuenta(APIView):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        Cuenta.objects.filter(id_cuenta=pk).update(baja=1)
        return Response({'mensaje': 'Creacion de cuenta cancelada'}, status=status.HTTP_200_OK)

################################# Entidad Persona #######################################

class EntidadPersonaViewSet(viewsets.ModelViewSet):
    queryset = EntidadPersona.objects.all().order_by('-id_entidad_persona')
    serializer_class = EntidadPersonaSerializer


class AgregarPersonaConvenioViewSet(APIView):

    def get(self, request, pk, *args, **kwargs):
        try:
            cuenta = Cuenta.objects.get(id_cuenta=pk)
            cuenta_data = CuentaSerializer(cuenta).data
            return Response({
                'AgregarPersonaConvenio': cuenta_data["id_cuenta"],
                'fecha_inicio': cuenta_data["fecha_inicio"],
                'fecha_fin': cuenta_data["fecha_fin"]
            })
        except Cuenta.DoesNotExist:
            return Response({'error': 'Cuenta no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        serializer = EntidadPersonaSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            nombre_completo = f"{data['nombre']} {data['ap_paterno']} {data['ap_materno']}"
            
            nueva_persona = EntidadPersona.objects.create(
                id_cuenta=data['id_cuenta'],
                id_punto_empadronamiento=data['id_punto_empadronamiento'],
                id_regional=data['id_regional'],
                nombre=data['nombre'],
                ap_paterno=data['ap_paterno'],
                ap_materno=data['ap_materno'],
                ci_persona=data['ci_persona'],
                direccion=data['direccion'],
                celular=data['celular'],
                telefono=data['telefono'],
                ciudad=data['ciudad'],
                correo=data['correo'],
                baja=0
            )

            seguimiento = Seguimiento.objects.create(estado='t', id_persona=nueva_persona)

            try:
                cuenta = nueva_persona.id_cuenta
                cuenta.nombre_entidad = nombre_completo
                cuenta.save(update_fields=['nombre_entidad'])

                contrato = EntidadContrato.objects.create(
                    id_entidad_persona=nueva_persona, 
                    fecha_ini_contrato=cuenta.fecha_inicio, 
                    fecha_fin_contrato=cuenta.fecha_fin,
                    baja_contrato=0, 
                    id_seguimiento=seguimiento
                )

                return Response({'message': 'Datos guardados correctamente'})

            except Cuenta.DoesNotExist:
                return Response({'error': 'Cuenta o entidad persona no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerPersonaConvenio(APIView):

    def get(self, request, pk, *args, **kwargs):
        try:
            # Obtener la persona y serializarla
            persona = EntidadPersona.objects.get(id_cuenta=pk)
            persona_serializer = EntidadPersonaSerializer(persona).data
            
            # Obtener la lista de vehículos y serializarla
            vehiculos = Vehiculo.objects.filter(id_cuenta=persona.id_cuenta.id_cuenta, baja=0)
            vehiculo_serializer = VehiculoSerializer(vehiculos, many=True).data
            
            # Obtener el saldo de la cuenta
            cuenta = Cuenta.objects.get(id_cuenta=persona.id_cuenta.id_cuenta, baja=0)
            saldo_cuenta = cuenta.saldo
            
            # Obtener el contrato activo y serializarlo
            contrato = EntidadContrato.objects.get(id_entidad_persona=persona.id_entidad_persona, baja_contrato=0)
            contrato_serializer = EntidadContratoSerializer(contrato).data
            
            # Determinar si se muestra el botón de comprobante
            verBotonComprobante = verBotonComprobanteRP(request, persona.id_entidad_persona)

            return Response({
                'persona_convenio': persona_serializer,
                'contrato': contrato_serializer,
                'lista_vehiculos': vehiculo_serializer,
                'verBotonComprobante': verBotonComprobante,
                'saldo_cuenta': saldo_cuenta
            }, status=status.HTTP_200_OK)

        except EntidadPersona.DoesNotExist:
            return Response({
                'estado': False,
                'mensaje': 'Entidad persona no existe o no se ha completado el registro de la entidad'
            }, status=status.HTTP_404_NOT_FOUND)

        except Cuenta.DoesNotExist:
            return Response({
                'estado': False,
                'mensaje': 'Cuenta asociada a la persona no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

        except EntidadContrato.DoesNotExist:
            return Response({
                'estado': False,
                'mensaje': 'Contrato asociado a la persona no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except MultipleObjectsReturned:
            return Response({
                'estado': False,
                'mensaje': 'Se encontraron múltiples objetos cuando se esperaba uno solo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError:
            return Response({
                'estado': False,
                'mensaje': 'Error de integridad en la base de datos'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except TypeError as e:
            return Response({
                'estado': False,
                'mensaje': f'Error de tipo: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ValueError as e:
            return Response({
                'estado': False,
                'mensaje': f'Error de valor: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'estado': False,
                'mensaje': f'Error inesperado: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def verBotonComprobanteRP(request,pk):
        # check=Seguimiento.objects.get(id_persona=pk)
        # return check.estado
    try:
        check = Seguimiento.objects.get(id_persona=pk)
        return (check.estado)
    except Seguimiento.DoesNotExist:
        return Response({'estado': 'Seguimiento de estado de comprobante no encontrada'})

class BajaPersonaConvenio(APIView):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        persona = get_object_or_404(EntidadPersona, id_entidad_persona=pk)
        persona.baja = 1
        persona.save()
        return Response({'mensaje': 'Los datos de la entidad Persona fueron dados de baja correctamente'}, status=status.HTTP_200_OK)


class EdicionPersonaConvenio(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        persona = EntidadPersona.objects.get(id_entidad_persona=pk)
        persona_serializer = EntidadPersonaSerializer(persona).data
        contrato = EntidadContrato.objects.filter(id_entidad_persona=persona.id_entidad_persona).get(baja_contrato=0)
        contrato_serializer = EntidadContratoSerializer(contrato).data
        return Response({
            'persona': persona_serializer,
            'contrato': contrato_serializer,
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        #pk = self.kwargs['pk']
        
        serializer = EntidadPersonaSerializer(data=request.data)
        #print("101010101010101010101010101010101", request.data['id_entidad_empresa'])
        if serializer.is_valid():
            data = serializer.validated_data
            #print("3213212313213213213132132131313", data)
            id_entidad_persona = request.data['id_entidad_persona']
            id_cuenta = data['id_cuenta']
            id_punto_empadronamiento = data['id_punto_empadronamiento']
            nombre = data['nombre']
            ap_paterno = data['ap_paterno']
            ap_materno = data['ap_materno']
            ci_persona = data['ci_persona']
            direccion = data['direccion']
            celular = data['celular']
            telefono = data['telefono']
            ciudad = data['ciudad']
            correo = data['correo']
            baja = 0

            #print("*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*", data)
            
            EntidadPersona.objects.filter(id_entidad_persona=id_entidad_persona).update(
                                                                                        nombre=nombre, 
                                                                                        ap_paterno=ap_paterno, 
                                                                                        ap_materno=ap_materno,
                                                                                        ci_persona=ci_persona, 
                                                                                        direccion=direccion, 
                                                                                        celular=celular,
                                                                                        telefono=telefono, 
                                                                                        ciudad=ciudad, 
                                                                                        correo=correo,
                                                                                        baja=baja
                                                                                        )
            
            try:

                persona = EntidadPersona.objects.get(id_entidad_persona=id_entidad_persona)
                nombre_completo = f"{nombre} {ap_paterno} {ap_materno}"
                Cuenta.objects.filter(id_cuenta=persona.id_cuenta.id_cuenta).update(nombre_entidad=nombre_completo)

                return Response({'message': 'Datos actualizados correctamente'})
            except ObjectDoesNotExist:
                return Response({'error': 'Cuenta o entidad pesona no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class habilitarBotonP(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            seguimiento = Seguimiento.objects.get(id_persona=pk)
            seguimiento.estado = 't'
            seguimiento.save()
            return Response({'message': 'Se habilitó el botón de reenvío del comprobante'}, status=status.HTTP_200_OK)
        except Seguimiento.DoesNotExist:
            return Response({'error': 'No se encontró la entidad de seguimiento'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error al habilitar el botón: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################################# Entidad Empresa #######################################
class EntidadEmpresaViewSet(viewsets.ModelViewSet):
    queryset = EntidadEmpresa.objects.all().order_by('-id_entidad_empresa')
    serializer_class = EntidadEmpresaSerializer



class AgregarEmpresaViewSet(APIView):

    def get(self, request, pk, *args, **kwargs):
        try:
            cuenta = Cuenta.objects.get(id_cuenta=pk)
            cuenta_data = CuentaSerializer(cuenta).data
            return Response({
                'AgregarEmpresaConvenio': cuenta_data["id_cuenta"],
                'fecha_inicio': cuenta_data["fecha_inicio"],
                'fecha_fin': cuenta_data["fecha_fin"]
            })
        except Cuenta.DoesNotExist:
            return Response({'error': 'Cuenta no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        serializer = EntidadEmpresaSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                nueva_empresa = EntidadEmpresa.objects.create(
                    id_cuenta=data['id_cuenta'],
                    id_punto_empadronamiento=data['id_punto_empadronamiento'],
                    id_regional=data['id_regional'],
                    razon_social=data['razon_social'],
                    nombre=data['nombre'],
                    direccion=data['direccion'],
                    sector=data['sector'],
                    tipo_empresa=data['tipo_empresa'],
                    correo=data['correo'],
                    nit=data['nit'],
                    interno_1=0,
                    interno_2=0,
                    telefono=data['telefono'],
                    celular=data['celular'],
                    baja=0
                )

                nuevo_seguimiento = Seguimiento.objects.create(estado='t', id_entidad_empresa=nueva_empresa.id_entidad_empresa)
                cuenta = Cuenta.objects.filter(id_cuenta=nueva_empresa.id_cuenta.id_cuenta).update(nombre_entidad=nueva_empresa.nombre)              
                contrato = EntidadContrato.objects.create(
                    id_entidad_empresa=nueva_empresa,
                    fecha_ini_contrato=nueva_empresa.id_cuenta.fecha_inicio,
                    fecha_fin_contrato=nueva_empresa.id_cuenta.fecha_fin,
                    baja_contrato=0,
                    id_seguimiento=None
                )
                if nuevo_seguimiento and cuenta and contrato:
                    return Response({'message': 'Datos guardados correctamente'},status=status.HTTP_200_OK)

            except (Cuenta.DoesNotExist, EntidadEmpresa.DoesNotExist):
                return Response({'error': 'Cuenta o entidad empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerEmpresaConvenio(APIView):

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']

        try:
            # Obtener la empresa y serializarla
            empresa = EntidadEmpresa.objects.get(id_cuenta=pk, baja=0)
            empresa_serializer = EntidadEmpresaSerializer(empresa).data
            
            # Obtener la lista de vehículos y serializarla
            vehiculos = Vehiculo.objects.filter(id_cuenta=empresa.id_cuenta, baja=0)
            lista_vehiculos_serializer = VehiculoSerializer(vehiculos, many=True).data
            
            # Obtener el saldo de la cuenta
            cuenta = Cuenta.objects.get(id_cuenta=empresa_serializer['id_cuenta'], baja=0)
            saldo_cuenta = cuenta.saldo
            
            # Obtener el contrato activo y serializarlo
            contrato = EntidadContrato.objects.filter(id_entidad_empresa=empresa.id_entidad_empresa, baja_contrato=0).first()
            contrato_serializer = EntidadContratoSerializer(contrato).data if contrato else {}

            # Determinar si se muestra el botón de comprobante
            verBotonComprobante = verBotonComprobanteRE(request, empresa.id_entidad_empresa)

            return Response({
                'empresa': empresa_serializer,
                'lista_vehiculos': lista_vehiculos_serializer,
                'contrato': contrato_serializer,
                #'verBotonComprobante': verBotonComprobante,
                'saldo_cuenta': saldo_cuenta
            }, status=status.HTTP_200_OK)

        except EntidadEmpresa.DoesNotExist:
            return Response({
                'estado': False,
                'mensaje': 'No se ha completado el registro de la entidad empresa o la entidad no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Cuenta.DoesNotExist:
            return Response({
                'estado': False,
                'mensaje': 'Cuenta asociada a la empresa no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)

def verBotonComprobanteRE(request, pk):
    try:
        check = Seguimiento.objects.get(id_entidad_empresa=pk)
        return (check.estado)
    except Seguimiento.DoesNotExist:
        return Response({'estado':'Seguimiento de estado de comprobante no encontrada'})


class BajaEmpresaConvenio(APIView):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        empresa = get_object_or_404(EntidadEmpresa, id_entidad_empresa=pk)
        empresa.baja = 1
        empresa.save()
        return Response({'mensaje': 'Los datos de la empresa fueron dados de baja correctamente'}, status=status.HTTP_200_OK)

class EdicionEmpresaConvenio(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        empresa = EntidadEmpresa.objects.get(id_entidad_empresa=pk)
        empresa_serializer = EntidadEmpresaSerializer(empresa).data
        contrato = EntidadContrato.objects.filter(id_entidad_empresa=empresa.id_entidad_empresa).get(baja_contrato=0)
        contrato_serializer = EntidadContratoSerializer(contrato).data
        return Response({
            'empresa': empresa_serializer,
            'contrato': contrato_serializer,
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        #pk = self.kwargs['pk']
        
        serializer = EntidadEmpresaSerializer(data=request.data)
        #print("101010101010101010101010101010101", request.data['id_entidad_empresa'])
        if serializer.is_valid():
            data = serializer.validated_data
            #print("3213212313213213213132132131313", data)
            id_entidad_empresa = request.data['id_entidad_empresa']
            razon_social = data['razon_social']
            nombre = data['nombre']
            direccion = data['direccion']
            sector = data['sector']
            tipo_empresa = data['tipo_empresa']
            correo = data['correo']
            telefono = data['telefono']
            celular = data['celular']
            nit = data['nit']

            #print("*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*", data)
            EntidadEmpresa.objects.filter(id_entidad_empresa=id_entidad_empresa).update(razon_social=razon_social, nit=nit,
                                                                    nombre=nombre, direccion=direccion, sector=sector, tipo_empresa=tipo_empresa,
                                                                    correo=correo, telefono=telefono, celular=celular)
            
            try:

                empresa = EntidadEmpresa.objects.get(id_entidad_empresa=id_entidad_empresa)
                Cuenta.objects.filter(id_cuenta=empresa.id_cuenta.id_cuenta).update(nombre_entidad=empresa.razon_social)

                return Response({'message': 'Datos actualizados correctamente'})
            except ObjectDoesNotExist:
                return Response({'error': 'Cuenta o entidad empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class HabilitarBotonC(APIView):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            seguimiento = Seguimiento.objects.get(id_entidad_empresa=pk)
            seguimiento.estado = 't'
            seguimiento.save()
            return Response({'message': 'Se habilitó el botón de reenvío del comprobante'}, status=status.HTTP_200_OK)
        except Seguimiento.DoesNotExist:
            return Response({'error': 'No se encontró la entidad de seguimiento'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error al habilitar el botón: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EntidadContratoViewSet(viewsets.ModelViewSet):
    queryset = EntidadContrato.objects.all().order_by('-id_contrato')
    serializer_class = EntidadContratoSerializer



class DepositosViewSet(viewsets.ModelViewSet):
    queryset = Depositos.objects.all().order_by('-id')
    serializer_class = DepositosSerializer


################################# tags #######################################
class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all().order_by('-id')
    serializer_class = TagsSerializer



class AsignacionTag(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        vehiculo=Vehiculo.objects.get(id_vehiculo=pk)
        vehiculo_seralizer = VehiculoSerializer(vehiculo).data
        lista_tags = TagsSerializer(Tags.objects.filter(asignado = 'no', estado = 'habilitado', id_cuenta = None).order_by('-id'), many = True)

        # lista_tags = Tags.objects.all().filter(asignado='no')
        # tags_serializer = TagsSerializer(lista_tags, many=True).data
        return Response({'vehiculo':vehiculo_seralizer, "lista_tags": lista_tags.data})
    
    def post(self, request, *args, **kwargs):
        vehiculo=Vehiculo.objects.get(id_vehiculo=request.data['id_vehiculo'])
        vehiculo_seralizer = VehiculoSerializer(vehiculo).data        
        id_vehiculo = vehiculo_seralizer['id_vehiculo']
        id_tag = request.data['id_tag']
        id_cuenta = request.data['id_cuenta']
        tag = TagsSerializer(Tags.objects.get(id=id_tag)).data
        Vehiculo.objects.filter(id_vehiculo=id_vehiculo).update(tag=tag['cod_tag'])
        asignado='si'
        Tags.objects.filter(id=id_tag).update(id_cuenta=id_cuenta,
                                              nombre_entidad=vehiculo.id_cuenta.nombre_entidad,
                                              placa=vehiculo.placa,asignado=asignado)        
        return Response({'mensaje': "Tag asignado correctamente al vehiculo", 'id_cuenta': id_cuenta, 'id_vehiculo': id_vehiculo})
    


@api_view(['GET', 'PATCH'])
def ReasignarTag(request, idv):
    try:
        vehiculo = VehiculoSerializer(Vehiculo.objects.get(id_vehiculo = idv))

    except Vehiculo.DoesNotExist:
        return Response({'error': 'El vehiculo no existe'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(vehiculo.data)

    elif request.method == 'PATCH':
        
        vehiculo = Vehiculo.objects.get(id_vehiculo=idv)
        vehiculo_serializer = VehiculoSerializer(vehiculo)
        #print("/8/8/8/8/8/8/8/8/8/8/8", vehiculo.tag)
        id_cuenta = request.data['id_cuenta']
        cod_tag = request.data['id_tag']
        id_vehiculo = request.data['id_vehiculo']
        codigo_tag=Tags.objects.get(id=cod_tag)
        Tags.objects.filter(cod_tag=vehiculo.tag).update(estado='inhabilitado')
        # print("---------------------------", Tags.objects.filter(cod_tag=vehiculo.tag))
        #Vehiculo.objects.filter(id_vehiculo = vehiculo.id_vehiculo).update(tag = '')
        #print("9595959595959595959599595959", cod_tag)
        Vehiculo.objects.filter(id_vehiculo = vehiculo.id_vehiculo).update(tag = codigo_tag.cod_tag)
        asignado='si'
        estado='habilitado'
        #print("---------------------------", vehiculo.tag)
        Tags.objects.filter(id = cod_tag).update(id_cuenta = vehiculo.id_cuenta.id_cuenta,
                                                nombre_entidad = vehiculo.id_cuenta.nombre_entidad,
                                                placa = vehiculo.placa,
                                                asignado = asignado,
                                                estado = estado)

        return Response({'mensaje': "Tag reasignado correctamente"}, status=status.HTTP_200_OK)



class VerEntidadTag(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            entidad=EntidadEmpresa.objects.get(id_cuenta=pk)
            return Response({'empresa':entidad.id_entidad_empresa})
        except:
            entidad=EntidadPersona.objects.get(id_cuenta=pk)
            return Response({'personal':entidad.id_entidad_persona})


class VerTag(APIView):
    def get(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            tag = Tags.objects.get(cod_tag=pk)
            datos = []
            serializer = TagsSerializer(tag).data
            # datos.append({'tag': serializer})
            # print("9*9*9*9*9*9**9*9*99*99*999*9*9*9*", serializer['cod_tag'])
            
            # Intenta obtener el vehículo relacionado con el tag
            try:
                vehiculo = Vehiculo.objects.get(tag=serializer['cod_tag'])
                vehiculo_serializer = VehiculoSerializer(vehiculo)
                #print("9*9*9*9*9*9**9*9*99*99*999*9*9*9*", vehiculo_serializer.data)
                id_cuenta = vehiculo_serializer.data['id_cuenta']
                id_categoria = vehiculo_serializer.data['id_categoria']
                cuenta = Cuenta.objects.get(id_cuenta=id_cuenta)
                cuenta_serializer = CuentaDetalleSerializer(cuenta)
                #print("6565656565656565665656565656", cuenta_serializer.data)
                saldo = cuenta_serializer.data['saldo']

                if(cuenta_serializer.data['tipo']=='empresa'):
                    empresa = EntidadEmpresa.objects.get(id_cuenta=vehiculo_serializer.data['id_cuenta'])
                    empresa_serializer = EntidadEmpresaSerializer(empresa)
                    id_regional = empresa_serializer.data['id_regional']
                    #print("/*/*/*///*/*/*/*/*/*/*/*/*/*", id_regional)
                else:
                    personal = EntidadPersona.objects.get(id_cuenta=vehiculo_serializer.data['id_cuenta']) 
                    personal_serializer = EntidadPersonaSerializer(personal)
                    #print("/*/*/*///*/*/0000000000000/*/*/*/*/*/*", personal_serializer.data)
                    id_regional = personal_serializer.data['id_regional'] 
                    #print("________________________________", id_regional)  

                print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;", id_regional, id_categoria)

                tarifa = Tarifario.objects.get(id_categoria=id_categoria, id_regional=id_regional)
                tarifa_vehiculo = TarifariosSerializer(tarifa)
                print("________________________________", serializer) 

                respuesta = {
                    'estado': True,
                    'mensaje': 'El tag existe',
                    'datos': {
                            'tag': serializer,
                            'vehiculo': vehiculo_serializer.data,
                            'cuenta': cuenta_serializer.data['tipo'],
                            'tarifa': tarifa_vehiculo.data['importe'],
                            'saldo': saldo
                        }
                }
                
                return Response(respuesta)
            except Vehiculo.DoesNotExist:
                # Manejar el caso donde el vehículo no existe para el tag dado
                return Response({
                    'estado': True,
                    'mensaje': 'El tag existe, pero no hay vehículo asociado.',
                    'data': []
                    })
                
        except Tags.DoesNotExist:
            # Manejar el caso donde el objeto Tags no existe
            return Response({
                'estado': False, 
                'mensaje': 'El tag no existe', 
                'data': []
                }, status=status.HTTP_404_NOT_FOUND)



class ListaTagDisponibles(APIView):
    def get(self, *args, **kwargs):
        #print("/8/8/8/8/8/8/8/8/8/8/8", pk)
        #print("/8/8/8/8/8/8/8/8/8/8/8", vehiculo)
        lista_tags = TagsSerializer(Tags.objects.filter(asignado = 'no', estado = 'habilitado', id_cuenta = None).order_by('-id'), many = True)
        #print("*/*/*/*/*/*/*/*/*/*/*/*/*/", lista_tags)
        return Response({'tags': lista_tags.data })
  



################################# Vehiculos #######################################
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404



class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all().order_by('-id_vehiculo')
    serializer_class = VehiculoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                cuenta = get_object_or_404(Cuenta, id_cuenta=data['id_cuenta'].id_cuenta)
                categoria = get_object_or_404(CategoriaVehiculo, id_categoria=data['id_categoria'].id_categoria)

                nuevo_vehiculo = Vehiculo.objects.create(
                    placa=data['placa'],
                    marca=data['marca'],
                    tipo=data['tipo'],
                    clase=data['clase'],
                    modelo=data['modelo'],
                    color=data['color'],
                    cilindrada=data['cilindrada'],
                    cap_carga=data.get('cap_carga'),
                    nro_ejes=data.get('nro_ejes'),
                    imagen_fronal_vehiculo=data.get('imagen_fronal_vehiculo'),
                    imagen_lateral_vehiculo=data.get('imagen_lateral_vehiculo'),
                    baja=0,
                    estado='habilitado',
                    id_cuenta=cuenta,
                    id_categoria=categoria,
                )

                return Response({
                    'message': 'Datos guardados correctamente',
                    'codigo_entidad': cuenta.id_cuenta,
                    'tipo_entidad': cuenta.tipo
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        # Conservar la imagen si no se proporciona una nueva
        if 'imagen_fronal_vehiculo' not in data or data['imagen_fronal_vehiculo'] is None or data['imagen_fronal_vehiculo']=='undefined':
            data['imagen_fronal_vehiculo'] = instance.imagen_fronal_vehiculo
        if 'imagen_lateral_vehiculo' not in data or data['imagen_lateral_vehiculo'] is None or data['imagen_lateral_vehiculo']=='undefined':
            data['imagen_lateral_vehiculo'] = instance.imagen_lateral_vehiculo

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='get-id-entidad')
    def get_id_entidad(self, request, pk=None):
        cuenta = get_object_or_404(Cuenta, id_cuenta=pk)
        return Response({'id_entidad': cuenta.id_cuenta}, status=status.HTTP_200_OK)

# class VehiculoViewSet(viewsets.ModelViewSet):
#     queryset = Vehiculo.objects.all().order_by('-id_vehiculo')
#     serializer_class = VehiculoSerializer
    


# class AgregarVehiculo(APIView):
    
#     def get(self, request, pk, *args, **kwargs):
#         try:
#             cuenta = Cuenta.objects.get(id_cuenta=pk)
#             cuenta_data = CuentaSerializer(cuenta).data
#             return Response({'id_entidad': cuenta_data['id_cuenta']})
#         except Cuenta.DoesNotExist:
#             return Response({'error': 'Cuenta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
#     def post(self, request, *args, **kwargs):
#         serializer = VehiculoSerializer(data=request.data)
        
#         if serializer.is_valid():
#             try:
#                 # Extracting validated data
#                 data = serializer.validated_data
#                 cuenta = Cuenta.objects.get(id_cuenta=data['id_cuenta'])
#                 categoria = CategoriaVehiculo.objects.get(id_categoria=data['id_categoria'])

#                 # Creating the new vehicle instance
#                 nuevo_vehiculo = Vehiculo.objects.create(
#                     placa=data['placa'],
#                     marca=data['marca'],
#                     tipo=data['tipo'],
#                     clase=data['clase'],
#                     modelo=data['modelo'],
#                     color=data['color'],
#                     cilindrada=data['cilindrada'],
#                     cap_carga=data['cap_carga'],
#                     nro_ejes=data['nro_ejes'],
#                     imagen_fronal_vehiculo=data.get('imagen_fronal_vehiculo'),
#                     imagen_lateral_vehiculo=data.get('imagen_lateral_vehiculo'),
#                     baja=0,
#                     estado='habilitado',
#                     id_cuenta=cuenta,
#                     id_categoria=categoria,
#                 )

#                 # Saving the new vehicle
#                 nuevo_vehiculo.save()

#                 return Response({
#                     'message': 'Datos guardados correctamente',
#                     'codigo_entidad': cuenta.id_cuenta,
#                     'tipo_entidad': cuenta.tipo
#                 })
#             except (Cuenta.DoesNotExist, CategoriaVehiculo.DoesNotExist):
#                 return Response({'error': 'Cuenta o categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)
#             except Exception as e:
#                 return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# class EditarVehiculo(APIView):
#     def get(self, *args, **kwargs):
#         pk = self.kwargs['pk']
#         vehiculo = VehiculoSerializer(Vehiculo.objects.get(id_vehiculo=pk)).data
#         #print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*", vehiculo)
      
#         return Response({
#             'empresa': vehiculo
#         }, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         serializer = VehiculoSerializer(data=request.data)
#         print("*0*0*0**0*0*0*0*0*0*0**0*0*0*0*", request.data)
#         # cuenta = Cuenta.objects.get(id_cuenta=request.data['id_cuenta'])
#         # cuenta_serializer = CuentaDetalleSerializer(cuenta)
#         # print("9090909090909090909090", cuenta)
#         if serializer.is_valid():
#             data = serializer.validated_data
#             #print("3213212313213213213132132131313", data['id_cuenta'])
            
#             id_vehiculo = request.data['id_vehiculo']
#             placa = request.data['placa']
#             marca = data['marca']
#             tipo = data['tipo']
#             clase = data['clase']
#             modelo = data['modelo']
#             color = data['color']
#             cilindrada = data['cilindrada']
#             cap_carga = data['cap_carga']
#             nro_ejes = data['nro_ejes']
#             imagen_fronal_vehiculo = data['imagen_fronal_vehiculo']
#             imagen_lateral_vehiculo = data['imagen_lateral_vehiculo']
#             id_cuenta = request.data['id_cuenta']

#             Vehiculo.objects.filter(id_vehiculo=id_vehiculo).update(
#                 placa=placa, 
#                 marca=marca, 
#                 tipo=tipo, 
#                 clase=clase, 
#                 modelo=modelo,
#                 color=color, 
#                 cilindrada=cilindrada, 
#                 cap_carga=cap_carga,
#                 nro_ejes=nro_ejes,
#                 imagen_fronal_vehiculo=imagen_fronal_vehiculo,
#                 imagen_lateral_vehiculo=imagen_lateral_vehiculo                
#                 )
        
#             try:
#                 return Response({'message': 'Datos actualizados correctamente', 'id_cuenta': id_cuenta})
#             except ObjectDoesNotExist:
#                 return Response({'error': 'vehiculo no encontrada'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def BajaVehiculo(request, id_vehiculo):
     idv = id_vehiculo
     vehiculo = Vehiculo.objects.filter(id_vehiculo= idv).update(baja=1)
     vehiculo = Vehiculo.objects.get(id_vehiculo= idv)
     vehiculo_serializer = VehiculoSerializer(vehiculo).data
     Tags.objects.filter(cod_tag=vehiculo.tag).update(estado='inhabilitado')
     return Response({'mensaje': 'Vehiculo dado de baja correctamente', 'id_cuenta': vehiculo_serializer['id_cuenta']}, status=status.HTTP_200_OK)  


class VerVehiculo(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        vehiculo = Vehiculo.objects.get(tag=pk, baja=0)
        vehiculo_serializer = VehiculoSerializer(vehiculo).data
        #cuenta = Cuenta.objects.get(id_cuenta=vehiculo.id_cuenta.id_cuenta)
        print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*", vehiculo_serializer['id_cuenta'])
        #Tags.objects.filter(id=vehiculo.tag).update(estado='inhabilitado')
        return Response({'mensaje': 'Vehiculo dado de baja correctamente', 'id_cuenta': vehiculo_serializer['id_cuenta']}, status=status.HTTP_200_OK)  
        
# -------------------------------------------RECARGA DE SALDO------------------------
class FormularioRecarga(APIView):
    
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            cuenta = Cuenta.objects.get(id_cuenta=pk)
            cuenta_serializer = CuentaDetalleSerializer(cuenta)

            if cuenta_serializer.data['tipo'] == 'empresa':
                empresa = EntidadEmpresa.objects.get(id_cuenta=pk)
                empresa_serializer = EntidadEmpresaSerializer(empresa)
                return Response({
                    "cuenta": cuenta_serializer.data,
                    "empresa": empresa_serializer.data
                })
            else:
                persona = EntidadPersona.objects.get(id_cuenta=pk)
                persona_serializer = EntidadPersonaSerializer(persona)
                lista_cuentas_bancarias = CuentasBancarias.objects.all()
                lista_cuentas_bancarias_serializer = CuentasBancariasSerializer(lista_cuentas_bancarias, many=True)
                return Response({
                    "cuenta": cuenta_serializer.data,
                    "persona": persona_serializer.data,
                    "cuentas_bancarias": lista_cuentas_bancarias_serializer.data
                })
        
        except Cuenta.DoesNotExist:
            return Response({'error': 'Cuenta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except (EntidadEmpresa.DoesNotExist, EntidadPersona.DoesNotExist):
            return Response({'error': 'Entidad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            cuenta = Cuenta.objects.get(id_cuenta=request.data['id_cuenta'])
            cuenta_serializer = CuentaDetalleSerializer(cuenta)

            nombre_depositante = request.data.get('nombre_depositante')
            celular = request.data.get('celular')
            monto_depositado = Decimal(request.data.get('monto_depositado'))
            tipo_pago = request.data.get('tipo_recarga')
            cuenta_bancaria = request.data.get('cuenta_bancaria', 0)
            id_cuenta = request.data.get('id_cuenta')
            fecha_deposito = datetime.now()

            if tipo_pago == 1:
                cuenta_bancaria = 0
            else:
                cuenta_bancaria = float(cuenta_bancaria) if cuenta_bancaria else 0

            if cuenta_serializer.data['tipo'] == 'empresa':
                empresa = EntidadEmpresa.objects.get(id_cuenta=id_cuenta)
                empresa_serializer = EntidadEmpresaSerializer(empresa)
                nombre_cuenta = empresa_serializer.data['razon_social']

            else:
                persona = EntidadPersona.objects.get(id_cuenta=id_cuenta)
                persona_serializer = EntidadPersonaSerializer(persona)
                nombre_cuenta = f"{persona_serializer.data['nombre']} {persona_serializer.data['ap_paterno']} {persona_serializer.data['ap_materno']}"

            # Crear depósito
            Depositos.objects.create(
                id_cuenta=cuenta,
                nombre_cuenta=nombre_cuenta,
                nombre_depositante=nombre_depositante,
                celular=celular,
                monto_depositado=monto_depositado,
                tipo_pago=tipo_pago,
                cuenta_bancaria=cuenta_bancaria,
                fecha_deposito=fecha_deposito
            )

            # Actualizar saldo de la cuenta
            cuenta_saldo = Decimal(cuenta_serializer.data['saldo']) + monto_depositado
            cuenta.saldo = cuenta_saldo
            cuenta.save()

            mensaje = 'Recarga exitosa'
            entidad_key = 'entidad_empresa' if cuenta_serializer.data['tipo'] == 'empresa' else 'entidad_persona'
            entidad_value = empresa_serializer.data['id_entidad_empresa'] if cuenta_serializer.data['tipo'] == 'empresa' else persona_serializer.data['id_entidad_persona']

            return Response({'mensaje': mensaje, entidad_key: entidad_value})

        except Cuenta.DoesNotExist:
            return Response({'error': 'Cuenta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except (EntidadEmpresa.DoesNotExist, EntidadPersona.DoesNotExist):
            return Response({'error': 'Entidad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        



class HistorialRecargas(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        cuenta=Cuenta.objects.get(id_cuenta=pk)
        cuenta_serializer = CuentaDetalleSerializer(cuenta)
        cuenta_tipo = cuenta_serializer.data['tipo']
        #print("*9*9*9*9*9*9*9*9*9*9*9*9*", cuenta_serializer.data)
        depositos=Depositos.objects.filter(id_cuenta=pk).order_by('-fecha_deposito')
        depositos_serializer = DepositosSerializer(depositos, many = True)
        print("*9*9*9*9*9*9*9*9*9*9*9*9*", depositos_serializer.data)
        if cuenta_tipo =='personal':
            persona=EntidadPersona.objects.get(id_cuenta=pk)
            persona_serializer = EntidadPersonaSerializer(persona)
            return Response({
                'entidad':persona_serializer.data,
                'lista_depositos':depositos_serializer.data
                })
        else:
            empresa=EntidadEmpresa.objects.get(id_cuenta=pk)
            empresa_serializer = EntidadEmpresaSerializer(empresa)
            return Response({
                'entidad':empresa_serializer.data,
                'lista_depositos':depositos_serializer.data
                })
                

# # ---------------------------------------------CONTRATOS EMPRESA/PERSONA---------------------------------------

class mostrarContratos(APIView):
    def get(self, request, *args, **kwargs):
        lista_contratos = EntidadContrato.objects.all().order_by('created')
        lista_contratos_serializer = EntidadContratoSerializer(lista_contratos, many = True)
        print("/888/8/8/8/8/8/8/8/8/8/", lista_contratos_serializer.data)
        if lista_contratos:
            return Response({'lista_contratos': lista_contratos_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'message':"No existe contratos para mostrarse"},status=status.HTTP_404_NOT_FOUND)

class VerContratoEmpresa(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        lista_contratos = EntidadContrato.objects.filter(id_entidad_empresa=pk).order_by('-id_contrato')
        lista_contratos_serializer = EntidadContratoSerializer(lista_contratos, many = True)
        contrato = EntidadContrato.objects.filter(id_entidad_empresa=pk).get(baja_contrato=0)
        contrato_serializer = EntidadContratoSerializer(contrato)
        if lista_contratos and contrato:
            return Response(lista_contratos_serializer.data)
        else:
            return Response({"message":"Hubo un error al intentar buscar contratos emresa"}, status=status.HTTP_404_NOT_FOUND)

class VerContratoPersona(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']     
        contrato = EntidadContrato.objects.filter(id_entidad_persona=pk).get(baja_contrato=0)
        contrato_serializer = EntidadContratoSerializer(contrato)
        lista_contratos = EntidadContrato.objects.filter(id_entidad_persona=pk).order_by('-id_contrato')
        lista_contratos_serializer = EntidadContratoSerializer(lista_contratos, many = True)
        if lista_contratos and contrato:
            return Response(lista_contratos_serializer.data)
        else:
            return Response({"message":"Hubo un error al intentar buscar contratos persona"}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET', 'PATCH'])
def BajaContratoEmpresa(request, idc):
    try:
        contrato = EntidadContrato.objects.get(id_contrato=idc)
        contrato_serializer = EntidadContratoSerializer(contrato)
    except EntidadContrato.DoesNotExist:
        return Response({'error': 'El contrato no existe'}, status=status.HTTP_404_NOT_FOUND)
    

    if request.method == 'GET':
        return Response(contrato_serializer.data)

    elif request.method == 'PATCH':
        # Lógica para manejar la solicitud PATCH
        if contrato.id_entidad_empresa:
            entidad_serializer = EntidadEmpresaSerializer(EntidadEmpresa.objects.get(id_entidad_empresa=contrato_serializer.data['id_entidad_empresa']))
        else:
            entidad_serializer = EntidadPersonaSerializer(EntidadPersona.objects.get(id_entidad_persona=contrato_serializer.data['id_entidad_persona']))
        print("121212121212121212121212121", entidad_serializer['id_cuenta'])
        # Ejemplo: Actualizar un campo específico del contrato
        contrato.estado = request.data.get('estado', contrato.estado)
        contrato.descripcion = request.data.get('descripcion', contrato.descripcion)
        contrato.save()

        # Volver a serializar el contrato después de actualizar
        contrato_serializer = EntidadContratoSerializer(contrato)

        if request.data.get('estado') == 1:
            cuenta = Cuenta.objects.get(id_cuenta=entidad_serializer.data['id_cuenta'])
            cuenta.estado = "habilitado"
            cuenta.save()
            #msj = "Contrato activo y actualizado correctamente"
        elif request.data.get('estado') == 2:
            cuenta = Cuenta.objects.get(id_cuenta=entidad_serializer.data['id_cuenta'])
            cuenta.estado = "inhabilitado"
            cuenta.save()
            #msj = "Contrato inactivo y Cuenta Inhabilitada"

        return Response({'mensaje': "Contrato y cuenta actualizada correctamente", 'contrato': contrato_serializer.data}, status=status.HTTP_200_OK)










class RegistrarNuevoContratoEmpresa(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        contrato = EntidadContrato.objects.get(id_contrato=pk)
        contrato_serializer = EntidadContratoSerializer(contrato)
        return Response({
            'contrato_actual': contrato_serializer.data
            })

    def post(self, request, *args, **kwargs):
        #pk = self.kwargs['pk']
        id_ultimo_contrato = request.data['id_ultimo_contrato']
        contrato = EntidadContrato.objects.get(id_contrato = id_ultimo_contrato)
        contrato_serializer = EntidadContratoSerializer(contrato)
              
        fecha_ini = request.data['fecha_ini_contrato']
        fecha_fin = request.data['fecha_fin_contrato']
        nuevo_doc = request.data['doc_contrato']
        baja = 0
        id_entidad_empresa = contrato_serializer.data['id_entidad_empresa']
        cuenta = EntidadEmpresa.objects.filter(id_entidad_empresa = id_entidad_empresa).get(baja = 0)
        cuenta_serializer = EntidadEmpresaSerializer(cuenta)
        EntidadContrato.objects.filter(id_contrato=id_ultimo_contrato).update(baja_contrato=1)

        nuevo_contrato=EntidadContrato.objects.create(
                                                        id_entidad_empresa = contrato.id_entidad_empresa, 
                                                        fecha_ini_contrato = fecha_ini,
                                                        fecha_fin_contrato = fecha_fin, 
                                                        baja_contrato = baja, 
                                                        doc_contrato = nuevo_doc
                                                     )

        ultimo_contrato = EntidadContrato.objects.last()
        ultimo_contrato_serializer = EntidadContratoSerializer(ultimo_contrato)
        #print("9*9*9*9*9*9*9*9*9*9*9*9*9*9*9*9*", ultimo_contrato.id_entidad_empresa.id_cuenta.id_cuenta)
        Cuenta.objects.filter(id_cuenta = ultimo_contrato.id_entidad_empresa.id_cuenta.id_cuenta).update(
                                                                        fecha_inicio=fecha_ini, 
                                                                        fecha_fin=fecha_fin
                                                                      )
        return Response({
            'mensaje': "Contrato adicionado correctamente",
            'VerContratoEmpresa':ultimo_contrato.id_entidad_empresa.id_entidad_empresa
            })

class RegistrarNuevoContratoPersona(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        contrato = EntidadContrato.objects.get(id_contrato=pk)
        contrato_serializer = EntidadContratoSerializer(contrato)
        return Response({
            'contrato_actual': contrato_serializer.data
            })

    def post(self, request, *args, **kwargs):
        #pk = self.kwargs['pk']
        id_ultimo_contrato = request.data['id_ultimo_contrato']
        contrato = EntidadContrato.objects.get(id_contrato = id_ultimo_contrato)
        contrato_serializer = EntidadContratoSerializer(contrato)
              
        fecha_ini = request.data['fecha_ini_contrato']
        fecha_fin = request.data['fecha_fin_contrato']
        nuevo_doc = request.data['doc_contrato']
        baja = 0
        id_entidad_persona = contrato_serializer.data['id_entidad_persona']
        cuenta = EntidadPersona.objects.filter(id_entidad_persona = id_entidad_persona).get(baja = 0)
        cuenta_serializer = EntidadPersona(cuenta)
        EntidadContrato.objects.filter(id_contrato=id_ultimo_contrato).update(baja_contrato=1)

        nuevo_contrato=EntidadContrato.objects.create(
                                                        id_entidad_persona = contrato.id_entidad_persona, 
                                                        fecha_ini_contrato = fecha_ini,
                                                        fecha_fin_contrato = fecha_fin, 
                                                        baja_contrato = baja, 
                                                        doc_contrato = nuevo_doc
                                                     )

        ultimo_contrato = EntidadContrato.objects.last()
        ultimo_contrato_serializer = EntidadContratoSerializer(ultimo_contrato)
        #print("9*9*9*9*9*9*9*9*9*9*9*9*9*9*9*9*", ultimo_contrato.id_entidad_empresa.id_cuenta.id_cuenta)
        Cuenta.objects.filter(id_cuenta = ultimo_contrato.id_entidad_persona.id_cuenta.id_cuenta).update(
                                                                        fecha_inicio=fecha_ini, 
                                                                        fecha_fin=fecha_fin                                                                      
                                                                      )
        return Response({
            'mensaje': "Contrato adicionado correctamente",
            'VerContratoPersona':ultimo_contrato.id_entidad_persona.id_entidad_persona
            })