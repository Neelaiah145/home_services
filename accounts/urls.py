from django.urls import path
from .views import *

urlpatterns = [

    # AUTH
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # DASHBOARDS
    path(
        'customer-dashboard/',
        CustomerDashboardView.as_view(),
        name='customer_dashboard'
    ),

    path(
        'admin-dashboard/',
        AdminDashboardView.as_view(),
        name='admin_dashboard'
    ),

    path(
        'vendor-dashboard/',
        VendorDashboardView.as_view(),
        name='vendor_dashboard'
    ),

    path(
        'superadmin-dashboard/',
        SuperDashboardView.as_view(),
        name='superadmin_dashboard'
    ),

    # USER STATUS
    path(
        'set-user-status/<int:user_id>/<str:status>/',
        SetUserStatusView.as_view(),
        name='set_user_status'
    ),

    # SUPERADMIN
    path(
        'create_admin/',
        CreateAdminView.as_view(),
        name='create_admin'
    ),

    path(
        "superadmin/all-users/",
        AllUsersView.as_view(),
        name="all_users"
    ),

    path(
        "api/all-users/",
        AllUsersAPI.as_view(),
        name="api_all_users"
    ),

    path(
        "user/delete/<int:id>/",
        DeleteUserView.as_view(),
        name="delete_user"
    ),

    # ADMIN
    path(
        "create_vendor/",
        CreateVendorView.as_view(),
        name="create_vendor"
    ),

    path(
        "vendors-approve/",
        AdminVendorApprovalView.as_view(),
        name="vendor_approval"
    ),

    path(
        "vendor-action/",
        VendorActionView.as_view(),
        name="vendor_action"
    ),

    path(
        "user/all-users/",
        AdminUsersView.as_view(),
        name="admin_all_users"
    ),

    path(
        "admin-booking/<int:booking_id>/",
        AdminBookingEditView.as_view(),
        name="admin_booking_edit"
    ),

    path(
        "admin-leads/",
        AdminLeadsView.as_view(),
        name="admin_leads"
    ),

    path(
        "admin-renewal-dashboard/",
        AdminRenewalDashboardView.as_view(),
        name="admin_renewal_dashboard"
    ),

    path(
        "vendor-verify/<int:id>/",
        AdminVendorVerifyView.as_view(),
        name="admin_vendor_verify"
    ),

    # SERVICES
    path(
        'service/<int:id>/',
        ServiceDetailView.as_view(),
        name='service_detail'
    ),

    path(
        'book_service/',
        BookServiceView.as_view(),
        name='book_service'
    ),

    path(
        'order_success/',
        BookingSuccessView.as_view(),
        name='order_success'
    ),

    path(
        "superadmin/create-service/",
        CreateServiceView.as_view(),
        name="create_service"
    ),

    path(
        "superadmin/update-service/<int:id>/",
        UpdateServiceView.as_view(),
        name="update_service"
    ),

    path(
        "delete-service/",
        DeleteServiceView.as_view(),
        name="delete_service"
    ),

    path(
        "services_page/",
        ServicesListingView.as_view(),
        name="services_listing_page"
    ),

    # AJAX SERVICES
    path(
        "get-services/",
        get_services,
        name="get_services"
    ),

    # OTP BOOKING
    path(
        'send-booking-otp/',
        send_booking_otp,
        name='send_booking_otp'
    ),

    path(
        'verify-booking-otp/',
        verify_booking_otp,
        name='verify_booking_otp'
    ),

    # ORDERS
    path(
        'my-orders/',
        CustomerOrdersView.as_view(),
        name='customer_orders'
    ),

    path(
        'vendor-orders/',
        VendorOrdersView.as_view(),
        name='vendor_orders'
    ),

    path(
        'admin-orders/',
        AdminOrdersView.as_view(),
        name='admin_orders'
    ),

    path(
        'superadmin-orders/',
        SuperAdminOrdersView.as_view(),
        name='superadmin_orders'
    ),

    path(
        "assign-vendor/",
        AssignVendorView.as_view()
    ),

    path(
        "update-status/",
        UpdateStatusView.as_view()
    ),

    path(
        'order-history/<int:id>/',
        OrderHistoryView.as_view(),
        name='order_history'
    ),

    path(
        'order/<int:id>/',
        CustomerOrderDetailView.as_view(),
        name='customer_order_detail'
    ),

    # PROFILE
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),

    path(
        "vendor/profile/<int:id>/",
        VendorProfileView.as_view(),
        name="vendor_profile"
    ),

    path(
        "user-profile/<int:id>/",
        UserProfileView.as_view(),
        name="user_profile"
    ),

    # PAYMENTS
    path(
        "superadmin-payments/",
        SuperAdminPaymentsView.as_view(),
        name="superadmin_payments"
    ),

    path(
        "admin-payments/",
        AdminPaymentsView.as_view(),
        name="admin_payments"
    ),

    path(
        "invoice/<int:pk>/",
        PaymentInvoiceView.as_view(),
        name="payment_invoice"
    ),

    path(
        'vendor/payments/',
        VendorPaymentsView.as_view(),
        name='vendor_payments'
    ),

    path(
        'vendor/payments_show/',
        VendorPaymentsShowView.as_view(),
        name='vendor_payment_show'
    ),

    path(
        "vendor/payment/<int:booking_id>/",
        VendorPaymentPageView.as_view(),
        name="vendor_payment_page"
    ),

    path(
        "customer/payments/",
        CustomerPaymentsView.as_view(),
        name="customer_payments"
    ),

    path(
        "customer-invoice/<int:booking_id>/",
        CustomerInvoiceView.as_view(),
        name="customer_invoice"
    ),

    # BOOKINGS
    path(
        "vendor/booking/<int:pk>/",
        VendorBookingDetailView.as_view(),
        name="vendor_booking_detail"
    ),

    path(
        "renew-service/<int:booking_id>/",
        renew_service,
        name="renew_service"
    ),

    path(
        "renew-booking/<int:booking_id>/",
        RenewBookingPageView.as_view(),
        name="renew_booking_page"
    ),

    # COMPLAINTS
    path(
        "my-bookings/",
        MyBookingsView.as_view(),
        name="my_bookings"
    ),

    path(
        "complaint/add/<int:booking_id>/",
        ComplaintCreateView.as_view(),
        name="complaint_add"
    ),

    path(
        "complaints/",
        ComplaintListView.as_view(),
        name="complaint_list"
    ),

    path(
        "complaint/<int:pk>/",
        ComplaintDetailView.as_view(),
        name="complaint_detail"
    ),

    path(
        "complaint/<int:pk>/delete/",
        ComplaintDeleteView.as_view(),
        name="complaint_delete"
    ),

    path(
        "complaint/ajax-update/<int:pk>/",
        ComplaintStatusAjaxUpdateView.as_view(),
        name="complaint_ajax_update"
    ),

    # TRACKING
    path(
        "customer/tracking/",
        CustomerTrackingView.as_view(),
        name="customer_tracking"
    ),

    path(
        "customer/tracking/<int:id>/",
        CustomerTrackingDetailView.as_view(),
        name="customer_tracking_detail"
    ),

    # PRIVACY POLICY
    path(
        "privacy-policy/",
        PrivacyPolicyView.as_view(),
        name="privacy_policy"
    ),

    path(
        "privacy-list/",
        PrivacyPolicyListView.as_view(),
        name="privacy_list"
    ),

    path(
        "privacy-create/",
        CreatePrivacyPolicyView.as_view(),
        name="add.privacy"
    ),

    path(
        "privacy-update/<int:id>/",
        UpdatePrivacyPolicyView.as_view(),
        name="update.privacy"
    ),

    path(
        "privacy-delete/<int:id>/",
        DeletePrivacyPolicyView.as_view(),
        name="delete.privacy"
    ),

]
