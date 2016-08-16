from __future__ import unicode_literals

from django.db import models


class Device(models.Model):
    device_id = models.CharField(
        'Unique string that represents the device',
        max_length=256, db_index=True, unique=True)
    online = models.BooleanField(
        'The online/offline state of the device', default=False)
    last_online = models.DateTimeField(
        'Last time when the device was online', null=True, blank=True)


class Operation(models.Model):
    spec = models.TextField('Operation specification')
    device = models.ForeignKey(
        'Device', on_delete=models.CASCADE, related_name='operations')
