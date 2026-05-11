from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from core.models import Category, CategoryService
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from .models import User
import random
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from accounts.mixins import RoleRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.hashers import make_password
import json
from .models import Booking, BookingHistory, Payment, VendorProfile, CustomerRemark
from django.core.paginator import Paginator
from accounts.utils import verify_otp
from accounts.utils import send_otp, can_resend
from core.models import CategoryService

from django.urls import reverse
User = get_user_model()


# login classes
def normalize_phone(phone):
    return phone.replace(" ", "").replace("+91", "").strip()


class LoginView(View):

    def get(self, request):
        next_url = request.GET.get("next", "")
        return render(request, "customer/customer_login.html", {
            "next": next_url
        })

    def post(self, request):
        data = json.loads(request.body)
        phone = data.get("phone", "").replace("+91", "").strip()
        otp = data.get("otp")
        next_url = data.get("next")

        if not phone.isdigit() or len(phone) != 10:

            return JsonResponse({
                "error": "Enter valid 10 digit phone number"
            })

        if otp:

            if otp != request.session.get("otp") or phone != request.session.get("phone"):

                return JsonResponse({
                    "error": "Invalid OTP"
                })
            user = User.objects.filter(
                phone__endswith=phone
            ).first()
            # USER NOT FOUND
            if not user:
                return JsonResponse({
                    "error": "User not found Please Register",
                    "redirect": f"/register/?phone={phone}"
                })
            # VENDOR NOT APPROVED
            if user.role == "vendor" and not user.is_active:
                return JsonResponse({

                    "error": "Your account is not approved yet. Please wait for admin approval."
                })

            # LOGIN
            login(request, user)
            print("LOGGED IN USER ROLE:", user.role)
            # REDIRECT
            if next_url:
                redirect_url = next_url
            else:
                if user.role == "superadmin":
                    redirect_url = "/superadmin-dashboard/"
                elif user.role == "admin":
                    redirect_url = "/admin-dashboard/"
                elif user.role == "vendor":
                    redirect_url = "/vendor-dashboard/"
                elif user.role == "customer":
                    redirect_url = "/customer-dashboard/"
                else:
                    redirect_url = "/"

            return JsonResponse({
                "success": True,
                "redirect": redirect_url
            })

        user = User.objects.filter(
            phone__endswith=phone
        ).first()

        # USER NOT FOUND

        if not user:
            return JsonResponse({
                "error": "User not found Please Register",
                "redirect": f"/register/?phone={phone}"

            })

        # VENDOR NOT APPROVED

        if user.role == "vendor" and not user.is_active:

            return JsonResponse({

                "error": "Your account is not approved yet. Please wait for admin approval."

            })

        # GENERATE OTP

        otp = str(random.randint(1000, 9999))
        request.session["otp"] = otp
        request.session["phone"] = phone
        print("OTP:", otp)

        return JsonResponse({
            "success": True,
            "message": "OTP sent"
        })

# register classes




class RegisterView(View):
    def get(self, request):

        category_id = request.GET.get("category")

        categories = Category.objects.all()
        services = CategoryService.objects.all()

        if category_id:
            services = services.filter(category_id=category_id)

        return render(request, "customer/register.html", {
            "categories": categories,
            "services": services,
            "selected_category": category_id
        })

    def post(self, request):

  
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid data"}, status=400)

        action = data.get("action")

        phone = data.get("phone")
        otp = data.get("otp")
        name = data.get("name")
        email = data.get("email")
        role = data.get("role", "customer")

        category_id = data.get("category")
        service_id = data.get("service")

      
        if action == "send_otp":

            if not phone or len(phone) != 10:
                return JsonResponse({"error": "Enter valid phone number"})

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({
                    "error": "User already exists. Please login.",
                    "redirect": "/login/"
                })

            otp_code = str(random.randint(1000, 9999))

            request.session["otp"] = otp_code
            request.session["phone"] = phone
            request.session["role"] = role

            print("OTP:", otp_code)  

            return JsonResponse({"success": True})

    
        if action == "verify_otp":

            if otp != request.session.get("otp") or phone != request.session.get("phone"):
                return JsonResponse({"error": "Invalid or expired OTP"})

   
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    "error": "Email already registered. Please login.",
                    "redirect": "/login/"
                })

            try:
    
                user = User.objects.create_user(
                    email=email,
                    password=None
                )

                user.phone = phone
                user.first_name = name
                user.role = role

       
                user.is_active = False if role == "vendor" else True

                user.save()

      
                if role == "vendor":

                    if not category_id:
                        user.delete()
                        return JsonResponse({"error": "Please select category"})

                    # Check services exist for category
                    services_qs = CategoryService.objects.filter(category_id=category_id)

                    if not services_qs.exists():
                        user.delete()
                        return JsonResponse({
                            "error": "No services available for selected category"
                        })

                    if not service_id:
                        user.delete()
                        return JsonResponse({
                            "error": "Please select a service"
                        })

                    # Validate correct service
                    ser_obj = CategoryService.objects.filter(
                        id=service_id,
                        category_id=category_id
                    ).first()

                    if not ser_obj:
                        user.delete()
                        return JsonResponse({"error": "Invalid service selected"})

                    cat_obj = get_object_or_404(Category, id=category_id)

                    profile = VendorProfile.objects.create(
                        user=user,
                        category=cat_obj,
                        experience=0,
                        locality="Default",
                        street="Default",
                        city="Default",
                        postal_code="000000"
                    )

                    profile.services.add(ser_obj)

    
                request.session.flush()

                return JsonResponse({
                    "success": True,
                    "redirect": "/login/"
                })

            except Exception as e:
                print("REGISTER ERROR:", e)
                try:
                    user.delete()
                except:
                    pass

                return JsonResponse({
                    "error": "Something went wrong. Please try again."
                }, status=500)

        return JsonResponse({"error": "Invalid request"}, status=400)


def get_services(request):
    category_id = request.GET.get("category_id")

    if not category_id:
        return JsonResponse({"services": []})

    services = CategoryService.objects.filter(category_id=category_id)

    data = [
        {
            "id": s.id,
            "title": s.title
        }
        for s in services
    ]

    return JsonResponse({"services": data})

# ================= SERVICES API =================
def get_services(request):
    category_id = request.GET.get("category_id")

    if not category_id:
        return JsonResponse({"services": []})

    services = CategoryService.objects.filter(category_id=category_id)

    return JsonResponse({
        "services": [
            {"id": s.id, "s_title": s.s_title}
            for s in services
        ]
    })


# optional
class GetServicesView(View):
    """
    Independent API endpoint to fetch services based on category selection.
    """
    def get(self, request):
        category_id = request.GET.get("category_id")

        if not category_id:
            return JsonResponse({"services": []})

        try:
    
            services = CategoryService.objects.filter(
                category_id=category_id
            ).values("id", "s_title")
            
            return JsonResponse({
                "services": list(services)
            })
        except Exception as e:
            return JsonResponse({"error": str(e), "services": []}, status=500)
    


class SendOTPView(View):
    def post(self, request):
        otp = str(random.randint(1000, 9999))
        request.session['otp'] = otp

        print("OTP:", otp) 
        return JsonResponse({"status": "sent"})


class VerifyOTPView(View):
    def post(self, request):
        if request.POST.get("otp") == request.session.get("otp"):
            return JsonResponse({"status": "verified"})
        return JsonResponse({"status": "failed"})


# logout classes
class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        auth_logout(request)
        return redirect("login")


# ====================================================================================================
# super admin classes
# ======================================================================================================


