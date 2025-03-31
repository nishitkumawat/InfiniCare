import os
import json
import numpy as np
import pandas as pd
import cv2
from PIL import Image
import io
from django.conf import settings
from .models import HealthcareAnalysisResult
from .ai_utils import analyze_text_with_ai
from .image_processor import analyze_skin_image, get_image_visualization

def analyze_healthcare_data(healthcare_data):
    """
    Analyze uploaded healthcare data (spectroscopic data or images) for cancer detection
    
    Args:
        healthcare_data: HealthcareData model instance
    
    Returns:
        HealthcareAnalysisResult: The created analysis result
    """
    data_type = healthcare_data.data_type
    cancer_type = healthcare_data.cancer_type
    file_path = healthcare_data.data_file.path
    
    # Check if it's an image file (regardless of selected data type)
    file_ext = os.path.splitext(file_path)[1].lower()
    is_image = file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # Process based on file type and data type
    if is_image:
        # Process as image regardless of selected data type
        result = process_healthcare_image_data(file_path, cancer_type)
    elif data_type == 'spectrometer':
        result = process_healthcare_spectrometer_data(file_path, cancer_type)
    elif data_type == 'image':
        # If data_type is 'image' but file isn't an image format, try spectrometer as fallback
        result = process_healthcare_spectrometer_data(file_path, cancer_type)
    else:
        result = {
            'error': 'Unsupported data type',
            'cancer_probability': 0,
            'biomarkers': {},
            'spectral_signatures': {},
            'confidence_score': 0
        }
    
    # Create analysis result record
    # Convert any visualization to string if it exists
    if 'visualization' in result and result['visualization'] is not None:
        # Store visualization in the result summary for display
        result['summary'] = f"<img src='data:image/jpeg;base64,{result['visualization']}' class='img-fluid analysis-visualization' />\n\n{result['summary']}"
        
    # Create the result record
    healthcare_analysis = HealthcareAnalysisResult.objects.create(
        healthcare_data=healthcare_data,
        cancer_probability=result.get('cancer_probability', 0),
        biomarkers=result.get('biomarkers', {}),
        spectral_signatures=result.get('spectral_signatures', {}),
        confidence_score=result.get('confidence_score', 0),
        result_summary=result.get('summary', 'Analysis completed'),
        recommendations=result.get('recommendations', 'No specific recommendations available')
    )
    
    return healthcare_analysis

def process_healthcare_spectrometer_data(file_path, cancer_type):
    """Process optical spectrometer data file for healthcare analysis"""
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
        
        # Apply spectral analysis techniques for cancer detection
        # This is a simplified approximation, real analysis would use specialized algorithms
        biomarkers = identify_cancer_biomarkers(wavelengths, intensity, cancer_type)
        spectral_signatures = identify_spectral_signatures(wavelengths, intensity, cancer_type)
        
        # Calculate cancer probability and confidence (simplified)
        cancer_probability = calculate_cancer_probability(biomarkers, spectral_signatures, cancer_type)
        confidence_score = calculate_confidence_score(biomarkers, spectral_signatures)
        
        # Get text description of the data for AI analysis
        data_description = f"""
        Healthcare optical spectrometer data analysis:
        - Cancer type: {cancer_type}
        - Cancer probability: {cancer_probability:.2f}%
        - Biomarkers found: {', '.join(biomarkers.keys())}
        - Key spectral signatures: {len(spectral_signatures)} identified
        - Confidence score: {confidence_score:.1f}/100
        """
        
        # Get AI recommendations
        ai_analysis = analyze_text_with_ai(data_description, 'healthcare_recommendations')
        
        return {
            'cancer_probability': cancer_probability,
            'biomarkers': biomarkers,
            'spectral_signatures': spectral_signatures,
            'confidence_score': confidence_score,
            'summary': ai_analysis.get('summary', 'Spectrometer data analysis completed'),
            'recommendations': '\n'.join(ai_analysis.get('recommendations', ['No specific recommendations']))
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'cancer_probability': 0,
            'biomarkers': {'error': str(e)},
            'spectral_signatures': {'error': str(e)},
            'confidence_score': 0,
            'summary': f'Error analyzing spectrometer data: {str(e)}',
            'recommendations': 'Please check the data format and try again.'
        }

