from django.urls import path
from tech.views import index
from tech.views import physionet_login, physionet_callback, physionet_dataset_check

urlpatterns = [
    path('', index, name='index'),
    # PhysioNet OAuth2 test flow
    path('physionet/login/',    physionet_login,         name='physionet-login'),
    path('physionet/callback/', physionet_callback,      name='physionet-callback'),
    path('physionet/dataset/',  physionet_dataset_check, name='physionet-dataset'),
]
