# Reve Digital Platform Requirements

## Software Requirements

### Core Framework
- Django (5.1.7)
- django-crispy-forms (2.1.0)
- crispy-bootstrap5 (0.7.0)

### Database
- mysqlclient (2.2.0)
- SQLAlchemy (2.0.23)

### Data Processing
- numpy (1.26.2)
- pandas (2.1.3)
- matplotlib (3.8.2)
- scikit-learn (1.3.2)
- scipy (1.11.4)

### Image Processing
- Pillow (10.1.0)
- opencv-python (4.8.1.78)

### AI and Machine Learning
- google-generativeai (0.3.2)
- Optional: openai (1.3.7)

### API and Networking
- requests (2.31.0)
- urllib3 (2.1.0)

### Security and Authentication
- django-allauth (0.61.0)
- django-otp (1.3.0)
- argon2-cffi (23.1.0)

### Development and Testing
- pytest (7.4.3)
- pytest-django (4.7.0)
- coverage (7.3.2)
- factory-boy (3.3.0)
- faker (20.1.0)

### Utilities
- python-dotenv (1.0.0)
- pytz (2023.3)
- tqdm (4.66.1)

## Installation Instructions

To install the required packages, use the following command:

```bash
pip install django django-crispy-forms crispy-bootstrap5 mysqlclient SQLAlchemy numpy pandas matplotlib scikit-learn scipy Pillow google-generativeai requests urllib3 django-allauth django-otp argon2-cffi
```

For development and testing, add these packages:

```bash
pip install pytest pytest-django coverage factory-boy faker python-dotenv pytz tqdm
```

## Environment Variables

The following environment variables should be configured:

```
# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=reve_digital_platform
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# API Keys
GEMINI_API_KEY=your_gemini_api_key
# Optional: OPENAI_API_KEY=your_openai_api_key

# Security
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your_domain.com
```

## System Requirements

- Python 3.9 or higher
- MySQL 8.0 or higher (or MySQL-compatible database like MariaDB)
- Minimum 2GB RAM for development, 4GB recommended for production
- 20GB disk space (including space for uploaded data files)

## External Services

- Google Gemini API for AI capabilities
- Optional: OpenAI API for additional AI capabilities

## Browser Compatibility

The web application is designed to work with:
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)