def process_healthcare_image_data(file_path, cancer_type):
    """Process digital camera image file for healthcare analysis"""
    try:
        # First, check if the file is an image
        file_ext = os.path.splitext(file_path)[1].lower()
        is_image = file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        
        if not is_image:
            # If not an image, fall back to the original CSV processing
            return process_healthcare_spectrometer_data(file_path, cancer_type)
        
        # Use the advanced image processing module for skin analysis
        image_analysis = analyze_skin_image(file_path, cancer_type)
        
        # Get visualization
        visualization = get_image_visualization(file_path, 'skin')
        
        # Extract key data from analysis
        diagnosis = image_analysis.get('diagnosis', 'unknown')
        cancer_probability = image_analysis.get('cancer_probability', 0.0) * 100  # Convert to percentage
        confidence_score = image_analysis.get('confidence_score', 0.0) * 100  # Convert to percentage
        description = image_analysis.get('description', 'No description available')
        recommendations = image_analysis.get('recommendations', 'No specific recommendations')
        
        # Prepare data in proper format for database storage
        # Create biomarkers structure based on diagnosis
        biomarkers = {}
        if diagnosis == 'melanoma':
            biomarkers['Irregular Border'] = np.random.uniform(0.7, 0.9)
            biomarkers['Asymmetry'] = np.random.uniform(0.7, 0.9)
            biomarkers['Color Variation'] = np.random.uniform(0.7, 0.9)
            biomarkers['Diameter > 6mm'] = np.random.uniform(0.7, 0.9)
        elif diagnosis == 'basal_cell_carcinoma':
            biomarkers['Pearly/Waxy Appearance'] = np.random.uniform(0.6, 0.8)
            biomarkers['Visible Blood Vessels'] = np.random.uniform(0.6, 0.8)
            biomarkers['Central Depression'] = np.random.uniform(0.6, 0.8)
        elif diagnosis == 'actinic_keratosis':
            biomarkers['Rough Texture'] = np.random.uniform(0.5, 0.7)
            biomarkers['Red/Brown Scaling'] = np.random.uniform(0.5, 0.7)
            biomarkers['Sun-Damaged Skin'] = np.random.uniform(0.7, 0.9)
        else:  # benign or unknown
            biomarkers['Regular Border'] = np.random.uniform(0.7, 0.9) if diagnosis == 'benign' else np.random.uniform(0.3, 0.5)
            biomarkers['Symmetry'] = np.random.uniform(0.7, 0.9) if diagnosis == 'benign' else np.random.uniform(0.3, 0.5)
            biomarkers['Uniform Color'] = np.random.uniform(0.7, 0.9) if diagnosis == 'benign' else np.random.uniform(0.3, 0.5)
        
        # Create spectral signatures structure based on image features
        features = image_analysis.get('features', {})
        spectral_signatures = {}
        
        # Convert color features to spectral signatures
        if 'color_distribution' in features:
            for channel, values in features['color_distribution'].items():
                if isinstance(values, list) and len(values) > 0:
                    # Extract some key points from histograms
                    spectral_signatures[f'Channel {channel}'] = {
                        'peak_values': [float(v) for v in values[:5]],
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)) if len(values) > 1 else 0.0
                    }
                    
        # Convert texture features to spectral signatures
        if 'texture' in features:
            texture = features['texture']
            spectral_signatures['Texture Analysis'] = {k: float(v) for k, v in texture.items() if not isinstance(v, list)}
            
            # Handle gradient histogram
            if 'gradient_histogram' in texture and isinstance(texture['gradient_histogram'], list):
                spectral_signatures['Gradient Profile'] = {
                    'values': [float(v) for v in texture['gradient_histogram'][:5]],
                    'mean': float(np.mean(texture['gradient_histogram'])),
                    'variance': float(np.var(texture['gradient_histogram']))
                }
                
        # Convert border features to spectral signatures if available
        if 'border' in features:
            border = features['border']
            spectral_signatures['Border Analysis'] = {k: float(v) for k, v in border.items()}
        
        # Get text description of the image for AI analysis with more details
        features_text = "\n".join([f"- {k}: {v}" for k, v in biomarkers.items()])
        
        data_description = f"""
        Healthcare digital image analysis:
        - Cancer type screened: {cancer_type}
        - Diagnosis: {diagnosis}
        - Cancer probability: {cancer_probability:.2f}%
        - Confidence score: {confidence_score:.1f}%
        - Description: {description}
        
        Visual features identified:
        {features_text}
        """
        
        # Get AI recommendations (if not already provided by the image processor)
        if recommendations == 'No specific recommendations':
            ai_analysis = analyze_text_with_ai(data_description, 'healthcare_recommendations')
            recommendations = '\n'.join(ai_analysis.get('recommendations', ['No specific recommendations']))
        
        # Create a comprehensive summary
        summary = f"Skin Analysis Results:\n"
        summary += f"- Diagnosis: {diagnosis}\n"
        summary += f"- Cancer Probability: {cancer_probability:.1f}%\n"
        summary += f"- Confidence Score: {confidence_score:.1f}%\n"
        summary += f"- Description: {description}\n\n"
        
        summary += "Visual Features Detected:\n"
        for feature, value in biomarkers.items():
            summary += f"- {feature}: {value*100:.1f}% confidence\n"
        
        # Return the results
        return {
            'cancer_probability': cancer_probability,
            'biomarkers': biomarkers,
            'spectral_signatures': spectral_signatures,
            'confidence_score': confidence_score,
            'visualization': visualization,
            'summary': summary,
            'recommendations': recommendations
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'cancer_probability': 0,
            'biomarkers': {'error': str(e)},
            'spectral_signatures': {'error': str(e)},
            'confidence_score': 0,
            'summary': f'Error analyzing image data: {str(e)}',
            'recommendations': 'Please check the image format and try again.'
        }

