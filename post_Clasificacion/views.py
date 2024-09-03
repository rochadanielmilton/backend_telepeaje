from django.shortcuts import render
from parametros.models import *
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from parametros.serializers import *
from administracion.serializers import *
from .serializers import TransaccionSerializer, TarifariosTransaccionSerializer
from rest_framework import status
# Create your views here.


class TransaccionesAPI(APIView):
    def get_fecha_actual(self):
        return datetime.now().date()
        # fecha_especifica = "2023-10-16"
        # return datetime.strptime(fecha_especifica, "%Y-%m-%d").date()

    def cargar_listas(self):
        lista_regionales = Regionales.objects.filter(baja=0)
        lista_regionales = RegionalesSerializer(
            lista_regionales, many=True).data
        lista_retenes = Retenes.objects.filter(id_regional=8)
        lista_retenes = RetenesSerializer(lista_retenes, many=True).data
        lista_recaudadores = AuthUser.objects.filter(id_regional=8)
        lista_recaudadores = AuthUserSerializer(
            lista_recaudadores, many=True).data
        lista_tarifarios = Tarifario.objects.filter(id_regional=8, baja=0)
        lista_tarifarios = TarifariosSerializer(
            lista_tarifarios, many=True).data
        return lista_regionales, lista_retenes, lista_recaudadores, lista_tarifarios

    def configurar_paginacion(self, queryset):
        paginator = Paginator(queryset, 20)
        page = self.request.GET.get('page')
        return paginator.get_page(page)

    def get(self, *args, **kwargs):
        fecha_actual = self.get_fecha_actual()
        transacciones = Transaccion.objects.filter(
            fecha=fecha_actual).order_by('-created')
        transacciones = TransaccionSerializer(transacciones, many=True).data

        lista_regionales, lista_retenes, lista_recaudadores, lista_tarifarios = self.cargar_listas()
        return Response(transacciones)

    def post(self, *args, **kwargs):
        data = self.request.data
        fecha = data['fecha']
        transacciones = Transaccion.objects.filter(
            fecha=fecha).order_by('-nombre_revisor')
        transacciones = TransaccionSerializer(transacciones, many=True).data

        lista_regionales, lista_retenes, lista_recaudadores, lista_tarifarios = self.cargar_listas()
        return Response(transacciones)


class TransaccionAPI(APIView):

    def get(self, *args, **kwargs):
        pk = self.kwargs['id']
        # print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",pk)
        transaccion = Transaccion.objects.get(id=pk)
        tarifario_lista = Tarifario.objects.filter(
            id_regional=transaccion.id_regional)
        tarifario_serializer = TarifariosTransaccionSerializer(
            tarifario_lista, many=True).data
        transaccion_serializer = TransaccionSerializer(transaccion).data
        return Response({"transacion": transaccion_serializer,
                         "tarifario": tarifario_serializer}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        datos = self.request.data
        id_tarifario = datos['id_tarifario']
        id_transaccion = datos['id_transaccion']
        comentario_revisor = datos['comentario_revisor']
        tarifario = Tarifario.objects.get(id_tarifario=id_tarifario).importe
        transaccion = Transaccion.objects.get(id=id_transaccion)
        transaccion.importe_revision = tarifario
        transaccion.comentario_revisor = comentario_revisor
        transaccion.estado='Correcto'
        transaccion.save()
        transaccion_serializer = TransaccionSerializer(transaccion)
        if transaccion_serializer:
            return Response({"transaccion": transaccion_serializer.data,
                             "message": "El importe de la transaccion se actualizo correctamente"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': "El importe no se puedo actualizar"}, status=status.HTTP_400_BAD_REQUEST)


