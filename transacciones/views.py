from django.shortcuts import render,redirect
from parametros.models import *
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date, timedelta,time
from rest_framework.views import APIView
from rest_framework.response import Response
from parametros.serializers import *
from administracion.serializers import *
from .serializers import *
from rest_framework import status
from django.contrib import messages
import random
from django.db.models import Sum
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from time import sleep
import os
from django.http import JsonResponse, HttpResponse
from django.template.loader import *
from num2words import num2words
#from rest_framework.request import Request
import random
import string
from django.utils import timezone
# from django.db import connection

# with connection.cursor() as cursor:
#     cursor.execute("SELECT now();")
#     result = cursor.fetchone()
#     print(result)

@api_view(['GET'])
def ListarTransaccionesTag(request):
    fecha_transacciones=datetime.now().date()
    lista_transacciones_tag = Transaccion.objects.filter(fecha=fecha_transacciones).exclude(id_cuenta=None).order_by('fecha')
    lista_transacciones_tag_serializer=Transaciones_Tag_Serializer(lista_transacciones_tag,many=True).data    
    return Response(lista_transacciones_tag_serializer)

@api_view(['POST'])
def Recibir_Tag(request):
    data = request.data
    tag_leido = data['tag_leido']  
    nueva_recepcion = ReceptorDatos.objects.create(tag_leido=tag_leido)
    if nueva_recepcion:
        if nueva_recepcion.tag_leido!='':
            return Registrar_Transaccion_Telepeaje(request,nueva_recepcion.tag_leido)

# @api_view(['POST'])
# def RecibirCodigo(request):
#     data = request.data
#     codigo = data['codigo']
#     tipo = data['tipo']  
#     nueva_recepcion = ReceptorDatos.objects.create(tag_leido=codigo,tipo=tipo)
#     if nueva_recepcion:
#         if nueva_recepcion.tag_leido!='':
#             return Registrar_Transaccion_Telepeaje(request,nueva_recepcion)
           


@api_view(['POST'])
def Recibir_Datos(request):
    data = request.data
    tag_leido = data['tag_leido']
    placa=data['placa']
    numero_ejes_inicio=data['numero_ejes_inicio']
    numero_ejes_salida=data['numero_ejes_salida']
    ancho_vehiculo=data['ancho_vehiculo']
    alto_vehiculo=data['alto_vehiculo']
    clase_vehiculo=data['clase_vehiculo']
    imagen_frontal=data['imagen_frontal']
    imagen_lateral=data['imagen_lateral']
    estado = data['estado']    
    nueva_recepcion = ReceptorDatos.objects.create(tag_leido=tag_leido,placa=placa,
                                                   numero_ejes_inicio=numero_ejes_inicio,
                                                   numero_ejes_salida=numero_ejes_salida,
                                                   ancho_vehiculo=ancho_vehiculo,
                                                   alto_vehiculo=alto_vehiculo,
                                                   clase_vehiculo=clase_vehiculo,
                                                   imagen_frontal=imagen_frontal,
                                                   imagen_lateral=imagen_lateral,
                                                   estado=estado,                                                   
                                                   )
    if nueva_recepcion:
        if nueva_recepcion.tag_leido!='':
            return Registrar_Transaccion_Telepeaje(request,nueva_recepcion.tag_leido)
            
        else:
            return ActualizarTransaccion(request,nueva_recepcion) 
           
