from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

import device.views as views


router = DefaultRouter()
router.register(None, views.DeviceReadOnly)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'(?P<device_id>[\w\d_-]+)/operations/$',
        views.DeviceOperationsList.as_view()),
    url(r'(?P<device_id>[\w\d_-]+)/operations/(?P<operation>[\w\d_]+)/$',
        views.DeviceDo.as_view())
]
