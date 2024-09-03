from .views import *
from django.urls import path, include
from rest_framework import routers
from .import views 
router = routers.DefaultRouter()
urlpatterns = [
   path('',include(router.urls)),
   path('transaccionesAPI',views.TransaccionesAPI.as_view(), name='transaccionesAPI'),
   path('transaccionAPI/<int:id>',views.TransaccionAPI.as_view(), name='transaccionAPI'),
   path('transaccionAPI',views.TransaccionAPI.as_view(), name='transaccionAPI'),
  
   
]

urlpatterns += router.urls