# super admin -- dashboard page
from django.utils import timezone
from datetime import datetime
class SuperDashboardView(LoginRequiredMixin, RoleRequiredMixin, View):

    allowed_roles = ['superadmin']

    def get(self, request):

        # TOTAL USERS

        total_customers = User.objects.filter(
            role="customer"
        ).count()

        total_vendors = User.objects.filter(
            role="vendor"
        ).count()

        total_admins = User.objects.filter(
            role="admin"
        ).count()

        total_bookings = Booking.objects.count()

        # BOOKING STATUS COUNTS

        total_pending = Booking.objects.filter(
            status="pending"
        ).count()

        total_assigned = Booking.objects.filter(
            status="assigned"
        ).count()

        total_accepted = Booking.objects.filter(
            status="accepted"
        ).count()

        total_in_progress = Booking.objects.filter(
            status="in_progress"
        ).count()

        total_completed = Booking.objects.filter(
            status="completed"
        ).count()

        total_cancelled = Booking.objects.filter(
            status="cancelled"
        ).count()

        # MONTHLY LEADS

        monthly_data = []

        month_labels = []

        current_year = timezone.now().year

        for month in range(1, 13):

            total = Booking.objects.filter(
                created_at__year=current_year,
                created_at__month=month
            ).count()

            month_name = datetime(
                current_year,
                month,
                1
            ).strftime("%b")

            month_labels.append(month_name)

            monthly_data.append(total)

        context = {

            'page_title': 'Dashboard',

            'total_customers': total_customers,
            'total_vendors': total_vendors,
            'total_admins': total_admins,
            'total_bookings': total_bookings,

            'total_pending': total_pending,
            'total_assigned': total_assigned,
            'total_accepted': total_accepted,
            'total_in_progress': total_in_progress,
            'total_completed': total_completed,
            'total_cancelled': total_cancelled,

            'month_labels': month_labels,
            'monthly_data': monthly_data,
        }

        return render(
            request,
            "superadmin/dashboard.html",
            context
        )




# user profile views code
class UserProfileView(LoginRequiredMixin, View):

    def get(self, request, id):

        # ONLY ADMIN & SUPERADMIN

        if request.user.role not in ["admin", "superadmin"]:
            return redirect("login")

        user_obj = get_object_or_404(
            User,
            id=id
        )

        # ADMIN CANNOT SEE SUPERADMIN

        if (
            request.user.role == "admin"
            and
            user_obj.role == "superadmin"
        ):
            return redirect("login")

        # BACK URL

        if request.user.role == "superadmin":

            back_url = "superadmin_dashboard"

        else:

            back_url = "admin_dashboard"

        context = {

            "user_obj": user_obj,
            "back_url": back_url,

        }

        return render(
            request,
            "admin/user_profile.html",
            context
        )











# super admin -- create admin(create admin page)


class CreateAdminView(LoginRequiredMixin, View):

    def get(self, request):
        admins = User.objects.filter(role="admin").order_by("-id")
        page_obj = paginate_queryset(request,admins,10)



        return render(request, "superadmin/create_admin.html", {
            "admins": page_obj,
            "page_obj":page_obj,
            "page_title": "Create_Admins"
        })

    def post(self, request):
        try:
            if request.user.role != "superadmin":
                return JsonResponse({"error": "Unauthorized"}, status=403)

            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            #  normalize phone
            phone = normalize_phone(phone)

            #  validations
            if not all([first_name, email, phone, password]):
                return JsonResponse({"error": "All fields required"}, status=400)

            if len(phone) != 10 or not phone.isdigit():
                return JsonResponse({"error": "Invalid phone number"}, status=400)

            if password != confirm_password:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({"error": "Phone already exists"}, status=400)

            if not request.session.get("otp_verified"):
                return JsonResponse({"error": "Phone not verified"}, status=400)

            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role="admin"
            )

            user.set_password(password)
            user.save()

            request.session.pop("otp_verified", None)
            request.session.pop("otp", None)

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# admin al users


class AdminUsersView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role not in [
            "admin"
        ]:
            return redirect("login")

        role = request.GET.get("role")

        search = request.GET.get("search")

        users = User.objects.filter(
            role__in=[
                "customer",
                "vendor"
            ]
        ).order_by("-id")

        if role:

            users = users.filter(
                role=role
            )

        if search:

            users = users.filter(

                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)

            )

        customer_count = User.objects.filter(
            role="customer"
        ).count()

        vendor_count = User.objects.filter(
            role="vendor"
        ).count()

        total_users = User.objects.filter(
            role__in=[
                "customer",
                "vendor"
            ]
        ).count()

        page_obj = paginate_queryset(request,users,10)
        return render(
            request,
            "admin/all_users.html",
            {
                "page_obj": page_obj,
                "users": page_obj,
                "customer_count": customer_count,
                "vendor_count": vendor_count,
                "total_users": total_users,
                "active_page": "admin_all_users",
            }
        )

    def post(self, request):

        if request.user.role != "admin":
            return JsonResponse({
                "success": False,
                "error": "Access Denied"
            })

        try:

            data = json.loads(request.body)

            user_id = data.get("user_id")

            behaviour = data.get("behaviour")

            user = User.objects.get(
                id=user_id
            )

            user.behaviour = behaviour

            user.save()

            return JsonResponse({
                "success": True
            })

        except Exception as e:

            return JsonResponse({
                "success": False,
                "error": str(e)
            })

# all users form the admin













# super admin see all admins/vendors/customers
import json
from .utils import paginate_queryset


class AllUsersView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role not in [
            "superadmin",
            "admin"
        ]:
            return redirect("login")

        users = User.objects.filter(
            role__in=[
                "customer",
                "vendor",
                "admin"
            ]
        ).order_by("-id")

        page_obj = paginate_queryset(
            request,
            users,
            10
        )

        customer_count = User.objects.filter(
            role="customer"
        ).count()

        admin_count = User.objects.filter(
            role="admin"
        ).count()

        vendor_count = User.objects.filter(
            role="vendor"
        ).count()

        return render(
            request,
            "superadmin/all_users.html",
            {
                "page_obj": page_obj,
                "active_page": "all_users",
                "users": users,
                "customer_count": customer_count,
                "admin_count": admin_count,
                "vendor_count": vendor_count,
            }
        )

    def post(self, request):

        if request.user.role not in [
            "superadmin",
            "admin"
        ]:

            return JsonResponse({
                "success": False,
                "error": "Access denied"
            })

        try:

            data = json.loads(request.body)
            user_id = data.get("user_id")
            behaviour = data.get("behaviour")
            user = User.objects.get(id=user_id)
            user.behaviour = behaviour
            user.save()
            return JsonResponse({
                "success": True
            })

        except Exception as e:

            return JsonResponse({
                "success": False,
                "error": str(e)
            })
# ===== API (SEARCH + FILTER) =====


class AllUsersAPI(View):

    def get(self, request):

        query = request.GET.get("q", "").strip()
        role = request.GET.get("role", "")

        users = User.objects.exclude(role="superadmin")

        if role:
            users = users.filter(role=role)

        if query:
            users = users.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )

        users = users.order_by("-id")

        data = [{
            "name": f"{u.first_name} {u.last_name}",
            "email": u.email,
            "phone": u.phone,
            "role": u.role
        } for u in users]

        return JsonResponse({"users": data})


class DeleteUserView(View):

    def post(self, request, id):

        user = get_object_or_404(User, id=id)

        if user.role == "superadmin":
            messages.error(request, "Superadmin cannot be deleted!")
            return redirect("all_users")

        if request.user == user:
            messages.error(request, "You cannot delete yourself!")
            return redirect("all_users")

        user.delete()
        messages.success(request, "User deleted successfully!")

        return redirect("all_users")


class SendOTPView(View):
    def post(self, request):
        phone = request.POST.get("phone")
        otp = str(random.randint(1000, 9999))
        request.session["otp"] = otp
        print("OTP:", otp)
        return JsonResponse({"status": "sent"})


