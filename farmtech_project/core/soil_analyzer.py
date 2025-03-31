import os
import json
import numpy as np
import pandas as pd
import cv2
from django.conf import settings
from .models import SoilAnalysisResult
from .ai_utils import analyze_text_with_ai
from .image_processor import analyze_leaf_image, get_image_visualization

def analyze_soil_data(soil_data):
    """
    Analyze uploaded soil data and create analysis results
    
    Args:
        soil_data: SoilData model instance
    
    Returns:
        SoilAnalysisResult: The created analysis result
    """
    data_type = soil_data.data_type
    file_path = soil_data.data_file.path
    
    # Check if it's an image file (regardless of selected data type)
    file_ext = os.path.splitext(file_path)[1].lower()
    is_image = file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # Process based on file type and data type
    if is_image:
        result = process_leaf_image(file_path)
    elif data_type == 'spectrometer':
        result = process_spectrometer_data(file_path)
    elif data_type == 'multi_param':
        result = process_multi_param_data(file_path)
    elif data_type == 'moisture':
        result = process_moisture_data(file_path)
    else:
        result = {
            'error': 'Unsupported data type',
            'moisture_content': 0,
            'nutrient_levels': {},
            'organic_matter': 0,
            'ph_level': 0,
            'soil_health_score': 0
        }
    
    # Handle visualizations from image processing
    if 'visualization' in result and result['visualization'] is not None:
        # Store visualization in the result summary for display
        result['summary'] = f"<img src='data:image/jpeg;base64,{result['visualization']}' class='img-fluid analysis-visualization' />\n\n{result['summary']}"
    
    # Create analysis result record
    analysis_result = SoilAnalysisResult.objects.create(
        soil_data=soil_data,
        moisture_content=result.get('moisture_content', 0),
        nutrient_levels=result.get('nutrient_levels', {}),
        organic_matter=result.get('organic_matter', 0),
        ph_level=result.get('ph_level', 0),
        soil_health_score=result.get('soil_health_score', 0),
        result_summary=result.get('summary', 'Analysis completed'),
        recommendations=result.get('recommendations', 'No specific recommendations available')
    )
    
    return analysis_result

def process_spectrometer_data(file_path):
    """Process optical spectrometer data file"""
    try:
        # Determine file type based on extension
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.csv', '.txt']:
            # Read CSV or TXT file
            data = pd.read_csv(file_path)
        elif ext in ['.json']:
            # Read JSON file
            with open(file_path, 'r') as f:
                data = pd.DataFrame(json.load(f))
        else:
            # Default to CSV with different delimiters
            try:
                data = pd.read_csv(file_path, delimiter=',')
            except:
                try:
                    data = pd.read_csv(file_path, delimiter='\t')
                except:
                    data = pd.read_csv(file_path, delimiter=';')
        
        # Extract wavelengths and absorbance/reflectance values
        wavelengths = data.iloc[:, 0].values if data.shape[1] > 1 else np.arange(data.shape[0])
        intensity = data.iloc[:, 1].values if data.shape[1] > 1 else data.iloc[:, 0].values
        
        # Process spectral data
        organic_matter = estimate_organic_matter(wavelengths, intensity)
        nutrients = estimate_nutrients_from_spectrum(wavelengths, intensity)
        moisture = estimate_moisture_from_spectrum(wavelengths, intensity)
        
        # Estimate pH from spectral data (simplified)
        # In a real system, this would use more sophisticated algorithms
        ph = 6.0 + 2.0 * (np.mean(intensity) - 0.5)  # Simplified placeholder
        ph = max(4.0, min(9.0, ph))  # Constrain to typical soil pH range
        
        # Calculate soil health score
        soil_health_score = calculate_soil_health_score(organic_matter, nutrients, moisture, ph)
        
        # Get text description of the soil for AI analysis
        soil_description = f"""
        Soil analysis results:
        - Organic matter: {organic_matter:.1f}%
        - pH level: {ph:.1f}
        - Moisture content: {moisture:.1f}%
        - Soil health score: {soil_health_score:.1f}/100
        - Nutrients: {', '.join([f"{k}: {v:.1f}" for k, v in nutrients.items()])}
        """
        
        # Get AI recommendations
        ai_analysis = analyze_text_with_ai(soil_description, 'soil_recommendations')
        
        return {
            'organic_matter': organic_matter,
            'nutrient_levels': nutrients,
            'moisture_content': moisture,
            'ph_level': ph,
            'soil_health_score': soil_health_score,
            'summary': ai_analysis.get('summary', 'Soil analysis completed'),
            'recommendations': '\n'.join(ai_analysis.get('recommendations', ['No specific recommendations']))
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'organic_matter': 0,
            'nutrient_levels': {'error': str(e)},
            'moisture_content': 0,
            'ph_level': 0,
            'soil_health_score': 0,
            'summary': f'Error analyzing spectrometer data: {str(e)}',
            'recommendations': 'Please check the data format and try again.'
        }

