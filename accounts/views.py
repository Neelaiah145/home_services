from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import User
import random
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from accounts.mixins import RoleRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q



User = get_user_model()

class LoginView(View):

    def get(self, request):
        return render(request, "customer/customer_login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        service_id = request.GET.get("service_id")

   
        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):

            login(request, user)

          
            if service_id:
                request.session['service_id'] = service_id
                return redirect("book_service")

            if user.role == "superadmin":
                return redirect("superadmin_dashboard")
            elif user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role == "vendor":
                return redirect("vendor_dashboard")
            else:
                return redirect("customer_dashboard")


        if not User.objects.filter(email=email).exists():
            return redirect(f"/register/?email={email}&service_id={service_id}")

        return render(request, "customer/customer_login.html", {
            "error": "Invalid credentials"
        })







class RegisterView(View):

    def get(self, request):
        return render(request, "customer/register.html")

    def post(self, request):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        user = User.objects.create_user(
        
            email=email,
            password=password,
            role="customer"
        )

        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.save()

        login(request, user)

        service_id = request.GET.get("service_id")
        if service_id:
            request.session['service_id'] = service_id
            return JsonResponse({"redirect": "/book-service/"})

        return JsonResponse({"redirect": "/login/"})







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



class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        auth_logout(request)
        return redirect("login")

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# ====================================================================================================
# super admin classes
# ======================================================================================================


# super admin -- dashboard page
class CustomerDashboardView(LoginRequiredMixin,RoleRequiredMixin, View):
    allowed_roles = ['customer']

    def get(self, request):
    
        return render(request, "customer/dashboard.html",)





# super admin -- create admin(create admin page)
class CreateAdminView(LoginRequiredMixin, View):

    def get(self, request):
        admins = User.objects.filter(role="admin")
        return render(request, "superadmin/create_admin.html", {"admins": admins})

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

         
            if not all([first_name, email, phone, password]):
                return JsonResponse({"error": "All fields required"}, status=400)

            if password != confirm_password:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

            if not request.session.get("otp_verified"):
                return JsonResponse({"error": "Phone not verified"}, status=400)

        
            user = User(
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
            print("ERROR:", str(e))  
            return JsonResponse({"error": str(e)}, status=500)


# super admin see all admins/vendors/customers
class AllUsersView(LoginRequiredMixin, View):

    def get(self, request):

        if request.user.role != "superadmin":
            return redirect("login")

        return render(request, "superadmin/all_users.html", {
            "active_page": "all_users"
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

        users = users.order_by("-id")   # optional

        data = [{
            "name": f"{u.first_name} {u.last_name}",
            "email": u.email,
            "phone": u.phone,
            "role": u.role
        } for u in users]

        return JsonResponse({"users": data})

        


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







# ====================================================================================================
# admin classes
# ======================================================================================================

# admin dashboard page
class AdminDashboardView(LoginRequiredMixin,RoleRequiredMixin, View):
    allowed_roles = ['admin']

    def get(self, request):
        return render(request, "admin/dashboard.html")


# admin create vendor


class CreateVendorView(LoginRequiredMixin, View):

    def get(self, request):
 
        if request.user.role != "admin":
            return JsonResponse({"error": "Unauthorized"}, status=403)

        vendors = User.objects.filter(role="vendor")
        return render(request, "admin/create_vendor.html", {"vendors": vendors})

    def post(self, request):
        try:
            if request.user.role != "admin":
                return JsonResponse({"error": "Unauthorized"}, status=403)

            first_name = request.POST.get("first_name") 
            last_name = request.POST.get("last_name") 
            email = request.POST.get("email") 
            phone = request.POST.get("phone") 
            password = request.POST.get("password") 
            confirm_password = request.POST.get("confirm_password") 

          
            if not first_name or not email or not phone or not password:
                return JsonResponse({"error": "All fields required"}, status=400)

            if password != confirm_password:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

            if not request.session.get("otp_verified"):
                return JsonResponse({"error": "Phone not verified"}, status=400)

       
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role="vendor",
                created_by=request.user  
            )

            user.set_password(password)
            user.save()

            request.session.pop("otp_verified", None)
            request.session.pop("otp", None)

            return JsonResponse({"status": "success"})

        except Exception as e:
            import traceback
            print("ERROR:", e)
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)


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





















class VendorDashboardView(LoginRequiredMixin,RoleRequiredMixin, View):
    allowed_roles = ['vendor']

    def get(self, request):
        # bookings = Booking.objects.filter(vendor=request.user)
        return render(request, "vendor/dashboard.html")




class SuperDashboardView(LoginRequiredMixin,RoleRequiredMixin, View):
    allowed_roles = ['superadmin']

    def get(self, request):
        return render(request, "superadmin/dashboard.html")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    




from .models import Service,Booking


class CreateServiceView(View):

    def get(self, request):
        services = Service.objects.all().order_by("-id")   
        return render(request, "superadmin/create_service.html", {
            "services": services
        })

    def post(self, request):
        Service.objects.create(
            name=request.POST.get("name"),
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            image=request.FILES.get("image")
        )
        return redirect("create_service")   

class UpdateServiceView(View):

    def get(self, request, id):
        service = Service.objects.get(id=id)

        return render(request, "superadmin/update_service.html", {
            "service": service
        })

    def post(self, request, id):
        service = Service.objects.get(id=id)

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

        Service.objects.filter(id=service_id).delete()

        return JsonResponse({"status": "deleted"})























class ServiceListView(View):

    def get(self, request):
        services = Service.objects.all()
        return render(request, "service/service_list.html", {"services": services})
    
    

class ServiceDetailView(View):

    def get(self, request, id):
        service = Service.objects.get(id=id)
        return render(request, "service/detail.html", {"service": service})

    def post(self, request, id):
        request.session["service_id"] = id
        return redirect("book_service")
    
    

class BookServiceView(View):

    def get(self, request):
        service_id = request.session.get("service_id")

        if not service_id:
            return redirect("service_list")

        service = Service.objects.get(id=service_id)

        return render(request, "service/book.html", {"service": service})


    def post(self, request):

        if not request.session.get("otp_verified"):
            return JsonResponse({"error": "OTP not verified"}, status=400)

        service_id = request.session.get("service_id")

        if not service_id:
            return JsonResponse({"error": "Invalid session"}, status=400)

        service = Service.objects.get(id=service_id)

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        address = request.POST.get("address")
        problem = request.POST.get("problem")

    
        email = f"user_{phone}@temp.com"


        user = User.objects.filter(email=email).first()

        if not user:
            user = User.objects.create_user(
                email=email,
                password=password,
                phone=phone,
                role="customer"
            )
        else:
          
            user.phone = phone
            user.save()

   
        login(request, user)

    
        Booking.objects.create(
            user=user,
            service=service,
            name=name,
            phone=phone,
            address=address,
            problem=problem,
        )

        request.session.pop("service_id", None)
        request.session.pop("otp_verified", None)

        return JsonResponse({"status": "success"})
    
    



class BookingSuccessView(View):

    def get(self, request):
        return render(request, "service/order_success.html")