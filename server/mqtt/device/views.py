from django.shortcuts import get_object_or_404

from rest_framework import generics

from device.serializers import OperationSerializer
from device.models import Operation, Device


class DeviceOperations(generics.ListAPIView):

    serializer_class = OperationSerializer

    def get_queryset(self):
        get_object_or_404(Device, device_id=self.kwargs.get('device_id'))
        return Operation.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(device__device_id=self.kwargs.get('device_id'))