def Registrar_Transaccion_Telepeaje(request,tag_leido):
    id_regional = Regionales.objects.get(id=3)

    if ExisteTag(tag_leido):
            id_categoria = ObtenerCategoriaCuenta(tag_leido) 
            saldo=TieneSaldo(tag_leido)
            importe_telepeaje = ObtenerImporteCuenta(id_categoria, id_regional)        
            if ContratoVigente(tag_leido):
                if saldo>importe_telepeaje:               
                    tag_leido = tag_leido
                    id_reten = Retenes.objects.get(id_reten=119)
                    id_carril = 2
                    id = GenerarId(request)
                    id_turno=BuscarTurnosDisponibles() 
                    if ObtenerIdCiclo(id_regional,id_reten,id_carril,request):
                        id_ciclo = ObtenerIdCiclo(id_regional,id_reten,id_carril,request)
                    else:
                        return Response({'message':'no existe el ciclo'})                
                    tipo_carril = 'Normal'
                    id_ruta = Rutas.objects.get(id_ruta=20)
                    tipo_recibo = ''
                    tipo_pago = ObtenerTipoPago(tag_leido)
                    nombre_revisor = ''
                    comentario_revisor = 's/c'    
                        # corregir con el nueva tabla de turnos
                    id_grupo_excento = 1
                    placa = ObtenerPlaca(tag_leido)
                    ancho_vehiculo = ''
                    alto_vehiculo = ''
                    numero_remolques = 0
                    clase_vehiculo = ObtenerClaseVehiculo(tag_leido)
                    imagen_frontal = ''
                    imagen_lateral = ''
                    id_denuncia = 0
                    mensaje_panel = 'Buen Viaje'
                    estado = 'Correcto' 
                    id_cuenta = ObtenerIdCuenta(tag_leido)
                        
                    localidad_ini = 'El Alto'
                    localidad_dest = 'La Paz'
                    vehiculo = Vehiculo.objects.filter(tag=tag_leido,baja=0).first()
                    numero_ejes = vehiculo.nro_ejes
                    clase_vehiculo = vehiculo.clase
                    imagen_frontal = vehiculo.imagen_fronal_vehiculo
                    imagen_lateral = vehiculo.imagen_lateral_vehiculo
                    tipo_carril = 'Telepeaje'
                    fecha_actual=datetime.now()
                    nueva_transaccion=Transaccion.objects.create(id=id, id_ciclo=id_ciclo, id_cuenta=id_cuenta, id_regional=id_regional, id_reten=id_reten, id_carril=id_carril,
                                                tipo_carril=tipo_carril, id_categoria=id_categoria, id_ruta=id_ruta, localidad_inicio=localidad_ini,
                                                localidad_fin=localidad_dest, importe_recaudador=0, importe_telepeaje=importe_telepeaje,# agregar el id_turno
                                                tipo_recibo=tipo_recibo, tipo_pago=tipo_pago, nombre_revisor=nombre_revisor,id_turno=id_turno.id_turno,
                                                id_grupo_exento=id_grupo_excento, placa=placa, numero_ejes_inicio=numero_ejes,
                                                numero_ejes_salida=numero_ejes, ancho_vehiculo=ancho_vehiculo, alto_vehiculo=alto_vehiculo,
                                                numero_remolques=numero_remolques, clase_vehiculo=clase_vehiculo, imagen_frontal=imagen_frontal,
                                                imagen_lateral=imagen_lateral, tag_leido=tag_leido, id_denuncia=id_denuncia, mensaje_panel=mensaje_panel, estado=estado,
                                                fecha=fecha_actual, hora=fecha_actual.time(),anio=fecha_actual.year,mes=fecha_actual.month,dia=fecha_actual.day)


                # -------------------EL SIGUIENTE CODIGO HACE LA RESTA DEL SALDO DE UNA CUENTA CUANDO EL VEHICULO CUENTA CON TAG-------------------------
                    vehiculo = Vehiculo.objects.filter(baja=0, tag=tag_leido)
                    cuenta = vehiculo[0].id_cuenta
                    cuenta.saldo -= importe_telepeaje
                    nueva_transaccion.saldo_restante=cuenta.saldo
                    nueva_transaccion.save()
                    cuenta.save()
                    print("WWWWWWWWWWWWWWWWWWWW",'Saldo Restante de Cuenta',cuenta.id_cuenta,' : ',cuenta.saldo,)
                    
                    if nueva_transaccion:
                        ciclo_transaccion=CicloTransacciones.objects.filter(id=1).first()
                        ciclo_transaccion.cantidad+=1
                        ciclo_transaccion.save()
                        if ciclo_transaccion.cantidad>=400:
                            CerrarCiclo()
                        respuesta="Importe: "+str(nueva_transaccion.importe_telepeaje)+" Bs"
                        return Response({'message':respuesta, 'estado':True},status=status.HTTP_200_OK)
                    else:
                        return Response({'message': 'error de registro', 'estado':False})
                else:
                    return Response({'message':'Saldo Insuficiente', 'estado':False})
            else:
                return Response({'message':'Contrado Finalisado', 'estado':False})
    else:
        return Response({'message':'', 'estado':False})
    
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Registrar_Transaccion_Roceta(request):
    numero_roceta=request.data['numero_roseta']
    id_regional = Regionales.objects.get(id=3)
    if ExisteRoceta(numero_roceta):
            vehiculo=Vehiculo.objects.filter(baja=0,numero_roceta=numero_roceta).first()
            id_categoria = vehiculo.id_categoria
            saldo=TieneSaldoRoceta(numero_roceta)
            importe_telepeaje = ObtenerImporteCuenta(id_categoria, id_regional)        
            if ContratoVigenteRoceta(numero_roceta):
                if saldo>importe_telepeaje:               
                    numero_roceta = numero_roceta
                    id_reten = Retenes.objects.get(id_reten=119)

                    id_usuario=request.user.id
                    caja_carril=CajaCarril.objects.filter(id_recaudador=id_usuario,estado='Abierto').first()

                    id_carril = caja_carril.numero_carril
                    id = GenerarId(request)
                    id_turno=BuscarTurnosDisponibles() 
                    if ObtenerIdCiclo(id_regional,id_reten,id_carril,request):
                        id_ciclo = ObtenerIdCiclo(id_regional,id_reten,id_carril,request)
                    else:
                        return Response({'message':'no existe el ciclo'})                
                    tipo_carril = 'mixto'
                    id_ruta = Rutas.objects.get(id_ruta=1)
                    tipo_recibo = ''
                    tipo_pago = 'Cobro Automatico'
                    nombre_revisor = ''
                    comentario_revisor = 's/c'    
                        # corregir con el nueva tabla de turnos
                    id_grupo_excento = 1
                    placa = vehiculo.placa
                    ancho_vehiculo = ''
                    alto_vehiculo = ''
                    numero_remolques = 0
  
                    imagen_frontal = ''
                    imagen_lateral = ''
                    id_denuncia = 0
                    mensaje_panel = 'Buen Viaje'
                    estado = 'Correcto' 
                    id_cuenta = vehiculo.id_cuenta
                        
                    localidad_ini = 'El Alto'
                    localidad_dest = 'La Paz'

                    numero_ejes = vehiculo.nro_ejes
                    clase_vehiculo = vehiculo.clase
                    imagen_frontal = vehiculo.imagen_fronal_vehiculo
                    imagen_lateral = vehiculo.imagen_lateral_vehiculo
                    tipo_carril = 'mixto'
                    fecha_actual=datetime.now()
                    nueva_transaccion=Transaccion.objects.create(id=id, id_ciclo=id_ciclo, id_cuenta=id_cuenta, id_regional=id_regional, id_reten=id_reten, id_carril=id_carril,
                                                tipo_carril=tipo_carril, id_categoria=id_categoria, id_ruta=id_ruta, localidad_inicio=localidad_ini,
                                                localidad_fin=localidad_dest, importe_recaudador=0, importe_telepeaje=importe_telepeaje,# agregar el id_turno
                                                tipo_recibo=tipo_recibo, tipo_pago=tipo_pago, nombre_revisor=nombre_revisor,id_turno=id_turno.id_turno,
                                                id_grupo_exento=id_grupo_excento, placa=placa, numero_ejes_inicio=numero_ejes,
                                                numero_ejes_salida=numero_ejes, ancho_vehiculo=ancho_vehiculo, alto_vehiculo=alto_vehiculo,
                                                numero_remolques=numero_remolques, clase_vehiculo=clase_vehiculo, imagen_frontal=imagen_frontal,
                                                imagen_lateral=imagen_lateral, tag_leido='',numero_roseta=numero_roceta, id_denuncia=id_denuncia, mensaje_panel=mensaje_panel, estado=estado,
                                                fecha=fecha_actual, hora=fecha_actual.time(),anio=fecha_actual.year,mes=fecha_actual.month,dia=fecha_actual.day)


                # -------------------EL SIGUIENTE CODIGO HACE LA RESTA DEL SALDO DE UNA CUENTA CUANDO EL VEHICULO CUENTA CON TAG-------------------------
                    vehiculo = Vehiculo.objects.filter(baja=0, numero_roceta=numero_roceta)
                    cuenta = vehiculo[0].id_cuenta
                    cuenta.saldo -= importe_telepeaje
                    nueva_transaccion.saldo_restante=cuenta.saldo
                    nueva_transaccion.save()
                    cuenta.save()
                    print("WWWWWWWWWWWWWWWWWWWW",'Saldo Restante de Cuenta',cuenta.id_cuenta,' : ',cuenta.saldo,)
                    
                    if nueva_transaccion:
                        ciclo_transaccion=CicloTransacciones.objects.filter(id=1).first()
                        ciclo_transaccion.cantidad+=1
                        ciclo_transaccion.save()
                        if ciclo_transaccion.cantidad>=400:
                            CerrarCiclo()
                        respuesta="Importe: "+str(nueva_transaccion.importe_telepeaje)+" Bs"
                        return Response({'message':respuesta, 'estado':True},status=status.HTTP_200_OK)
                    else:
                        return Response({'message': 'error de registro', 'estado':False})
                else:
                    return Response({'message':'Saldo Insuficiente', 'estado':False})
            else:
                return Response({'message':'Contrado Finalisado', 'estado':False})
    else:
        return Response({'message':'', 'estado':False})
      
def ExisteTag(tag_leido):
    #print("RRRRRRRRRRRRRRRRRRR",'Tag leido: ',tag_leido)
    resultado=Vehiculo.objects.filter(baja=0,tag=tag_leido)
    if resultado:
        return True
    else:
        return False
def ExisteRoceta(numero_roceta):
    resultado=Vehiculo.objects.filter(baja=0,numero_roceta=numero_roceta)
    if resultado:
        return True
    else:
        return False
    
