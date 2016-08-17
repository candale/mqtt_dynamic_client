from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

import device.views as views


router = DefaultRouter()
router.register(None, views.DeviceReadOnly)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'(?P<pk>\d+)/operations/',
        views.DeviceOperationsList.as_view()),
]
