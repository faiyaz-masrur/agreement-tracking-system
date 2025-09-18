from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from rest_framework import generics
from .models import Department, Vendor, DepartmentPermission, User
from .serializers import DepartmentSerializer, VendorSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import SlidingToken


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            # csrf_token = get_token(request)
            token = SlidingToken.for_user(user)
            
            # Get user's department and permissions
            department_ids = set()
            if user.department:
                department_ids.add(user.department.id)
            
            permitted_dept_ids = DepartmentPermission.objects.filter(
                user=user,
                permission_type='edit'
            ).values_list('department_id', flat=True)
            department_ids.update(permitted_dept_ids)
            
            # Get permitted departments
            permitted_departments = Department.objects.filter(id__in=department_ids)
            
            # Prepare user data
            user_data = {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'department': {
                    'id': user.department.id,
                    'name': user.department.name
                } if user.department else None,
                'permitted_departments': DepartmentSerializer(permitted_departments, many=True).data,
                'is_executive': Department.objects.filter(
                    executive=True,
                    users=user
                ).exists()
            }
            
            return Response({
                'message': 'Login successful', 
                'token': str(token),
                'user': user_data
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard data for the authenticated user"""
        user = request.user
        
        # Get user's department and permissions
        department_ids = set()
        if user.department:
            department_ids.add(user.department.id)
        
        permitted_dept_ids = DepartmentPermission.objects.filter(
            user=user,
            permission_type='edit'
        ).values_list('department_id', flat=True)
        department_ids.update(permitted_dept_ids)
        
        # Get permitted departments
        permitted_departments = Department.objects.filter(id__in=department_ids)
        
        # Check if user is executive
        is_executive = Department.objects.filter(
            executive=True,
            users=user
        ).exists()
        
        # Prepare dashboard data
        dashboard_data = {
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'department': {
                    'id': user.department.id,
                    'name': user.department.name
                } if user.department else None,
                'is_executive': is_executive
            },
            'permissions': {
                'permitted_departments': DepartmentSerializer(permitted_departments, many=True).data,
                'can_create_agreements': not is_executive,
                'can_edit_agreements': not is_executive
            }
        }
        
        return Response(dashboard_data)

class DepartmentListAPIView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class VendorListAPIView(generics.ListAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class MyDepartmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get departments where user has access (own department + permitted departments)"""
        department_ids = set()
        
        # Add user's own department if they have one
        if request.user.department:
            department_ids.add(request.user.department.id)
        
        # Add departments where user has edit permission
        permitted_dept_ids = DepartmentPermission.objects.filter(
            user=request.user,
            permission_type='edit'
        ).values_list('department_id', flat=True)
        department_ids.update(permitted_dept_ids)
        
        # Get all departments that user has access to
        permitted_departments = Department.objects.filter(id__in=department_ids)
        serializer = DepartmentSerializer(permitted_departments, many=True)
        
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or len(new_password) < 8:
            return Response({'error': 'New password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'success': 'Password changed successfully.'})