def TieneSaldo(tag_leido):
    vehiculo=Vehiculo.objects.filter(baja=0,tag=tag_leido).first()
    cuenta=Cuenta.objects.filter(id_cuenta=vehiculo.id_cuenta.id_cuenta).first()
    return cuenta.saldo
def TieneSaldoRoceta(numero_roceta):
    vehiculo=Vehiculo.objects.filter(baja=0,numero_roceta=numero_roceta).first()
    cuenta=Cuenta.objects.filter(id_cuenta=vehiculo.id_cuenta.id_cuenta).first()
    return cuenta.saldo

def ContratoVigente(tag_leido):
    vehiculo=Vehiculo.objects.filter(baja=0,tag=tag_leido).first()
    cuenta=Cuenta.objects.get(id_cuenta=vehiculo.id_cuenta.id_cuenta)
    fecha_actual=datetime.now().date()
    if fecha_actual<=cuenta.fecha_fin:
        return True
    else:
        return False
def ContratoVigenteRoceta(numero_roceta):
    vehiculo=Vehiculo.objects.filter(baja=0,numero_roceta=numero_roceta).first()
    cuenta=Cuenta.objects.get(id_cuenta=vehiculo.id_cuenta.id_cuenta)
    fecha_actual=datetime.now().date()
    if fecha_actual<=cuenta.fecha_fin:
        return True
    else:
        return False
   
def GenerarId(request):
    try:
        usuario=request.user.id
        id_regional=AuthUser.objects.get(id=usuario).id_regional.id
    except:
        id_regional=Regionales.objects.filter(baja=0).first().id

    id_reten=Retenes.objects.filter(id_regional=id_regional).first().id_reten
    fecha_actual = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    id = str(id_regional)+str(id_reten) + fecha_actual
    id=int(id)
    return id


def ObtenerIdCiclo(id_regional,id_reten,id_carril,request):
    hora_actual=datetime.now()
    try:
        ciclo = Ciclo.objects.get(finalizado=False)
        return ciclo            
    except ObjectDoesNotExist:
        nuevo_ciclo=Ciclo.objects.create(id=GenerarId(request),
                                           fecha_inicio=hora_actual.date(),
                                           hora_inicio=hora_actual.time(),
                                           created=hora_actual,
                                           id_regional=id_regional,
                                           id_reten=id_reten,
                                           id_carril=id_carril,
                                           id_turno=BuscarTurnosDisponibles(),
                                           finalizado=False)
        return nuevo_ciclo
def CerrarCiclo():
    ciclos = Ciclo.objects.filter(finalizado=False)
    ciclo_transaccion=CicloTransacciones.objects.get(id=1)
    ciclo_transaccion.cantidad=0
    ciclo_transaccion.save()
    hora_actual=datetime.now()
    if ciclos:
        for ciclo in ciclos:
            ciclo.finalizado = True
            ciclo.fecha_fin=hora_actual.date()
            ciclo.hora_fin=hora_actual.time()
            ciclo.modified=hora_actual
            ciclo.save()  # Asegúrate de guardar los cambios en la base de datos
        return True
    return False
     
def ObtenerTag():
    tag = ''
    tiene_tag = random.randint(0, 3)
    if (tiene_tag == 0):
        lista_tag = Vehiculo.objects.filter(
            ~Q(tag=None), baja=0).values_list('tag', flat=True)
        tag_random = random.choice(lista_tag)
        tag = str(tag_random)
    else:
        tag = ''
    return tag


def ObtenerCategoria(id_categoria):
    try:
        categoria=CategoriaVehiculo.objects.get(id_categoria=id_categoria)
        #print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRR",categoria)
        return categoria
    except ObjectDoesNotExist:
        return Response({'message':'No existe la Categoria Para este Vehiculo'})


def ObtenerImporte(id_categoria, id_regional):
    tarifario = Tarifario.objects.get(
        id_categoria=id_categoria, id_regional=id_regional)
    importe = tarifario.importe
    return importe


def ObtenerTipoPago(tag_leido):
    tipo_pago = ''
    if not tag_leido:
        tipo_pago = 'Efectivo'
    else:
        tipo_pago = 'Cobro Automatico'
    return tipo_pago


def ObtenerPlaca(tag_leido):
    placa = ''
    if (tag_leido != ''):
        vehiculo = Vehiculo.objects.filter(tag=tag_leido,baja=0).first()
        placa = vehiculo.placa
        return placa
    else:
        return placa


def ObtenerClaseVehiculo(tag_leido):
    clase_vehiculo = Vehiculo.objects.filter(tag=tag_leido).first().clase
    return clase_vehiculo


def VerificarEstado(importe_recaudador, importe_telepeaje):
    estado = 'Observado'
    if (importe_recaudador == importe_telepeaje):
        estado = 'Correcto'
        return estado
    else:
        return estado


def ObtenerIdCuenta(tag_leido):
    id_cuenta = Vehiculo.objects.filter(tag=tag_leido,baja=0).first().id_cuenta
    return id_cuenta 


def ObtenerCategoriaCuenta(tag_leido):
    id_categoria = Vehiculo.objects.get(baja=0,tag=tag_leido).id_categoria
    return id_categoria

def ObtenerTarifarios(id_regional):
    lista_tarifarios = Tarifario.objects.filter(baja=0, id_regional=id_regional)
    return lista_tarifarios

def ObtenerImporteCuenta(id_categoria, id_regional):
    try:
        importe = Tarifario.objects.filter(id_categoria=id_categoria,
                                    id_regional=id_regional,
                                    localidad_origen='El Alto',
                                    localidad_destino='La Paz').first()
        return importe.importe 
    except ObjectDoesNotExist:
        return Response({'message':'No existe Tarifario para este vehiculo'})
        

def BuscarTurnosDisponibles():
    hora_actual = datetime.now().time()
    hora_00 = time(0, 0)  # 00:00
    hora_06 = time(6, 0)  # 06:00
    hora_18 = time(18, 0)  # 18:00
    hora_23 = time(23, 0)  # 23:

    if hora_00 <= hora_actual < hora_06:
        turno = Turnos.objects.get(id_turno=5)      
    elif hora_06 <= hora_actual < hora_18:
        turno = Turnos.objects.get(id_turno=4)
    elif hora_18 <= hora_actual < hora_23:       
        turno = Turnos.objects.get(id_turno=5)
    #print("TTTTTTTTTTTTTTTTTTTTTTTTTTT",turno.nombre)
    return turno

def ObtenerIdCajaCarril(id_usuario):
    try:
        caja_carril = CajaCarril.objects.get(id_recaudador=id_usuario, estado='Abierto', fecha_operaciones=datetime.now().date())
        return caja_carril
    except ObjectDoesNotExist:        
        return None
    
