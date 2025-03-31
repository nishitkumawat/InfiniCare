<<<<<<< HEAD
# InfiniCare
=======
# Reve Digital Platform

A comprehensive Django platform for AI-driven healthcare and farming data analysis, created for the Reve Sponsored Track Algorithm Development Hackathon.

## Project Overview

This platform integrates two major domains:

1. **Digital Farming**: AI-powered soil analysis for optimizing agricultural productivity
2. **Digital Healthcare**: Early cancer detection through imaging and spectral analysis

Both domains leverage advanced AI capabilities through Google's Gemini API to provide intelligent insights and recommendations.

## Features

### Digital Farming
- Upload and analyze soil data from multiple sensor types
- Support for optical spectrometer, multi-parameter sensors, and moisture sensors
- AI-powered analysis of soil health, nutrient levels, and moisture content
- Personalized recommendations for improving soil quality
- Visual dashboards for monitoring farm health

### Digital Healthcare
- Early cancer detection for breast, throat, and skin cancers
- Support for optical spectrometer data and digital camera images
- AI-based probability and confidence scoring for cancer detection
- Analysis of biomarkers and spectral signatures
- Detailed recommendations for healthcare professionals

### Common Features
- Intelligent AI chatbot for customer support
- User authentication system with secure data handling
- Responsive dashboard with data visualization
- Comprehensive analysis results with exportable reports
- MySQL database integration for robust data storage

## Technical Architecture

- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Backend**: Django web framework (Python)
- **Database**: MySQL (through XAMPP)
- **AI**: Google Gemini API integration
- **Data Processing**: NumPy, Pandas, Scikit-learn, Matplotlib
- **Image Processing**: Pillow, OpenCV

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/reve-digital-platform.git
   cd reve-digital-platform
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r project_requirements.md
   ```

4. Configure database:
   - Install XAMPP and start MySQL service
   - Create a database named `reve_digital_platform`
   - Import the provided SQL schema: `mysql -u root reve_digital_platform < database_schema.sql`

5. Configure environment variables:
   - Create a `.env` file in the project root
   - Add required environment variables (see project_requirements.md)

6. Run migrations:
   ```bash
   cd farmtech_project
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver 0.0.0.0:5000
   ```

## Usage

1. Access the application at `http://localhost:5000`
2. Sign up for a new account or log in
3. Choose between Digital Farming or Digital Healthcare domains
4. Upload data files for analysis
5. View analysis results on the dashboard
6. Interact with the AI chatbot for assistance

## Project Structure

```
farmtech_project/
├── core/                  # Main application
│   ├── ai_utils.py        # AI integration utilities
│   ├── healthcare_analyzer.py  # Healthcare data analysis
│   ├── soil_analyzer.py   # Soil data analysis
│   ├── models.py          # Database models
│   ├── views.py           # View controllers
│   └── forms.py           # Form definitions
├── farmtech_project/      # Project settings
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   └── core/              # Core app templates
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and illustrations
└── manage.py              # Django management script
```

## Data Examples

### Soil Data
- **Optical Spectrometer**: CSV files with wavelength/intensity readings
- **Multi-parameter Sensors**: JSON files with soil attribute measurements
- **Moisture Sensors**: Simple CSV files with moisture readings over time

### Healthcare Data
- **Optical Spectrometer**: CSV files with spectral readings
- **Digital Camera Images**: JPEG/PNG images for visual analysis

## API Integration

The platform uses Google's Gemini API for AI capabilities. You'll need to set up API access:

1. Get a Gemini API key from Google AI Studio
2. Add the key to your `.env` file as `GEMINI_API_KEY`

## Licensing

This project is developed for the Reve Sponsored Track Algorithm Development Hackathon and is not licensed for commercial use without permission.

## Acknowledgments

- Reve for sponsoring the Algorithm Development Hackathon
- Google for providing the Gemini API platform
- The Django community for the robust web framework
- Contributors and mentors who provided guidance

## Contact

For questions about this project, please contact [your-email@example.com].
>>>>>>> a835c7f (Initial commit)
