from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.conf import settings

from rest_framework import generics, viewsets, status

from device.serializers import (
    OperationSerializer, DeviceSerializer, DeviceDoSerializer)
from device.models import Operation, Device
from device.utils import build_topic, send_message_from_api


class NotSentException(Exception):
    pass


class DeviceOfflineException(Exception):
    pass


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
        except (DeviceOfflineException, NotSentException) as e:
            return JsonResponse(
                {"status": "error", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({"status": "ok"})

    def perform_create(self, serializer):
        obj = self.get_object()

        if obj.device.online is False:
            raise DeviceOfflineException('Device offline')

        published = send_message_from_api(
            obj.topic, serializer.validated_data['args'],
            serializer.validated_data['payload'])

        if published is False:
            raise NotSentException('Message not sent')