def ActualizarTransaccion(response,data):
    placa=data.placa
    numero_ejes_inicio=data.numero_ejes_inicio
    numero_ejes_salida=data.numero_ejes_inicio
    ancho_vehiculo=data.ancho_vehiculo
    alto_vehiculo=data.alto_vehiculo
    clase_vehiculo=''
    imagen_frontal=data.imagen_frontal
    imagen_lateral=data.imagen_lateral
    estado=data.estado
    if estado:
        try:
            #ultima_transaccion = Transaccion.objects.filter(id_cuenta=None).latest('created')
            ultima_transaccion = Transaccion.objects.filter(id_cuenta=None).latest('correlacion')
            #ultima_transaccion = Transaccion.objects.last()
            

        except Transaccion.DoesNotExist:
            ultima_transaccion = None

    if ultima_transaccion:
    # Hacer algo con la última transacción que cumple con la condición
        ultima_transaccion.placa=placa
        ultima_transaccion.numero_ejes_inicio=numero_ejes_inicio
        ultima_transaccion.numero_ejes_salida=numero_ejes_salida
        ultima_transaccion.ancho_vehiculo=ancho_vehiculo
        ultima_transaccion.alto_vehiculo=alto_vehiculo
        ultima_transaccion.clase_vehiculo=clase_vehiculo
        ultima_transaccion.imagen_frontal=imagen_frontal
        ultima_transaccion.imagen_lateral=imagen_lateral
        ultima_transaccion.save()
        print(f'ID de la última transacción: {ultima_transaccion.id}')
    else:       
        print('No hay transacciones que cumplan con la condición en la base de datos')

    return Response({'message':'ok'},status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Registrar_Transaccion_Recaudador(request):
    id_usuario = request.user.id
    datos= request.data
    caja_carril = ObtenerIdCajaCarril(id_usuario)
    datos_boleto={}
    if caja_carril:
        id = GenerarId(request)
        id_reten = caja_carril.id_reten
        id_regional = Regionales.objects.filter(id=3).first()
        id_carril = caja_carril.numero_carril
        id_ciclo = ObtenerIdCiclo(id_regional,id_reten,id_carril,request) 
        tipo_carril = 'Normal'
        id_categoria = ObtenerCategoria(datos['id_categoria'])
        id_ruta = Rutas.objects.get(id_ruta=1)
        tarifario_seleccionado=Tarifario.objects.filter(id_tarifario=datos['id_tarifario']).first()
        localidad_inicio = tarifario_seleccionado.localidad_origen
        localidad_fin = tarifario_seleccionado.localidad_destino
        importe_recaudador = tarifario_seleccionado.importe
        importe_telepeaje = 0
        tipo_recibo = ''
        tipo_pago = 'Efectivo'
        nombre_revisor = ''
        comentario_revisor = 's/c'
        #id_turno = caja_carril.turno
        
        id_caja_carril=caja_carril
        placa = '' # OBTENER DISPOSITIVOS
        numero_ejes = 0 # OBTENER DISPOSITIVOS
        ancho_vehiculo = '' # OBTENER DISPOSITIVOS
        alto_vehiculo = '' # OBTENER DISPOSITIVOS
        numero_remolques = 0 # OBTENER DISPOSITIVOS
        clase_vehiculo = '' # OBTENER DISPOSITIVOS
        imagen_frontal = '' # OBTENER DISPOSITIVOS
        imagen_lateral = '' # OBTENER DISPOSITIVOS
        id_denuncia = 0
        recaudador=AuthUser.objects.get(id=id_usuario)
        mensaje_panel = 'Buen Viaje'
        estado = VerificarEstado(importe_recaudador, importe_telepeaje)
        fecha_actual=datetime.now()
        print("KKKKKKKKKKKKKKKKKKKKKKKKKKKK",fecha_actual)  
        reciboid_generado = generar_reciboid()  
        nueva_transaccion=Transaccion.objects.create(id=id, id_ciclo=id_ciclo, id_regional=id_regional, id_reten=id_reten, id_carril=id_carril, tipo_carril=tipo_carril,
                                    id_categoria=id_categoria, id_ruta=id_ruta, localidad_inicio=localidad_inicio, localidad_fin=localidad_fin, id_recaudador=recaudador,
                                    importe_recaudador=importe_recaudador, importe_telepeaje=0, tipo_recibo=tipo_recibo, tipo_pago=tipo_pago,id_caja_carril=id_caja_carril,
                                    nombre_revisor=nombre_revisor, placa='',comentario_revisor=comentario_revisor,
                                    numero_ejes_inicio=numero_ejes, numero_ejes_salida=numero_ejes, ancho_vehiculo=ancho_vehiculo,
                                    alto_vehiculo=alto_vehiculo, numero_remolques=numero_remolques, clase_vehiculo='', imagen_frontal='', imagen_lateral='',
                                    id_denuncia=id_denuncia, mensaje_panel=mensaje_panel, estado=estado, fecha=fecha_actual, hora=fecha_actual.time(),
                                    anio=fecha_actual.year,mes=fecha_actual.month,dia=fecha_actual.day,codigo_boleto=reciboid_generado)
        if nueva_transaccion:
            datos_boleto={}
            datos_boleto['fecha']=nueva_transaccion.fecha.strftime('%Y-%m-%d')
            datos_boleto['hora']=nueva_transaccion.hora.strftime('%H:%M:%S')
            datos_boleto['importe']=str(nueva_transaccion.importe_recaudador)+'Bs'
            datos_boleto['literal']=OptenerLiteral(nueva_transaccion.importe_recaudador)
            datos_boleto['carril']=nueva_transaccion.id_carril
            datos_boleto['estacion']=nueva_transaccion.id_reten.nombre_reten
            datos_boleto['recaudador']=nueva_transaccion.id_recaudador.username
            datos_boleto['categoria']=nueva_transaccion.id_categoria.nombre_categoria
            datos_boleto['tramo']=nueva_transaccion.localidad_fin+" - "+nueva_transaccion.localidad_inicio
            datos_boleto['sentido']='('+Tarifario.objects.filter(id_tarifario=datos['id_tarifario']).first().sentido+')'
            datos_boleto['boleto']=nueva_transaccion.codigo_boleto
            datos_boleto['estado']='ok'
            monitor=Monitor.objects.filter(id_categoria=nueva_transaccion.id_categoria.id_categoria).first()
            cantidad=monitor.cantidad+1
            monitor.cantidad=cantidad
            monitor.importe_total=monitor.importe* cantidad
            monitor.save()
            monitor_total=MonitorTotal.objects.get(id=1)
            monitor_total.monto+=nueva_transaccion.importe_recaudador
            monitor_total.save()

            ciclo_transaccion=CicloTransacciones.objects.filter(id=1).first()
            ciclo_transaccion.cantidad+=1
            ciclo_transaccion.save()
            if ciclo_transaccion.cantidad>=400:
                CerrarCiclo()
            return Response(datos_boleto,status=status.HTTP_200_OK)
        else:
            return Response({'message':'la Transaccion no se puedo resgistrar'},status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message':'No existe apertura de caja para este usuario'},status=status.HTTP_400_BAD_REQUEST)

#=============================================================================================================================
#=============================FUNCIONES PARA LA TRANSACCION DE BOLETOS========================================================
def OptenerLiteral(importe):
    literal=num2words(int(importe), lang='es')
    literal=str(literal)
    literal=literal.upper()
    decimal= round(importe % 1, 2)
    decimal=int(decimal)
    decimal= round(importe % 1, 2)
    decimal=str(decimal)
    decimal=decimal[2:4]
    if len(decimal)==1:
        decimal=decimal+'0'
    decimal=decimal.upper()
    literal=literal+' '+decimal+'/100 Bs'
    return literal
def Optener_Categoria(request):
    categorias=CategoriaVehiculo.objects.filter(baja=0)
    return categorias

@api_view(['GET'])
def Obtener_Tarifario(request,id_categoria):
    tarifario= Tarifario.objects.filter(id_categoria=id_categoria,baja=0)
    tarifario_serializer=TarifariosSerializer(tarifario, many=True).data
    return tarifario_serializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Obtener_Datos_Estacion(request):
    usuario_id = request.user.id
    datos_estacion = {}
    
    usuario_regional = AuthUser.objects.get(id=usuario_id)
    datos_estacion['usuario'] = usuario_regional.username
    
    regional = Regionales.objects.filter(id=usuario_regional.id_regional.id).first()
    datos_estacion['nombre_regional'] = regional.nombre_regional

    reten = Retenes.objects.filter(id_regional=usuario_regional.id_regional.id).first()
    datos_estacion['nombre_reten'] = reten.nombre_reten
    
    caja_carril = ObtenerIdCajaCarril(usuario_id)
    if caja_carril:
        datos_estacion['numero_carril'] = caja_carril.numero_carril
    else:
        return Response({'message':"no existe una caja aperturada para este usuario"})
    
    lista_tarifarios = ObtenerTarifarios(usuario_regional.id_regional.id)
    tarifario_serializer = TarifarioTransaccionSerializer(lista_tarifarios, many=True).data
    
    fecha_actual = datetime.now().date()
    datos_estacion['fecha_actual'] = fecha_actual
    

    categorias_vehiculo = CategoriaVehiculo.objects.filter(Q(tarifario__id_regional=8)).distinct()
    categorias_serializer = CategoriaTransaccionSerializer(categorias_vehiculo, many=True).data
    
    return Response({
        'datos_estacion': datos_estacion,
        'lista_tarifario': tarifario_serializer
    })




def generar_reciboid():
    letras_mayusculas = string.ascii_uppercase  # Letras mayúsculas
    numeros = string.digits                      # Dígitos del 0 al 9
    especial = '!@#$%^&*()_-+='                  # Caracteres especiales
    # Genera un ID con 10 caracteres entre letras mayúsculas y números
    id_parte = ''.join(random.choice(letras_mayusculas + numeros) for _ in range(10))
    # Agrega un carácter especial en la penúltima posición
    reciboid = id_parte[:9] + random.choice(especial) + id_parte[9:]
    return reciboid


#=======================================================================================
#=============================REPORTES==================================================

# -------------------REPORTE RECAUDACION NACIONAL/REGIONAL POR FECHA----------------------------

class RecaudacionNacionalRegionalFecha(APIView):
    def get(self, *args, **kwargs):
        lista_regionales = self.cargar_listas()
        regionales_serializer= RegionalesReportesSerializer(lista_regionales,many=True).data
        fecha = datetime.now().date()
        registros_agrupados = []
        regional_seleccionado = 0
        return Response({'lista_cierres': registros_agrupados,
                        'lista_regionales': regionales_serializer,                                                                               
                        'fecha': fecha,
                        'regional_seleccionado': regional_seleccionado})

    def cargar_listas(self):
        lista_regionales = Regionales.objects.filter(baja=0)
        #lista_retenes = Retenes.objects.filter(baja=0)
        return lista_regionales

    def post(self, *args, **kwargs):
        fecha = self.request.data['fecha']
        id_regional = self.request.data['id_regional']
        lista_regionales = self.cargar_listas()
        regionales_serializer= RegionalesReportesSerializer(lista_regionales,many=True).data
                
        registros_agrupados = []
        recaudacion_total='0,00'        
        regional_registro = None
        registros_agrupados = []  # Inicializamos registros_agrupados como None

        if id_regional == 0 :
            regional_seleccionado_serializer=0            
            for regional in lista_regionales:
                # Inicializa registro como una lista con dos elementos
                registro = [regional.nombre_regional, 0]
                registros_caja = CajaCarril.objects.filter(estado='Cerrado', fecha_operaciones=fecha, id_disloque__id_regional=regional.id
                ).aggregate(Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
                registro[1] = registros_caja
                registros_agrupados.append(registro)           
            recaudacion_total = CajaCarril.objects.filter(estado='Cerrado', fecha_operaciones=fecha).aggregate(
                Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
            registros_agrupados.append(['RECAUDACIÓN TOTAL',recaudacion_total])
        elif id_regional != 0:
            regional_seleccionado=Regionales.objects.get(id=id_regional)
            regional_seleccionado_serializer=RegionalesReportesSerializer(regional_seleccionado).data
            lista_retenes=Retenes.objects.filter(baja=0,id_regional=id_regional)
            retenes_serializer=RetenesSerializer(lista_retenes,many=True).data
            for reten in lista_retenes:
                # Inicializa registro como una lista con dos elementos
                registro = [reten.nombre_reten, 0]
                registros_caja = CajaCarril.objects.filter( estado='Cerrado', fecha_operaciones=fecha, id_reten=reten.id_reten
                ).aggregate(Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
                registro[1] = registros_caja
                registros_agrupados.append(registro) 
            recaudacion_total = CajaCarril.objects.filter(estado='Cerrado', fecha_operaciones=fecha,id_disloque__id_regional=id_regional).aggregate(
                Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
            registros_agrupados.append(['RECAUDACIÓN TOTAL',recaudacion_total])
        return Response({'lista_cierres': registros_agrupados,
                        'recaudacion_total':recaudacion_total,
                        'lista_regionales': regionales_serializer,                                                                               
                        'regional_seleccionado': regional_seleccionado_serializer,                                                                              
                        'fecha': fecha
                         })
        

# -------------------RECAUDACION TURNO/REGIONAL POR FECHA----------------------------

class RecaudacionTurnoRegionalFecha(APIView):
    def get(self, *args, **kwargs):
        lista_regionales, lista_retenes = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_retenes_serializer=RetenesReportesSerializer(lista_retenes,many=True).data
        fecha = datetime.now().date()
        id_regional = 0
        id_reten = 0
        turno = 0
        registros_agrupados = []
        return Response({'lista_cierres': registros_agrupados,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_retenes': lista_retenes_serializer,
                        'regional_seleccionado': id_regional,
                        'reten_seleccionado': id_reten,
                        'fecha': fecha,
                        'turno': turno})

    def cargar_listas(self):
        lista_regionales = Regionales.objects.filter(baja=0)
        lista_retenes = Retenes.objects.filter(baja=0)
        return lista_regionales, lista_retenes

    def post(self, *args, **kwargs):
        lista_regionales, lista_retenes = self.cargar_listas()
        fecha = self.request.data['fecha']
        id_regional = self.request.data['id_regional']
        id_reten = self.request.data['id_reten']
        id_turno = self.request.data['id_turno']
        if id_regional!=0:
            regional=Regionales.objects.get(id=id_regional)
            regional_serializer=RegionalesReportesSerializer(regional).data
        else:
            regional_serializer=0
        if id_reten!=0:
            reten=Retenes.objects.get(id_reten=id_reten)
            reten_serializer=RetenesReportesSerializer(reten).data
        else:
            reten_serializer=0

        registros_agrupados = None  # Inicializamos registros_agrupados como None

        if id_regional == 0 and id_reten == 0 and id_turno == 0:

            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha)

        elif id_regional != 0 and id_reten == 0 and id_turno == 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_disloque__id_regional=id_regional)

        elif id_regional == 0 and id_reten != 0 and id_turno == 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_reten=id_reten)
        elif id_regional == 0 and id_reten == 0 and id_turno !=0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_turno=id_turno)
        elif id_regional != 0 and id_reten != 0 and id_turno == 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_disloque__id_regional=id_regional, id_reten=id_reten)
        elif id_regional == 0 and id_reten != 0 and id_turno != 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_reten=id_reten, id_turno=id_turno)
        elif id_regional != 0 and id_reten == 0 and id_turno != 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_disloque__id_regional=id_regional, id_turno=id_turno)
        elif id_regional != 0 and id_reten != 0 and id_turno != 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_disloque__id_regional=id_regional, id_reten=id_reten, id_turno=id_turno)
        registros_agrupados_serializer=CajaCarrilSerializer(registros_agrupados,many=True).data
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_retenes_serializer=RetenesReportesSerializer(lista_retenes,many=True).data
        return Response({'lista_registros': registros_agrupados_serializer,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_retenes': lista_retenes_serializer,
                        'regional_seleccionado': regional_serializer,
                        'reten_seleccionado': reten_serializer,
                        'fecha': fecha,
                        'turno': id_turno})



