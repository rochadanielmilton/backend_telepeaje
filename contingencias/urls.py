from .views import ContingenciasViewSet, ListaTipoContingencia
from django.urls import path, include
from rest_framework import routers
from .import views 
router = routers.DefaultRouter()
router.register(r'contingencia', ContingenciasViewSet)
urlpatterns = [
   path('',include(router.urls)),
   path('contingencia/baja/<int:pk>',views.BajaContingenciaView.as_view(), name='contingencia'),
   path('listaTipoContingencia', ListaTipoContingencia, name='listaTipoContingencia'),
   
]

urlpatterns += router.urls