class VerifyOTPView(View):
    def post(self, request):
        otp = request.POST.get("otp")

        if otp == request.session.get("otp"):
            request.session["otp_verified"] = True
            return JsonResponse({"status": "verified"})

        return JsonResponse({"status": "invalid"})


# create services for super admin(create/delete)
class CreateServiceView(View):

    def get(self, request):
        services = CategoryService.objects.all().order_by("-id")
        return render(request, "superadmin/create_service.html", {
            "services": services
        })

    def post(self, request):
        CategoryService.objects.create(
            name=request.POST.get("name"),
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            image=request.FILES.get("image")
        )
        return redirect("create_service")


class UpdateServiceView(View):

    def get(self, request, id):
        service = CategoryService.objects.get(id=id)

        return render(request, "superadmin/update_service.html", {
            "service": service
        })

    def post(self, request, id):
        service = CategoryService.objects.get(id=id)

        service.name = request.POST.get("name")
        service.title = request.POST.get("title")
        service.description = request.POST.get("description")

        if request.FILES.get("image"):
            service.image = request.FILES.get("image")

        service.save()

        return redirect("create_service")


class DeleteServiceView(View):

    def post(self, request):
        service_id = request.POST.get("id")

        CategoryService.objects.filter(id=service_id).delete()

        return JsonResponse({"status": "deleted"})


# ====================================================================================================
# admin classes
# ======================================================================================================

# admin dashboard page
class AdminDashboardView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request):
        return render(request, "admin/dashboard.html")


# admin create vendor


class CreateVendorView(LoginRequiredMixin, View):

    def get(self, request):

        category_id = request.GET.get("category")

        vendors = User.objects.filter(role="vendor")\
            .select_related("vendor_profile")\
            .order_by("-id")

        categories = Category.objects.all()

        services = CategoryService.objects.all()

        if category_id:
            services = services.filter(category_id=category_id)

        return render(request, "admin/create_vendor.html", {
            "vendors": vendors,
            "categories": categories,
            "services": services,
            "selected_category": category_id
        })

    def post(self, request):
        try:
            if request.user.role != "admin":
                return JsonResponse({"error": "Unauthorized"}, status=403)

            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            experience = request.POST.get("experience")
            locality = request.POST.get("locality")
            street = request.POST.get("street")
            city = request.POST.get("city")
            pincode = request.POST.get("pincode")
            category_id = request.POST.get("category")
            service_id = request.POST.get("service")
            company_name = request.POST.get("company_name")
            company_address = request.POST.get("company_address")

            if not first_name or not email or not phone:
                return JsonResponse({"error": "Basic fields required"}, status=400)

            if not email.endswith("@gmail.com"):
                return JsonResponse({"error": "Enter valid Gmail"}, status=400)

            if not phone.isdigit() or len(phone) != 10:
                return JsonResponse({"error": "Invalid phone number"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({"error": "Phone already exists"}, status=400)

            if not request.session.get("otp_verified"):
                return JsonResponse({"error": "Verify OTP first"}, status=400)

            if not city or not locality or not pincode:
                return JsonResponse({"error": "Location required"}, status=400)

            if not category_id:
                return JsonResponse({"error": "Select category"}, status=400)

            if not service_id:
                return JsonResponse({"error": "Select service"}, status=400)

            service_exists = CategoryService.objects.filter(
                id=service_id,
                category_id=category_id
            ).exists()

            if not service_exists:
                return JsonResponse({
                    "error": "Selected service does not belong to this category"
                }, status=400)

            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role="vendor",
                created_by=request.user
            )

            user.set_unusable_password()
            user.save()

            VendorProfile.objects.create(
                user=user,
                experience=experience or 0,
                locality=locality,
                street=street,
                city=city,
                postal_code=pincode,
                category_id=category_id,
                service_id=service_id,
                company_name=company_name,
                company_address=company_address
            )

            request.session.pop("otp_verified", None)
            request.session.pop("phone", None)

            return JsonResponse({
                "status": "success",
                "message": "Vendor created successfully"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def get_services(request):
    category_id = request.GET.get("category")

    print("RAW:", category_id)

    if not category_id:
        return JsonResponse({"services": []})

    try:
        category_id = int(category_id)
    except:
        return JsonResponse({"services": []})

    services = CategoryService.objects.filter(
        category_id=category_id
    ).values("id", "s_title")

    print("RESULT:", list(services))

    return JsonResponse({
        "services": list(services)
    })


class SendOTPView(View):
    def post(self, request):
        phone = request.POST.get("phone")

        if User.objects.filter(phone=phone).exists():
            return JsonResponse({"error": "Phone already used"})

        if not can_resend(phone):
            return JsonResponse({"error": "Wait 30 seconds to resend"})

        send_otp(phone)

        request.session["phone"] = phone

        return JsonResponse({"status": "sent"})


class VerifyOTPView(View):
    def post(self, request):
        phone = request.session.get("phone")
        otp = request.POST.get("otp")

        if verify_otp(phone, otp):
            request.session["otp_verified"] = True
            return JsonResponse({"status": "verified"})

        return JsonResponse({"error": "Invalid OTP"})


class VendorDashboardView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['vendor']

    def get(self, request):
        # bookings = Booking.objects.filter(vendor=request.user)
        return render(request, "vendor/dashboard.html")






class CustomerDashboardView(LoginRequiredMixin, RoleRequiredMixin, View):
    login_url = "/login/"
    allowed_roles = ["customer"]

    def get(self, request):
        return render(request, "customer/dashboard.html", {
            "user": request.user
        })

# ===================================================================================
# public pages
# ===================================================================================


# class ServiceListView(View):

#     def get(self, request):

#         services = Service.objects.all().order_by("-id")  # latest first

#         return render(request, "service/service_list.html", {
#             "services": services
#         })


class ServiceDetailView(View):

    def get(self, request, id):
        service = CategoryService.objects.get(id=id)
        return render(request, "service/detail.html", {"service": service})

    def post(self, request, id):
        request.session["service_id"] = id
        return redirect("book_service")


# ====================================================================================================
# customer classes
# ======================================================================================================


# booking page  send otp
def send_booking_otp(request):
    phone = request.POST.get("phone")

    otp = str(random.randint(1000, 9999))
    request.session["otp"] = otp
    request.session["phone"] = phone

    print("OTP:", otp)
    return JsonResponse({"status": "sent"})


# booking page verify otp
def verify_booking_otp(request):
    entered_otp = request.POST.get("otp")
    session_otp = request.session.get("otp")
    phone = request.session.get("phone")

    if entered_otp != session_otp:
        return JsonResponse({"status": "invalid"})

    request.session["otp_verified"] = True

    user = User.objects.filter(phone=phone).first()

    if user:
        return JsonResponse({"status": "existing_user"})
    else:
        return JsonResponse({"status": "new_user"})


User = get_user_model()


class SetUserStatusView(LoginRequiredMixin, View):

    def get(self, request, user_id, status):

        if request.user.role not in ["admin", "superadmin"]:
            return redirect("login")

        user = get_object_or_404(
            User,
            id=user_id
        )
        if status == "active":

            user.is_active = True

        elif status == "inactive":

            user.is_active = False

        user.save()

        if request.user.role == "superadmin":

            return redirect("all_users")

        return redirect("admin_all_users")


# booking functionality



from datetime import datetime
import json



class BookServiceView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request):

        categories = Category.objects.filter(
            is_active=True
        )

        return render(
            request,
            "service/book.html",
            {
                "categories": categories
            }
        )

    def post(self, request):

        try:

            data = json.loads(request.body)

            name = data.get("name")
            phone = data.get("phone")

            category_id = data.get("category_id")
            service_id = data.get("service_id")

            booking_type = data.get("booking_type")

            # VALIDATION

            if not name or not phone:

                return JsonResponse({
                    "error": "Enter name and phone"
                })

            if not category_id or not service_id:

                return JsonResponse({
                    "error": "Select category and service"
                })

            # CATEGORY

            category = Category.objects.get(
                id=category_id
            )

            # SERVICE

            service = CategoryService.objects.get(
                id=service_id
            )

            # FIND VENDOR

            vendor = User.objects.filter(
                role="vendor",
                services=service
            ).first()

            # SINGLE SERVICE

            if booking_type == "single":

                booking_date = data.get("date")
                time_value = data.get("time")

                if not booking_date:

                    return JsonResponse({
                        "error": "Select booking date"
                    })

                time_slots = {

                    "09-11": "09 AM - 11 AM",
                    "11-1": "11 AM - 01 PM",
                    "1-3": "01 PM - 03 PM",
                    "3-5": "03 PM - 05 PM"

                }

                formatted_time = time_slots.get(
                    time_value,
                    ""
                )

                Booking.objects.create(

                    user=request.user,

                    category=category,

                    service=service,

                    vendor=vendor,

                    name=name,

                    phone=phone,

                    city=data.get("city"),

                    address=data.get("address"),

                    problem=data.get("problem"),

                    scheduled_date=booking_date,

                    scheduled_time=formatted_time,

                    start_date=None,

                    end_date=None,

                    status="pending"

                )

            # MULTIPLE SERVICE

            else:

                start_date = data.get("start_date")
                end_date = data.get("end_date")

                if not start_date or not end_date:

                    return JsonResponse({
                        "error": "Select start date and end date"
                    })

                Booking.objects.create(

                    user=request.user,

                    category=category,

                    service=service,

                    vendor=vendor,

                    name=name,

                    phone=phone,

                    city=data.get("city"),

                    address=data.get("address"),

                    problem=data.get("problem"),

                    scheduled_date=None,

                    scheduled_time=None,

                    start_date=start_date,

                    end_date=end_date,

                    status="pending"

                )

            return JsonResponse({

                "success": True,
                "message": "Service booked successfully",
                "redirect": "/customer-dashboard/"

            })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            })


