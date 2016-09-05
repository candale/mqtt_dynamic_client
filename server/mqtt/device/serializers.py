from rest_framework import serializers

from device.models import Operation, Device, Arg
from device.constants import ArgType


class ArgSerializer(serializers.ModelSerializer):

    class Meta:
        model = Arg
        fields = ('name', 'type')


class OperationSerializer(serializers.ModelSerializer):

    args = ArgSerializer(many=True)

    class Meta:
        model = Operation
        fields = ('name', 'type', 'interval', 'description', 'args', 'topic')


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('id', 'device_id', 'online', 'last_offline')


class DeviceDoSerialier(serializers.BaseSerializer):

    payload = serializers.CharField()
    args = serializers.ListField()
