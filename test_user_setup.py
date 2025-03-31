import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmtech_project.settings')
sys.path.insert(0, 'farmtech_project')  # Add the project directory to path
django.setup()

# Import Django models
from django.contrib.auth.models import User

# Create a test user
username = 'testuser'
email = 'test@example.com'
password = 'testpassword123'

# Check if user already exists
if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists")
else:
    # Create the user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    user.save()
    print(f"Created test user: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print("You can now log in with these credentials to test the application.")