class GetServicesView(View):
    def get(self, request):
        category_id = request.GET.get("category_id")

        if not category_id:
            return JsonResponse({"services": []})

        services = CategoryService.objects.filter(category_id=category_id)

        data = {
            "services": [
                {
                    "id": s.id,
                    "name": s.s_title,
                    "desc": s.s_desc,
                    "tag": s.s_tag,
                    "image": s.image.url if s.image else ""
                }
                for s in services
            ]
        }

        return JsonResponse(data)


# booking success page

class BookingSuccessView(View):

    def get(self, request):
        return render(request, "service/order_success.html")


# oders


class CustomerOrdersView(LoginRequiredMixin, View):

    def get(self, request):

        bookings = Booking.objects.filter(
            user=request.user
        ).select_related(
            "service",
            "vendor",
            "category"
        ).prefetch_related(
            "payments"
        ).order_by("-id")

        # FILTERS

        status = request.GET.get("status")
        search = request.GET.get("search")

        if status:
            bookings = bookings.filter(status=status)

        if search:

            bookings = bookings.filter(

                Q(order_id__icontains=search) |
                Q(service__s_title__icontains=search)

            )
     

        page_obj = paginate_queryset(request,bookings,10)
        return render(
            request,
            "customer/customer_orders.html",
            {
                "bookings": bookings,
                "bookings": page_obj,
                "page_obj": page_obj,
            }
        )


class CustomerOrderDetailView(LoginRequiredMixin, View):

    def get(self, request, id):
        booking = Booking.objects.get(id=id, user=request.user)

        history = booking.history.all().order_by("-created_at")

        return render(request, "customer/order_detail.html", {
            "booking": booking,
            "history": history
        })






# renew the service in customer
class RenewBookingPageView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request, booking_id):

        booking = Booking.objects.get(
            id=booking_id,
            user=request.user
        )

        return render(
            request,
            "service/renew_booking.html",
            {
                "booking": booking
            }
        )

    def post(self, request, booking_id):

        booking = Booking.objects.get(
            id=booking_id,
            user=request.user
        )

        booking.end_date = request.POST.get(
            "end_date"
        )
        booking.renewal_requested = True
        booking.status = "pending"

        booking.save()

        return redirect(
            "customer_orders"
        )



# admin track the leads and renews tracks
# views.py

class AdminLeadsView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request):

        if request.user.role != "admin":
            return HttpResponse(
                "Not allowed"
            )

        bookings = Booking.objects.select_related(

            "user",
            "vendor",
            "service",
            "category"

        ).prefetch_related(

            "payments"

        ).order_by("-id")

        # FILTERS

        status = request.GET.get(
            "status"
        )

        search = request.GET.get(
            "search"
        )

        if status:

            bookings = bookings.filter(
                status=status
            )

        if search:

            bookings = bookings.filter(

                Q(order_id__icontains=search) |

                Q(service__s_title__icontains=search) |

                Q(user__first_name__icontains=search) |

                Q(vendor__first_name__icontains=search)

            )

        return render(

            request,

            "admin/admin_leads.html",

            {
                "bookings": bookings
            }

        )

    def post(self, request):

        try:

            data = json.loads(
                request.body
            )

            booking_id = data.get(
                "booking_id"
            )

            action = data.get(
                "action"
            )

            booking = get_object_or_404(

                Booking,

                id=booking_id

            )

            # ACCEPT RENEWAL

            if action == "accept_renewal":

                booking.renewal_requested = False

                booking.is_renewed = True

                booking.status = "accepted"

                booking.save()

                BookingHistory.objects.create(

                    booking=booking,

                    status="Renewal Accepted",

                    updated_by=request.user

                )

                return JsonResponse({
                    "success": True
                })

            # EDIT SLOT

            if action == "edit_slot":

                booking.scheduled_date = data.get(
                    "scheduled_date"
                )

                booking.scheduled_time = data.get(
                    "scheduled_time"
                )

                booking.start_date = data.get(
                    "start_date"
                )

                booking.end_date = data.get(
                    "end_date"
                )

                booking.save()

                BookingHistory.objects.create(

                    booking=booking,

                    status="Booking Updated",

                    updated_by=request.user

                )

                return JsonResponse({
                    "success": True
                })

            # STATUS UPDATE

            status = data.get(
                "status"
            )

            booking.status = status

            booking.save()

            BookingHistory.objects.create(

                booking=booking,

                status=status,

                updated_by=request.user

            )

            return JsonResponse({
                "success": True
            })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            })



# track renewals
# views.py

# views.py

