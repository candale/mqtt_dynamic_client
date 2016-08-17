from django.shortcuts import get_object_or_404

from rest_framework import generics, viewsets

from device.serializers import OperationSerializer, DeviceSerializer
from device.models import Operation, Device


class DeviceOperationsList(generics.ListAPIView):

    serializer_class = OperationSerializer

    def get_queryset(self):
        get_object_or_404(Device, pk=self.kwargs.get('pk'))
        return Operation.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(device__id=self.kwargs.get('pk'))


class DeviceReadOnly(viewsets.ReadOnlyModelViewSet):

    serializer_class = DeviceSerializer
    queryset = Device.objects.all()