#-----------------------REPORTE POR USUARIO FECHA REGIONAL--------------------
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class TransaccionesRecaudadorRegionalFecha(APIView):
    def get(self, *args, **kwargs):
        lista_regionales, lista_recaudadores = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        #lista_recaudadores_serializer=UsuariosReportesSerializer(lista_recaudadores,many=True).data
        fecha = datetime.now().date()
        registros_agrupados = []
        regional_seleccionado=0
        recaudador_seleccionado=0
        return Response({'lista_cierres': registros_agrupados,
                        'lista_regionales': lista_regionales_serializer,
                        
                        'fecha':fecha,
                        'regional_seleccionado':regional_seleccionado,
                        'recaudador_seleccionado':recaudador_seleccionado})
    
    def cargar_listas(self):        
        lista_regionales = Regionales.objects.filter(baja=0)
        lista_recaudadores = AuthUser.objects.filter(is_active=True)
        return lista_regionales, lista_recaudadores

    def post(self, *args, **kwargs):
        lista_regionales, lista_recaudadores = self.cargar_listas()
        fecha = self.request.data['fecha']
        id_regional = self.request.data['id_regional']
        id_recaudador = self.request.data['id_recaudador']
        if id_recaudador!=0:
            recaudador=AuthUser.objects.get(id=id_recaudador)
            recaudador_serializer=UsuariosReportesSerializer(recaudador).data
        else:
            recaudador_serializer=0
        if id_regional!=0:
            regional=Regionales.objects.get(id=id_regional)
            regional_serializer=RegionalesReportesSerializer(regional).data
        else:
            regional_serializer=0
        registros_agrupados = None  # Inicializamos registros_agrupados como None
        if id_regional == 0 and id_recaudador == 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha)

        elif id_regional != 0 and id_recaudador == 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_disloque__id_regional=id_regional)

        elif id_regional == 0 and id_recaudador != 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_recaudador=id_recaudador)
        elif id_regional != 0 and id_recaudador != 0:
            registros_agrupados = CajaCarril.objects.filter(
                estado='Cerrado', fecha_operaciones=fecha, id_disloque__id_regional=id_regional, id_recaudador=id_recaudador)
        registros_agrupados_serializer=CajaCarrilSerializer(registros_agrupados,many=True).data
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_recaudadores_serializer=UsuariosReportesSerializer(lista_recaudadores,many=True).data
        return Response({'lista_cierres': registros_agrupados_serializer,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_recaudadores': lista_recaudadores_serializer,
                        'regional_seleccionado':regional_serializer,
                        'recaudador_seleccionado':recaudador_serializer,
                        'fecha': fecha})
    