class AdminRenewalDashboardView(LoginRequiredMixin, View):

    login_url = "/login/"

    # PAGE LOAD

    def get(self, request):

        if request.user.role != "admin":

            return HttpResponse(
                "Not allowed"
            )

        bookings = Booking.objects.select_related(

            "user",
            "vendor",
            "service",
            "category"

        ).order_by("-id")

        customer = request.GET.get(
            "customer"
        )

        vendor = request.GET.get(
            "vendor"
        )

        renewal_status = request.GET.get(
            "renewal_status"
        )

        if customer:

            bookings = bookings.filter(
                user__first_name__icontains=customer
            )

        if vendor:

            bookings = bookings.filter(
                vendor__first_name__icontains=vendor
            )

        if renewal_status == "renewed":

            bookings = bookings.filter(
                is_renewed=True
            )

        if renewal_status == "pending":

            bookings = bookings.filter(renewal_requested=True)

        total_renewals = bookings.filter(is_renewed=True).count()
        active_services = bookings.filter(status="accepted").count()
        completed_services = bookings.filter(status="completed").count()
        total_service_days = sum(
            [
                booking.total_days or 0
                for booking in bookings
            ]
        )
        page_obj = paginate_queryset(request,bookings,10)
        context = {

            "bookings": bookings,
            "bookings": page_obj,
            "page_obj": page_obj,
            "total_renewals": total_renewals,
            "active_services": active_services,
            "completed_services": completed_services,
            "total_service_days": total_service_days

        }
        return render(request,"admin/admin_renewal_dashboard.html",context)

    def post(self, request):

        if request.user.role != "admin":

            return HttpResponse(
                "Not allowed"
            )

        booking_id = request.POST.get(
            "booking_id"
        )

        booking = Booking.objects.get(
            id=booking_id
        )

        # MULTIPLE DAYS UPDATE

        start_date = request.POST.get(
            "start_date"
        )

        end_date = request.POST.get(
            "end_date"
        )

        if start_date:

            booking.start_date = start_date

        if end_date:

            booking.end_date = end_date

        # SINGLE DAY UPDATE

        scheduled_date = request.POST.get(
            "scheduled_date"
        )

        scheduled_time = request.POST.get(
            "scheduled_time"
        )

        if scheduled_date:

            booking.scheduled_date = scheduled_date

        if scheduled_time:

            booking.scheduled_time = scheduled_time

        booking.save()

        return redirect(
            "admin_renewal_dashboard"
        )



# admin can assign the lead to vendor
class AssignVendorView(LoginRequiredMixin, View):

    def post(self, request):
        try:
            if request.user.role != "admin":
                return JsonResponse({"error": "Not allowed"}, status=403)

            data = json.loads(request.body)

            booking = get_object_or_404(Booking, id=data.get("booking_id"))
            vendor = get_object_or_404(
                User, id=data.get("vendor_id"), role="vendor")

            booking.vendor = vendor
            booking.status = "assigned"
            booking.save()

            BookingHistory.objects.create(
                booking=booking,
                status="assigned",
                updated_by=request.user
            )

            return JsonResponse({
                "success": True,
                "vendor_name": vendor.first_name
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class UpdateStatusView(LoginRequiredMixin, View):

    def post(self, request):
        try:
            data = json.loads(request.body)

            booking = get_object_or_404(Booking, id=data.get("booking_id"))
            status = data.get("status")
            vendor_id = data.get("vendor_id")

            allowed = ["progress", "completed"]

            if status not in allowed:
                return JsonResponse({"error": "Invalid status"}, status=400)

            if vendor_id:
                vendor = User.objects.get(id=vendor_id, role="vendor")
                booking.vendor = vendor

            if not booking.vendor:
                return JsonResponse({"error": "Assign vendor first"}, status=400)

            booking.status = status
            booking.save()

            BookingHistory.objects.create(
                booking=booking,
                status=status,
                updated_by=request.user
            )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class VendorOrdersView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role != "vendor":
            return HttpResponse("Not allowed")

        bookings = Booking.objects.filter(
            vendor=request.user
        ).select_related(
            "service",
            "user",
            "category"
        ).prefetch_related(
            "payments"
        ).order_by("-id")

        status = request.GET.get("status")
        date = request.GET.get("date")

        if status:
            bookings = bookings.filter(status=status)

        if date:
            bookings = bookings.filter(created_at__date=date)
     

        page_obj = paginate_queryset(request,bookings,10)
        return render(
            request,
            "vendor/vendor_orders.html",
            {
                "bookings": bookings,
                "bookings": page_obj,
                "page_obj": page_obj,
            }
        )

    def post(self, request):

        # PAYMENT UPLOAD

        if "screenshot" in request.FILES:

            booking_id = request.POST.get("booking_id")
            txn = request.POST.get("transaction_id")
            file = request.FILES["screenshot"]

            booking = get_object_or_404(
                Booking,
                id=booking_id
            )

            if booking.vendor != request.user:

                return JsonResponse({
                    "error": "Not allowed"
                }, status=403)

            if booking.status != "completed":

                return JsonResponse({
                    "error": "Complete order first"
                }, status=400)

            payment, created = Payment.objects.get_or_create(

                booking=booking,

                defaults={

                    "vendor": request.user,

                    "service": booking.service,

                }

            )

            if not created and payment.status == "paid":

                return JsonResponse({
                    "error": "Payment already submitted"
                }, status=400)

            payment.transaction_id = txn
            payment.screenshot = file
            payment.status = "paid"
            payment.vendor = request.user

            payment.save()

            return JsonResponse({
                "success": True
            })

        # STATUS UPDATE

        try:

            data = json.loads(request.body)

            booking_id = data.get("booking_id")

            renew_accept = data.get("renew_accept")

            # ACCEPT RENEWAL

            if renew_accept:

                booking = get_object_or_404(
                    Booking,
                    id=booking_id
                )

                if booking.vendor != request.user:

                    return JsonResponse({
                        "error": "Not allowed"
                    }, status=403)

                booking.renewal_requested = False

                booking.is_renewed = True

                booking.status = "accepted"

                booking.save()

                BookingHistory.objects.create(

                    booking=booking,

                    status="accepted",

                    updated_by=request.user

                )

                return JsonResponse({
                    "success": True
                })

            status = data.get("status")

            allowed_status = [

                "pending",

                "accepted",

                "in_progress",

                "completed",

                "cancelled"

            ]

            if status not in allowed_status:

                return JsonResponse({
                    "error": "Invalid status"
                }, status=400)

            booking = get_object_or_404(
                Booking,
                id=booking_id
            )

            if booking.vendor != request.user:

                return JsonResponse({
                    "error": "Not allowed"
                }, status=403)

            booking.status = status

            booking.save()

            BookingHistory.objects.create(

                booking=booking,

                status=status,

                updated_by=request.user

            )

            return JsonResponse({
                "success": True
            })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            }, status=400)

# admin can assigned the lead in vendor


from decimal import Decimal

