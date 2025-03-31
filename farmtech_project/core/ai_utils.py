import os
import json
import logging
from django.conf import settings

# Setup logging
logger = logging.getLogger(__name__)

# Get Gemini API key from environment
GEMINI_API_KEY = "AIzaSyB-tGExkleTwNnsCXkXXSV-nBuTgfubRjA"

# Flag to track if Gemini is properly initialized
GEMINI_INITIALIZED = False

# Initialize Gemini AI if API key is available
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_INITIALIZED = True
    else:
        logger.warning("Gemini API key not found. AI features will be disabled.")
except Exception as e:
    logger.error(f"Failed to initialize Gemini AI: {str(e)}")

def get_chatbot_response(message, username):
    """
    Get a response from Gemini API for the chatbot
    
    Args:
        message (str): User's message
        username (str): Username for personalization
        
    Returns:
        str: AI response
    """
    # Check if Gemini is properly initialized
    if not GEMINI_INITIALIZED:
        return "AI assistant is currently unavailable. Please ensure a valid Gemini API key is provided in the environment or contact the administrator to configure the AI services."
    
    try:
        # Using Gemini 1.5 Pro model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        system_prompt = """You are a helpful assistant for Reve Digital Platform. 
        You can help with both farming and healthcare topics.
        For farming: You specialize in soil health, crop management, and agricultural practices.
        For healthcare: You can help understand cancer screening data and general health information.
        
        Answer questions about:
        - Interpreting soil health data (pH, nutrients, moisture, etc.)
        - Improving crop yields and soil fertility
        - Sustainable farming practices
        - Understanding cancer screening results
        - General health recommendations
        - How to use the platform for analyzing data
        
        If you don't know something, admit it clearly rather than making up information.
        Keep responses under 150 words unless detailed technical information is required.
        """
        
        # Log the attempt to use the chatbot
        logger.info(f"Attempting to generate response for user: {username}")
        
        chat = model.start_chat(history=[])
        response = chat.send_message(
            f"{system_prompt}\n\nUser (username: {username}) message: {message}"
        )
        
        return response.text
    except Exception as e:
        logger.error(f"Error generating chatbot response: {str(e)}")
        return f"I'm having trouble connecting to the assistant right now. Please try again later. Error: {str(e)}"

def analyze_text_with_ai(text, task_type):
    """
    Use Gemini AI to analyze text data with specific instructions based on task type
    
    Args:
        text (str): Text to analyze
        task_type (str): Type of analysis to perform
        
    Returns:
        dict: Analysis results
    """
    # Check if Gemini is properly initialized
    if not GEMINI_INITIALIZED:
        return {
            "error": "Gemini API not initialized", 
            "message": "AI assistant is currently unavailable. Please ensure a valid Gemini API key is provided."
        }
    
    task_prompts = {
        'soil_recommendations': """
            Based on the provided soil data description, generate recommendations for:
            1. Improving soil health
            2. Optimizing nutrient levels
            3. Adjusting watering practices
            4. Suggesting suitable crops
            
            Format your response as a JSON object with these keys:
            {
                "summary": "Brief summary of soil condition",
                "recommendations": ["list", "of", "specific", "recommendations"],
                "priority_actions": ["1-3", "top", "priority", "actions"]
            }
            
            Your response should only contain valid JSON that can be parsed by json.loads() in Python.
        """,
        'data_interpretation': """
            Interpret the provided soil sensor data information. Explain:
            1. What the values indicate about soil health
            2. How these readings compare to optimal levels
            3. Any concerning patterns or values
            
            Format your response as a JSON object with these keys:
            {
                "interpretation": "Overall interpretation of the data",
                "concerns": ["list", "of", "concerns", "if", "any"],
                "positive_indicators": ["list", "of", "positive", "indicators"]
            }
            
            Your response should only contain valid JSON that can be parsed by json.loads() in Python.
        """,
        'healthcare_recommendations': """
            Based on the provided healthcare data analysis, provide medical recommendations and insights.
            Remember that this is for screening purposes only and not a definitive diagnosis.
            
            Consider:
            1. The detected biomarkers and their significance
            2. The cancer probability and confidence scores
            3. Appropriate next steps for the patient
            4. Further tests or specialist consultations needed
            
            Format your response as a JSON object with these keys:
            {
                "summary": "Brief summary of the analysis results",
                "recommendations": ["list", "of", "medical", "recommendations"],
                "priority_actions": ["1-3", "immediate", "next", "steps"]
            }
            
            Your response should only contain valid JSON that can be parsed by json.loads() in Python.
        """
    }
    
    prompt = task_prompts.get(task_type, "Analyze this text and provide insights. Format your response as valid JSON.")
    
    try:
        # Using Gemini 1.5 Pro model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Combine the prompt and the text to analyze
        full_prompt = f"{prompt}\n\nText to analyze: {text}"
        
        # Log the attempt to analyze text
        logger.info(f"Attempting to analyze text for task type: {task_type}")
        
        response = model.generate_content(full_prompt)
        
        # Extract JSON from the response
        response_text = response.text
        
        # Look for JSON content within the response
        # Sometimes Gemini includes markdown formatting for JSON
        if "```json" in response_text:
            # Extract JSON from code block
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            # Extract from generic code block
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            # Use as is
            json_text = response_text
        
        # Parse the JSON response
        return json.loads(json_text)
    except Exception as e:
        logger.error(f"Error analyzing text with AI: {str(e)}")
        return {
            "error": str(e), 
            "message": "Failed to analyze the text with AI. Please check the API key configuration."
        }