def ObtenerListaAnio(cantidadAnios):
    fecha_actual = datetime.now().date()
    lista_anios = []
    for i in range(cantidadAnios):
        anio = fecha_actual.year-i
        lista_anios.append(anio)
    return lista_anios

def obtener_lista_de_dias_numeros(year, month):
    # Calcula el último día del mes
    siguiente_mes = date(year, month, 1).replace(day=28) + timedelta(days=4)
    ultimo_dia = siguiente_mes - timedelta(days=siguiente_mes.day)
    # Crea una lista de números del 1 al último día del mes
    lista_dias_numeros = list(range(1, ultimo_dia.day + 1))

    return lista_dias_numeros
   
#------------------------------REPORTE MENSUAL NACIONAL -----------------------------------------------

class ReporteMensualNacional(APIView):
    def get(self, *args, **kwargs):
        lista_regionales, lista_meses = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_meses_serializer=MesesReportesSerializer(lista_meses,many=True).data
        lista_cierres = []
        lista_anios = ObtenerListaAnio(5)
        mes_seleccionado = 1
        regional_seleccionado = 1
        return Response({'lista_cierres': lista_cierres,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_anios': lista_anios,
                        'lista_meses': lista_meses_serializer,
                        'mes_seleccionado': mes_seleccionado,
                        'regional_seleccionado': regional_seleccionado})

    def cargar_listas(self):
        lista_regionales = Regionales.objects.filter(baja=0)
        lista_meses = Meses.objects.all()
        return lista_regionales, lista_meses

    def post(self, *args, **kwargs):        
        id_mes = self.request.data['id_mes']
        anio = self.request.data['anio']
        id_regional = self.request.data['id_regional']
        fecha=datetime.now()
        
        mes = Meses.objects.filter(id=id_mes).first()
        #print("YYYYYYYYYYYYYYYYYYYYYYYYYYY",mes)
        mes_serializer=MesesReportesSerializer(mes).data
        regional = Regionales.objects.get(id=id_regional)
        regional_seleccionado=RegionalesReportesSerializer(regional).data
        #print(type(id_mes), type(anio), type(id_regional))
        lista_recaudacion_mensual = []
        lista_dias = obtener_lista_de_dias_numeros(int(anio), int(id_mes))
        recaudacion_total_mes = CajaCarril.objects.filter(estado='Cerrado', anio=anio, mes=id_mes, id_disloque__id_regional=id_regional).aggregate(
            Sum('total_cierre_sistema'))['total_cierre_sistema__sum']

        for dia in lista_dias:
            recaudacion_diaria = CajaCarril.objects.filter(estado='Cerrado', anio=anio, mes=id_mes, dia=dia, id_disloque__id_regional=id_regional).aggregate(
                Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
            lista_recaudacion_mensual.append(
                [str(dia)+"/"+str(id_mes)+"/"+str(anio), recaudacion_diaria])
        lista_recaudacion_mensual.append(
            ['RECAUDACIÓN TOTAL', recaudacion_total_mes])
        
        lista_regionales, lista_meses = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_meses_serializer=MesesReportesSerializer(lista_meses,many=True).data
        lista_anios = ObtenerListaAnio(5)

        return Response({'recaudacion_mensual': lista_recaudacion_mensual,
                        'monto_total_mensual': recaudacion_total_mes,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_anios': lista_anios,
                        'lista_meses': lista_meses_serializer,
                        'mes_seleccionado': mes_serializer,
                        'anio': anio,
                        'fecha':fecha,
                        'regional_seleccionado': regional_seleccionado})

#-------------------------------------------REPORTE TRNSACCIONES POR REGIONAL Y ANUAL------------------------------

class ReportePorRegionalAnual(APIView):
    def get(self, *args, **kwargs):
        lista_regionales = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_cierres = []
        lista_anios = ObtenerListaAnio(5)
        return Response({'lista_cierres': lista_cierres,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_anios': lista_anios})

    def cargar_listas(self):
        lista_regionales = Regionales.objects.filter(baja=0)
        return lista_regionales

    def post(self, *args, **kwargs):        
        anio = self.request.data['anio']
        id_regional = self.request.data['id_regional']
        regional_seleccionado = Regionales.objects.get(id=id_regional)
        regional_seleccionado_serializer=RegionalesReportesSerializer(regional_seleccionado).data
        meses = Meses.objects.all()
        lista_recaudacion_anual = []
        fecha=datetime.now()
        for mes in meses:
            recaudacion_mensual = CajaCarril.objects.filter(estado='Cerrado', anio=anio, mes=mes.id, id_disloque__id_regional=id_regional).aggregate(
                Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
            lista_recaudacion_anual.append([mes.mes, recaudacion_mensual])

        monto_total_anual = CajaCarril.objects.filter(estado='Cerrado', anio=anio, id_disloque__id_regional=id_regional).aggregate(
            Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
        lista_recaudacion_anual.append(
            ['TOTAL RECAUDACION', monto_total_anual])
        lista_regionales = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_anios = ObtenerListaAnio(5)
        return Response({'lista_recaudacion_anual': lista_recaudacion_anual,
                        'lista_regionales': lista_regionales_serializer,
                        'monto_total_anual': monto_total_anual,
                        'lista_anios': lista_anios,
                        'anio_seleccionado': anio,
                        'fecha':fecha,
                        'regional_seleccionado': regional_seleccionado_serializer})


#-------------------------------------------REPORTE TRNSACCIONES POR REGIONAL,RETEN Y ANUAL------------------------------
class ReportePorRegionalRetenAnual(APIView):
    def get(self, *args, **kwargs):
        lista_regionales = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_cierres = []
        lista_anios = ObtenerListaAnio(5)
        return Response({'lista_cierres': lista_cierres,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_anios': lista_anios
                                                    })

    def cargar_listas(self):
        lista_regionales = Regionales.objects.filter(baja=0)
        return lista_regionales

    def post(self, *args, **kwargs):
        anio = self.request.data['anio']
        id_regional = self.request.data['id_regional']

        regional_seleccionado = Regionales.objects.filter(id=id_regional).first()
        regional_seleccionado_serializer=RegionalesReportesSerializer(regional_seleccionado).data
        lista_retenes = Retenes.objects.filter(baja=0, id_regional=id_regional)
        lista_meses = Meses.objects.all()
        recaudacion_mensual_reten = ['TOTAL MENSUAL']
        recaudacion_anual_reten = []

        for reten in lista_retenes:
            recaudacion_mensual = [reten.nombre_reten]
            for mes in lista_meses:
                recaudacion = ObtenerRecaudacionMensualReten(
                    anio, mes.id, reten.id_reten)
                if recaudacion:
                    recaudacion_mensual.append(recaudacion)
                else:
                    recaudacion_mensual.append('0,00')
            recaudacion_mensual.append(ObtenerRecaudacionAnualReten(anio, reten.id_reten))
            recaudacion_anual_reten.append(recaudacion_mensual)
        for mes in lista_meses:
            recaudacion_mensual_reten.append(ObtenerRecaudacionMensual(anio, mes.id, id_regional))
        recaudacion_mensual_reten.append(ObtenerRecaudacionAnualRegional(anio, id_regional))
        recaudacion_anual_reten.append(recaudacion_mensual_reten)

        recaudacion_anual = ObtenerRecaudacionAnualRegional(anio, id_regional)
        lista_regionales = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_anios = ObtenerListaAnio(5)
        return Response({'recaudacion_anual': recaudacion_anual_reten,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_anios': lista_anios,
                        'recaudacion_nacional_anual': recaudacion_anual,
                        'anio': anio,
                        'regional_seleccionado': regional_seleccionado_serializer})
    
def ObtenerRecaudacionAnualReten(anio, id_reten):
    recaudacion_anual_reten = CajaCarril.objects.filter(estado='Cerrado', anio=anio, id_reten=id_reten).aggregate(
        Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
    if not recaudacion_anual_reten:
        recaudacion_anual_reten = '0,00'
        return recaudacion_anual_reten
    return recaudacion_anual_reten


def ObtenerRecaudacionMensualReten(anio, id_mes, id_reten):
    recaudacion_mensual_reten = CajaCarril.objects.filter(estado='Cerrado', anio=anio, mes=id_mes, id_reten=id_reten).aggregate(
        Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
    return recaudacion_mensual_reten


def ObtenerRecaudacionMensual(anio, id_mes, id_regional):
    recaudacion_mensual = CajaCarril.objects.filter(estado='Cerrado', anio=anio, mes=id_mes, id_disloque__id_regional=id_regional).aggregate(
        Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
    if not recaudacion_mensual:
        recaudacion_mensual = '0,00'
        return recaudacion_mensual
    return recaudacion_mensual

def ObtenerRecaudacionAnualRegional(anio, id_regional):
    recaudacion_anual_regional = CajaCarril.objects.filter(estado='Cerrado', anio=anio, id_disloque__id_regional=id_regional).aggregate(
        Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
    if not recaudacion_anual_regional:
        recaudacion_anual_regional = '0,00'
        return recaudacion_anual_regional
    return recaudacion_anual_regional

# ------------------------RECAUDACION NACIONAL POR AÑO -----------------------------------------

class ReporteNacionalAnual(APIView):
    def get(self, *args, **kwargs):
        fecha = datetime.now().date()
        anio = fecha.year
        registros_agrupados = []
        lista_anios = ObtenerListaAnio(5)
        # print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",lista_anios)
        return Response({'lista_cierres': registros_agrupados,
                        'lista_anios': lista_anios,
                        'anio': anio})

    def post(self, *args, **kwargs):        
        anio = self.request.data['anio']
        recaudacion_anual = []
        lista_regionales = Regionales.objects.filter(baja=0)
        lista_meses = Meses.objects.all()
        totales_nacional_mensual = ['RECAUDACIÓN TOTAL NACIONAL']
        for regional in lista_regionales:
            recaudacion_mensual = [regional.nombre_regional]
            for mes in lista_meses:
                recaudacion = ObtenerRecaudacionMensualRegional(
                    anio, regional.id, mes.id)
                if recaudacion:
                    recaudacion_mensual.append(recaudacion)
                else:
                    recaudacion_mensual.append('0,00')

            recaudacion_mensual.append(
                ObtenerRecaudacionAnualRegional(anio, regional.id))
            recaudacion_anual.append(recaudacion_mensual)
        for mes in lista_meses:
            recaudacion_mesual_total = ObtenerRecaudacionNacionalMensual(
                anio, mes.id)
            totales_nacional_mensual.append(recaudacion_mesual_total)
        recaudacion_nacional_anual = ObtenerRecaudacionNacionalAnual(anio)
        totales_nacional_mensual.append(recaudacion_nacional_anual)
        recaudacion_anual.append(totales_nacional_mensual)
        lista_anios = ObtenerListaAnio(5)
        return Response({'recaudacion_anual': recaudacion_anual,
                        'lista_anios': lista_anios,
                        'recaudacion_nacional_anual': recaudacion_nacional_anual,
                        'anio': anio})

def ObtenerRecaudacionMensualRegional(anio, id_regional, id_mes):
    recaudacion_regional = CajaCarril.objects.filter(estado='Cerrado', anio=anio, id_disloque__id_regional=id_regional, mes=id_mes).aggregate(
        Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
    return recaudacion_regional


def ObtenerRecaudacionNacionalAnual(anio):
    recaudacion_nacional_anual = CajaCarril.objects.filter(estado='Cerrado', anio=anio).aggregate(
        Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
    return recaudacion_nacional_anual


def ObtenerRecaudacionNacionalMensual(anio, id_mes):
    recaudacion_nacional_mensual = CajaCarril.objects.filter(estado='Cerrado', anio=anio, mes=id_mes).aggregate(
        Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
    if not recaudacion_nacional_mensual:
        recaudacion_nacional_mensual = '0,00'
        return recaudacion_nacional_mensual
    return recaudacion_nacional_mensual

# --------------------------------RECAUDACION EN RANGO----------------------------------------

class ReporteRangoRegionalReten(APIView):
    def get(self, *args, **kwargs):
        lista_regionales, lista_retenes = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_retenes_serializer=RetenesReportesSerializer(lista_retenes,many=True).data
        fecha = datetime.now().date()
    
        #registros_agrupados = CajaCarril.objects.filter(estado='Cerrado', fecha_operaciones=fecha)
        registros_agrupados=[]
        return Response({'lista_cierres': registros_agrupados,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_retenes': lista_retenes_serializer,
                        'fecha_inicio': fecha,
                        'fecha_fin': fecha})

    def cargar_listas(self):
        lista_regionales = Regionales.objects.filter(baja=0)
        lista_retenes = Retenes.objects.filter(baja=0)
        return lista_regionales, lista_retenes

    def post(self, *args, **kwargs):        
        fecha_inicio = self.request.data['fecha_inicio']
        if not fecha_inicio:
            fecha_inicio=datetime.now().date()
        fecha_fin = self.request.data['fecha_fin']
        if not fecha_fin:
            fecha_fin=datetime.now().date()
        id_regional = self.request.data['id_regional']
        id_reten = self.request.data['id_reten']
        registros_agrupados = []  # Inicializamos registros_agrupados como None
        lista_regionales, lista_retenes = self.cargar_listas()
        lista_regionales_serializer=RegionalesReportesSerializer(lista_regionales,many=True).data
        lista_retenes_serializer=RetenesReportesSerializer(lista_retenes,many=True).data
        if id_regional:
            regional_seleccionado=RegionalesReportesSerializer(Regionales.objects.get(id=id_regional)).data
        else:
            regional_seleccionado=None
        if id_reten:
            reten_seleccionado=RetenesReportesSerializer(Retenes.objects.get(id_reten=id_reten)).data
        else:
            reten_seleccionado=None

        if id_regional == 0:
            for regional in lista_regionales:
                # Inicializa registro como una lista con dos elementos
                registro = [regional.nombre_regional, 0]
                registros_caja = CajaCarril.objects.filter(
                    estado='Cerrado', fecha_operaciones__gte=fecha_inicio, fecha_operaciones__lte=fecha_fin, id_disloque__id_regional=regional.id
                ).aggregate(Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
                registro[1] = registros_caja
                registros_agrupados.append(registro)
            recaudacion_total = CajaCarril.objects.filter(estado='Cerrado',fecha_operaciones__gte=fecha_inicio, fecha_operaciones__lte=fecha_fin).aggregate(
                Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
            registros_agrupados.append(
                ['RECAUDACIÓN TOTAL', recaudacion_total])
        elif id_regional != 0 and id_reten==0:
            lista_retenes_regional=Retenes.objects.filter(baja=0,id_regional=id_regional)
            for reten in lista_retenes_regional:
                # Inicializa registro como una lista con dos elementos
                registro = [reten.nombre_reten, 0]
                registros_caja = CajaCarril.objects.filter(
                    estado='Cerrado', fecha_operaciones__gte=fecha_inicio, fecha_operaciones__lte=fecha_fin, id_reten=reten.id_reten,id_disloque__id_regional=id_regional
                ).aggregate(Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
                registro[1] = registros_caja
                registros_agrupados.append(registro)
            recaudacion_total = CajaCarril.objects.filter(estado='Cerrado', fecha_operaciones__gte=fecha_inicio, fecha_operaciones__lte=fecha_fin, id_disloque__id_regional=id_regional).aggregate(
                Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
            registros_agrupados.append(
                ['RECAUDACIÓN TOTAL', recaudacion_total])
        elif id_regional!=0 and id_reten!=0:
              registro = [Retenes.objects.get(id_reten=id_reten).nombre_reten, 0]
              registros_caja = CajaCarril.objects.filter(estado='Cerrado',
                                                         fecha_operaciones__gte=fecha_inicio,
                                                         fecha_operaciones__lte=fecha_fin,
                                                         id_reten=id_reten,
                                                         id_disloque__id_regional=id_regional
                ).aggregate(Sum('total_cierre_sistema'))['total_cierre_sistema__sum']
              registro[1]=registros_caja
              registros_agrupados.append(registro)
        return Response({'resultados': registros_agrupados,
                        'lista_regionales': lista_regionales_serializer,
                        'lista_retenes': lista_retenes_serializer,
                        'regional_seleccionado': regional_seleccionado,
                        'reten_seleccionado': reten_seleccionado,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin})

class MonitorApi(APIView):
    def get(self, *args, **kwargs):
        #ultimas_tres_transacciones = Transaccion.objects.order_by('-modified')[:3]
        ultimas_tres_transacciones = Transaccion.objects.last()
        ultimas_tres_transacciones_serializer=TransaccionSerializer(ultimas_tres_transacciones).data
        monitor=Monitor.objects.all()
        monitor_serializer=MonitorSerializer(monitor,many=True).data
        monitor_total=MonitorTotal.objects.get(id=1)
        return Response({'transacciones':ultimas_tres_transacciones_serializer,
                         'monitor':monitor_serializer,
                         'monitor_total':monitor_total.monto})
