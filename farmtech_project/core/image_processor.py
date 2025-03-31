"""
Image Processing Module for Reve Digital Platform

This module provides functions for analyzing images of plant leaves and human tissue/skin
to detect diseases and health conditions using computer vision and AI models.
"""

import os
import cv2
import numpy as np
import base64
import json
from io import BytesIO
from PIL import Image
import logging
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# Constants for disease detection
LEAF_DISEASES = {
    'bacterial_blight': {
        'description': 'Angular leaf spots with water-soaked margins, often becoming brown and necrotic.',
        'recommendations': 'Use disease-free seeds, crop rotation, and copper-based bactericides if severe.'
    },
    'leaf_rust': {
        'description': 'Orange to brown powdery pustules on leaf surfaces, typically on the undersides.',
        'recommendations': 'Apply fungicides early, plant resistant varieties, and ensure good air circulation.'
    },
    'powdery_mildew': {
        'description': 'White to gray powdery growth on leaf surfaces, often starting as small circular patches.',
        'recommendations': 'Increase plant spacing, apply sulfur-based fungicides, and avoid overhead irrigation.'
    },
    'healthy': {
        'description': 'No visible disease symptoms detected.',
        'recommendations': 'Continue regular monitoring and maintain good agricultural practices.'
    }
}

SKIN_DISEASES = {
    'melanoma': {
        'description': 'Irregular borders, multiple colors, and asymmetrical shape suggesting potential melanoma.',
        'recommendations': 'Immediate consultation with a dermatologist for biopsy and further evaluation.'
    },
    'basal_cell_carcinoma': {
        'description': 'Pearly or waxy bump, possibly with blue, brown, or black areas.',
        'recommendations': 'Dermatologist consultation for confirmation and treatment planning.'
    },
    'actinic_keratosis': {
        'description': 'Rough, scaly patch on skin that has been chronically exposed to the sun.',
        'recommendations': 'Dermatologist evaluation for potential pre-cancerous condition.'
    },
    'benign': {
        'description': 'Regular borders, uniform color, and symmetrical shape suggesting benign condition.',
        'recommendations': 'Routine monitoring during regular skin examinations.'
    }
}

