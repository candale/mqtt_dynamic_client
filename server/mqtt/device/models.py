from __future__ import unicode_literals

from django.db import models

from device.constants import ArgType, OpType


class Device(models.Model):
    device_id = models.CharField(
        'Unique string that represents the device',
        max_length=256, db_index=True, unique=True)
    online = models.BooleanField(
        'The online/offline state of the device', default=False)
    last_offline = models.DateTimeField(
        'Last time the device went offline', null=True, blank=True)


class Operation(models.Model):

    name = models.CharField(
        'Valid (language specific) operation name',
        max_length=256, db_index=True)
    type = models.CharField(
        'Operation data direction', max_length=32, choices=OpType.CHOICES)
    interval = models.IntegerField(
        'Interval (in ms) at which data is published by this operation',
        null=True, blank=True)
    description = models.TextField('Description of operation', blank=True)
    topic = models.CharField(max_length=1024)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name='operations')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('name', 'device'))

    def __str__(self):
        return self.name


# TODO: consider having the arguments as a list or something like that on the
#       operation so you don't hit the database so many times
# TODO: enforce arg order because in topic they must be in a specific order
class Arg(models.Model):
    type = models.CharField(
        'Type of argument', max_length=32, choices=ArgType.CHOICES)
    name = models.CharField('Argument name', max_length=256)
    operation = models.ForeignKey(
        Operation, on_delete=models.CASCADE, related_name='args')
