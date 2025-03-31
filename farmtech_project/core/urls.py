from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Data upload paths
    path('upload/', views.upload_data, name='upload_data'),
    path('upload/soil/', views.upload_soil_data, name='upload_soil_data'),
    path('upload/healthcare/', views.upload_healthcare_data, name='upload_healthcare_data'),
    
    # Analysis results paths
    path('analysis/<str:data_type>/<int:data_id>/', views.analysis_results, name='analysis_results'),
    path('analysis/soil/<int:data_id>/', views.soil_analysis_results, name='soil_analysis_results'),
    path('analysis/healthcare/<int:data_id>/', views.healthcare_analysis_results, name='healthcare_analysis_results'),
    
    # Chatbot paths
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]