class AdminOrdersView(LoginRequiredMixin, View):

    def get(self, request):

        category_id = request.GET.get("category")

        service_id = request.GET.get("service")

        city = request.GET.get("city")

        q = request.GET.get("q")

        # BOOKINGS

        bookings = Booking.objects.select_related(
            "service",
            "vendor"
        ).order_by("-id")

        # CATEGORY FILTER

        if category_id:

            bookings = bookings.filter(
                service__category_id=category_id
            )

        # SERVICE FILTER

        if service_id:

            bookings = bookings.filter(
                service_id=service_id
            )

        # CITY FILTER

        if city:

            bookings = bookings.filter(
                city__icontains=city
            )

        # SEARCH

        if q:

            bookings = bookings.filter(

                Q(name__icontains=q) |

                Q(phone__icontains=q) |

                Q(city__icontains=q) |

                Q(order_id__icontains=q)

            )

        # CATEGORIES

        categories = Category.objects.all()

        # SERVICES

        services = CategoryService.objects.all()

        if category_id:

            services = services.filter(
                category_id=category_id
            )

        # CITIES

        cities = Booking.objects.exclude(
            city__isnull=True
        ).exclude(
            city=""
        ).values_list(
            "city",
            flat=True
        ).distinct()

        # VENDORS

        vendors = User.objects.filter(
            role="vendor"
        ).select_related(
            "vendor_profile"
        ).prefetch_related(
            "vendor_profile__services"
        )

        if service_id:

            vendors = vendors.filter(
                vendor_profile__services__id=service_id
            )

        elif category_id:

            vendors = vendors.filter(
                vendor_profile__category_id=category_id
            )

        if city:

            vendors = vendors.filter(
                city__icontains=city
            )

        vendors = vendors.distinct()

        # PAGINATION

        page_obj = paginate_queryset(
            request,
            bookings,
            10
        )

        return render(
            request,
            "admin/admin_orders.html",
            {

                "bookings": page_obj,

                "page_obj": page_obj,

                "vendors": vendors,

                "categories": categories,

                "services": services,

                "cities": cities,

                "selected_category": category_id,

                "selected_service": service_id,

                "selected_city": city,

                "q": q,

            }
        )

    def post(self, request):

        try:

            data = json.loads(request.body)

            booking_id = data.get("booking_id")

            status = data.get("status")

            total_amount = data.get("total_amount")

            allowed_status = [

                "pending",

                "assigned",

                "accepted",

                "in_progress",

                "completed",

                "cancelled"

            ]

            # BOOKING

            booking = get_object_or_404(
                Booking,
                id=booking_id
            )

            # =====================================
            # PAYMENT SAVE
            # =====================================

            if total_amount:

                total_amount = Decimal(total_amount)

                payment = Payment.objects.filter(
                    booking=booking
                ).first()

                # UPDATE EXISTING PAYMENT

                if payment:

                    payment.total_amount = total_amount

                    payment.remaining_amount = (

                        total_amount
                        -
                        payment.paid_amount

                    )

                    payment.save()

                # CREATE NEW PAYMENT

                else:

                    payment = Payment.objects.create(

                        booking=booking,

                        vendor=booking.vendor,

                        service=booking.service,

                        total_amount=total_amount,

                        paid_amount=Decimal("0"),

                        remaining_amount=total_amount

                    )

                return JsonResponse({

                    "success": True,

                    "total_amount": str(payment.total_amount)

                })

            # =====================================
            # STATUS UPDATE
            # =====================================

            if status:

                if status not in allowed_status:

                    return JsonResponse({

                        "error": "Invalid status"

                    }, status=400)

                booking.status = status

                booking.save()

                BookingHistory.objects.create(

                    booking=booking,

                    status=status,

                    updated_by=request.user

                )

            return JsonResponse({

                "success": True

            })

        except Exception as e:

            print("ERROR:", e)

            return JsonResponse({

                "error": str(e)

            }, status=400)
            
            
            

# super-admin orders
class SuperAdminOrdersView(LoginRequiredMixin, View):

    def get(self, request):

        bookings = Booking.objects.select_related(
            'user', 'service', 'vendor'
        ).prefetch_related("history").order_by('-created_at')

        services = CategoryService.objects.all()
        vendors = User.objects.filter(role="vendor")

    
        q = request.GET.get('q')
        if q:
            bookings = bookings.filter(
                Q(order_id__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__phone__icontains=q)
            )

        service_id = request.GET.get('service')
        if service_id:
            bookings = bookings.filter(service_id=service_id)

        vendor_id = request.GET.get('vendor')
        if vendor_id:
            bookings = bookings.filter(vendor_id=vendor_id)

        status = request.GET.get('status')
        if status:
            bookings = bookings.filter(status=status)

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            bookings = bookings.filter(
                created_at__date__range=[start_date, end_date]
            )

  
        total_count = bookings.count()
        pending_count = bookings.filter(status="pending").count()
        progress_count = bookings.filter(status="progress").count()
        completed_count = bookings.filter(status="completed").count()
        page_obj = paginate_queryset(request,bookings,10)

        context = {
            "bookings": page_obj,   
            "services": services,
            "vendors": vendors,
            "page_obj": page_obj,
            "total_count": total_count,
            "pending_count": pending_count,
            "progress_count": progress_count,
            "completed_count": completed_count,
        }

        return render(request, "superadmin/superadmin_orders.html", context)




# order history


class OrderHistoryView(LoginRequiredMixin, View):

    def get(self, request, id):

        booking = get_object_or_404(
            Booking.objects.select_related("user", "service", "vendor"),
            id=id
        )

        history = booking.history.all().order_by("-created_at")

   
        total_services = 1   

   
        total_amount = getattr(booking, "total_amount", 0)
        paid_amount = getattr(booking, "paid_amount", 0)

        due_amount = total_amount - paid_amount

        return render(request, "superadmin/order_history.html", {
            "booking": booking,
            "history": history,

            "total_services": total_services,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "due_amount": due_amount,
        })

# profile page

class ProfileView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request):

        return render(
            request,
            "profile/profile.html"
        )

    def post(self, request):

        user = request.user

        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")

        # EMAIL VALIDATION

        if not email:

            messages.error(
                request,
                "Email is required"
            )

            return redirect("profile")

        # UPDATE USER

        user.email = email
        user.address = address
        user.city = city

        # PROFILE IMAGE

        if request.FILES.get("profile_image"):

            user.profile_image = request.FILES.get(
                "profile_image"
            )

        user.save()

        messages.success(
            request,
            "Profile updated successfully"
        )

        return redirect("profile")



class AdminPaymentsView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):

        if request.user.role not in ["admin", "superadmin"]:
            return redirect("dashboard")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        payments = Payment.objects.select_related(
            "booking",
            "booking__user",
            "vendor",
            "service",
            "service__category"
        ).order_by("-id")

        payment_status = request.GET.get("payment_status")

        if payment_status:
            payments = payments.filter(status=payment_status)


        for p in payments:

            if not p.payment_method:
                p.payment_method = "Cash"

        page_obj = paginate_queryset(request, payments, 10)

        return render(
            request,
            "admin/admin_payments.html",
            {
                "payments": page_obj,
                "page_obj": page_obj,
            }
        )
    def post(self, request):

        payment_id = request.POST.get("payment_id")

        payment_method = request.POST.get("payment_method")

        payment = get_object_or_404(
        Payment,
        id=payment_id
    )

        payment.payment_method = payment_method

        payment.save()

        return redirect("admin_payments")
    
    
    
    
    
    
    
# superadmin
class SuperAdminPaymentsView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):

        if request.user.role not in ["admin", "superadmin"]:
            return redirect("dashboard")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        payments = Payment.objects.select_related(
            "booking",
            "booking__user",
            "vendor",
            "service"
        ).order_by("-id")

        payment_status = request.GET.get("payment_status")
        page_obj = paginate_queryset(request,payments,10)

        if payment_status:
            payments = payments.filter(status=payment_status)

        return render(
            request,
            "superadmin/superadmin_payments.html",
            {
                "payments": payments,
                "payments": page_obj,
                "page_obj": page_obj
            }
        )
   
   
   
   
   
   
   
   
   
         
# vendor payment show view
from decimal import Decimal

class VendorPaymentsShowView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role != "vendor":
            return redirect("login")

        bookings = Booking.objects.filter(
            vendor=request.user,
            status="completed"
        ).select_related(
            "user",
            "service"
        ).prefetch_related(
            "payments"
        ).order_by("-id")

        payment_status = request.GET.get("payment_status")

        if payment_status == "paid":

            bookings = [

                b for b in bookings

                if (
                    b.payments.first()
                    and
                    b.payments.first().status == "paid"
                )
            ]

        elif payment_status == "partial_paid":

            bookings = [

                b for b in bookings

                if (
                    b.payments.first()
                    and
                    b.payments.first().status == "partial_paid"
                )
            ]

        elif payment_status == "pending":

            bookings = [

                b for b in bookings

                if (
                    not b.payments.first()
                    or
                    b.payments.first().status == "pending"
                )
            ]

        for b in bookings:

            payment = b.payments.first()

            if payment:

                b.total_amount_value = payment.total_amount or 0

                b.paid_amount_value = payment.paid_amount or 0

                b.remaining_amount_value = payment.remaining_amount or 0

                b.transaction_id_value = payment.transaction_id

            else:

                b.total_amount_value = 0

                b.paid_amount_value = 0

                b.remaining_amount_value = 0

                b.transaction_id_value = ""

        page_obj = paginate_queryset(request, bookings, 10)

        return render(
            request,
            "vendor/vendor_payment_show.html",
            {
                "bookings": page_obj,
                "page_obj": page_obj,
            }
        )

    def post(self, request):

        if request.user.role != "vendor":
            return redirect("login")

        booking_id = request.POST.get("booking_id")

        paid_amount = request.POST.get("paid_amount")

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            vendor=request.user
        )

        payment = booking.payments.first()

        if payment:

            paid_amount_decimal = Decimal(paid_amount)

            payment.paid_amount = paid_amount_decimal

            remaining = payment.total_amount - paid_amount_decimal

            if remaining < 0:
                remaining = Decimal("0")

            payment.remaining_amount = remaining

            # AUTO STATUS

            if paid_amount_decimal >= payment.total_amount:

                payment.status = "paid"

            elif paid_amount_decimal > 0:

                payment.status = "partial_paid"

            else:

                payment.status = "pending"

            payment.save()

        return redirect("vendor_payment_show")
    
    
