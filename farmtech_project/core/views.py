# import json
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.views.decorators.csrf import ensure_csrf_cookie
# from django.conf import settings
# from .models import SoilData, SoilAnalysisResult, HealthcareData, HealthcareAnalysisResult
# from .forms import SoilDataUploadForm, HealthcareDataUploadForm
# from .ai_utils import get_chatbot_response
# from .soil_analyzer import analyze_soil_data
# from .healthcare_analyzer import analyze_healthcare_data

# def index(request):
#     """Home page view"""
#     return render(request, 'core/index.html')

# def signup_view(request):
#     """User registration view using HTML forms"""
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')
        
#         # Basic validation
#         if password != confirm_password:
#             return render(request, 'core/signup.html', {'error': 'Passwords do not match'})
        
#         if User.objects.filter(username=username).exists():
#             return render(request, 'core/signup.html', {'error': 'Username already exists'})
        
#         if User.objects.filter(email=email).exists():
#             return render(request, 'core/signup.html', {'error': 'Email already exists'})
        
#         # Create user
#         user = User.objects.create_user(username=username, email=email, password=password)
#         login(request, user)
#         return redirect('dashboard')
    
#     return render(request, 'core/signup.html')

# def login_view(request):
#     """User login view using HTML forms"""
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('dashboard')
#         else:
#             return render(request, 'core/login.html', {'error': 'Invalid username or password'})
    
#     return render(request, 'core/login.html')

# @login_required
# def dashboard(request):
#     """User dashboard showing analysis results"""
#     # Get farming data
#     soil_data_list = SoilData.objects.filter(user=request.user).order_by('-upload_date')
#     soil_analysis_results = SoilAnalysisResult.objects.filter(soil_data__user=request.user).order_by('-analysis_date')
    
#     # Get healthcare data
#     healthcare_data_list = HealthcareData.objects.filter(user=request.user).order_by('-upload_date')
#     healthcare_analysis_results = HealthcareAnalysisResult.objects.filter(healthcare_data__user=request.user).order_by('-analysis_date')
    
#     # Get counts for dashboard statistics
#     stats = {
#         # Farming stats
#         'soil_total_uploads': soil_data_list.count(),
#         'soil_total_analyses': soil_analysis_results.count(),
#         'soil_spectrometer_data': soil_data_list.filter(data_type='spectrometer').count(),
#         'soil_multi_param_data': soil_data_list.filter(data_type='multi_param').count(),
#         'soil_moisture_data': soil_data_list.filter(data_type='moisture').count(),
        
#         # Healthcare stats
#         'healthcare_total_uploads': healthcare_data_list.count(),
#         'healthcare_total_analyses': healthcare_analysis_results.count(),
#         'healthcare_spectrometer_data': healthcare_data_list.filter(data_type='spectrometer').count(),
#         'healthcare_image_data': healthcare_data_list.filter(data_type='image').count(),
        
#         # Combined stats
#         'total_uploads': soil_data_list.count() + healthcare_data_list.count(),
#         'total_analyses': soil_analysis_results.count() + healthcare_analysis_results.count(),
#     }
    
#     # Get recent data
#     recent_soil_data = soil_data_list[:3]
#     recent_soil_results = soil_analysis_results[:3]
#     recent_healthcare_data = healthcare_data_list[:3]
#     recent_healthcare_results = healthcare_analysis_results[:3]
    
#     context = {
#         'stats': stats,
#         'recent_soil_data': recent_soil_data,
#         'recent_soil_results': recent_soil_results,
#         'recent_healthcare_data': recent_healthcare_data,
#         'recent_healthcare_results': recent_healthcare_results,
#         'section': request.GET.get('section', 'all'),  # Allow filtering by section
#     }
    
#     return render(request, 'core/dashboard.html', context)

# @login_required
# def upload_data(request):
#     """Upload soil data view"""
#     data_type = request.GET.get('type', 'soil')
    
#     if data_type == 'healthcare':
#         return upload_healthcare_data(request)
#     else:  # default to soil data
#         return upload_soil_data(request)

# @login_required
# def upload_soil_data(request):
#     """Upload soil data view"""
#     if request.method == 'POST':
#         form = SoilDataUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             soil_data = form.save(commit=False)
#             soil_data.user = request.user
#             soil_data.save()
            
#             # Process the data and create analysis
#             analyze_soil_data(soil_data)
            
#             return redirect('analysis_results', data_id=soil_data.id, data_type='soil')
#     else:
#         form = SoilDataUploadForm()
    
#     return render(request, 'core/upload.html', {
#         'form': form,
#         'data_type': 'soil',
#         'title': 'Upload Soil Data',
#         'description': 'Upload soil data from your farm for AI-powered analysis.',
#     })

# @login_required
# def upload_healthcare_data(request):
#     """Upload healthcare data view"""
#     if request.method == 'POST':
#         form = HealthcareDataUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             healthcare_data = form.save(commit=False)
#             healthcare_data.user = request.user
#             healthcare_data.save()
            
#             # Process the data and create analysis
#             analyze_healthcare_data(healthcare_data)
            