def process_multi_param_data(file_path):
    """Process multi-parameter soil sensor data file"""
    try:
        # Read data file
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = pd.read_csv(file_path).to_dict('records')[0]  # Assume first row
        
        # Extract parameters from data
        # In a real system, this would handle different file formats and structures
        organic_matter = data.get('organic_matter', 0)
        moisture = data.get('moisture', 0)
        ph = data.get('ph', 7.0)
        
        # Extract nutrients 
        nutrients = {}
        potential_nutrients = ['N', 'P', 'K', 'Ca', 'Mg', 'S', 'Fe', 'Mn', 'Zn', 'Cu', 'B', 'Mo', 'Cl']
        for nutrient in potential_nutrients:
            if nutrient in data:
                nutrients[nutrient] = data[nutrient]
        
        # If no nutrients were found in the expected format, try some other common keys
        if not nutrients:
            if 'nutrients' in data and isinstance(data['nutrients'], dict):
                nutrients = data['nutrients']
            else:
                # Look for keys containing 'nutrient'
                for key in data:
                    if 'nutri' in key.lower():
                        nutrients[key] = data[key]
        
        # Calculate soil health score
        soil_health_score = calculate_soil_health_score(organic_matter, nutrients, moisture, ph)
        
        # Get text description for AI analysis
        soil_description = f"""
        Soil analysis results:
        - Organic matter: {organic_matter:.1f}%
        - pH level: {ph:.1f}
        - Moisture content: {moisture:.1f}%
        - Soil health score: {soil_health_score:.1f}/100
        - Nutrients: {', '.join([f"{k}: {v}" for k, v in nutrients.items()])}
        """
        
        # Get AI recommendations
        ai_analysis = analyze_text_with_ai(soil_description, 'soil_recommendations')
        
        return {
            'organic_matter': organic_matter,
            'nutrient_levels': nutrients,
            'moisture_content': moisture,
            'ph_level': ph,
            'soil_health_score': soil_health_score,
            'summary': ai_analysis.get('summary', 'Soil analysis completed'),
            'recommendations': '\n'.join(ai_analysis.get('recommendations', ['No specific recommendations']))
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'organic_matter': 0,
            'nutrient_levels': {'error': str(e)},
            'moisture_content': 0,
            'ph_level': 0,
            'soil_health_score': 0,
            'summary': f'Error analyzing multi-parameter data: {str(e)}',
            'recommendations': 'Please check the data format and try again.'
        }

