from django.urls import path
from .views import LoginView, LogoutView, DashboardView, DepartmentListAPIView, VendorListAPIView, MyDepartmentsAPIView
from .views import ChangePasswordView

urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
    path('dashboard/', DashboardView.as_view(), name='api-dashboard'),
    path('departments/', DepartmentListAPIView.as_view(), name='department-list-api'),
    path('vendors/', VendorListAPIView.as_view(), name='vendor-list-api'),
    path('my_departments/', MyDepartmentsAPIView.as_view(), name='my-departments-api'),
    path('change-password/', ChangePasswordView.as_view(), name='api-change-password'),
]