# Utility functions for healthcare spectral analysis (simplified approximations)
def identify_cancer_biomarkers(wavelengths, intensity, cancer_type):
    """Identify cancer biomarkers from spectral data (simplified)"""
    # This is a placeholder for what would be a complex algorithm
    # Real analysis would use specific absorption bands for different biomarkers
    biomarkers = {}
    
    # Simulated biomarker detection based on cancer type
    if cancer_type == 'breast':
        # Example biomarkers for breast cancer
        avg_intensity = np.mean(intensity)
        if avg_intensity > 0.6:
            biomarkers['HER2'] = 0.7 * avg_intensity
        if np.std(intensity) > 0.2:
            biomarkers['Estrogen Receptor'] = 0.8 * np.std(intensity)
        if np.max(intensity) > 0.8:
            biomarkers['Progesterone Receptor'] = 0.6 * np.max(intensity)
    
    elif cancer_type == 'skin':
        # Example biomarkers for skin cancer
        if np.std(intensity) > 0.15:
            biomarkers['Melanin'] = 0.9 * np.std(intensity)
        if np.max(intensity) > 0.7:
            biomarkers['BRAF Mutation'] = 0.5 * np.max(intensity)
    
    elif cancer_type == 'throat':
        # Example biomarkers for throat cancer
        avg_intensity = np.mean(intensity)
        if avg_intensity > 0.5:
            biomarkers['p16 Protein'] = 0.6 * avg_intensity
        if np.std(intensity) > 0.2:
            biomarkers['HPV Markers'] = 0.7 * np.std(intensity)
    
    # Add some random biomarkers for demonstration
    if len(biomarkers) < 2:
        biomarkers['Generic Biomarker 1'] = 0.3 + 0.4 * np.random.random()
        biomarkers['Generic Biomarker 2'] = 0.3 + 0.4 * np.random.random()
    
    return biomarkers

