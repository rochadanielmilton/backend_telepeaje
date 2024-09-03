from django.contrib.auth import authenticate
from rest_framework import viewsets, serializers, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from parametros.models import *
from parametros.serializers import RegionalesSerializer
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime, timedelta, time
from django.views.generic import View
from django.contrib.auth.models import User, Permission
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Prefetch, Sum
from django.http import Http404
from django.db.models import Count


class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(username=username, password=password)

        if user:
            login_serializer = self.serializer_class(data=request.data)
            if login_serializer.is_valid():
                user_serializer = CustomUserSerializer(user)

                # #-------------Accede a los grupos a los que pertenece el usuario--------
                grupos_del_usuario = user.groups.all()
                for grupo in grupos_del_usuario:
                    menus_relacionados = Menu.objects.filter(
                        menugroup__id_group=grupo.id, fid_menu__isnull=True)
                    # menu_serialiazer = MenuSerializer(menus_relacionados, many=True).data

                for grupo2 in grupos_del_usuario:
                    sub_menus_relacionados = Menu.objects.filter(
                        menugroup__id_group=grupo2.id, fid_menu__isnull=False)

                # -------------Serializa la información de los grupos----------
                grupos_serializer = AuthGroupSerializer(
                    grupos_del_usuario, many=True).data
                # print("o0o0o0o0o0o0o", menu_serialiazer)

                # ----Obtiene todos los permisos asociados a los grupos del usuario--------
                permisos_del_usuario = Permission.objects.filter(
                    group__in=grupos_del_usuario)
                # ---------------Serializa la información de los permisos------------
                permisos_serializer = PermissionSerializer(
                    permisos_del_usuario, many=True).data
                menu_json = []

                # Función para generar la estructura de menú recursivamente
                def generate_menu_structure(menu):
                    menu_data = {
                        'id_menu': menu.id_menu,
                        'nombre': menu.nombre,
                        'ruta': menu.ruta,
                        'icono': menu.icono,
                        'label': menu.label,
                        'fid_menu': menu.fid_menu,
                        'es_menu': menu.es_menu,
                        'submenu': []
                    }
                    # Obtener los submenús recursivamente
                    submenus = Menu.objects.filter(
                        fid_menu=menu.id_menu, fid_menu__isnull=False, id_menu__in=sub_menus_relacionados)
                    for submenu in submenus:
                        submenu_data = generate_menu_structure(submenu)
                        menu_data['submenu'].append(submenu_data)

                    return menu_data

                # Generar el JSON para cada menú principal
                for main_menu in menus_relacionados:
                    main_menu_data = generate_menu_structure(main_menu)
                    menu_json.append(main_menu_data)

                # return menu_json

                return Response({
                    'token': login_serializer.validated_data.get('access'),
                    'refresh-token': login_serializer.validated_data.get('refresh'),
                    'user': user_serializer.data,
                    'roles': grupos_serializer,
                    'message': 'Inicio de Sesión exitoso',
                    'menu': menu_json,
                    'permisos': permisos_serializer
                }, status=status.HTTP_200_OK)

            return Response({'error': 'Contraseña o nombre incorrecto'}, status=status.HTTP_200_OK)

        return Response({'error': 'Contraseña o nombre incorrecto'}, status=status.HTTP_200_OK)


