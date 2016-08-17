from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.routers import DefaultRouter

import device.views as device_views


router = DefaultRouter()
router.register('device', device_views.DeviceReadOnly)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rest-auth/', include('rest_auth.urls')),

    url(r'^', include(router.urls)),
    url(r'^device/', include('device.urls')),
]
