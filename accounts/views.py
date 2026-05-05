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
from .models import Booking, BookingHistory, Payment, VendorProfile, CustomerRemark, PrivacyPolicy
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
            return JsonResponse({"error": "Enter valid 10 digit phone number"})

        # ===== VERIFY OTP =====
        if otp:
            if otp != request.session.get("otp") or phone != request.session.get("phone"):
                return JsonResponse({"error": "Invalid OTP"})

            user = User.objects.filter(phone__endswith=phone).first()

            if not user:
                return JsonResponse({
                    "error": "User not found",
                    "redirect": f"/register/?phone={phone}"
                })

            login(request, user)

            #  ROLE BASED REDIRECT
            if next_url:
                redirect_url = next_url
            else:
                if user.role == "superadmin":
                    redirect_url = "/superadmin-dashboard/"
                elif user.role == "admin":
                    redirect_url = "/admin-dashboard/"
                elif user.role == "vendor":
                    redirect_url = "/vendor-dashboard/"
                else:
                    redirect_url = "/customer-dashboard/"

            return JsonResponse({
                "success": True,
                "redirect": redirect_url
            })

        # ===== SEND OTP =====
        user = User.objects.filter(phone__endswith=phone).first()

        if not user:
            return JsonResponse({
                "error": "User not found",
                "redirect": f"/register/?phone={phone}"
            })

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
        return render(request, "customer/register.html")

    def post(self, request):
        data = json.loads(request.body)

        phone = data.get("phone")
        otp = data.get("otp")
        create_user = data.get("create_user")

        if phone and not otp and not create_user:

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({
                    "error": "User already exists, please login",
                    "redirect": "/login/"
                })

            otp_code = str(random.randint(1000, 9999))

            request.session['otp'] = otp_code
            request.session['phone'] = phone
            request.session['otp_verified'] = False

            print("OTP:", otp_code)

            return JsonResponse({
                "success": True,
                "message": "OTP sent"
            })

        if otp and not create_user:

            if (
                otp == request.session.get("otp") and
                phone == request.session.get("phone")
            ):
                request.session['otp_verified'] = True

                return JsonResponse({
                    "success": True,
                    "otp_verified": True
                })

            return JsonResponse({"error": "Invalid OTP"})

        if create_user:

            if not request.session.get("otp_verified"):
                return JsonResponse({"error": "OTP not verified"})

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({
                    "error": "User already exists",
                    "redirect": "/login/"
                })

            user = User.objects.create_user(
                email=data.get("email"),
                password=None,
                role="customer"
            )

            user.first_name = data.get("name")
            user.phone = phone
            user.save()

            request.session.flush()

            return JsonResponse({
                "success": True,
                "redirect": "/login/"
            })

        return JsonResponse({"error": "Invalid request"})


class SendOTPView(View):
    def post(self, request):
        otp = str(random.randint(1000, 9999))
        request.session['otp'] = otp

        print("OTP:", otp)  # replace with API
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

class SuperDashboardView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ['superadmin']

    def get(self, request):
        return render(request, "superadmin/dashboard.html", {'page_title': 'Dashboard'})


# super admin -- create admin(create admin page)


