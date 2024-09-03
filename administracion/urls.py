from .views import *
from django.urls import path, include
from rest_framework import routers
from .import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView 
router = routers.DefaultRouter()
router.register(r'usuarios', AuthUserViewSet)
router.register(r'grupos',AuthGroupViewSet)
router.register(r'permisos',AuthPermissionViewSet)
router.register(r'usuariosGrupos',AuthUserGroupsViewSet)
router.register(r'registroDisloque', RegistroDisloqueViewSet, basename='registroDisloque')
router.register(r'menu',MenuViewSet)
router.register(r'menuGroup',MenuGroupViewSet)
urlpatterns = [
   path('',include(router.urls)),
   #-----------------------LOGIN Y LOGOUT-----------------------------------
   path('login', Login.as_view(), name='login'),
   path('logout', Logout.as_view(), name='logout'),

   #-----------------------GESTIÓN DE GRUPOS DE USUARIOS-----------------------
   path('listaContentType', ContentType, name='listaContentType'),#GET
   path('grupos/baja/<int:pk>', views.BajaGrupoView.as_view(), name='bajaGrupos'),#GET
   path('asignarRol/<int:id_usuario>/<int:id_grupo>', AsignarRol, name='asignarRol'),#POST
   path('asignarMenu', AsignarMenu, name='asignarMenu'),#POST
   

   #---------------------GESTIÓN DISLOQUE------------------------------------   
   path('disloque', views.ListaDisloqueAPI.as_view(), name='disloque'),#GET---------lista disloques
   path('usuariosLibres', UsuariosLibresAPI.as_view(), name='usuariosLibres'),#POST ------------recibe id_regional y fecha_ini  
   path('retenesNoDisloqueAPI', RetenesNoDisloqueAPI.as_view(), name='retenesNoDisloqueAPI'),#POST-----------recibe id_regional y fecha_ini
   path('aprobarDisloque/<int:id_disloque>',AprobarDisloqueAPI,name='aprobarDisloque'),
   path('bajaDisloque/<int:id_disloque>',BajaDisloqueAPI,name='bajaDisloque'),
   path('verListaDetalleDisloque/<int:pk>',views.VerListaDetalleDisloque.as_view(),name='verListaDetalleDisloque'),
   path('asignarResponsable/<int:id_detalle_disloque>',AsignarResponsableAPI,name='asignarResponsable'),
   path('quitarResponsable/<int:id_detalle_disloque>',QuitarResponsableAPI,name='quitarResponsable'),
   path('agregarUnRecaudador',AgregarUnRecaudadorAPI,name='agregarUnRecaudador'),
   path('quitarUnRecaudadorAPI/<int:id_detalle_disloque>',QuitarUnRecaudadorAPI,name='quitarUnRecaudadorAPI'),   
   
   #---------------------GESTIÓN DE CAJA CARRIL-----------------------------
   path('cajaCarril', views.AperturaCajaCarril.as_view(), name='cajaCarril'),#
   path('confirmacionCierreCaja', views.ConfirmacionCierreCaja.as_view(), name='confirmacionCierreCaja'),
   path('consolidarRecaudacion', views.ConsolidarRecaudacion.as_view(), name='consolidarRecaudacion'),# 
   path('consolidarRecaudacion/<int:id_caja_carril>', views.ConsolidarRecaudacion.as_view(), name='consolidarRecaudacion'),#     
   path('datosCreacionCaja/<int:reten_id>/<int:disloque_id>',DatosCreacionCajaApi,name='datosCreacionCaja'),
   path('resumenCierreCaja/<int:pk>',views.ResumenCierreCaja.as_view(),name='resumenCierreCaja'),
   path('resumenTransacicionesSinTag/<int:pk>',views.ResumenTransacicionesSinTag.as_view(),name='resumenTransacicionesSinTag'),
   path('resumenTransacicionesConTag/<int:pk>',views.ResumenTransacicionesConTag.as_view(),name='resumenTransacicionesConTag'),
   path('listaDisloquesParaApertura',ListaDisloquesParaApertura,name='listaDisloquesParaApertura'),
   
   

   #path('menu', MenuView.as_view(), name='menu-list'),
   #path('bajaContingencia/baja/<int:pk>',views.BajaContingenciaView.as_view(), name='bajaContingencia'),
   #path('listaTipoContingencia', ListaTipoContingencia, name='listaTipoContingencia'),
   
]

urlpatterns += router.urls