from rest_framework import routers
from.import views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'regionales', views.RegionalesViewSet)
router.register(r'retenes',views.RetenesViewSet)
router.register(r'categorias', views.CategoriasViewSet)
router.register(r'tarifarios', views.TarifariosViewSet)
router.register(r'rutas', views.RutasViewSet)
router.register(r'cargos', views.CargosViewSet)
router.register(r'entidadFinanciera', views.EntidadFinancieraViewSet)
router.register(r'localidades',views.LocalidadViewSet)
router.register(r'cuentasbancarias',views.CuentasBancariasViewSet)
router.register(r'turnos',views.TurnosViewSet)

urlpatterns = [
    path('',include(router.urls)),
    #----------------------------Rutas para Regionales--------------------------
    path('regionales/baja/<int:pk>', views.BajaRegionalView.as_view(), name='bajaRegional'), 
    path('categorias/baja/<int:pk>', views.BajaCategoriaView.as_view(), name='bajaCategoria'),
    path('tarifarios/baja/<int:pk>', views.BajaTarifarioView.as_view(), name='bajaTarifarios'),
    path('rutas/baja/<int:pk>', views.BajaRutaView.as_view(), name='bajaRuta'),
    path('cargos/baja/<int:pk>', views.BajaCargoView.as_view(), name='baja-cargo'),
    path('entidadFinanciera/baja/<int:pk>', views.BajaEntidadFinancieraView.as_view(), name='bajaEntidadFinanciera'),
    path('localidades/baja/<int:pk>', views.BajaLocalidadView.as_view(), name='bajaLocalidad'),
    path('retenes/baja/<int:pk>', views.BajaRetenesView.as_view(), name='bajaRetenes'),
    
    #------------------------------------------------------------------------------------      
    #path('retenesApi',views.RetenesAPIView.as_view(), name='retenesApi'),
    path('api/upload-image/', views.upload_image, name='upload-image'),
    #------------------------------------------------------------------------------------
    path('listaRegionales', views.ListaRegionales, name='listaRegionales'),
    path('listaRetenes', views.ListaRetenes, name='listaRetenes'),
    path('listaRutas', views.ListaRutas, name='listaRutas'),
    path('listaCategorias', views.ListaCategorias, name='listaCategorias'),
    path('listaLocalidades', views.ListaLocalidades, name='listaLocalidades'),
    path('listaUsuariosDeRegional/<int:id_regional>', views.ListaUsuariosDeRegional, name='listaUsuariosDeRegional'),    
    path('listaLocalidadesDeRegional/<int:id_regional>', views.ListaLocalidadesDeRegional, name='listaLocalidadesDeRegional'),
    path('listaRutasDeRegional/<int:id_regional>', views.ListaRutasDeRegional, name='listaRutasDeRegional'),
    path('listaRetenesDeRegional/<int:id_regional>', views.ListaRetenesDeRegional, name='listaRetenesDeRegional'),

]

urlpatterns += router.urls