class CreateAdminView(LoginRequiredMixin, View):

    def get(self, request):
        admins = User.objects.filter(role="admin").order_by("-id")

        paginator = Paginator(admins, 10)
        page_number = request.GET.get("page")
        admins = paginator.get_page(page_number)

        return render(request, "superadmin/create_admin.html", {
            "admins": admins,
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


# super admin see all admins/vendors/customers
class AllUsersView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role not in ["superadmin", "admin"]:
            return redirect("login")

        users = User.objects.all().order_by('-id')

        paginator = Paginator(users, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        customer_count = User.objects.filter(role="customer").count()
        admin_count = User.objects.filter(role="admin").count()
        vendor_count = User.objects.filter(role="vendor").count()

        return render(request, "superadmin/all_users.html", {
            "page_obj": page_obj,
            "active_page": "all_users",
            "users": users,
            "customer_count": customer_count,
            "admin_count": admin_count,
            "vendor_count": vendor_count,
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
    allowed_roles = ['customer']

    def get(self, request):

        return render(request, "customer/dashboard.html",)


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


class SetUserStatusView(View):

    def get(self, request, user_id, status):
        user = get_object_or_404(User, id=user_id)

        if user.role == "superadmin":
            return redirect('all_users')

        if status == "active":
            user.is_active = True
        elif status == "inactive":
            user.is_active = False

        user.save()
        return redirect('all_users')


# booking functionality


class BookServiceView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        return render(request, "service/book.html", {
            "categories": categories
        })

    def post(self, request):
        data = json.loads(request.body)
        step = data.get("step")

        if step == "phone":
            phone = data.get("phone")

            user = User.objects.filter(phone=phone).first()
            if not user:
                return JsonResponse({"error": "Register first"})

            otp_code = str(random.randint(1000, 9999))

            request.session["phone"] = phone
            request.session["otp"] = otp_code
            request.session["otp_verified"] = False

            print("OTP:", otp_code)

            return JsonResponse({"success": True})

        if step == "otp":
            otp = data.get("otp")

            if otp != request.session.get("otp"):
                return JsonResponse({"error": "Invalid OTP"})

            request.session["otp_verified"] = True
            return JsonResponse({"success": True})

        if step == "details":

            if not request.session.get("otp_verified"):
                return JsonResponse({"error": "OTP not verified"})

            user = User.objects.filter(
                phone=request.session.get("phone")
            ).first()

            category = Category.objects.get(id=data.get("category_id"))
            service = CategoryService.objects.get(id=data.get("service_id"))

            admin_user = User.objects.filter(role="admin").first()

            vendor_user = User.objects.filter(
                role="vendor",
                services=service
            ).first()

            assigned_user = vendor_user if vendor_user else None

            booking = Booking.objects.create(
                user=user,
                category=category,
                service=service,
                vendor=assigned_user,   # will be None if no vendor
                name=user.first_name,
                phone=user.phone,
                address=data.get("address"),
                problem=data.get("problem"),
                scheduled_date=data.get("date"),
                scheduled_time=data.get("time"),
                status="pending"  # better default
            )
            request.session.flush()

            return JsonResponse({
                "success": True,
                "redirect": "/"
            })

        return JsonResponse({"error": "Invalid request"})


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
        bookings = Booking.objects.filter(user=request.user)
        return render(request, "customer/customer_orders.html", {"bookings": bookings})


class CustomerOrderDetailView(LoginRequiredMixin, View):

    def get(self, request, id):
        booking = Booking.objects.get(id=id, user=request.user)

        history = booking.history.all().order_by("-created_at")

        return render(request, "customer/order_detail.html", {
            "booking": booking,
            "history": history
        })


# admij can assign the lead to vendor
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
        ).select_related("service").order_by("-id")

        return render(request, "vendor/vendor_orders.html", {
            "bookings": bookings
        })

    def post(self, request):
        if "screenshot" in request.FILES:

            booking_id = request.POST.get("booking_id")
            txn = request.POST.get("transaction_id")
            file = request.FILES["screenshot"]

            print("FILE RECEIVED:", file)

            booking = get_object_or_404(Booking, id=booking_id)

            if booking.vendor != request.user:
                return JsonResponse({"error": "Not allowed"}, status=403)

            if booking.status != "completed":
                return JsonResponse({"error": "Complete order first"}, status=400)

            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    "vendor": request.user,
                    "service": booking.service,
                }
            )

            if not created and payment.status == "paid":
                return JsonResponse({"error": "Payment already submitted"}, status=400)

            payment.transaction_id = txn
            payment.screenshot = file
            payment.status = "paid"
            payment.vendor = request.user
            payment.save()

            print("SAVED PATH:", payment.screenshot.path)

            return JsonResponse({"success": True})

        try:
            data = json.loads(request.body)

            booking_id = data.get("booking_id")
            status = data.get("status")

            allowed_status = ["assigned", "progress", "completed"]

            if status not in allowed_status:
                return JsonResponse({"error": "Invalid status"}, status=400)

            booking = get_object_or_404(Booking, id=booking_id)

            if booking.vendor != request.user:
                return JsonResponse({"error": "Not allowed"}, status=403)

            booking.status = status
            booking.save()

            BookingHistory.objects.create(
                booking=booking,
                status=status,
                updated_by=request.user
            )

            return JsonResponse({"success": True})

        except Exception as e:
            print("ERROR:", e)
            return JsonResponse({"error": str(e)}, status=400)


# admin can assigned the lead in vendor
class AdminOrdersView(LoginRequiredMixin, View):

    def get(self, request):

        category_id = request.GET.get("category")
        service_id = request.GET.get("service")
        q = request.GET.get("q")

        bookings = Booking.objects.select_related("service", "vendor")

        if category_id:
            bookings = bookings.filter(service__category_id=category_id)

        if service_id:
            bookings = bookings.filter(service_id=service_id)

        if q:
            bookings = bookings.filter(name__icontains=q)

        categories = Category.objects.all()

        services = CategoryService.objects.all()
        if category_id:
            services = services.filter(category_id=category_id)

        vendors = User.objects.filter(
            role="vendor").prefetch_related("services")

        if service_id:
            vendors = vendors.filter(services__id=service_id)

        elif category_id:
            vendors = vendors.filter(services__category_id=category_id)

        vendors = vendors.distinct()

        return render(request, "admin/admin_orders.html", {
            "bookings": bookings,
            "vendors": vendors,
            "categories": categories,
            "services": services,
            "selected_category": category_id,
            "selected_service": service_id,
            "q": q
        })


# super-admin orders
class SuperAdminOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        bookings = Booking.objects.all().select_related(
            'user', 'service', 'vendor').prefetch_related("history").order_by('-created_at')
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
            bookings = bookings.filter(created_at__date__range=[
                                       start_date, end_date])
        paginator = Paginator(bookings, 10)  # 10 orders per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "bookings": bookings,
            "services": services,
            "vendors": vendors,
            "page_obj": page_obj,
        }
        return render(request, "superadmin/superadmin_orders.html", context)


# order history
class OrderHistoryView(LoginRequiredMixin, View):

    def get(self, request, id):

        if request.user.role == "customer":
            booking = get_object_or_404(
                Booking.objects.select_related("service", "vendor"),
                id=id,
                user=request.user
            )

        elif request.user.role == "vendor":
            booking = get_object_or_404(
                Booking.objects.select_related("service", "vendor"),
                id=id,
                vendor=request.user
            )

        else:
            booking = get_object_or_404(
                Booking.objects.select_related("service", "vendor"),
                id=id
            )

        history = booking.history.all().order_by("-created_at")

        vendor = booking.vendor if booking.vendor and booking.vendor.role == "vendor" else None

        return render(request, "superadmin/order_history.html", {
            "booking": booking,
            "history": history,
            "vendor": vendor
        })

# profile page


class ProfileView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "profile/profile.html")

    def post(self, request):
        user = request.user

        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")

        if not email:
            messages.error(request, "Email is required")
            return redirect("profile")

        user.email = email
        user.address = address
        user.city = city

        user.save()

        messages.success(request, "Profile updated successfully")
        return redirect("profile")