class Logout(GenericAPIView):
    serializer_class = EmptySerializer

    def post(self, request, *args, **kwargs):
        id_usuario = request.data.get('id')
        user = User.objects.filter(id=id_usuario).first()

        if user:
            refresh_token = RefreshToken.for_user(user)
            return Response({'message': 'Sesión cerrada correctamente'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No existe este usuario'}, status=status.HTTP_400_BAD_REQUEST)
        
# -----------------OPCION LOGIN CON GRUPOS Y PERMISOS-----------------------------------
# class Login(TokenObtainPairView):
    # serializer_class = CustomTokenObtainPairSerializer

    # def post(self, request, *args, **kwargs):
        # username = request.data.get('username', '')
        # password = request.data.get('password', '')
        # user = authenticate(username=username, password=password)

        # if user:
            # login_serializer = self.serializer_class(data=request.data)
            # if login_serializer.is_valid():
            # user_serializer = CustomUserSerializer(user)

            # -------------Accede a los grupos a los que pertenece el usuario--------
            # grupos_del_usuario = user.groups.all()

            # -------------Serializa la información de los grupos----------
            # grupos_serializer = AuthGroupSerializer(grupos_del_usuario, many=True).data

            # ----Obtiene todos los permisos asociados a los grupos del usuario--------
            # permisos_del_usuario = Permission.objects.filter(group__in=grupos_del_usuario)

            # ---------------Serializa la información de los permisos------------
            # permisos_serializer = PermissionSerializer(permisos_del_usuario, many=True).data

            # return Response({
            # 'token': login_serializer.validated_data.get('access'),
            # 'refresh-token': login_serializer.validated_data.get('refresh'),
            # 'user': user_serializer.data,
            # 'roles': grupos_serializer,
            # 'menu': permisos_serializer,
            # 'message': 'Inicio de Sesión exitoso'
            # }, status=status.HTTP_200_OK)

            # return Response({'error': 'Contraseña o nombre incorrecto'}, status=status.HTTP_200_OK)

        # return Response({'error': 'Contraseña o nombre incorrecto'}, status=status.HTTP_200_OK)
# -------------------------------------------------------------------------------------------------


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all().order_by('-id_menu')
    serializer_class = MenuSerializer


class MenuGroupViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = MenuGroup.objects.all()
    serializer_class = MenuGroupSerializer


class AuthUserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AuthUser.objects.filter(is_active=True).order_by('-id')

    def get_serializer_class(self):
        return AuthUserSerializer


class AuthGroupViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AuthGroup.objects.all().order_by('-id')
    serializer_class = AuthGroupSerializer


class BajaGrupoView(generics.UpdateAPIView):
    queryset = AuthGroup.objects.filter(baja=False)
    serializer_class = AuthGroupSerializer

    def update(self, *args, **kwargs):
        instance = self.get_object()
        instance.baja = True
        instance.save()
        return Response({'message': f'La entidad {instance.name} fue dada de baja.'})


class AuthUserGroupsViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AuthUserGroups.objects.all()
    serializer_class = AuthUserGroupsSerializer


class AuthPermissionViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AuthPermission.objects.all()
    serializer_class = AuthPermissionSerializer


@api_view(['GET'])
def ContentType(request):
    lista_content_type = DjangoContentType.objects.all()
    data_content_type = ContentTypeSerializer(
        lista_content_type, many=True).data
    return Response(data_content_type)


@api_view(['GET'])
def AsignarRol(request, id_usuario, id_grupo):
    nueva_asignacion = AuthUserGroups.objects.create(
        user_id=id_usuario, group_id=id_grupo)
    if nueva_asignacion:
        return Response({'message': 'grupo asignado correctamente'}, status=201)
    else:
        return Response({'message': 'no se puedo asignar el grupo'})
    
@api_view(['POST'])
def AsignarMenu(request):
    try:
        data = request.data
        id_group = data.get('id_group')
        id_menu = data.get('id_menu')

        # Validación de datos
        if id_group is None or id_menu is None:
            raise ValueError('Los campos id_group e id_menu son obligatorios.')
        id_group=AuthGroup.objects.get(id=id_group)
        id_menu=Menu.objects.get(id=id_menu)
        nueva_asignacion = MenuGroup.objects.create(id_group=id_group, id_menu=id_menu)

        if nueva_asignacion:
            return Response({'message': 'Menú asignado correctamente'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'No se pudo asignar el menú'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# =============================API GESTION DE DISLOQUE=============================


class ListaDisloqueAPI(APIView):
    def get(self, request):
        fecha_año_pasado = datetime.today() - timedelta(days=365)
        disloques = Disloque.objects.filter(
            fecha_inicio__gte=fecha_año_pasado).order_by('-id')
        serializer = DisloqueSerializer(disloques, many=True)
        return Response(serializer.data)
    # ---------------listar usuarios que no pertenecen a un disloque dado una regional y una fecha inicio-----

class UsuariosLibresAPI(APIView):
    def post(self, request):
        serializer = UsuariosLibresSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            usuarios_libres = RecaudadoresNoDisloque(data['id_regional'], data['fecha_ini'])
            #print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",usuarios_libres)
            usuarios_libres_serializer = AuthUserSerializer(usuarios_libres, many=True).data
            return Response(usuarios_libres_serializer)
        else:
            return Response(serializer.errors, status=400)

    # ------------funcion que permite buscar recaudadores que no esten asigandos en un disloque------------------


def RecaudadoresNoDisloque(id_regional, fecha_ini):

    lista_disloque = DisloqueDetalle.objects.filter(id_regional=id_regional, fecha_inicio=fecha_ini)
    # optiene los ids de todos los los usuarios de la lista lista_disloque
    usuarios_en_disloque = lista_disloque.values_list('id_recaudador', flat=True)
    usuarios_libres = AuthUser.objects.filter(id_regional=id_regional, is_active='t').exclude(id__in=usuarios_en_disloque)
    # print("#######################",usuarios_no_en_disloque)
    return usuarios_libres

    # ------------permite obtener los retenes que no estan asigandos en un disloque------------------------------


class RetenesNoDisloqueAPI(APIView):
    def post(self, request):
        serializer = RetenesNoDisloqueSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
        lista_retenes_asignados = DisloqueDetalle.objects.filter(id_regional=data['id_regional'], fecha_inicio=data['fecha_ini'])
        lista_retenes_asignados = lista_retenes_asignados.values_list('id_reten', flat=True)
        lista_retenes_asignados_sin_duplicados = list(set(lista_retenes_asignados))
        retenes_libres = Retenes.objects.filter(id_regional=data['id_regional'], baja=0).exclude(id_reten__in=lista_retenes_asignados_sin_duplicados)

    # Serializar los datos antes de enviar la respuesta
        serializer = RetenesSerializer(retenes_libres, many=True).data

        return Response(serializer, status=status.HTTP_200_OK)

    # --------busca un disloques que se ha iniciado en un rango de fechas y si no esta crea uno---------------


def BuscarNumeroDisloque(self, id_regional, fecha_ini, fecha_fin):
    id_disloque = Disloque.objects.filter(
        id_regional=id_regional, fecha_inicio=fecha_ini, fecha_fin=fecha_fin).first()
    if id_disloque:
        return id_disloque.id
    else:
        responsable_disloque = self.request.user.first_name+' '+self.request.user.last_name
        nuevo_disloque = Disloque.objects.create(id_regional=Regionales.objects.get(id=id_regional), fecha_inicio=fecha_ini,
                                                 fecha_fin=fecha_fin, fecha_creacion=datetime.now(), estado='Pendiente', responsable_disloque=responsable_disloque, baja=0)

        return nuevo_disloque.id

    # -----------Registro de un nuevo disloque y registro de detalle disloque----------------------------


class RegistroDisloqueViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = DisloqueDetalleSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            data = serializer.validated_data
            reten_seleccionado = Retenes.objects.get(id_reten=data['reten_id'])
            regional_seleccionado = reten_seleccionado.id_regional
            recaudadores_seleccionados = data['recaudadores_seleccionados']
            fecha_actual = datetime.now()
            responsable_disloque = self.request.user.first_name+' '+self.request.user.last_name
            responsable_reten = 'No'
            estado = 'Pendiente'
            id_disloque = BuscarNumeroDisloque(self, data['regional_id'], data['fecha_ini'], data['fecha_fin'])
            # print("DDDDDDDDDDDDDDDDDDDDDDD",id_disloque)
            for id_recaudador in recaudadores_seleccionados:
                # print("DDDDDDDDDDDDDDDDDDDDDDD",id_recaudador)
                id_recaudador = AuthUser.objects.get(id=id_recaudador)
                disloque_detalle = DisloqueDetalle.objects.create(
                    numero_disloque=id_disloque,
                    id_regional=regional_seleccionado,
                    id_reten=reten_seleccionado,
                    id_recaudador=id_recaudador,
                    fecha_inicio=data['fecha_ini'],
                    fecha_fin=data['fecha_fin'],
                    fecha_creacion=fecha_actual,
                    responsable_disloque=responsable_disloque,
                    responsable_reten=responsable_reten,
                    estado=estado
                )

            if disloque_detalle:
                return Response({'message': 'Disloque creado correctamente'}, status=201)
            else:
                return Response({'no se pudo crear el disloque'})
        else:
            return Response(serializer.errors, status=400)


@api_view(['PUT'])
def AprobarDisloqueAPI(request, id_disloque):
    disloque_aprobado = Disloque.objects.filter(id=id_disloque).update(estado='Aprobado')
    if disloque_aprobado:
        return Response({'message': 'disloque aprobado correctamente'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'el disloque no se puede aprobar'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
def BajaDisloqueAPI(request, id_disloque):
    disloque_aprobado = Disloque.objects.filter(id=id_disloque).update(baja=1)
    if disloque_aprobado:
        return Response({'message': 'El disloque fue dado de baja correctamente'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'El disloque no pudo darse de baja'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
def AsignarResponsableAPI(request, id_detalle_disloque):
    disloque_detalle = DisloqueDetalle.objects.filter(id=id_detalle_disloque).update(responsable_reten='Si')
    if disloque_detalle:
        return Response({'message': 'El usuario fue asigando como responsable'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'El usuario no pudo ser asiganado'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
def QuitarResponsableAPI(request, id_detalle_disloque):
    disloque_detalle = DisloqueDetalle.objects.filter(id=id_detalle_disloque).update(responsable_reten='No')
    if disloque_detalle:
        return Response({'message': 'El usuario ya no es Responsable de reten'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Error al intentar eliminar Responsable'}, status=status.HTTP_204_NO_CONTENT)

    # ---------------------------asigna un recaudador a un disloque---------------------------


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def AgregarUnRecaudadorAPI(request):
    authentication_classes = [JWTAuthentication]
    datos=request.data
    id_reten=datos['id_reten']
    id_disloque=datos['id_disloque']
    id_recaudador=datos['id_recaudador']
    try:
        disloque = Disloque.objects.get(id=id_disloque)
    except Disloque.DoesNotExist:
        return Response({'message': 'El disloque no existe'}, status=status.HTTP_404_NOT_FOUND)
    try:
        recaudador = AuthUser.objects.get(id=id_recaudador)
    except AuthUser.DoesNotExist:
        return Response({'message': 'El disloque no existe'}, status=status.HTTP_404_NOT_FOUND)
    try:
        reten = Retenes.objects.get(id_reten=id_reten)
    except Retenes.DoesNotExist:
        return Response({'message': 'El disloque no existe'}, status=status.HTTP_404_NOT_FOUND)

    fecha_actual = datetime.now()
    # responsable_disloque = request.user.first_name + ' ' + request.user.last_name
    responsable_disloque = ''
    responsable_reten = 'No'

    nuevo_registro = DisloqueDetalle.objects.create(
        numero_disloque=disloque.id,
        id_regional=disloque.id_regional,
        id_reten=reten,
        id_recaudador=recaudador,
        fecha_inicio=disloque.fecha_inicio,
        fecha_fin=disloque.fecha_fin,
        fecha_creacion=fecha_actual,
        responsable_disloque=responsable_disloque,
        responsable_reten=responsable_reten,
        estado=disloque.estado
    )

    if nuevo_registro:
        return Response({'message': 'El recaudador fue asignado correctamente'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'No se asignó un nuevo recaudador'}, status=status.HTTP_204_NO_CONTENT)


class VerListaDetalleDisloque(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        lista_retenes_con_recaudadores = []

        try:
            disloque = Disloque.objects.get(id=pk)            
            lista_retenes = Retenes.objects.filter(id_regional=disloque.id_regional, baja=0)
            lista_detalle_disloques = DisloqueDetalle.objects.filter(numero_disloque=pk)
            for reten in lista_retenes:
                reten_registros = {'nombre_reten': reten.nombre_reten,'id_reten':reten.id_reten,'registros': []}

                for detalle in lista_detalle_disloques:                    
                    if reten.id_reten == detalle.id_reten.id_reten:                      
                        reten_registros['registros'].append({
                            "id":       detalle.id,
                            "recaudador": detalle.id_recaudador.username,
                            "responsable":    detalle.responsable_reten
                            })

                lista_retenes_con_recaudadores.append(reten_registros)

            return Response(lista_retenes_con_recaudadores)  
        except Disloque.DoesNotExist:
            raise Http404('Registro de disloque no encontrado')
        
    # ---------------------------elimina un recaudador que se asigno a un disloque---------------------------

@api_view(['DELETE'])
def QuitarUnRecaudadorAPI(request,id_detalle_disloque):
    disloque_detalle = DisloqueDetalle.objects.filter(id=id_detalle_disloque)
    if disloque_detalle:
        disloque_detalle.delete()
        return Response({'message': 'Se quito el recaudador correctamente'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Error al intentar eliminar un recaudador'}, status=status.HTTP_204_NO_CONTENT)
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
            ciclo.save()  # Asegúrate de guardar los cambios en la base de datos
        return True
    return False
# ============================================================================================================
# =======================================APERTURA DE CAJA CARRIL==============================================


class AperturaCajaCarril(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # -----------------Listar cajas aperturadas-----------------------
    def get(self, *args, **kwargs):
        id_usuario=self.request.user.id
        usuario_autenticado=AuthUser.objects.get(id=id_usuario)
        if usuario_autenticado.id_grupo==7:
            try:               
                
                cajas_usuario=CajaCarril.objects.filter(id_recaudador=id_usuario,fecha_operaciones=datetime.now().date())
                print("RRRRRRRRRRRRRRRRRRRR",cajas_usuario)        
                cajas_usuario_serializer=CajaCarrilSerializer(cajas_usuario,many=True).data
                return Response(cajas_usuario_serializer)
            except:
                return Response({'message':'No existen cajas por cerrar para este usuario!!'})
        else:
            #lista_cajas_aperturadas = CajaCarril.objects.filter(fecha_operaciones=datetime.now().date()).order_by('-id')
            lista_cajas_aperturadas = CajaCarril.objects.all().order_by('-id')
            serializer = CajaCarrilSerializer(lista_cajas_aperturadas, many=True)
            return Response(serializer.data)

    # ---------------cerrar caja--------------------------------------
    
    def put(self, *args, **kwargs):
        request = self.request.data.get('id')
        try:
            caja = CajaCarril.objects.get(id=request)
        except CajaCarril.DoesNotExist:
            return Response({'message': 'La caja no Existe'}, status=status.HTTP_404_NOT_FOUND)

        caja.estado = 'Cerrado'
        caja.save()
        return Response({'message': 'la caja se cerro correctamente'}, status=status.HTTP_200_OK)

    # ---------------creacion de una caja--------------------------------
    def post(self, request):
        request = self.request.data
        id_recaudador = request['id_recaudador']
        id_disloque = request['id_disloque']
        #id_regional = request['id_regional']
        id_reten = request['id_reten']
        fecha_operaciones_str = request['fecha_operaciones']
        fecha_operaciones = datetime.strptime(fecha_operaciones_str, '%Y-%m-%d')

        # Obtener el año, mes, día y hora de la fecha
        anio = fecha_operaciones.year
        mes = fecha_operaciones.month
        dia = fecha_operaciones.day
        id_turno = request['turno']
        carril =request['numero_carril']
        fecha_apertura = datetime.now()
        encargado_apertura = self.request.user.first_name+' '+self.request.user.last_name
        estado = 'Abierto'
        total_apertura = request['total_apertura']
        try:
            disloque = Disloque.objects.get(id=id_disloque)
            recaudador = AuthUser.objects.get(id=id_recaudador)
            reten = Retenes.objects.get(id_reten=id_reten)
            consolidado='No'
            
            nueva_caja = CajaCarril.objects.create(
                id_disloque=disloque,
                numero_carril=carril,
                id_reten=reten,
                id_turno=id_turno,
                fecha_apertura=fecha_apertura,
                encargado_apertura=encargado_apertura,
                estado=estado,
                total_apertura=total_apertura,
                total_cierre_sistema=0.0,
                total_cierre_recaudador=0.0,
                id_recaudador=recaudador,
                fecha_operaciones=fecha_operaciones,
                anio=anio,
                mes=mes,
                dia=dia,
                consolidado=consolidado              

            )
            if nueva_caja:
                IntentosCierre.objects.create(id_caja_carril=nueva_caja.id,intentos_cierre=0,id_recaudador=id_recaudador)
                return Response({'message': 'la caja se aperturo correctamente'}, status=status.HTTP_200_OK)
            else:                    
                return Response({'message':'la caja no se pudo aperturar'}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message':'verifique que exista un disloque aperturada, que el reten sea el correcto y que exista un recaudador'})

@api_view(['GET'])
def ListaDisloquesParaApertura(request):
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]
        disloques = Disloque.objects.filter(estado='Aprobado', baja=0)
        serializers_disloques= DisloqueSerializer(disloques,many=True).data
        return Response(serializers_disloques)

class ConfirmacionCierreCaja(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, *args, **kwargs):
        datos = self.request.data
        total_cierre_recaudador=datos['total_cierre_recaudador']
        hora_actual = datetime.now()
        registro_cierre_caja = CajaCarril.objects.filter(id=datos['id_cajaCarril'])
        importe_sistema=sumaMontoTransacciones(datos['id_cajaCarril'])
        #print("QQQQQQQQQQQQQQQQQQQQQ",'sistema :',importe_sistema,'importe_recaudador :',total_cierre_recaudador)
        if float(importe_sistema) <= float(total_cierre_recaudador):          
            
            registro_cierre = registro_cierre_caja.first()
            obtener_lista_tarifario = ObtenerListaTarifarios(registro_cierre.id_disloque.id_regional.id)
            
            for tarifario in obtener_lista_tarifario:
                cantidad_transacciones = ObtenerCantidad(datos['id_cajaCarril'], tarifario.id_categoria.id_categoria)              
                cierre_caja=CierreCaja.objects.create(
                id_recaudador=registro_cierre.id_recaudador,
                id_caja_carril=registro_cierre,
                id_regional=registro_cierre.id_disloque.id_regional,
                id_reten=registro_cierre.id_reten,
                carril=registro_cierre.numero_carril,
                turno=registro_cierre.id_turno,
                nombre_categoria=tarifario.id_categoria.nombre_categoria,
                importe_categoria=tarifario.importe,
                cantidad_transacciones=cantidad_transacciones,
                importe_total=cantidad_transacciones*tarifario.importe,
                fecha_operaciones=registro_cierre.fecha_operaciones)

            registro_cierre_caja.update(
                observacion=datos['observaciones'],
                fecha_cierre=hora_actual,
                estado='Cerrado',
                total_cierre_sistema=importe_sistema,
                total_cierre_recaudador=total_cierre_recaudador,
                excedente=float(total_cierre_recaudador)-float(importe_sistema),
                consolidado='Si',
                diferencia=0.00)
            CerrarCiclo()
            if(cierre_caja and registro_cierre_caja):
                return Response({'message':f'La caja se cerro y se consolido correctamente con : {total_cierre_recaudador} Bs.'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'hubo un error en el intento de cierre y consolidacion verifique el cierre y la consolidadcion'},status=status.HTTP_200_OK)
        else:
            intentos=IntentosCierre.objects.get(id_caja_carril=registro_cierre_caja.first().id)
            intentos.intentos_cierre+=1
            intentos.save()
            if intentos.intentos_cierre==3:
                
                registro_cierre = registro_cierre_caja.first()
                obtener_lista_tarifario = ObtenerListaTarifarios(registro_cierre.id_disloque.id_regional.id)
            
                for tarifario in obtener_lista_tarifario:
                    cantidad_transacciones = ObtenerCantidad(datos['id_cajaCarril'], tarifario.id_categoria.id_categoria)              
                    cierre_caja=CierreCaja.objects.create(
                    id_recaudador=registro_cierre.id_recaudador,
                    id_caja_carril=registro_cierre,
                    id_regional=registro_cierre.id_disloque.id_regional,
                    id_reten=registro_cierre.id_reten,
                    carril=registro_cierre.numero_carril,
                    turno=registro_cierre.id_turno,
                    nombre_categoria=tarifario.id_categoria.nombre_categoria,
                    importe_categoria=tarifario.importe,
                    cantidad_transacciones=cantidad_transacciones,
                    importe_total=cantidad_transacciones*tarifario.importe,
                    fecha_operaciones=registro_cierre.fecha_operaciones)

                registro_cierre_caja.update(
                observacion=datos['observaciones'],
                fecha_cierre=hora_actual,estado='Cerrado',
                total_cierre_sistema=importe_sistema,
                total_cierre_recaudador=total_cierre_recaudador,
                diferencia=float(importe_sistema) - float(total_cierre_recaudador),
                consolidado='Si',
                excedente=0)
                CerrarCiclo()
                if(cierre_caja and registro_cierre_caja):
                    return Response({'message':f'La caja se cerro y se consolido correctamente con : {total_cierre_recaudador} Bs.'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'hubo un error en el intento de cierre y consolidacion verifique el cierre y la consolidadcion'},status=status.HTTP_200_OK)
        return Response({'message':'El monto ingresado no corresponde con el monto sistema'},status=status.HTTP_400_BAD_REQUEST)  
               
# class ConfirmacionCierreCaja(APIView):

#     def post(self, *args, **kwargs):
#         datos = self.request.data
#         total_cierre_recaudador=datos['total_cierre_recaudador']
#         hora_actual = datetime.now()
#         registro_cierre_caja = CajaCarril.objects.filter(id=datos['id_cajaCarril'])
#         importe_sistema=sumaMontoTransacciones(datos['id_cajaCarril'])
#         #print("QQQQQQQQQQQQQQQQQQQQQ",'sistema :',importe_sistema,'importe_recaudador :',total_cierre_recaudador)
#         if int(importe_sistema) < int(total_cierre_recaudador):
#             registro_cierre_caja.update(
#                 observacion=datos['observaciones'],
#                 fecha_cierre=hora_actual,estado='Cerrado',
#                 total_cierre_sistema=importe_sistema,
#                 total_cierre_recaudador=total_cierre_recaudador,
#                 diferencia=int(total_cierre_recaudador)-int(importe_sistema))           
           
#             return Response({'message':'La caja se cerro correctamente'},status=status.HTTP_200_OK)
#         else:
#             intentos=IntentosCierre.objects.get(id_caja_carril=registro_cierre_caja.first().id)
#             intentos.intentos_cierre+=1
#             intentos.save()
#             if intentos.intentos_cierre==3:
#                 registro_cierre_caja.update(
#                 observacion=datos['observaciones'],
#                 fecha_cierre=hora_actual,estado='Cerrado',
#                 total_cierre_sistema=importe_sistema,
#                 total_cierre_recaudador=total_cierre_recaudador,
#                 diferencia=int(total_cierre_recaudador)-int(importe_sistema))
            
#                 return Response({'message':f'La caja  se cerro correctamente con : {total_cierre_recaudador} Bs.'},status=status.HTTP_200_OK)
                
#             return Response({'message':'El monto ingresado no corresponde con el monto sistema'},status=status.HTTP_400_BAD_REQUEST)
        
class ConsolidarRecaudacion(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, *args, **kwargs):
        id_caja_carril=self.kwargs['id_caja_carril']
        registro=CajaCarril.objects.filter(id=id_caja_carril).first()
        return Response({'id_caja_carril':registro.id,
                         'total_cierre_recaudador':registro.total_cierre_recaudador,
                         'observacion_consolidado':registro.descripcion_de_observacion
                         })

    def post(self, *args, **kwargs):
        datos = self.request.data
        total_cierre_recaudador=datos['total_cierre_recaudador']
        registro_cierre_caja = CajaCarril.objects.get(id=datos['id_caja_carril'])
        registro_cierre_caja.descripcion_de_observacion=datos['observacion_consolidado']
        registro_cierre_caja.total_cierre_recaudador=total_cierre_recaudador
        if(float(registro_cierre_caja.total_cierre_sistema) <= float(total_cierre_recaudador)):
            registro_cierre_caja.excedente=float(total_cierre_recaudador)-float(registro_cierre_caja.total_cierre_sistema)
            registro_cierre_caja.diferencia=0
        elif(float(registro_cierre_caja.total_cierre_sistema) > float(total_cierre_recaudador)):
            registro_cierre_caja.diferencia=float(registro_cierre_caja.total_cierre_sistema) - float(total_cierre_recaudador)
            registro_cierre_caja.excedente=0

            nombre_usuario=registro_cierre_caja.id_recaudador.first_name+' '+registro_cierre_caja.id_recaudador.last_name
            DeudaRecaudador.objects.create(fecha=registro_cierre_caja.fecha_operaciones,reten=registro_cierre_caja.id_reten.nombre_reten,
                                           turno=Turnos.objects.get(id_turno=registro_cierre_caja.id_turno).nombre,valor=registro_cierre_caja.diferencia,
                                           nombre_usuario=nombre_usuario,regional=registro_cierre_caja.id_disloque.id_regional,id_caja_carril=registro_cierre_caja)
        registro_cierre_caja.consolidado='Si'
        registro_cierre_caja.save()

        registro_cierre = registro_cierre_caja
        obtener_lista_tarifario = ObtenerListaTarifarios(registro_cierre.id_disloque.id_regional.id)
            
        for tarifario in obtener_lista_tarifario:
            cantidad_transacciones = ObtenerCantidad(datos['id_caja_carril'], tarifario.id_categoria.id_categoria)              
            cierre_caja=CierreCaja.objects.create(
                id_recaudador=registro_cierre.id_recaudador,
                id_caja_carril=registro_cierre,
                id_regional=registro_cierre.id_disloque.id_regional,
                id_reten=registro_cierre.id_reten,
                carril=registro_cierre.numero_carril,
                turno=registro_cierre.id_turno,
                nombre_categoria=tarifario.id_categoria.nombre_categoria,
                importe_categoria=tarifario.importe,
                cantidad_transacciones=cantidad_transacciones,
                importe_total=cantidad_transacciones*tarifario.importe,
                fecha_operaciones=registro_cierre.fecha_operaciones)
  
        return Response({'message':f'La caja con id : {cierre_caja.id_caja_carril.id}  se consolido correctamente con : {total_cierre_recaudador} Bs. / con {round(registro_cierre.diferencia,2)} Bs. de deuda / con {round(registro_cierre.excedente,2)} Bs. de excedente'},status=status.HTTP_200_OK)
                
            #return Response({'message': f'debe ingresar igual o mayor a: {sumaMontoTransacciones(datos["id_cajaCarril"])}'}, status=status.HTTP_400_BAD_REQUEST)
            # cantidad_transacciones = ObtenerCantidadTags(registro_cierre_caja.first().fecha_operaciones, tarifario.id_categoria.id_categoria)
            # cierre_caja_tag=CierreCajaTags.objects.create(
            #     id_recaudador=registro_cierre.id_recaudador,
            #     id_caja_carril=registro_cierre,
            #     regional=registro_cierre.id_disloque.id_regional.nombre_regional,
            #     reten=registro_cierre.id_reten.id_reten,
            #     carril=registro_cierre.numero_carril,
            #     turno=registro_cierre.turno,
            #     nombre_categoria=tarifario.id_categoria.nombre_categoria,
            #     importe_categoria=tarifario.importe,
            #     cantidad_transacciones=cantidad_transacciones,
            #     importe_total=cantidad_transacciones*tarifario.importe,
            #     fecha_operaciones=registro_cierre.fecha_operaciones,
            #     created=hora_actual,
            #     modified=hora_actual,
            # )
            # print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",registro_cierre_caja[0])     
        
        
    
def ObtenerListaTarifarios(id_regional):
    lista_tarifarios = Tarifario.objects.filter(baja=0, id_regional=id_regional)
    #print("hhhhhhhhhhhhhhhhhh",lista_categorias)
    return lista_tarifarios



def ObtenerCantidad(pk, id_categoria):
    cantidad = Transaccion.objects.filter(id_caja_carril=pk, id_categoria=id_categoria, tag_leido=None).count()
    return cantidad


def ObtenerCantidadTags(pk, id_categoria):
    cantidad = Transaccion.objects.filter(
        id_caja_carril=pk, id_categoria=id_categoria).exclude(tag_leido='').count()
    # print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR",cantidad)
    return cantidad

    # ----------------obtiene la lista de recaudadores disponibles, numero_de carriles y turnos disponibles------------------
    # ---------------para la creaccion de una caja filtrando unicamente solo usuarios que pertenescan a un regional y reten--

@api_view(['GET'])
def DatosCreacionCajaApi(request, reten_id, disloque_id):
    try:
        # Obtener el número de carriles del retén
        numero_carriles = Retenes.objects.get(id_reten=reten_id).num_carril

        # Obtener la lista de recaudadores en el disloque y retén
        lista_disloques = DisloqueDetalle.objects.filter(
            numero_disloque=disloque_id, id_reten=reten_id)
        usuarios_sin_caja = lista_disloques.values_list(
            'id_recaudador', flat=True)

        # Obtener la lista de recaudadores con caja abierta
        usuarios_caja = CajaCarril.objects.filter(estado='Abierto')
        usuarios_con_caja = usuarios_caja.values_list(
            'id_recaudador', flat=True)

        # Obtener la lista de recaudadores libres (sin caja abierta)
        lista_recaudadores = AuthUser.objects.filter(
            id__in=usuarios_sin_caja).exclude(id__in=usuarios_con_caja)
        usuarios_serializer = AuthUserSerializer(
            lista_recaudadores, many=True).data
    except Retenes.DoesNotExist:
        return Response({'message': 'No se encontró el retén'}, status=404)
    except Exception as e:
        return Response({'message': f'Error: {str(e)}'}, status=500)

    # Obtener los turnos disponibles
    turnos_disponibles = BuscarTurnosDisponibles()

    return Response({
        'lista_recaudadores': usuarios_serializer,
        'numero_de_carriles': numero_carriles,
        'turnos_disponibles': turnos_disponibles
    })


def BuscarTurnosDisponibles():
    turnos=Turnos.objects.filter(id_turno__in=[4,5])
    turnos=TurnosSerializer(turnos,many=True).data
    return turnos
    

class ResumenCierreCaja(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        #print("AAAAAAAAAAAAAAAAAAAA",pk)
        try:
            registroCaja = CajaCarril.objects.get(id=pk)            
            fecha_actual = datetime.now().date()
            usuario = self.request.user
            # Puedes ajustar el nombre y la estructura del serializer según tu modelo
            serializer = CajaCarrilSerializer(registroCaja)
            return Response({
                'registroCaja': serializer.data,
                'regional':registroCaja.id_disloque.id_regional.nombre_regional,
                'reten':registroCaja.id_reten.nombre_reten,
                'fecha_actual': fecha_actual,
                'usuario_actual': usuario.username  # Ajusta según la estructura de tu modelo de usuario
            })
        except CajaCarril.DoesNotExist:
            return Response({'error': 'Registro de caja no encontrado'}, status=status.HTTP_404_NOT_FOUND)

def sumaMontoTransacciones(id_cajaCarril):
    # Obtener la suma del campo importe_recaudador para las transacciones relacionadas
    suma_transacciones = Transaccion.objects.filter(id_caja_carril=id_cajaCarril, tag_leido=None).aggregate(
        Sum('importe_recaudador'))['importe_recaudador__sum']
    #print("EEEEEEEEEEEEEEEEEEEEEEEE",suma_transacciones)
    if suma_transacciones:        
        return suma_transacciones
    else:
        return 0


def sumaMontoTransaccionesSinTags(id_cajaCarril):
    apertura = CajaCarril.objects.get(id=id_cajaCarril)
    # Obtener la suma del campo importe_recaudador para las transacciones relacionadas
    suma_transacciones = Transaccion.objects.filter(id_caja_carril=id_cajaCarril).exclude(
        tag_leido='').aggregate(Sum('importe_telepeaje'))['importe_telepeaje__sum']
    if suma_transacciones is None:
        suma_transacciones = 0
    return suma_transacciones

class ResumenTransacicionesSinTag(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        try:
            caja_carril = CajaCarril.objects.get(id=pk)
            resumen_por_categoria = CierreCaja.objects.filter(id_caja_carril=pk)
            serializer_resumen = CierreCajaSerializer(resumen_por_categoria,many=True).data
            total_recaudado = CierreCaja.objects.filter(id_caja_carril=pk).aggregate(Sum('importe_total'))['importe_total__sum']
            fecha_actual = datetime.now()
            usuario =self.request.user  # Ajusta según la estructura de tu modelo de usuario
            return Response({
                'fecha': fecha_actual,
                'usuario': usuario.username,  # Ajusta según la estructura de tu modelo de usuario
                'resumen_por_categoria': serializer_resumen,
                'regional':caja_carril.id_disloque.id_regional.nombre_regional,
                'reten':caja_carril.id_reten.nombre_reten,
                'turno':Turnos.objects.get(id_turno=caja_carril.id_turno).nombre,
                'carril':caja_carril.numero_carril,
                'fecha_operacion': caja_carril.fecha_operaciones,
                #'caja_carril': {'id': caja_carril.id, 'otros_campos': caja_carril.otros_campos},  # Ajusta según la estructura de tu modelo de caja_carril
                'total_recaudado': total_recaudado
            })

        except CajaCarril.DoesNotExist:
            return Response({'error': 'Registro de caja no encontrado'}, status=404)

class ResumenTransacicionesConTag(APIView):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        #caja_carril = CajaCarril.objects.get(id=pk)
        resumen_por_categoria_tags = CierreCajaTags.objects.filter(id_caja_carril=pk)
        serializer_resumen_tags = CierreCajaSerializer(resumen_por_categoria_tags, many=True).data
        total_recaudado = CierreCajaTags.objects.filter(id_caja_carril=pk).aggregate(Sum('importe_total'))['importe_total__sum']
        fecha_actual = datetime.now()
        usuario = self.request.user
        return Response ({'fecha': fecha_actual,
                          'usuario': usuario.username,
                          'transacciones_cierre_caja': serializer_resumen_tags,                  
                          'total_recaudado': total_recaudado})