def process_moisture_data(file_path):
    """Process capacitive soil moisture sensor data file"""
    try:
        # Read data file
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Extract moisture values
            if isinstance(data, list):
                # If it's a time series, take the average
                moisture_values = [entry.get('moisture', 0) for entry in data if 'moisture' in entry]
                moisture = sum(moisture_values) / len(moisture_values) if moisture_values else 0
            else:
                # Single reading
                moisture = data.get('moisture', 0)
        else:
            # CSV or text file
            data = pd.read_csv(file_path)
            if 'moisture' in data.columns:
                moisture = data['moisture'].mean()
            else:
                # Assume first column is moisture
                moisture = data.iloc[:, 0].mean()
        
        # Dummy values for other parameters since this is just a moisture sensor
        organic_matter = 0  # Not measured by moisture sensor
        ph = 0  # Not measured by moisture sensor
        nutrients = {}  # Not measured by moisture sensor
        
        # Calculate a simplified soil health score based primarily on moisture
        soil_health_score = 50  # Base score
        
        # Adjust based on moisture (optimal around 20-45%)
        if 20 <= moisture <= 45:
            soil_health_score += 30
        elif 10 <= moisture < 20 or 45 < moisture <= 60:
            soil_health_score += 15
        
        # Get text description for AI analysis
        soil_description = f"""
        Soil moisture analysis results:
        - Moisture content: {moisture:.1f}%
        - No other soil parameters measured with this sensor type
        """
        
        # Get AI recommendations
        ai_analysis = analyze_text_with_ai(soil_description, 'soil_recommendations')
        
        return {
            'organic_matter': organic_matter,
            'nutrient_levels': nutrients,
            'moisture_content': moisture,
            'ph_level': ph,
            'soil_health_score': soil_health_score,
            'summary': ai_analysis.get('summary', 'Moisture analysis completed'),
            'recommendations': '\n'.join(ai_analysis.get('recommendations', ['No specific recommendations']))
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'organic_matter': 0,
            'nutrient_levels': {'error': str(e)},
            'moisture_content': 0,
            'ph_level': 0,
            'soil_health_score': 0,
            'summary': f'Error analyzing moisture data: {str(e)}',
            'recommendations': 'Please check the data format and try again.'
        }