class AdminPaymentsView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["admin", "superadmin"]:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        payments = Payment.objects.select_related(
            "booking",
            "booking__user",      # customer
            "vendor",
            "service"
        ).order_by("-created_at")

        return render(request, "superadmin/admin_payments.html", {
            "payments": payments
        })


# vendor payment view

class VendorPaymentsView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role != "vendor":
            return redirect("login")

        payments = Payment.objects.filter(
            vendor=request.user
        ).order_by('-id')

        return render(request, "vendor/vendor_payments.html", {
            "payments": payments
        })


# invoice number
class PaymentInvoiceView(View):
    def get(self, request, pk):
        payment = get_object_or_404(Payment, id=pk)
        return render(request, "service/invoice.html", {"p": payment})


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

        return render(request, "customer/my_bookings.html", {
            "bookings": bookings
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

        if request.user.is_superuser:
            complaints = CustomerRemark.objects.all().order_by("-created_at")
        else:
            complaints = CustomerRemark.objects.filter(
                user=request.user).order_by("-created_at")

        return render(request, "complaints/list.html", {"complaints": complaints})


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


class PrivacyPolicyView(View):
    def get(self, request):
        policies = PrivacyPolicy.objects.filter(is_active=True)
        return render(request, "privacy_policy/privacy_policy.html", {
            "policies": policies
        })


class PrivacyPolicyListView(View):
    def get(self, request):
        policies = PrivacyPolicy.objects.all().order_by("-id")
        return render(request, "pages/privacy_policy/list.html", {
            "policies": policies
        })


class CreatePrivacyPolicyView(View):

    def get(self, request):
        return render(request, "pages/privacy_policy/create.html")

    def post(self, request):
        title = request.POST.get("title")
        content = request.POST.get("content")
        is_active = request.POST.get("is_active") == "True"

        PrivacyPolicy.objects.create(
            title=title,
            content=content,
            is_active=is_active
        )

        messages.success(request, "Privacy Policy created successfully")
        return redirect("privacy_list")


class UpdatePrivacyPolicyView(View):

    def get(self, request, id):
        policy = PrivacyPolicy.objects.get(id=id)
        return render(request, "pages/privacy_policy/update.html", {
            "policy": policy
        })

    def post(self, request, id):
        policy = PrivacyPolicy.objects.get(id=id)

        policy.title = request.POST.get("title")
        policy.content = request.POST.get("content")
        policy.is_active = request.POST.get("is_active") == "True"
        policy.save()

        messages.success(request, "Privacy Policy updated successfully")
        return redirect("privacy_list")

class DeletePrivacyPolicyView(View):

    def get(self, request, id):
        policy = get_object_or_404(PrivacyPolicy, id=id)
        policy.delete()

        messages.success(request, "Privacy Policy deleted successfully")
        return redirect("privacy_list")
