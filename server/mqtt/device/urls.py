from django.conf.urls import url

from device.views import DeviceOperations


urlpatterns = [
    url(r'(?P<device_id>.*)/operations/', DeviceOperations.as_view()),
]