def process_leaf_image(file_path):
    """
    Process leaf image for plant health analysis
    
    Args:
        file_path (str): Path to the leaf image file
        
    Returns:
        dict: Analysis results including health status and recommendations
    """
    try:
        # Use the image processor to analyze the leaf image
        image_analysis = analyze_leaf_image(file_path)
        
        # Get visualization image
        visualization = get_image_visualization(file_path, 'leaf')
        
        # Extract key data from the analysis
        health_status = image_analysis.get('health_status', 'unknown')
        confidence = image_analysis.get('confidence', 0.0)
        description = image_analysis.get('description', 'No description available')
        recommendations = image_analysis.get('recommendations', 'No specific recommendations')
        
        # Infer soil parameters based on plant health
        if health_status == 'healthy':
            # Healthy plants typically indicate good soil conditions
            organic_matter = np.random.uniform(3.0, 6.0)  # Good range
            ph_level = np.random.uniform(6.0, 7.0)  # Optimal pH
            moisture_content = np.random.uniform(20.0, 30.0)  # Good moisture
            
            # Good nutrient levels for healthy plants
            nutrient_levels = {
                'N': np.random.uniform(80, 140),
                'P': np.random.uniform(30, 60),
                'K': np.random.uniform(150, 250),
                'Ca': np.random.uniform(1000, 1400),
                'Mg': np.random.uniform(180, 280),
                'S': np.random.uniform(90, 140)
            }
            
            soil_health_score = np.random.uniform(75, 95)
            
        elif health_status == 'leaf_rust':
            # Leaf rust often indicates nutrient imbalances
            organic_matter = np.random.uniform(2.0, 4.0)
            ph_level = np.random.uniform(5.0, 6.0)  # Slightly acidic
            moisture_content = np.random.uniform(30.0, 40.0)  # High moisture (promotes rust)
            
            nutrient_levels = {
                'N': np.random.uniform(140, 200),  # High nitrogen can promote disease
                'P': np.random.uniform(10, 30),  # Low phosphorus
                'K': np.random.uniform(100, 150),  # Lower potassium
                'Ca': np.random.uniform(800, 1000),
                'Mg': np.random.uniform(150, 180),
                'S': np.random.uniform(80, 100)
            }
            
            soil_health_score = np.random.uniform(50, 70)
            
        elif health_status == 'bacterial_blight':
            # Bacterial blight can be associated with certain soil conditions
            organic_matter = np.random.uniform(1.5, 3.0)
            ph_level = np.random.uniform(7.0, 8.0)  # Alkaline conditions
            moisture_content = np.random.uniform(35.0, 45.0)  # Excessive moisture
            
            nutrient_levels = {
                'N': np.random.uniform(150, 210),  # High nitrogen
                'P': np.random.uniform(20, 40),
                'K': np.random.uniform(80, 120),  # Low potassium
                'Ca': np.random.uniform(700, 900),
                'Mg': np.random.uniform(140, 170),
                'S': np.random.uniform(70, 90)
            }
            
            soil_health_score = np.random.uniform(40, 60)
            
        elif health_status == 'powdery_mildew':
            # Powdery mildew associated with different conditions
            organic_matter = np.random.uniform(2.0, 4.0)
            ph_level = np.random.uniform(6.5, 7.5)
            moisture_content = np.random.uniform(15.0, 25.0)  # Drier conditions
            
            nutrient_levels = {
                'N': np.random.uniform(160, 220),  # High nitrogen
                'P': np.random.uniform(25, 45),
                'K': np.random.uniform(110, 160),
                'Ca': np.random.uniform(800, 1100),
                'Mg': np.random.uniform(150, 190),
                'S': np.random.uniform(75, 95)
            }
            
            soil_health_score = np.random.uniform(55, 75)
            
        else:
            # Default case for unknown or other conditions
            organic_matter = np.random.uniform(2.0, 5.0)
            ph_level = np.random.uniform(5.5, 7.5)
            moisture_content = np.random.uniform(15.0, 35.0)
            
            nutrient_levels = {
                'N': np.random.uniform(50, 150),
                'P': np.random.uniform(20, 70),
                'K': np.random.uniform(100, 300),
                'Ca': np.random.uniform(800, 1500),
                'Mg': np.random.uniform(150, 300),
                'S': np.random.uniform(80, 150)
            }
            
            soil_health_score = np.random.uniform(50, 80)
        
        # Create a comprehensive analysis summary
        summary = f"Leaf Analysis Results:\n"
        summary += f"- Health Status: {health_status}\n"
        summary += f"- Confidence: {confidence:.2f}\n"
        summary += f"- Description: {description}\n\n"
        
        summary += f"Estimated Soil Parameters Based on Plant Health:\n"
        summary += f"- Organic Matter: {organic_matter:.1f}%\n"
        summary += f"- pH Level: {ph_level:.1f}\n"
        summary += f"- Moisture Content: {moisture_content:.1f}%\n"
        summary += f"- Soil Health Score: {soil_health_score:.1f}/100\n"
        summary += "- Estimated Nutrient Levels:\n"
        
        for nutrient, value in nutrient_levels.items():
            summary += f"  * {nutrient}: {value:.1f} mg/kg\n"
        
        # Combine the plant-specific recommendations with soil recommendations
        soil_recommendations = f"\nRecommendations for Soil Management:\n"
        
        if health_status == 'healthy':
            soil_recommendations += "- Your current soil conditions appear favorable. Maintain your current practices.\n"
            soil_recommendations += "- Continue regular monitoring of soil moisture and nutrient levels.\n"
            soil_recommendations += "- Consider crop rotation to prevent nutrient depletion.\n"
            
        elif health_status == 'leaf_rust':
            soil_recommendations += "- Address potential phosphorus deficiency with appropriate fertilizers.\n"
            soil_recommendations += "- Reduce nitrogen applications which may be promoting disease development.\n"
            soil_recommendations += "- Improve drainage to reduce moisture levels in the soil.\n"
            soil_recommendations += "- Consider pH adjustment to bring soil into the optimal range (6.0-7.0).\n"
            
        elif health_status == 'bacterial_blight':
            soil_recommendations += "- Improve soil drainage to reduce excessive moisture.\n"
            soil_recommendations += "- Adjust pH downward to a more neutral range using sulfur amendments.\n"
            soil_recommendations += "- Increase potassium levels which may help improve plant resistance.\n"
            soil_recommendations += "- Balance nitrogen levels as excess can promote disease.\n"
            
        elif health_status == 'powdery_mildew':
            soil_recommendations += "- Reduce nitrogen applications which may promote susceptibility.\n"
            soil_recommendations += "- Ensure adequate spacing between plants to improve air circulation.\n"
            soil_recommendations += "- Maintain consistent watering practices - avoid drought stress.\n"
            soil_recommendations += "- Consider increasing silicon content in soil which may improve resistance.\n"
            
        else:
            soil_recommendations += "- Conduct a complete soil test to determine specific nutrient needs.\n"
            soil_recommendations += "- Maintain soil moisture at appropriate levels for your crop.\n"
            soil_recommendations += "- Monitor pH and adjust if needed to the optimal range for your crop.\n"
        
        # Combine plant recommendations with soil recommendations
        combined_recommendations = f"{recommendations}\n{soil_recommendations}"
        
        return {
            'health_status': health_status,
            'confidence': confidence,
            'visualization': visualization,
            'organic_matter': organic_matter,
            'nutrient_levels': nutrient_levels,
            'moisture_content': moisture_content,
            'ph_level': ph_level,
            'soil_health_score': soil_health_score,
            'summary': summary,
            'recommendations': combined_recommendations
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'health_status': 'error',
            'organic_matter': 0,
            'nutrient_levels': {'error': str(e)},
            'moisture_content': 0,
            'ph_level': 0,
            'soil_health_score': 0,
            'summary': f'Error analyzing leaf image: {str(e)}',
            'recommendations': 'Please check that the image is a clear photo of plant leaves and try again.'
        }

