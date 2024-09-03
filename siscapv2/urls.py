from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from django.conf import settings
from rest_framework.documentation import include_docs_urls
urlpatterns = [
    path('admin/', admin.site.urls),    
    path('', include_docs_urls(title='Api Documentation')),
    #path('docs/', include_docs_urls(title='Api Documentation')),
    path('empadronamiento/',include('empadronamiento.urls')),
    path('parametros/',include('parametros.urls')),
    path('contingencias/',include('contingencias.urls')),
    path('administracion/',include('administracion.urls')),
    path('post_clasificacion/',include('post_Clasificacion.urls')),
    path('transacciones/',include('transacciones.urls')),     
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)