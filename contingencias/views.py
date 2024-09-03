from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from parametros.models import Contingencias,TipoContingencia
from .serializers import ContingenciasSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view

class ContingenciasViewSet(viewsets.ModelViewSet):
    queryset = Contingencias.objects.filter(baja=0).order_by('-id')
    serializer_class = ContingenciasSerializer

class BajaContingenciaView(generics.UpdateAPIView):
    queryset = Contingencias.objects.all()
    serializer_class = ContingenciasSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.baja = 1
        instance.save()
        return Response({'message': f'La entidad {instance.resumen_hecho} fue dada de baja.'})
    
@api_view(['GET'])
def ListaTipoContingencia(request):
    lista_tipo_contingencias=TipoContingencia.objects.values('id','tipo')
    tipo_contingencias_data=[{'id':item['id'],'tipo':item['tipo']} for item in lista_tipo_contingencias]
    data=tipo_contingencias_data
    return Response(data)