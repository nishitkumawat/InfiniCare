from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SoilData, SoilAnalysisResult
import tempfile
import os

class CoreViewsTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        self.temp_file.write(b'moisture,ph,nitrogen,phosphorus\n35.5,6.8,20.3,15.2')
        self.temp_file.close()
        
        # Create test soil data
        self.soil_data = SoilData.objects.create(
            user=self.user,
            data_file=self.temp_file.name,
            data_type='multi_param',
            farm_name='Test Farm',
            location='Test Location',
            notes='Test notes'
        )
        
        # Create test analysis result
        self.analysis = SoilAnalysisResult.objects.create(
            soil_data=self.soil_data,
            moisture_content=35.5,
            nutrient_levels={'nitrogen': 20.3, 'phosphorus': 15.2, 'potassium': 25.1},
            organic_matter=2.5,
            ph_level=6.8,
            soil_health_score=70.5,
            result_summary='Test summary',
            recommendations='Test recommendations'
        )
    
    def tearDown(self):
        # Clean up temporary file
        os.unlink(self.temp_file.name)
    
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
    
    def test_login_view(self):
        # Test GET request
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        
        # Test POST request with valid credentials
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('dashboard'))
        
        # Test POST request with invalid credentials
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_dashboard_view(self):
        # Login required, should redirect if not logged in
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # Login and test again
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')
        
        # Check content
        self.assertContains(response, 'Test Farm')
        self.assertContains(response, '70.5')  # soil health score
    
    def test_analysis_results_view(self):
        # Login required
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('analysis_results', args=[self.soil_data.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/analysis_results.html')
        
        # Check content
        self.assertContains(response, 'Test Farm')
        self.assertContains(response, 'Test summary')
        self.assertContains(response, 'Test recommendations')
