import uuid
import json

from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.conf import settings

from rest_framework import generics, viewsets, status

from device.serializers import (
    OperationSerializer, DeviceSerializer, DeviceDoSerializer)
from device.models import Operation, Device
from device.utils import build_topic

import paho.mqtt.client as mqtt


class DeviceOperationsList(generics.ListAPIView):

    serializer_class = OperationSerializer

    def get_queryset(self):
        get_object_or_404(Device, device_id=self.kwargs.get('device_id'))
        return Operation.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(device__device_id=self.kwargs.get('device_id'))


class DeviceReadOnly(viewsets.ReadOnlyModelViewSet):

    serializer_class = DeviceSerializer
    queryset = Device.objects.all()
    lookup_field = 'device_id'
    lookup_url_kwarg = 'device_id'


class DeviceDo(generics.CreateAPIView):

    queryset = Operation.objects.all()
    serializer_class = DeviceDoSerializer

    def get_object(self):
        qs = self.filter_queryset(self.get_queryset())

        device = get_object_or_404(
            Device, device_id=self.kwargs.get('device_id'))

        try:
            operation = qs.get(
                device=device, name=self.kwargs.get('operation'))
        except Operation.DoesNotExist:
            raise Http404

        return operation

    def create(self, request, *args, **kwargs):
        try:
            super(DeviceDo, self).create(request, *args, **kwargs)
        except ValueError, e:
            return JsonResponse(
                {"status": "error", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({"status": "ok"})

    def perform_create(self, serializer):
        obj = self.get_object()

        if obj.device.online is False:
            return ValueError('Device offline')

        mqtt_client = mqtt.Client(str(uuid.uuid4())[:8])
        mqtt_client.connect(
            settings.MQTT_SERVER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)

        mqtt_client.publish(
            build_topic(obj.topic, serializer.validated_data['args']),
            serializer.validated_data['payload'])
        mqtt_client.disconnect()