# Utility functions for soil data interpretation
def estimate_organic_matter(wavelengths, intensity):
    """Estimate organic matter from spectral data (simplified)"""
    # In a real system, this would use specific absorption bands for organic matter
    # This is a simplified approximation for demonstration
    
    # Focus on certain wavelength regions known to correlate with organic matter
    # For example, around 1100-1300nm and 1600-1800nm
    region1_indices = np.where((wavelengths >= 1100) & (wavelengths <= 1300))[0]
    region2_indices = np.where((wavelengths >= 1600) & (wavelengths <= 1800))[0]
    
    if len(region1_indices) > 0 and len(region2_indices) > 0:
        # Calculate mean reflectance in these regions
        mean_region1 = np.mean(intensity[region1_indices]) if len(region1_indices) > 0 else 0
        mean_region2 = np.mean(intensity[region2_indices]) if len(region2_indices) > 0 else 0
        
        # Simplified model: higher absorption (lower reflectance) in these bands
        # correlates with higher organic matter
        organic_matter = 20.0 - 25.0 * (mean_region1 + mean_region2) / 2.0
    else:
        # If we can't identify the specific wavelength regions,
        # use a more general approach based on overall reflectance
        mean_reflectance = np.mean(intensity)
        organic_matter = 15.0 - 20.0 * mean_reflectance
    
    # Ensure result is in a reasonable range for soil organic matter (0-15%)
    return max(0.0, min(15.0, organic_matter))

def estimate_nutrients_from_spectrum(wavelengths, intensity):
    """Estimate nutrient levels from spectral data (simplified)"""
    # In a real system, this would use machine learning models
    # trained on large datasets of soil spectra with known nutrient levels
    # This is a simplified approximation for demonstration
    
    nutrients = {}
    
    # Simplified correlations for demonstration purposes
    # N (Nitrogen) - correlated with organic matter, so similar wavelengths
    region_n = np.where((wavelengths >= 1900) & (wavelengths <= 2100))[0]
    if len(region_n) > 0:
        mean_n = np.mean(intensity[region_n])
        nutrients['N'] = max(0, min(100, 80 - 100 * mean_n))
    else:
        nutrients['N'] = 40 + 20 * np.random.random()
    
    # P (Phosphorus)
    region_p = np.where((wavelengths >= 2200) & (wavelengths <= 2300))[0]
    if len(region_p) > 0:
        mean_p = np.mean(intensity[region_p])
        nutrients['P'] = max(0, min(100, 70 - 90 * mean_p))
    else:
        nutrients['P'] = 30 + 20 * np.random.random()
    
    # K (Potassium)
    region_k = np.where((wavelengths >= 2400) & (wavelengths <= 2500))[0]
    if len(region_k) > 0:
        mean_k = np.mean(intensity[region_k])
        nutrients['K'] = max(0, min(100, 60 - 75 * mean_k))
    else:
        nutrients['K'] = 35 + 25 * np.random.random()
    
    # Add some additional common nutrients with simulated values
    nutrients['Ca'] = 25 + 15 * np.random.random()
    nutrients['Mg'] = 20 + 10 * np.random.random()
    nutrients['S'] = 15 + 10 * np.random.random()
    
    # Micronutrients
    nutrients['Fe'] = 5 + 5 * np.random.random()
    nutrients['Zn'] = 2 + 3 * np.random.random()
    nutrients['Mn'] = 3 + 4 * np.random.random()
    
    return nutrients

