from django import forms
from .models import SoilData, HealthcareData

class SoilDataUploadForm(forms.ModelForm):
    class Meta:
        model = SoilData
        fields = ['data_file', 'data_type', 'farm_name', 'location', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_data_file(self):
        data_file = self.cleaned_data['data_file']
        data_type = self.cleaned_data.get('data_type')
        
        # Get file extension
        ext = data_file.name.split('.')[-1].lower()
        
        # Always allow image file formats as we auto-detect them
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        
        # Define valid extensions based on data type
        if data_type == 'spectrometer':
            data_extensions = ['.csv', '.txt', '.asc', '.jdx', '.spc']
        elif data_type in ['multi_param', 'moisture']:
            data_extensions = ['.csv', '.txt', '.xlsx', '.json']
        else:
            data_extensions = ['.csv', '.txt']
        
        # Combine both valid extension lists
        valid_extensions = image_extensions + data_extensions
        
        if f'.{ext}' not in valid_extensions:
            raise forms.ValidationError(f"File type not supported. Please upload an image file ({', '.join(image_extensions)}) or data file ({', '.join(data_extensions)}) appropriate for {data_type} data.")
        
        # Check file size (15MB limit to accommodate images)
        if data_file.size > 15 * 1024 * 1024:
            raise forms.ValidationError("File size should not exceed 15MB")
        
        return data_file

class HealthcareDataUploadForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('', 'Prefer not to say')
    ]
    
    patient_gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    
    class Meta:
        model = HealthcareData
        fields = ['data_file', 'data_type', 'cancer_type', 'patient_id', 'patient_age', 'patient_gender', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_data_file(self):
        data_file = self.cleaned_data['data_file']
        data_type = self.cleaned_data.get('data_type')
        
        # Get file extension
        ext = data_file.name.split('.')[-1].lower()
        
        # Always allow image file formats as we auto-detect them
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']
        
        # Define valid extensions based on data type
        if data_type == 'spectrometer':
            data_extensions = ['.csv', '.txt', '.asc', '.jdx', '.spc', '.json']
        else:
            data_extensions = ['.csv', '.txt']
        
        # Combine both valid extension lists
        valid_extensions = image_extensions + data_extensions
        
        if f'.{ext}' not in valid_extensions:
            raise forms.ValidationError(f"File type not supported. Please upload an image file ({', '.join(image_extensions)}) or data file ({', '.join(data_extensions)}) appropriate for {data_type} data.")
        
        # Check file size (15MB limit for healthcare data which may include images)
        if data_file.size > 15 * 1024 * 1024:
            raise forms.ValidationError("File size should not exceed 15MB")
        
        return data_file
        
    def clean_patient_age(self):
        age = self.cleaned_data.get('patient_age')
        if age is not None and (age < 0 or age > 120):
            raise forms.ValidationError("Please enter a valid age between 0 and 120")
        return age