# vendor payment view

class VendorPaymentsView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role != "vendor":

            return redirect("login")

        bookings = Booking.objects.filter(
            vendor=request.user,
            status="completed"
        ).select_related(
            "user",
            "service"
        ).prefetch_related(
            "payments"
        ).order_by("-id")

        payment_status = request.GET.get("payment_status")
        if payment_status == "paid":

            bookings = [

                b for b in bookings

                if (
                    b.payments.first()
                    and
                    b.payments.first().status == "paid"
                )
            ]

        elif payment_status == "partial_paid":

            bookings = [

                b for b in bookings

                if (
                    b.payments.first()
                    and
                    b.payments.first().status == "partial_paid"
                )
            ]

        elif payment_status == "pending":
            bookings = [

                b for b in bookings

                if (
                    not b.payments.first()
                    or
                    b.payments.first().status == "pending"
                )
            ]
         

        page_obj = paginate_queryset(request,bookings,10)
        return render(
            request,
            "vendor/vendor_payments.html",
            {
                "bookings": bookings,
                "bookings": page_obj,
                "page_obj": page_obj,
            }
        )

# invoice number
class PaymentInvoiceView(View):
    def get(self, request, pk):
        payment = get_object_or_404(Payment, id=pk)
        return render(request, "service/invoice.html", {"p": payment})
    

# customer invoice 
class CustomerInvoiceView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request, booking_id):

        booking = get_object_or_404(

            Booking,

            id=booking_id,

            user=request.user

        )

        payment = booking.payments.first()

        return render(

            request,

            "customer/customer_invoice.html",

            {

                "booking": booking,

                "payment": payment

            }

        )

class VendorBookingDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        return render(request, "vendor/vendor_booking_detail.html", {
            "booking": booking
        })


class MyBookingsView(View):

    def get(self, request):

        bookings = Booking.objects.filter(user=request.user) \
            .select_related("vendor", "service") \
            .prefetch_related("remarks") \
            .order_by("-id")
        page_obj = paginate_queryset(request,bookings,10)
        return render(request, "customer/my_bookings.html", {
            "bookings": bookings,
            "bookings": page_obj,
            "page_obj": page_obj,
        })


class ComplaintCreateView(View):

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        return render(request, "complaints/create.html", {
            "booking": booking
        })

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        #  Prevent other users accessing
        if booking.user != request.user:
            messages.error(request, "Unauthorized access!")
            return redirect("my_bookings")

        #  Prevent duplicate complaint
        if booking.remarks.exists():
            messages.error(
                request, "Complaint already raised for this booking!")
            return redirect("my_bookings")

        #  Get vendor safely
        vendor = booking.vendor

        if not vendor:
            messages.error(request, "Vendor not assigned to this booking!")
            return redirect("my_bookings")

        message = request.POST.get("message")
        priority = request.POST.get("priority", "medium")

        #  Basic validation
        if not message:
            messages.error(request, "Message is required!")
            return redirect("complaint_add", booking_id=booking.id)

        #  Create complaint
        CustomerRemark.objects.create(
            booking=booking,
            user=request.user,
            vendor=vendor,
            message=message,
            priority=priority
        )

        messages.success(request, "Complaint raised successfully!")

        return redirect("complaint_list")


class ComplaintListView(View):

    def get(self, request):

        if request.user.role in ["admin", "superadmin"]:

            complaints = CustomerRemark.objects.all().order_by("-created_at")

        else:

            complaints = CustomerRemark.objects.filter(
                user=request.user
            ).order_by("-created_at")

        return render(
            request,
            "complaints/list.html",
            {
                "complaints": complaints
            }
        )


class ComplaintDetailView(View):

    def get(self, request, pk):
        complaint = get_object_or_404(CustomerRemark, pk=pk)

        return render(request, "complaints/detail.html", {
            "complaint": complaint
        })


class ComplaintDeleteView(View):

    def post(self, request, pk):

        complaint = get_object_or_404(CustomerRemark, pk=pk)

        if request.user.is_superuser or complaint.user == request.user:
            complaint.delete()

        return redirect("complaint_list")


class ComplaintStatusAjaxUpdateView(View):

    def post(self, request, pk):

        complaint = get_object_or_404(CustomerRemark, pk=pk)

        status = request.POST.get("status")

        if status in ["open", "in_progress", "resolved"]:
            complaint.status = status

            if status == "resolved":
                complaint.resolved_by = request.user

            complaint.save()

            return JsonResponse({
                "success": True,
                "status": complaint.status,
                "updated_at": complaint.updated_at.strftime("%d-%m-%Y %H:%M")
            })

        return JsonResponse({"success": False})



class VendorPaymentPageView(LoginRequiredMixin, View):

    def get(self, request, booking_id):

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            vendor=request.user
        )

        payment = Payment.objects.filter(
            booking=booking
        ).first()

        context = {
            "booking": booking,
            "payment": payment
        }

        return render(
            request,
            "vendor/payment_page.html",
            context
        )

    def post(self, request, booking_id):

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            vendor=request.user
        )

        transaction_id = request.POST.get("transaction_id")
        status = request.POST.get("status")
        screenshot = request.FILES.get("screenshot")
        payment, created = Payment.objects.get_or_create(

            booking=booking,

            defaults={

                "vendor": request.user,
                "service": booking.service,
                "total_amount": 0,
                "status": "pending"
            }
        )

        if status:
            payment.status = status
        if transaction_id:
            payment.transaction_id = transaction_id
        if screenshot:
            payment.screenshot = screenshot

        payment.vendor = request.user
        payment.save()
        messages.success(
            request,
            "Payment Updated Successfully"
        )

        return redirect("vendor_payments")




# admin can approve vendor

class AdminVendorApprovalView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role != "admin":
            return JsonResponse({"error": "Unauthorized"}, status=403)

        vendors = User.objects.filter(role="vendor")\
            .select_related("vendor_profile")\
            .prefetch_related("vendor_profile__services")\
            .order_by("-id")

        q = request.GET.get("q")
        status = request.GET.get("status")

        if q:
            vendors = vendors.filter(first_name__icontains=q)

        if status == "active":
            vendors = vendors.filter(is_active=True)
        elif status == "pending":
            vendors = vendors.filter(is_active=False)
        page_obj = paginate_queryset(request,vendors,10)
        categories = Category.objects.all()

        return render(request, "admin/admin_approve_vendor.html", {
            "vendors": vendors,
            "vendors": page_obj,
            "page_obj": page_obj,
            "categories": categories,
            "q": q,
            "status": status
        })


