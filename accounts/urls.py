from django.urls import path
from .views import *

urlpatterns = [
    
    
    
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    
    
    
    
    # rediret the dashboards
    
    path('customer-dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('vendor-dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('super-dashboard/', SuperDashboardView.as_view(), name='superadmin_dashboard'),
    
    # superadmin-create admin
    path('create_admin/', CreateAdminView.as_view(), name='create_admin'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path("superadmin/all-users/", AllUsersView.as_view(), name="all_users"),
    path("api/all-users/", AllUsersAPI.as_view(), name="api_all_users"),
    
    # admin create vendor
    path("create_vendor/", CreateVendorView.as_view(), name="create_vendor"),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    
    
    
    # services
    path('', ServiceListView.as_view(), name='service_list'),
    path('service/<int:id>/', ServiceDetailView.as_view(), name='service_detail'),

    path('book_service/', BookServiceView.as_view(), name='book_service'),
    path('order_success/', BookingSuccessView.as_view(), name='order_success'),
    
    
path("superadmin/create-service/", CreateServiceView.as_view(), name="create_service"),
path("superadmin/update-service/<int:id>/", UpdateServiceView.as_view(), name="update_service"),
path("delete-service/", DeleteServiceView.as_view(), name="delete_service"),
    
]