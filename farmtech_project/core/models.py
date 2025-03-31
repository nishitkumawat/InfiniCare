from django.db import models
from django.contrib.auth.models import User
import uuid
import os

def get_data_file_path(instance, filename):
    # Generate a unique path for uploaded data files
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Determine the folder based on data category
    if hasattr(instance, 'data_category') and instance.data_category == 'healthcare':
        return os.path.join('healthcare_data', str(instance.user.id), filename)
    else:
        return os.path.join('soil_data', str(instance.user.id), filename)

class SoilData(models.Model):
    DATA_TYPE_CHOICES = [
        ('spectrometer', 'Optical Spectrometer Data'),
        ('multi_param', 'Multi-parameter Soil Sensor Data'),
        ('moisture', 'Capacitive Soil Moisture Data'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soil_data')
    data_file = models.FileField(upload_to=get_data_file_path)
    # Note: For image files (jpg, png, etc.), leaf image processing will automatically be used
    # regardless of the data_type selection. This field is mainly for UI display purposes.
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    upload_date = models.DateTimeField(auto_now_add=True)
    farm_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    data_category = models.CharField(max_length=20, default='farming')
    
    def __str__(self):
        return f"{self.farm_name} - {self.get_data_type_display()} - {self.upload_date.strftime('%Y-%m-%d')}"

class SoilAnalysisResult(models.Model):
    soil_data = models.ForeignKey(SoilData, on_delete=models.CASCADE, related_name='analysis_results')
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    # Analysis results
    moisture_content = models.FloatField(null=True, blank=True)
    nutrient_levels = models.JSONField(null=True, blank=True)
    organic_matter = models.FloatField(null=True, blank=True)
    ph_level = models.FloatField(null=True, blank=True)
    soil_health_score = models.FloatField(null=True, blank=True)
    
    # Overall analysis
    result_summary = models.TextField()
    recommendations = models.TextField()
    
    def __str__(self):
        return f"Analysis for {self.soil_data} on {self.analysis_date.strftime('%Y-%m-%d')}"

class HealthcareData(models.Model):
    DATA_TYPE_CHOICES = [
        ('spectrometer', 'Optical Spectrometer Data'),
        ('image', 'Digital Camera Image'),
    ]
    
    CANCER_TYPE_CHOICES = [
        ('breast', 'Breast Cancer'),
        ('throat', 'Throat Cancer'),
        ('skin', 'Skin Cancer'),
        ('other', 'Other Cancer Type'),
        ('screening', 'General Screening'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='healthcare_data')
    data_file = models.FileField(upload_to=get_data_file_path)
    # Note: For image files (jpg, png, etc.), image processing will automatically be used
    # regardless of the data_type selection. This field is mainly for UI display purposes.
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    cancer_type = models.CharField(max_length=20, choices=CANCER_TYPE_CHOICES)
    upload_date = models.DateTimeField(auto_now_add=True)
    patient_id = models.CharField(max_length=100)
    patient_age = models.IntegerField(null=True, blank=True)
    patient_gender = models.CharField(max_length=10, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    data_category = models.CharField(max_length=20, default='healthcare')
    
    def __str__(self):
        return f"{self.patient_id} - {self.get_cancer_type_display()} - {self.upload_date.strftime('%Y-%m-%d')}"

class HealthcareAnalysisResult(models.Model):
    healthcare_data = models.ForeignKey(HealthcareData, on_delete=models.CASCADE, related_name='analysis_results')
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    # Analysis results
    cancer_probability = models.FloatField(null=True, blank=True)
    biomarkers = models.JSONField(null=True, blank=True)
    spectral_signatures = models.JSONField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Overall analysis
    result_summary = models.TextField()
    recommendations = models.TextField()
    
    def __str__(self):
        return f"Analysis for {self.healthcare_data} on {self.analysis_date.strftime('%Y-%m-%d')}"
