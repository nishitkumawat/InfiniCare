import os
import sys
import django
from django.core.files import File

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmtech_project.settings')
sys.path.insert(0, 'farmtech_project')  # Add the project directory to path
django.setup()

# Import Django models
from django.contrib.auth.models import User
from core.models import SoilData, SoilAnalysisResult
from core.soil_analyzer import analyze_soil_data

# Get the test user
try:
    user = User.objects.get(username='testuser')
    print(f"Found test user: {user.username}")
    
    # Soil image path
    soil_image_path = 'test_images/test_images/soil_sample.jpg'
    
    if not os.path.exists(soil_image_path):
        print(f"Error: Test image not found at {soil_image_path}")
        sys.exit(1)
    
    # Create soil data entry
    soil_data = SoilData()
    soil_data.user = user
    soil_data.data_type = 'spectrometer'  # You can change this to 'multi_param' or 'moisture'
    soil_data.farm_name = 'Test Farm'
    soil_data.location = 'Test Field A'
    soil_data.notes = 'This is a test soil sample image for automated testing'
    
    # Open and attach the soil image
    with open(soil_image_path, 'rb') as img_file:
        soil_data.data_file.save(
            os.path.basename(soil_image_path),
            File(img_file),
            save=True
        )
    
    print(f"Created soil data entry: {soil_data}")
    
    # Analyze the soil data
    result = analyze_soil_data(soil_data)
    
    print("\nAnalysis Results:")
    print(f"Moisture Content: {result.moisture_content}%")
    print(f"pH Level: {result.ph_level}")
    print(f"Organic Matter: {result.organic_matter}%")
    
    if result.nutrient_levels:
        print("\nNutrient Levels:")
        for nutrient, value in result.nutrient_levels.items():
            print(f"  {nutrient}: {value}")
    
    print(f"\nSoil Health Score: {result.soil_health_score}")
    print(f"\nSummary: {result.result_summary}")
    print(f"\nRecommendations: {result.recommendations}")
    
    print("\nTest completed successfully.")
    
except User.DoesNotExist:
    print("Error: Test user 'testuser' not found. Please run test_user_setup.py first.")
except Exception as e:
    print(f"Error during test: {str(e)}")