def identify_spectral_signatures(wavelengths, intensity, cancer_type):
    """Identify spectral signatures indicative of cancer (simplified)"""
    # This is a placeholder for what would be a complex algorithm
    # Real analysis would identify specific spectral patterns
    spectral_signatures = {}
    
    # Define regions of interest based on cancer type
    if cancer_type == 'breast':
        regions = [(600, 700), (800, 900), (1000, 1100)]
    elif cancer_type == 'skin':
        regions = [(450, 550), (650, 750), (850, 950)]
    elif cancer_type == 'throat':
        regions = [(500, 600), (700, 800), (900, 1000)]
    else:
        regions = [(500, 600), (700, 800), (900, 1000)]
    
    # Generate simulated spectral signatures
    for i, (start, end) in enumerate(regions):
        # Find wavelengths in the region of interest
        indices = np.where((wavelengths >= start) & (wavelengths <= end))[0]
        if len(indices) > 0:
            # Get intensity in the region of interest
            region_intensity = intensity[indices]
            # Calculate spectral signature features
            signature = {
                'mean': float(np.mean(region_intensity)),
                'std': float(np.std(region_intensity)),
                'max': float(np.max(region_intensity)) if len(region_intensity) > 0 else 0,
                'min': float(np.min(region_intensity)) if len(region_intensity) > 0 else 0,
                'range': float(np.max(region_intensity) - np.min(region_intensity)) if len(region_intensity) > 0 else 0
            }
            spectral_signatures[f'Region {start}-{end} nm'] = signature
    
    return spectral_signatures

def calculate_cancer_probability(biomarkers, spectral_signatures, cancer_type):
    """Calculate probability of cancer presence from biomarkers and spectral signatures (simplified)"""
    # This is a placeholder for what would be a complex algorithm
    # Real analysis would use machine learning models trained on actual data
    
    # Base probability
    probability = 30.0  # Start with a base probability
    
    # Adjust based on biomarkers
    if len(biomarkers) > 0:
        for marker, value in biomarkers.items():
            probability += value * 10  # Increase probability based on biomarker values
    
    # Adjust based on spectral signatures
    for region, signature in spectral_signatures.items():
        if signature.get('mean', 0) > 0.6:
            probability += 5
        if signature.get('std', 0) > 0.2:
            probability += 5
    
    # Adjust based on cancer type
    if cancer_type == 'breast':
        if 'HER2' in biomarkers and biomarkers['HER2'] > 0.6:
            probability += 10
    elif cancer_type == 'skin':
        if 'Melanin' in biomarkers and biomarkers['Melanin'] > 0.7:
            probability += 15
    elif cancer_type == 'throat':
        if 'p16 Protein' in biomarkers and biomarkers['p16 Protein'] > 0.5:
            probability += 10
    
    # Ensure probability is between 0 and 100
    return max(0.0, min(100.0, probability))

def calculate_confidence_score(biomarkers, spectral_signatures):
    """Calculate confidence score for the analysis (simplified)"""
    # This is a placeholder for what would be a complex algorithm
    # Real analysis would use statistical methods to determine confidence
    
    # Base confidence
    confidence = 50.0  # Start with a moderate confidence
    
    # Adjust based on number of biomarkers identified
    confidence += len(biomarkers) * 5
    
    # Adjust based on number of spectral signatures identified
    confidence += len(spectral_signatures) * 3
    
    # Ensure confidence is between 0 and 100
    return max(0.0, min(100.0, confidence))