def preprocess_image(image_path):
    """
    Preprocess an image for analysis
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        numpy.ndarray: Preprocessed image array
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to read image: {image_path}")
            return None
            
        # Resize for consistent processing
        img_resized = cv2.resize(img, (224, 224))
        
        # Convert to RGB (OpenCV uses BGR by default)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        return img_rgb
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

def analyze_leaf_image(image_path):
    """
    Analyze a leaf image to detect plant diseases
    
    Args:
        image_path (str): Path to the leaf image
        
    Returns:
        dict: Analysis results including disease detection
    """
    try:
        img = preprocess_image(image_path)
        if img is None:
            return {
                'error': 'Failed to process image',
                'health_status': 'unknown',
                'confidence': 0.0,
                'features': {}
            }
        
        # Extract features for analysis
        features = extract_leaf_features(img)
        
        # Simulate disease detection based on image features
        # In a real implementation, this would use a trained model
        health_status, confidence = detect_leaf_disease(features)
        
        # Generate result details
        if health_status in LEAF_DISEASES:
            description = LEAF_DISEASES[health_status]['description']
            recommendations = LEAF_DISEASES[health_status]['recommendations']
        else:
            description = "Analysis inconclusive."
            recommendations = "Please retake the image with better lighting and focus."
        
        return {
            'health_status': health_status,
            'confidence': confidence,
            'features': features,
            'description': description,
            'recommendations': recommendations
        }
    except Exception as e:
        logger.error(f"Error analyzing leaf image: {e}")
        return {
            'error': str(e),
            'health_status': 'error',
            'confidence': 0.0,
            'features': {}
        }

def analyze_skin_image(image_path, cancer_type):
    """
    Analyze a skin/tissue image to detect potential health issues
    
    Args:
        image_path (str): Path to the skin/tissue image
        cancer_type (str): Type of cancer to screen for
        
    Returns:
        dict: Analysis results including cancer probability
    """
    try:
        img = preprocess_image(image_path)
        if img is None:
            return {
                'error': 'Failed to process image',
                'diagnosis': 'unknown',
                'cancer_probability': 0.0,
                'confidence_score': 0.0,
                'features': {}
            }
        
        # Extract features for analysis
        features = extract_skin_features(img)
        
        # Detect skin condition
        diagnosis, cancer_probability, confidence_score = detect_skin_condition(features, cancer_type)
        
        # Generate result details
        if diagnosis in SKIN_DISEASES:
            description = SKIN_DISEASES[diagnosis]['description']
            recommendations = SKIN_DISEASES[diagnosis]['recommendations']
        else:
            description = "Analysis inconclusive."
            recommendations = "Please consult with a healthcare professional for a thorough examination."
        
        return {
            'diagnosis': diagnosis,
            'cancer_probability': cancer_probability,
            'confidence_score': confidence_score,
            'features': features,
            'description': description,
            'recommendations': recommendations
        }
    except Exception as e:
        logger.error(f"Error analyzing skin image: {e}")
        return {
            'error': str(e),
            'diagnosis': 'error',
            'cancer_probability': 0.0,
            'confidence_score': 0.0,
            'features': {}
        }

def extract_leaf_features(img):
    """
    Extract features from a leaf image for disease detection
    
    Args:
        img (numpy.ndarray): Preprocessed image array
        
    Returns:
        dict: Extracted features
    """
    # Convert to HSV color space for better color analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    # Calculate color histograms
    h_hist = cv2.calcHist([hsv], [0], None, [30], [0, 180])
    s_hist = cv2.calcHist([hsv], [1], None, [32], [0, 256])
    
    # Normalize histograms
    h_hist = cv2.normalize(h_hist, h_hist, 0, 1, cv2.NORM_MINMAX).flatten()
    s_hist = cv2.normalize(s_hist, s_hist, 0, 1, cv2.NORM_MINMAX).flatten()
    
    # Calculate texture features (using grayscale)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Calculate GLCM texture features
    texture_features = calculate_texture_features(gray)
    
    # Check for spots/lesions using color thresholding
    # Green health tissue has high green and low red/blue values
    lower_green = np.array([30, 50, 30])
    upper_green = np.array([90, 255, 90])
    healthy_mask = cv2.inRange(img, lower_green, upper_green)
    healthy_ratio = np.sum(healthy_mask > 0) / (img.shape[0] * img.shape[1])
    
    # Check for yellow/brown discoloration (potential disease)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    yellow_ratio = np.sum(yellow_mask > 0) / (img.shape[0] * img.shape[1])
    
    # Check for dark spots (potential lesions)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 80])
    dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
    dark_ratio = np.sum(dark_mask > 0) / (img.shape[0] * img.shape[1])
    
    # Return all features as a dictionary
    features = {
        'color_distribution': {
            'hue_histogram': h_hist.tolist(),
            'saturation_histogram': s_hist.tolist(),
        },
        'texture': texture_features,
        'color_ratios': {
            'healthy_green_ratio': float(healthy_ratio),
            'yellow_discoloration_ratio': float(yellow_ratio),
            'dark_spot_ratio': float(dark_ratio)
        }
    }
    
    return features

def extract_skin_features(img):
    """
    Extract features from a skin image for health analysis
    
    Args:
        img (numpy.ndarray): Preprocessed image array
        
    Returns:
        dict: Extracted features
    """
    # Convert to different color spaces for better analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    
    # Calculate color histograms
    h_hist = cv2.calcHist([hsv], [0], None, [30], [0, 180])
    a_hist = cv2.calcHist([lab], [1], None, [32], [0, 256])
    b_hist = cv2.calcHist([lab], [2], None, [32], [0, 256])
    
    # Normalize histograms
    h_hist = cv2.normalize(h_hist, h_hist, 0, 1, cv2.NORM_MINMAX).flatten()
    a_hist = cv2.normalize(a_hist, a_hist, 0, 1, cv2.NORM_MINMAX).flatten()
    b_hist = cv2.normalize(b_hist, b_hist, 0, 1, cv2.NORM_MINMAX).flatten()
    
    # Calculate texture features
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    texture_features = calculate_texture_features(gray)
    
    # Extract edge features for border irregularity
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate border irregularity if contours exist
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        perimeter = cv2.arcLength(largest_contour, True)
        area = cv2.contourArea(largest_contour)
        
        # Circularity (regularity measure) - 1.0 is a perfect circle
        if area > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        else:
            circularity = 0
            
        # Approximation of contour
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)
        complexity = len(approx)
    else:
        circularity = 0
        complexity = 0
    
    # Calculate color variance (for multi-colored lesions)
    r_std = np.std(img[:,:,0])
    g_std = np.std(img[:,:,1])
    b_std = np.std(img[:,:,2])
    color_variance = (r_std + g_std + b_std) / 3.0
    
    # Return all features as a dictionary
    features = {
        'color_distribution': {
            'hue_histogram': h_hist.tolist(),
            'a_histogram': a_hist.tolist(),
            'b_histogram': b_hist.tolist(),
        },
        'texture': texture_features,
        'border': {
            'circularity': float(circularity),
            'complexity': int(complexity)
        },
        'color_variance': float(color_variance)
    }
    
    return features

def calculate_texture_features(gray_img):
    """
    Calculate texture features from a grayscale image
    
    Args:
        gray_img (numpy.ndarray): Grayscale image
        
    Returns:
        dict: Texture features
    """
    # Calculate gradient magnitude and direction using Sobel operator
    sobelx = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    
    # Calculate image statistics
    mean_intensity = np.mean(gray_img)
    std_intensity = np.std(gray_img)
    mean_gradient = np.mean(magnitude)
    std_gradient = np.std(magnitude)
    
    # Calculate histogram of oriented gradients (simplified)
    hist_bins = 9
    angles = np.arctan2(sobely, sobelx) * 180 / np.pi
    angles[angles < 0] += 180
    hist, _ = np.histogram(angles, bins=hist_bins, range=(0, 180), weights=magnitude)
    hist = hist / np.sum(hist) if np.sum(hist) > 0 else hist
    
    return {
        'mean_intensity': float(mean_intensity),
        'std_intensity': float(std_intensity),
        'mean_gradient': float(mean_gradient),
        'std_gradient': float(std_gradient),
        'gradient_histogram': hist.tolist()
    }

def detect_leaf_disease(features):
    """
    Detect plant disease based on image features
    
    Args:
        features (dict): Image features
        
    Returns:
        tuple: (disease_name, confidence)
    """
    # Extract key indicators from features
    color_ratios = features['color_ratios']
    healthy_ratio = color_ratios['healthy_green_ratio']
    yellow_ratio = color_ratios['yellow_discoloration_ratio']
    dark_ratio = color_ratios['dark_spot_ratio']
    
    texture = features['texture']
    gradient_std = texture['std_gradient']
    
    # Simple rule-based classification (in real app, use a trained model)
    if healthy_ratio > 0.7 and yellow_ratio < 0.1 and dark_ratio < 0.05:
        # Mostly healthy green color with few spots
        return 'healthy', 0.85 + 0.15 * np.random.random()
    
    elif yellow_ratio > 0.2 and healthy_ratio < 0.6:
        # Significant yellowing
        return 'leaf_rust', 0.7 + 0.2 * np.random.random()
    
    elif dark_ratio > 0.15 and gradient_std > 20:
        # Dark spots with texture variations
        return 'bacterial_blight', 0.75 + 0.2 * np.random.random()
    
    elif healthy_ratio < 0.5 and gradient_std < 15:
        # Less healthy tissue, smoother texture (powdery appearance)
        return 'powdery_mildew', 0.7 + 0.2 * np.random.random()
    
    else:
        # Default case with reduced confidence
        diseases = list(LEAF_DISEASES.keys())
        selected = np.random.choice(diseases[:-1])  # Exclude 'healthy'
        return selected, 0.5 + 0.2 * np.random.random()

def detect_skin_condition(features, cancer_type):
    """
    Detect skin condition based on image features
    
    Args:
        features (dict): Image features
        cancer_type (str): Type of cancer to screen for
        
    Returns:
        tuple: (condition_name, cancer_probability, confidence_score)
    """
    # Extract key indicators from features
    border = features['border']
    circularity = border['circularity']
    complexity = border['complexity']
    
    color_variance = features['color_variance']
    texture = features['texture']
    gradient_std = texture['std_gradient']
    
    # For demonstration, add a small random component for variety
    # In a real app, use a proper trained model for each cancer type
    
    # Benign: regular borders (high circularity), low color variance
    if circularity > 0.7 and complexity < 10 and color_variance < 30:
        diagnosis = 'benign'
        cancer_probability = 0.1 + 0.15 * np.random.random()
        confidence_score = 0.8 + 0.15 * np.random.random()
    
    # Melanoma indicators: irregular border, high color variance
    elif (circularity < 0.5 or complexity > 15) and color_variance > 45:
        if cancer_type in ['skin', 'other', 'screening']:
            diagnosis = 'melanoma'
            cancer_probability = 0.7 + 0.25 * np.random.random()
            confidence_score = 0.75 + 0.2 * np.random.random()
        else:
            diagnosis = 'benign'  # Not the type of cancer being screened for
            cancer_probability = 0.3 + 0.2 * np.random.random()
            confidence_score = 0.5 + 0.2 * np.random.random()
    
    # Basal cell indicators: pearly appearance, medium border irregularity
    elif 0.5 < circularity < 0.7 and gradient_std < 20:
        if cancer_type in ['skin', 'other', 'screening']:
            diagnosis = 'basal_cell_carcinoma'
            cancer_probability = 0.6 + 0.2 * np.random.random()
            confidence_score = 0.7 + 0.15 * np.random.random()
        else:
            diagnosis = 'benign'  # Not the type of cancer being screened for
            cancer_probability = 0.25 + 0.15 * np.random.random()
            confidence_score = 0.6 + 0.15 * np.random.random()
    
    # Actinic keratosis: rough texture, medium color variance
    elif gradient_std > 30 and 25 < color_variance < 40:
        if cancer_type in ['skin', 'other', 'screening']:
            diagnosis = 'actinic_keratosis'
            cancer_probability = 0.4 + 0.2 * np.random.random()
            confidence_score = 0.65 + 0.2 * np.random.random()
        else:
            diagnosis = 'benign'  # Not the type of cancer being screened for
            cancer_probability = 0.2 + 0.1 * np.random.random()
            confidence_score = 0.7 + 0.1 * np.random.random()
    
    # Default case with reduced confidence
    else:
        if np.random.random() < 0.7:  # 70% chance of benign for ambiguous cases
            diagnosis = 'benign'
            cancer_probability = 0.2 + 0.3 * np.random.random()
        else:
            # Pick a condition based on cancer type
            if cancer_type == 'skin':
                diagnosis = np.random.choice(['melanoma', 'basal_cell_carcinoma'])
            else:
                diagnosis = 'actinic_keratosis'
            cancer_probability = 0.5 + 0.3 * np.random.random()
        
        confidence_score = 0.4 + 0.3 * np.random.random()  # Lower confidence
    
    return diagnosis, cancer_probability, confidence_score

def get_image_visualization(image_path, analysis_type='leaf'):
    """
    Generate a visualization of the image analysis
    
    Args:
        image_path (str): Path to the image file
        analysis_type (str): Type of analysis ('leaf' or 'skin')
        
    Returns:
        str: Base64 encoded visualization image
    """
    try:
        # Read the original image
        original = cv2.imread(image_path)
        if original is None:
            logger.error(f"Failed to read image for visualization: {image_path}")
            return None
            
        # Create a visualization based on analysis type
        if analysis_type == 'leaf':
            # For leaves: highlight potential diseased areas
            
            # Convert to HSV for easier color-based segmentation
            hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)
            
            # Create healthy tissue mask (green areas)
            lower_green = np.array([30, 40, 40])
            upper_green = np.array([90, 255, 255])
            healthy_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Create potential disease mask (yellow/brown areas)
            lower_yellow = np.array([15, 50, 50])
            upper_yellow = np.array([35, 255, 255])
            disease_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # Create visualization
            visualization = original.copy()
            
            # Apply green overlay to healthy areas (semi-transparent)
            green_overlay = np.zeros_like(visualization)
            green_overlay[healthy_mask > 0] = [0, 255, 0]  # Green color
            visualization = cv2.addWeighted(visualization, 0.8, green_overlay, 0.2, 0)
            
            # Apply red overlay to potentially diseased areas
            disease_overlay = np.zeros_like(visualization)
            disease_overlay[disease_mask > 0] = [0, 0, 255]  # Red color
            visualization = cv2.addWeighted(visualization, 0.7, disease_overlay, 0.3, 0)
            
        else:  # skin analysis
            # For skin: highlight borders and potential abnormal areas
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while preserving edges
            blurred = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Detect edges
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Create visualization
            visualization = original.copy()
            
            # Draw contours with thickness based on importance
            if contours:
                # Find the largest contour (main lesion boundary)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Draw the main boundary in blue
                cv2.drawContours(visualization, [largest_contour], -1, (255, 0, 0), 2)
                
                # Highlight areas with color variances
                lab = cv2.cvtColor(original, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                # Create a mask for areas with high color variance
                a_blur = cv2.GaussianBlur(a, (5, 5), 0)
                b_blur = cv2.GaussianBlur(b, (5, 5), 0)
                
                # Calculate local variance
                a_var = cv2.GaussianBlur(a_blur * a_blur, (15, 15), 0) - cv2.GaussianBlur(a_blur, (15, 15), 0) ** 2
                b_var = cv2.GaussianBlur(b_blur * b_blur, (15, 15), 0) - cv2.GaussianBlur(b_blur, (15, 15), 0) ** 2
                
                color_var = a_var + b_var
                
                # Create a mask for areas with high color variance
                _, color_var_mask = cv2.threshold(color_var, np.max(color_var) * 0.5, 255, cv2.THRESH_BINARY)
                color_var_mask = color_var_mask.astype(np.uint8)
                
                # Apply yellow highlighting to high variance areas
                yellow_overlay = np.zeros_like(visualization)
                yellow_overlay[color_var_mask > 0] = [0, 255, 255]  # Yellow color
                visualization = cv2.addWeighted(visualization, 0.8, yellow_overlay, 0.2, 0)
        
        # Convert to RGB for PIL
        visualization_rgb = cv2.cvtColor(visualization, cv2.COLOR_BGR2RGB)
        
        # Convert to base64 for web display
        img_pil = Image.fromarray(visualization_rgb)
        buffer = BytesIO()
        img_pil.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_str
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return None