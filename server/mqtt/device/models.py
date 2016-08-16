from __future__ import unicode_literals

from django.db import models


class Device(models.Model):
    device_id = models.CharField(
        'Unique string that represents the device',
        max_length=256, db_index=True, unique=True)
    spec = models.TextField('Exposed operations specifications')
    online = models.BooleanField(
        'The online/offline state of the device', default=False)
    last_online = models.DateTimeField(
        'Last time when the device was online', null=True, blank=True)
