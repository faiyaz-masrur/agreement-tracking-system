from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgreementViewSet, AgreementListAPIView, AgreementDetailAPIView, AgreementFormDataAPIView, SubmitAgreementAPIView, EditAgreementAPIView, users_with_access
from django.urls import path
from .views import (
    users_with_access, 
    manage_user_access,
    available_users
) 
from .views import DashboardStatsAPIView


router = DefaultRouter()
router.register(r'agreements', AgreementViewSet, basename='agreement')

urlpatterns = [
    # path('', include(router.urls)),
    # Match frontend expectations
    path('', AgreementListAPIView.as_view(), name='api-agreement-list'),
    path('form-data/', AgreementFormDataAPIView.as_view(), name='api-agreement-form-data'),
    path('submit/', SubmitAgreementAPIView.as_view(), name='api-submit-agreement'),
    path('<int:pk>/', AgreementDetailAPIView.as_view(), name='api-agreement-detail'),
    path('edit/<int:agreement_id>/', EditAgreementAPIView.as_view(), name='api-edit-agreement'),
    path('<int:agreement_id>/users-with-access/', users_with_access, name='api-users-with-access'),
    path('<int:agreement_id>/users/', users_with_access, name='users_with_access'),
    path('<int:agreement_id>/users/manage/', manage_user_access, name='manage_user_access'),
    path('users/available/', available_users, name='available_users'),
    path('dashboard-stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    
]
