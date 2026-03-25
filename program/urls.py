from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Program URLs
    path('', views.home, name='home'),
    path('programs/', views.programs_list, name='programs_list'),
    path('programs/<int:id>/', views.program_detail, name='program_detail'),
    path('programs/create/', views.program_create, name='program_create'),
    path('programs/<int:id>/edit/', views.program_update, name='program_update'),
    path('programs/<int:id>/delete/', views.program_delete, name='program_delete'),

    path('our-vision/', views.our_vision, name='our_vision'),
    path('help/', views.help, name='help'),
    path('upcoming-updates/', views.upcoming_updates, name='upcoming_updates'),
    
    # Beneficiary URLs
    path('beneficiaries/', views.beneficiaries_list, name='beneficiaries_list'),
    path('beneficiaries/<int:id>/', views.beneficiary_detail, name='beneficiary_detail'),
    path('beneficiaries/create/', views.beneficiary_create, name='beneficiary_create'),
    path('beneficiaries/<int:id>/edit/', views.beneficiary_update, name='beneficiary_update'),
    path('beneficiaries/<int:id>/delete/', views.beneficiary_delete, name='beneficiary_delete'),

    # Ticket URLs
    path('beneficiaries/<int:beneficiary_id>/ticket/<int:program_id>/', views.beneficiary_ticket, name='beneficiary_ticket'),

    # AJAX API Endpoints
    path('search-beneficiaries/', views.search_beneficiaries_ajax, name='search_beneficiaries_ajax'),
]