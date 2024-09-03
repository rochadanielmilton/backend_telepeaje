from .views import *
from django.urls import path, include
from rest_framework import routers
from .import views 
router = routers.DefaultRouter()
urlpatterns = [
   path('',include(router.urls)),   
   path('recibir_tag',views.Recibir_Tag,name='recibir_Tag'),
   #path('recibir_tag',views.RecibirCodigo,name='recibir_Tag'),
   path('Registrar_Transaccion_Recaudador',views.Registrar_Transaccion_Recaudador, name='Registrar_Transaccion_Recaudador'),
   path('Registrar_Transaccion_Roceta',views.Registrar_Transaccion_Roceta, name='Registrar_Transaccion_Roceta'),
   path('obtener_datos_estacion',views.Obtener_Datos_Estacion,name='obtener_datos_estacion'),
   path('recaudacionNacionalRegionalFecha',views.RecaudacionNacionalRegionalFecha.as_view(),name='recaudacionNacionalRegionalFecha'),
   path('recaudacionTurnoRegionalFecha',views.RecaudacionTurnoRegionalFecha.as_view(),name='recaudacionTurnoRegionalFecha'),
   path('transaccionesRecaudadorRegionalFecha',views.TransaccionesRecaudadorRegionalFecha.as_view(),name='transaccionesRecaudadorRegionalFecha'),
   path('reporteMensualNacional',views.ReporteMensualNacional.as_view(),name='reporteMensualNacional'),
   path('reportePorRegionalAnual',views.ReportePorRegionalAnual.as_view(),name='reportePorRegionalAnual'),
   path('reportePorRegionalRetenAnual',views.ReportePorRegionalRetenAnual.as_view(),name='reportePorRegionalRetenAnual'),
   path('reporteNacionalAnual',views.ReporteNacionalAnual.as_view(),name='reporteNacionalAnual'),
   path('reporteRangoRegionalReten',views.ReporteRangoRegionalReten.as_view(),name='reporteRangoRegionalReten'),
   path('listarTransaccionesTag',views.ListarTransaccionesTag, name='listarTransaccionesTag'),
   path('monitorApi',views.MonitorApi.as_view(),name='monitorApi'),
   
]

urlpatterns += router.urls