from django.db import models


class Medicine(models.Model):
    medicine_id = models.CharField(max_length=45, primary_key=True)
    medicine_name = models.CharField(max_length=45, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.medicine_name or self.medicine_id


class MedicineInstance(models.Model):
    instance_id = models.CharField(max_length=45, primary_key=True)
    medicine = models.ForeignKey("Medicine.Medicine", on_delete=models.CASCADE)
    pharmacy = models.ForeignKey("Pharmacy.Pharmacy", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.medicine} @ {self.pharmacy}"


class PatientMedicine(models.Model):
    patient_medicine_id = models.CharField(max_length=45, primary_key=True)
    days_of_intake = models.CharField(max_length=45, blank=True, null=True)
    intake_note = models.TextField(blank=True, null=True)
    medicine = models.ForeignKey("Medicine.Medicine", on_delete=models.CASCADE)
    patient_record = models.ForeignKey("PatientRecord.PatientRecord", on_delete=models.CASCADE)

    def __str__(self):
        return f"Prescription: {self.medicine} for {self.patient_record.user.username}"