#             return redirect('analysis_results', data_id=healthcare_data.id, data_type='healthcare')
#     else:
#         form = HealthcareDataUploadForm()
    
#     return render(request, 'core/upload_healthcare.html', {
#         'form': form,
#         'data_type': 'healthcare',
#         'title': 'Upload Healthcare Data',
#         'description': 'Upload medical imaging or spectroscopic data for cancer detection analysis.',
#     })

# @login_required
# def analysis_results(request, data_id, data_type='soil'):
#     """View analysis results for specific data"""
#     if data_type == 'healthcare':
#         return healthcare_analysis_results(request, data_id)
#     else:  # default to soil data
#         return soil_analysis_results(request, data_id)

# @login_required
# def soil_analysis_results(request, data_id):
#     """View analysis results for specific soil data"""
#     soil_data = get_object_or_404(SoilData, id=data_id, user=request.user)
#     analysis_results = soil_data.analysis_results.order_by('-analysis_date').first()
    
#     if not analysis_results:
#         return render(request, 'core/soil_analysis_results.html', {
#             'data': soil_data,
#             'error': 'Analysis is not available for this data yet.'
#         })
    
#     # Prepare data for charts
#     nutrient_data = analysis_results.nutrient_levels if analysis_results.nutrient_levels else {}
    
#     context = {
#         'data': soil_data,
#         'analysis': analysis_results,
#         'nutrient_data': json.dumps(nutrient_data),
#         'soil_health_score': analysis_results.soil_health_score,
#         'data_type': 'soil'
#     }
    
#     return render(request, 'core/soil_analysis_results.html', context)

# @login_required
# def healthcare_analysis_results(request, data_id):
#     """View analysis results for specific healthcare data"""
#     healthcare_data = get_object_or_404(HealthcareData, id=data_id, user=request.user)
#     analysis_results = healthcare_data.analysis_results.order_by('-analysis_date').first()
    
#     if not analysis_results:
#         return render(request, 'core/healthcare_analysis_results.html', {
#             'data': healthcare_data,
#             'error': 'Analysis is not available for this data yet.'
#         })
    
#     # Prepare data for charts
#     biomarkers_data = analysis_results.biomarkers if analysis_results.biomarkers else {}
    
#     context = {
#         'data': healthcare_data,
#         'analysis': analysis_results,
#         'biomarkers_data': json.dumps(biomarkers_data),
#         'cancer_probability': analysis_results.cancer_probability,
#         'confidence_score': analysis_results.confidence_score,
#         'data_type': 'healthcare'
#     }
    
#     return render(request, 'core/healthcare_analysis_results.html', context)

# @login_required
# @ensure_csrf_cookie
# def chatbot_view(request):
#     """Chatbot interface view"""
#     return render(request, 'core/chatbot.html')

# @login_required
# def chatbot_api(request):
#     """API endpoint for chatbot interactions"""
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         message = data.get('message', '')
        
#         if not message:
#             return JsonResponse({'error': 'No message provided'}, status=400)
        
#         # Get response from AI chatbot
#         response = get_chatbot_response(message, request.user.username)
        
#         return JsonResponse({'response': response})
    
#     return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import SoilData, SoilAnalysisResult, HealthcareData, HealthcareAnalysisResult
from .forms import SoilDataUploadForm, HealthcareDataUploadForm
from .ai_utils import get_chatbot_response
from .soil_analyzer import analyze_soil_data
from .healthcare_analyzer import analyze_healthcare_data

def index(request):
    """Home page view"""
    return render(request, 'core/index.html')

def logout(request):
    logout(request)
    return redirect(request,'index.html')

def signup_view(request):
    """User registration view using HTML forms"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Basic validation
        if password != confirm_password:
            return render(request, 'core/signup.html', {'error': 'Passwords do not match'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'core/signup.html', {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'core/signup.html', {'error': 'Email already exists'})
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'core/signup.html')

def login_view(request):
    """User login view using HTML forms"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'core/login.html')

