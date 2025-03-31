from django.contrib import admin
from .models import SoilData, SoilAnalysisResult, HealthcareData, HealthcareAnalysisResult

@admin.register(SoilData)
class SoilDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'upload_date', 'farm_name', 'location', 'data_type')
    list_filter = ('data_type', 'upload_date')
    search_fields = ('farm_name', 'location', 'notes')

@admin.register(SoilAnalysisResult)
class SoilAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('soil_data', 'analysis_date', 'result_summary')
    list_filter = ('analysis_date',)
    search_fields = ('result_summary',)

@admin.register(HealthcareData)
class HealthcareDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'upload_date', 'patient_id', 'cancer_type', 'data_type')
    list_filter = ('data_type', 'cancer_type', 'upload_date')
    search_fields = ('patient_id', 'notes')

@admin.register(HealthcareAnalysisResult)
class HealthcareAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('healthcare_data', 'analysis_date', 'cancer_probability', 'confidence_score', 'result_summary')
    list_filter = ('analysis_date',)
    search_fields = ('result_summary', 'recommendations')
