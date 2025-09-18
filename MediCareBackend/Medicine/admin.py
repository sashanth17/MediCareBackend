from django.contrib import admin
from .models import Medicine,MedicineInstance,PatientMedicine
# Register your models here.
admin.site.register(Medicine)
admin.site.register(MedicineInstance)
admin.site.register(PatientMedicine)