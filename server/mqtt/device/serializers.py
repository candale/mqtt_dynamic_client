from rest_framework import serializers

from device.models import Operation, Device


class OperationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Operation
        fields = ('spec',)


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('id', 'device_id', 'online', 'last_online')