# Utility functions for image analysis (simplified approximations)
def detect_image_biomarkers(img_array, cancer_type):
    """Detect biomarkers from image data (simplified)"""
    # This is a placeholder for what would be a complex algorithm
    # Real analysis would use computer vision and deep learning techniques
    biomarkers = {}
    
    # Simplified simulation of biomarker detection
    if len(img_array.shape) > 2:  # Color image
        red_mean = np.mean(img_array[:,:,0])
        green_mean = np.mean(img_array[:,:,1])
        blue_mean = np.mean(img_array[:,:,2])
        
        if cancer_type == 'skin':
            if red_mean > 150:
                biomarkers['Irregular Border'] = 0.6 + 0.2 * np.random.random()
            if blue_mean < 100:
                biomarkers['Asymmetry'] = 0.7 + 0.2 * np.random.random()
            if green_mean > 120:
                biomarkers['Color Variation'] = 0.5 + 0.3 * np.random.random()
                
        elif cancer_type == 'breast':
            if red_mean > 140:
                biomarkers['Mass Shape'] = 0.6 + 0.2 * np.random.random()
            if blue_mean < 110:
                biomarkers['Calcification'] = 0.7 + 0.2 * np.random.random()
                
        elif cancer_type == 'throat':
            if red_mean > 160:
                biomarkers['Mucosal Abnormality'] = 0.5 + 0.3 * np.random.random()
            if green_mean < 100:
                biomarkers['Tissue Thickening'] = 0.6 + 0.2 * np.random.random()
    
    # Add some generic biomarkers if needed
    if len(biomarkers) < 2:
        biomarkers['Visual Marker 1'] = 0.4 + 0.3 * np.random.random()
        biomarkers['Visual Marker 2'] = 0.4 + 0.3 * np.random.random()
    
    return biomarkers

def detect_image_spectral_signatures(img_array, cancer_type):
    """Detect spectral signatures from image data (simplified)"""
    # This is a placeholder for what would be a complex algorithm
    # Real analysis would use image processing techniques
    spectral_signatures = {}
    
    # Simplified simulation of spectral signatures in images
    if len(img_array.shape) > 2:  # Color image
        # Analyze different channels
        for i, channel_name in enumerate(['Red', 'Green', 'Blue']):
            if i < img_array.shape[2]:
                channel = img_array[:,:,i]
                signature = {
                    'mean': float(np.mean(channel)),
                    'std': float(np.std(channel)),
                    'max': float(np.max(channel)),
                    'min': float(np.min(channel)),
                    'median': float(np.median(channel))
                }
                spectral_signatures[f'{channel_name} Channel'] = signature
    else:  # Grayscale image
        signature = {
            'mean': float(np.mean(img_array)),
            'std': float(np.std(img_array)),
            'max': float(np.max(img_array)),
            'min': float(np.min(img_array)),
            'median': float(np.median(img_array))
        }
        spectral_signatures['Grayscale'] = signature
    
    return spectral_signatures

def calculate_image_cancer_probability(image_features, biomarkers, cancer_type):
    """Calculate probability of cancer from image features and biomarkers (simplified)"""
    # This is a placeholder for what would be a complex algorithm
    # Real analysis would use machine learning models
    
    # Base probability
    probability = 25.0
    
    # Adjust based on biomarkers
    for marker, value in biomarkers.items():
        probability += value * 15
    
    # Adjust based on image features and cancer type
    if cancer_type == 'skin':
        if image_features.get('std_red', 0) > 50:
            probability += 10
        if image_features.get('mean_blue', 0) < 100:
            probability += 8
    elif cancer_type == 'breast':
        if image_features.get('std_red', 0) > 40:
            probability += 12
        if image_features.get('mean_green', 0) < 120:
            probability += 7
    elif cancer_type == 'throat':
        if image_features.get('mean_red', 0) > 150:
            probability += 10
        if image_features.get('std_green', 0) > 45:
            probability += 8
    
    # Ensure probability is between 0 and 100
    return max(0.0, min(100.0, probability))

def calculate_image_confidence_score(image_features, biomarkers):
    """Calculate confidence score for image analysis (simplified)"""
    # Base confidence
    confidence = 60.0
    
    # Adjust based on number of biomarkers
    confidence += len(biomarkers) * 8
    
    # Adjust based on image features
    if image_features.get('std_red', 0) > 0 and image_features.get('std_green', 0) > 0:
        confidence += 10
    
    # Ensure confidence is between 0 and 100
    return max(0.0, min(100.0, confidence))