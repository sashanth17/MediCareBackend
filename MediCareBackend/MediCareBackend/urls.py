from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('VideoCall/',include('VideoCall.urls')),
    path('patient/',include('UserDetails.urls')),
    path('Doctors/',include('Doctor.urls'))
]
