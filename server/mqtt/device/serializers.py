from rest_framework import serializers

from device.models import Operation


class OperationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Operation
        fields = ('spec',)
