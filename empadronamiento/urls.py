from .views import PuntoEmpadronamientoViewSet
#from .views import CuentaViewSet, EntidadPersonaViewSet, EntidadEmpresaViewSet, EntidadContratoViewSet, DepositosViewSet, TagsViewSet, VehiculoViewSet, RegistrarCuentaViewSet, AgregarEmpresaViewSet, AgregarPersonaConvenioViewSet, CancelarRegistroNuevaCuenta, VerEmpresaConvenio, BajaEmpresaConvenio, EdicionEmpresaConvenio, HabilitarBotonC, AgregarVehiculo, EditarVehiculo, VerEntidadTag, AsignacionTag, ReasignarTag, VerEntidadTag, FormularioRecarga, HistorialRecargas, mostrarContratos
from .views import *
from django.urls import path, include
from rest_framework import routers
from .import views

router = routers.DefaultRouter()
router.register(r'pempadronamiento', PuntoEmpadronamientoViewSet)
router.register(r'cuentas', CuentaViewSet)
router.register(r'registrarCuenta', RegistrarCuentaViewSet, basename='registrarCuenta')
router.register(r'entidadPersonas', EntidadPersonaViewSet)
router.register(r'entidadEmpresas', EntidadEmpresaViewSet)
router.register(r'entidadContratos', EntidadContratoViewSet)
router.register(r'entidadDepositos', DepositosViewSet)
router.register(r'entidadTags', TagsViewSet)
# router.register(r'vehiculo', VehiculoViewSet)
router.register(r'vehiculo', VehiculoViewSet, basename='vehiculo')


urlpatterns = [
    # Otras rutas de tu aplicación
    path('', include(router.urls)),
    path('pempadronamiento/baja/<int:pk>', views.BajaPuntoEmpadronamientolView.as_view(), name='bajaPuntoEmpadronamiento'),
     ################ Cuentas ##################

     path('cancelarRegistroNuevaCuenta/<int:pk>',views.CancelarRegistroNuevaCuenta.as_view(), name='CancelarRegistroNuevaCuenta'),

      
    ################ Personas Convenio ##################

    path('agregarPersonaConvenio', views.AgregarPersonaConvenioViewSet.as_view(), name='agregarPersonaConvenio'),
    path('agregarPersonaConvenio/<int:pk>', views.AgregarPersonaConvenioViewSet.as_view(), name='agregarPersonaConvenio'), 
    path('verPersonaConvenio/<int:pk>',views.VerPersonaConvenio.as_view(), name='VerPersonaConvenio'),
    path('bajaPersonaConvenio/<int:pk>', views.BajaPersonaConvenio.as_view(), name='bajaPersonaConvenio'),
    path('edicionPersonaConvenio/<int:pk>', views.EdicionPersonaConvenio.as_view(), name='EdicionPersonaConvenio'),
    path('edicionPersonaConvenio', views.EdicionPersonaConvenio.as_view(), name='EdicionPersonaConvenio'),
    path('habilitarBotonP/<int:pk>', views.habilitarBotonP.as_view(), name='habilitarBotonP'),

 

    ################ Empresas Convenio ##################
    path('agregarEmpresa', views.AgregarEmpresaViewSet.as_view(), name='AgregarEmpresa'),
    path('agregarEmpresa/<int:pk>', views.AgregarEmpresaViewSet.as_view(), name='AgregarEmpresa'),
    path('verEmpresa/<int:pk>', views.VerEmpresaConvenio.as_view(), name='VerEmpresa'),
    path('bajaEmpresaConvenio/<int:pk>', views.BajaEmpresaConvenio.as_view(), name='BajaEntidadEmpresa'),
    path('edicionEmpresaConvenio/<int:pk>', views.EdicionEmpresaConvenio.as_view(), name='EdicionEmpresaConvenio'),
    path('edicionEmpresaConvenio', views.EdicionEmpresaConvenio.as_view(), name='EdicionEmpresaConvenio'),
    path('habilitarBotonC/<int:pk>', views.HabilitarBotonC.as_view(), name='habilitarBotonC'),


    ################ Vehiculos ##################
    # path('agregarVehiculo/<int:pk>', views.AgregarVehiculo.as_view(), name='AgregarVehiculo'),
    # path('agregarVehiculo', views.AgregarVehiculo.as_view(), name='AgregarVehiculo'),
    # path('editarVehiculo/<int:pk>', views.EditarVehiculo.as_view(), name='EditarVehiculo'),
    # path('editarVehiculo', views.EditarVehiculo.as_view(), name='EditarVehiculo'),
    path('bajaVehiculo/<int:id_vehiculo>', BajaVehiculo, name='BajaVehiculo'),

    ################ tags ##################
    path('asignacionTag/<int:pk>',views.AsignacionTag.as_view(), name='asignacionTag'),
    path('asignacionTag',views.AsignacionTag.as_view(), name='asignacionTag'),
    path('reasignarTag/<int:idv>',ReasignarTag, name='reasignarTag'),
    path('verTag/<pk>',views.VerTag.as_view(), name='verTag'),
    path('verEntidadTag/<pk>',views.VerEntidadTag.as_view(), name='verEntidadTag'),
     path('listaTagsDisponibles',views.ListaTagDisponibles.as_view(), name='listaTagsDisponibles'),


      #-----------------------------------------RECARGAS DE SALDO-----------------------------------------------------
    path('formularioRecarga/<int:pk>',views.FormularioRecarga.as_view(), name='formularioRecarga'),
    path('formularioRecarga',views.FormularioRecarga.as_view(), name='formularioRecarga'),
    path('historialRecargas/<int:pk>',views.HistorialRecargas.as_view(), name='historialRecargas'),


#-----------------------------------------CONTRATOS EMPRESA/PERSONA-----------------------------------
    path('contratos',views.mostrarContratos.as_view(), name='mostrar_contratos'),
    path('verContratoEmpresa/<int:pk>', views.VerContratoEmpresa.as_view(), name='VerContratoEmpresa'),
    path('verContratoPersona/<int:pk>', views.VerContratoPersona.as_view(), name='VerContratoPersona'),
    path('registrarNuevoContratoEmpresa/<int:pk>',views.RegistrarNuevoContratoEmpresa.as_view(),name='registrarNuevoContratoEmpresa'),
    path('registrarNuevoContratoEmpresa',views.RegistrarNuevoContratoEmpresa.as_view(),name='registrarNuevoContratoEmpresa'),
    path('registrarNuevoContratoPersona/<int:pk>',views.RegistrarNuevoContratoPersona.as_view(),name='registrarNuevoContratoPersona'),
    path('registrarNuevoContratoPersona',views.RegistrarNuevoContratoPersona.as_view(),name='registrarNuevoContratoPersona'),
    path('bajaContratoEmpresa/<int:idc>',BajaContratoEmpresa,name='bajaContratoEmpresa'),
    #path('bajaContratoEmpresa',BajaContratoEmpresa,name='bajaContratoEmpresa'),


]

#urlpatterns += router.urls