class VendorActionView(LoginRequiredMixin, View):

    def post(self, request):
        try:
      
            if request.user.role != "admin":
                return JsonResponse({
                    "error": "Unauthorized access"
                }, status=403)

            user_id = request.POST.get("user_id")
            action = request.POST.get("action")

            if not user_id or not action:
                return JsonResponse({
                    "error": "Missing required data"
                }, status=400)

            user = get_object_or_404(User, id=user_id, role="vendor")

            if action == "approve":
                user.is_active = True
                user.save()

                return JsonResponse({
                    "success": True,
                    "msg": "Vendor approved successfully"
                })

            elif action == "deactivate":
                user.is_active = False
                user.save()

                return JsonResponse({
                    "success": True,
                    "msg": "Vendor deactivated successfully"
                })

            elif action == "delete":
                user.delete()

                return JsonResponse({
                    "success": True,
                    "msg": "Vendor deleted successfully"
                })

            else:
                return JsonResponse({
                    "error": "Invalid action type"
                }, status=400)

        except Exception as e:
            return JsonResponse({
                "error": f"Server error: {str(e)}"
            }, status=500)



# admin vendor profile page
class AdminVendorVerifyView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request, id):

        if request.user.role != "admin":
            return HttpResponse("Not allowed")

        vendor = get_object_or_404(
            User,
            id=id,
            role="vendor"
        )

        profile = vendor.vendor_profile

        context = {

            "vendor": vendor,
            "profile": profile

        }

        return render(
            request,
            "admin/vendor_verify.html",
            context
        )

    def post(self, request, id):

        if request.user.role != "admin":
            return HttpResponse("Not allowed")

        vendor = get_object_or_404(
            User,
            id=id,
            role="vendor"
        )

        profile = vendor.vendor_profile

        # TOGGLE VERIFICATION

        if "verify_status" in request.POST:

            profile.is_verified = True

        else:

            profile.is_verified = False

        profile.save()

        return redirect(
            "admin_vendor_verify",
            id=vendor.id
        )
        
        
        
# admin can edit or change the payemnt method

class AdminBookingEditView(View):

    def get(self, request, booking_id):

        if request.user.role != "admin":
            return redirect("/")

        booking = get_object_or_404(Booking, id=booking_id)
        payment = booking.payments.first()

        return render(request, "admin/change_payment.html", {
            "booking": booking,
            "payment": payment
        })

    def post(self, request, booking_id):

        if request.user.role != "admin":
            return redirect("/")

        booking = get_object_or_404(Booking, id=booking_id)
        payment = booking.payments.first()

       
        booking.service_days = request.POST.get("service_days")
        booking.expiry_date = request.POST.get("expiry_date")
        booking.save()

      
        if payment:
            payment.total_amount = request.POST.get("total_amount")
            payment.paid_amount = request.POST.get("paid_amount")
            payment.status = request.POST.get("status")
            payment.save()

        messages.success(request, "Updated successfully")

        return redirect("admin_booking_edit", booking_id=booking.id)
    



def renew_service(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # extend 30 days (or your logic)
    booking.expiry_date = booking.expiry_date + timedelta(days=30)
    booking.save()

    messages.success(request, "Service renewed successfully")

    return redirect("my_orders")   # your pa



# vendor profile
class VendorProfileView(LoginRequiredMixin, View):

    def get(self, request, id):

        if request.user.role != "vendor":

            return redirect("login")

        vendor = get_object_or_404(User,id=id,role="vendor")

        profile, created = VendorProfile.objects.get_or_create(user=vendor)

        categories = Category.objects.all()

        services = CategoryService.objects.filter(

            category=profile.category

        ) if profile.category else CategoryService.objects.none()

        return render(

            request,

            "vendor/vendor_profile.html",

            {

                "vendor": vendor,
                "profile": profile,
                "categories": categories,
                "services": services
            }
        )

    def post(self, request, id):

        if request.user.role != "vendor":

            return redirect("login")

        vendor = get_object_or_404(User,id=id,role="vendor")

        profile, created = VendorProfile.objects.get_or_create(user=vendor)
        category_id = request.POST.get("category")
        vendor.first_name = request.POST.get("first_name")
        vendor.last_name = request.POST.get("last_name")
        vendor.email = request.POST.get("email")
        vendor.save()
        profile.experience = request.POST.get("experience")
        profile.locality = request.POST.get("locality")
        profile.street = request.POST.get("street")
        profile.city = request.POST.get("city")
        profile.postal_code = request.POST.get("postal_code")
        profile.company_name = request.POST.get("company_name")
        profile.company_address = request.POST.get("company_address")
        profile.pan_number = request.POST.get("pan_number")
        profile.license_number = request.POST.get("license_number")

        if request.FILES.get("pan_card"):

            profile.pan_card = request.FILES.get(
                "pan_card"
            )

        if request.FILES.get("license_file"):

            profile.license_file = request.FILES.get(
                "license_file"
            )

        if category_id:
            profile.category = Category.objects.get(
                id=category_id
            )

        profile.save()
        service_ids = request.POST.getlist(
            "services"
        )

        if service_ids:
            profile.services.set(
                service_ids
            )
        return redirect(
            "vendor_profile",
            id=vendor.id
        )
# admin see the vendor profiles   

    
# cutomer track the order

class CustomerTrackingView(LoginRequiredMixin, View):

    def get(self, request):

        bookings = Booking.objects.filter(
            user=request.user
        ).select_related(
            "service",
            "vendor"
        ).order_by("-id")

        status = request.GET.get("status")
        search = request.GET.get("search")

        if status:
            bookings = bookings.filter(status=status)

        if search:

            bookings = bookings.filter(

                Q(order_id__icontains=search) |
                Q(service__s_title__icontains=search)

            )
        page_obj = paginate_queryset(request,bookings,10)
        return render(
            request,
            "customer/customer_tracking.html",
            {
                "bookings": bookings,
                "bookings": page_obj,
                "page_obj": page_obj,
            }
        )
        
class CustomerTrackingDetailView(LoginRequiredMixin, View):

    def get(self, request, id):

        booking = get_object_or_404(

            Booking.objects.select_related(
                "service",
                "vendor"
            ),

            id=id,
            user=request.user

        )

        history = BookingHistory.objects.filter(
            booking=booking
        ).order_by("created_at")

        return render(
            request,
            "customer/tracking_detail.html",
            {
                "booking": booking,
                "history": history
            }
        )


# payments
class CustomerPaymentsView(LoginRequiredMixin, View):

    def get(self, request):

        bookings = (
            Booking.objects.filter(
                user=request.user
            )
            .select_related(
                "service",
                "vendor",
                "category"
            )
            .prefetch_related(
                "payments"
            )
            .order_by("-id")
        )

        payment_status = request.GET.get("payment_status")
        search = request.GET.get("search")

        booking_data = []

        for booking in bookings:

            payment = booking.payments.first()
            if payment_status == "paid":

                if not payment or payment.status != "paid":
                    continue

            elif payment_status == "pending":

                if payment and payment.status == "paid":
                    continue

            if search:

                search_value = search.lower()

                order_match = (
                    search_value in str(booking.order_id).lower()
                )

                service_match = (
                    booking.service and
                    search_value in booking.service.s_title.lower()
                )

                transaction_match = (
                    payment and
                    payment.transaction_id and
                    search_value in payment.transaction_id.lower()
                )

                if not (
                    order_match or
                    service_match or
                    transaction_match
                ):
                    continue

            booking_data.append({
                "booking": booking,
                "payment": payment
            })
        page_obj = paginate_queryset(request,bookings,10)
        context = {
            "booking_data": booking_data,
            "bookings": page_obj,
            "page_obj": page_obj,
            
        }

        return render(
            request,
            "customer/customer_payments.html",
            context
        )
        