@login_required
def dashboard(request):
    """User dashboard showing analysis results"""
    # Get farming data
    soil_data_list = SoilData.objects.filter(user=request.user).order_by('-upload_date')
    soil_analysis_results = SoilAnalysisResult.objects.filter(soil_data__user=request.user).order_by('-analysis_date')
    
    # Get healthcare data
    healthcare_data_list = HealthcareData.objects.filter(user=request.user).order_by('-upload_date')
    healthcare_analysis_results = HealthcareAnalysisResult.objects.filter(healthcare_data__user=request.user).order_by('-analysis_date')
    
    # Get counts for dashboard statistics
    stats = {
        # Farming stats
        'soil_total_uploads': soil_data_list.count(),
        'soil_total_analyses': soil_analysis_results.count(),
        'soil_spectrometer_data': soil_data_list.filter(data_type='spectrometer').count(),
        'soil_multi_param_data': soil_data_list.filter(data_type='multi_param').count(),
        'soil_moisture_data': soil_data_list.filter(data_type='moisture').count(),
        
        # Healthcare stats
        'healthcare_total_uploads': healthcare_data_list.count(),
        'healthcare_total_analyses': healthcare_analysis_results.count(),
        'healthcare_spectrometer_data': healthcare_data_list.filter(data_type='spectrometer').count(),
        'healthcare_image_data': healthcare_data_list.filter(data_type='image').count(),
        
        # Combined stats
        'total_uploads': soil_data_list.count() + healthcare_data_list.count(),
        'total_analyses': soil_analysis_results.count() + healthcare_analysis_results.count(),
    }
    
    # Get recent data
    recent_soil_data = soil_data_list[:3]
    recent_soil_results = soil_analysis_results[:3]
    recent_healthcare_data = healthcare_data_list[:3]
    recent_healthcare_results = healthcare_analysis_results[:3]
    
    context = {
        'stats': stats,
        'recent_soil_data': recent_soil_data,
        'recent_soil_results': recent_soil_results,
        'recent_healthcare_data': recent_healthcare_data,
        'recent_healthcare_results': recent_healthcare_results,
        'section': request.GET.get('section', 'all'),  # Allow filtering by section
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def upload_data(request):
    """Upload soil data view"""
    data_type = request.GET.get('type', 'soil')
    
    if data_type == 'healthcare':
        return upload_healthcare_data(request)
    else:  # default to soil data
        return upload_soil_data(request)

@login_required
def upload_soil_data(request):
    """Upload soil data view"""
    if request.method == 'POST':
        form = SoilDataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            soil_data = form.save(commit=False)
            soil_data.user = request.user
            soil_data.save()
            
            # Process the data and create analysis
            analyze_soil_data(soil_data)
            
            return redirect('analysis_results', data_id=soil_data.id, data_type='soil')
    else:
        form = SoilDataUploadForm()
    
    return render(request, 'core/upload.html', {
        'form': form,
        'data_type': 'soil',
        'title': 'Upload Soil Data',
        'description': 'Upload soil data from your farm for AI-powered analysis.',
    })

@login_required
def upload_healthcare_data(request):
    """Upload healthcare data view"""
    if request.method == 'POST':
        form = HealthcareDataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            healthcare_data = form.save(commit=False)
            healthcare_data.user = request.user
            healthcare_data.save()
            
            # Process the data and create analysis
            analyze_healthcare_data(healthcare_data)
            
            return redirect('analysis_results', data_id=healthcare_data.id, data_type='healthcare')
    else:
        form = HealthcareDataUploadForm()
    
    return render(request, 'core/upload_healthcare.html', {
        'form': form,
        'data_type': 'healthcare',
        'title': 'Upload Healthcare Data',
        'description': 'Upload medical imaging or spectroscopic data for cancer detection analysis.',
    })

@login_required
def analysis_results(request, data_id, data_type='soil'):
    """View analysis results for specific data"""
    if data_type == 'healthcare':
        return healthcare_analysis_results(request, data_id)
    else:  # default to soil data
        return soil_analysis_results(request, data_id)

@login_required
def soil_analysis_results(request, data_id):
    """View analysis results for specific soil data"""
    soil_data = get_object_or_404(SoilData, id=data_id, user=request.user)
    analysis_results = soil_data.analysis_results.order_by('-analysis_date').first()
    
    if not analysis_results:
        return render(request, 'core/soil_analysis_results.html', {
            'data': soil_data,
            'error': 'Analysis is not available for this data yet.'
        })
    
    # Prepare data for charts
    nutrient_data = analysis_results.nutrient_levels if analysis_results.nutrient_levels else {}
    
    context = {
        'data': soil_data,
        'analysis': analysis_results,
        'nutrient_data': json.dumps(nutrient_data),
        'soil_health_score': analysis_results.soil_health_score,
        'data_type': 'soil'
    }
    
    return render(request, 'core/soil_analysis_results.html', context)

@login_required
def healthcare_analysis_results(request, data_id):
    """View analysis results for specific healthcare data"""
    healthcare_data = get_object_or_404(HealthcareData, id=data_id, user=request.user)
    analysis_results = healthcare_data.analysis_results.order_by('-analysis_date').first()
    
    if not analysis_results:
        return render(request, 'core/healthcare_analysis_results.html', {
            'data': healthcare_data,
            'error': 'Analysis is not available for this data yet.'
        })
    
    # Prepare data for charts
    biomarkers_data = analysis_results.biomarkers if analysis_results.biomarkers else {}
    
    context = {
        'data': healthcare_data,
        'analysis': analysis_results,
        'biomarkers_data': json.dumps(biomarkers_data),
        'cancer_probability': analysis_results.cancer_probability,
        'confidence_score': analysis_results.confidence_score,
        'data_type': 'healthcare'
    }
    
    return render(request, 'core/healthcare_analysis_results.html', context)

@login_required
@ensure_csrf_cookie
def chatbot_view(request):
    """Chatbot interface view"""
    return render(request, 'core/chatbot.html')

@login_required
def chatbot_api(request):
    """API endpoint for chatbot interactions"""
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        # Get response from AI chatbot
        response = get_chatbot_response(message, request.user.username)
        
        return JsonResponse({'response': response})
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)