def estimate_moisture_from_spectrum(wavelengths, intensity):
    """Estimate moisture content from spectral data (simplified)"""
    # In a real system, this would focus on water absorption bands
    # particularly around 1400nm and 1900nm
    # This is a simplified approximation for demonstration
    
    # Water absorption bands
    region1_indices = np.where((wavelengths >= 1350) & (wavelengths <= 1450))[0]
    region2_indices = np.where((wavelengths >= 1850) & (wavelengths <= 1950))[0]
    
    if len(region1_indices) > 0 and len(region2_indices) > 0:
        # Calculate mean reflectance in these regions
        mean_region1 = np.mean(intensity[region1_indices])
        mean_region2 = np.mean(intensity[region2_indices])
        
        # Simplified model: higher absorption (lower reflectance) in these bands
        # correlates with higher moisture
        moisture = 50.0 - 60.0 * (mean_region1 + mean_region2) / 2.0
    else:
        # If we can't identify the specific wavelength regions,
        # use a more general approach
        std_reflectance = np.std(intensity)
        moisture = 20.0 + 40.0 * std_reflectance
    
    # Ensure result is in a reasonable range for soil moisture (5-50%)
    return max(5.0, min(50.0, moisture))

def calculate_soil_health_score(organic_matter, nutrient_levels, moisture, ph):
    """Calculate an overall soil health score based on multiple parameters"""
    # Start with a base score
    score = 50.0
    
    # Adjust for organic matter (optimal range 3-8%)
    if 3 <= organic_matter <= 8:
        score += 10
    elif 1 <= organic_matter < 3 or 8 < organic_matter <= 12:
        score += 5
    
    # Adjust for pH (optimal range 6.0-7.0)
    if 6.0 <= ph <= 7.0:
        score += 10
    elif 5.5 <= ph < 6.0 or 7.0 < ph <= 7.5:
        score += 5
    
    # Adjust for moisture (optimal range 20-35%)
    if 20 <= moisture <= 35:
        score += 10
    elif 15 <= moisture < 20 or 35 < moisture <= 45:
        score += 5
    
    # Adjust for nutrient balance
    if isinstance(nutrient_levels, dict):
        # Check if major nutrients (N, P, K) are present and in good proportions
        n_value = nutrient_levels.get('N', 0)
        p_value = nutrient_levels.get('P', 0)
        k_value = nutrient_levels.get('K', 0)
        
        # Get the average of available macronutrients
        macro_avg = 0
        macro_count = 0
        for nutrient in ['N', 'P', 'K', 'Ca', 'Mg', 'S']:
            if nutrient in nutrient_levels:
                macro_avg += nutrient_levels[nutrient]
                macro_count += 1
        
        if macro_count > 0:
            macro_avg /= macro_count
            
            # Good average macronutrient level
            if 30 <= macro_avg <= 70:
                score += 10
            elif 20 <= macro_avg < 30 or 70 < macro_avg <= 80:
                score += 5
        
        # Check micronutrients
        micro_count = 0
        for nutrient in ['Fe', 'Mn', 'Zn', 'Cu', 'B', 'Mo']:
            if nutrient in nutrient_levels and nutrient_levels[nutrient] > 1:
                micro_count += 1
        
        # Bonus for having good micronutrient levels
        if micro_count >= 3:
            score += 10
        elif micro_count >= 1:
            score += 5
    
    # Ensure score is between 0 and 100
    return max(0.0, min(100.0, score))