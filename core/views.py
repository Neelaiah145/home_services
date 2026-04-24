from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Contact, News, HeroBanner, Category, CategoryService, ServicesCards, Job, ServiceFeedback, Footer
from django.views import View
from datetime import datetime
from django.core.paginator import Paginator
import re
# Create your views here.


class IndexView(View):
    def get(self, request):
        footer = Footer.objects.first()
        news = News.objects.all().order_by('id')
        banners = HeroBanner.objects.all().order_by('id')
        categories = Category.objects.all().order_by('title')
        services_cards = ServicesCards.objects.all().order_by('servicename')
        jobs = Job.objects.all().order_by('title')
        feedbacks = ServiceFeedback.objects.all().order_by('-id')
        return render(request, 'index.html', {'footer': footer, 'news': news, 'banners': banners, 'categories': categories, 'services_cards': services_cards, 'jobs': jobs, 'feedbacks': feedbacks})


class ServicesListView(View):
    def get(self, request, pk):
        footer = Footer.objects.first()
        selected_category = get_object_or_404(Category, pk=pk)
        news = News.objects.all().order_by('id')
        category_services = CategoryService.objects.filter(
            category=selected_category).order_by('s_title')
        paginator = Paginator(category_services, 3)

        page_number = request.GET.get('page')
        category_servicess = paginator.get_page(page_number)

        return render(request, 'serviceslist.html', {
            'selected_category': selected_category,
            'category_servicess': category_servicess,
            'footer': footer,
            'news': news,
        })


class ContactForm(View):

    def get(self, request):
        footer = Footer.objects.first()
        news = News.objects.all().order_by('id')
        return render(request, 'contact.html', {
            'footer': footer,
            'news': news
        })

    def post(self, request):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        message = request.POST.get('message', '').strip()

        errors = {}

        if not name:
            errors['name'] = "Name is required"

        if not email:
            errors['email'] = "Email is required"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors['email'] = "Invalid email format"

        if not phone:
            errors['phone'] = "Phone number is required"
        elif not re.match(r"^[6-9]\d{9}$", phone):
            errors['phone'] = "Enter valid 10-digit phone number"

        if not city:
            errors['city'] = "City is required"

        if not message:
            errors['message'] = "Message cannot be empty"

        footer = Footer.objects.first()
        news = News.objects.all().order_by('id')

        if errors:
            return render(request, 'contact.html', {
                'errors': errors,
                'old': request.POST,
                'footer': footer,
                'news': news
            })

        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            city=city,
            message=message,
            status='pending'
        )

        messages.success(request, "Your request submitted successfully!")

        return redirect('contact')

class ContactListView(View):
    def get(self, request):
        contacts = Contact.objects.all().order_by('-created_at')

        return render(request, 'pages/contact/list.html', {
            'contacts': contacts
        })
    
class ContactUpdateView(View):
    def get(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk)
        return render(request, 'pages/contact/update.html', {
            'contact': contact
        })

    def post(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk)

        status = request.POST.get('status')

        if not status:
            messages.error(request, "Status is required")
            return redirect('contact.update', pk=pk)

        contact.status = status
        contact.save()

        messages.success(request, "Status updated successfully!")
        return redirect('list.contact')

class DeleteContact(View):
    def get(self,request,pk):
        conatct=get_object_or_404(Contact,pk=pk)
        conatct.delete()
        messages.success(request, "Contact  deleted")
        return redirect('list.contact')


class FeedbackForm(View):

    def get(self, request):
        footer = Footer.objects.first()
        news = News.objects.all().order_by('id')
        return render(request, 'feedback.html',{'footer':footer,'news':news})

    def post(self, request):

        service_name = request.POST.get('service_name')
        customer_name = request.POST.get('customer_name')
        customer_type = request.POST.get('customer_type')
        rating = request.POST.get('rating')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if not service_name:
            messages.error(request, "Service name is required")
            return redirect('feedbackform')

        if not customer_name:
            messages.error(request, "Customer name is required")
            return redirect('feedbackform')

        if not customer_type or customer_type == "Select Type":
            messages.error(request, "Please select customer type")
            return redirect('feedbackform')

        if not rating:
            messages.error(request, "Please select rating")
            return redirect('feedbackform')

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, "Invalid rating value")
        except:
            messages.error(request, "Invalid rating value")
            return redirect('feedbackform')

        if not description:
            messages.error(request, "Description is required")
            return redirect('feedbackform')

        ServiceFeedback.objects.create(
            service_name=service_name,
            customer_name=customer_name,
            customer_type=customer_type,
            rating=rating,
            description=description,
            image=image
        )

        messages.success(request, "Feedback submitted successfully")

        return redirect('feedbackform')


class ListFeedback(View):
    def get(self, request):
        feedbacks = ServiceFeedback.objects.all().order_by('-created_at')
        return render(request, 'pages/feedback/list.html', {
            'feedbacks': feedbacks
        })


class DeleteFeedback(View):
    def get(self, request, id):
        feebback = get_object_or_404(ServiceFeedback, id=id)
        feebback.delete()
        messages.success(request, "feedback deleted")
        return redirect('list.feedback')


class DashBoard(View):
    def get(self, request):
        return render(request, 'dashboardbase.html')


class NewsListView(View):
    def get(self, request):
        news = News.objects.all().order_by('-created_at')
        return render(request, 'pages/news/list_news.html', {'news': news})


class CreateNews(View):
    def get(self, request):
        return render(request, 'pages/news/create_news.html')

    def post(self, request):
        news_headline = request.POST.get('news_headline')

        news = News.objects.create(
            content=news_headline

        )
        news.save()
        return redirect('news.list')


class UpdateNews(View):

    def get(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        return render(request, 'pages/news/update_news.html', {'news': news})

    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk)

        news.content = request.POST.get('update_headline')
        news.create_date = datetime.now()
        news.save()

        return redirect('news.list')


class DeleteNews(View):
    def get(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        news.delete()
        return redirect('news.list')

# hero section


class ListBanner(View):
    def get(self, request):
        banner = HeroBanner.objects.all()
        return render(request, 'pages/hero_section/list_banner.html', {'banner': banner})


class CreateBanner(View):
    def get(self, request):
        return render(request, 'pages/hero_section/create_banner.html')

    def post(self, request):
        image = request.FILES.get('image')
        heading = request.POST.get('heading')
        sub_heading = request.POST.get('sub_heading')
        banner_save = HeroBanner.objects.create(
            heading=heading,
            sub_heading=sub_heading,
            image=image
        )
        banner_save.save()

        return redirect("list.banner")


class UpdateBanner(View):

    def get(self, request, pk):
        banner = get_object_or_404(HeroBanner, pk=pk)
        return render(request, 'pages/hero_section/update_banner.html', {'banner': banner})

    def post(self, request, pk):
        banner = get_object_or_404(HeroBanner, pk=pk)

        banner.heading = request.POST.get('heading')
        banner.sub_heading = request.POST.get('sub_heading')

        image = request.FILES.get('image')
        if image:
            banner.image = image

        banner.save()

        return redirect('list.banner')


class DeleteBanner(View):
    def get(self, request, pk):
        banner = get_object_or_404(HeroBanner, pk=pk)
        banner.delete()
        return redirect('list.banner')


class ListCategory(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'pages/categories/list.html', {'categories': categories})


class CreateCategory(View):
    def get(self, request):
        return render(request, 'pages/categories/create.html')

    def post(self, request):
        icon = request.FILES.get('icon')
        title = request.POST.get('title')
        description = request.POST.get('description')
        badge = request.POST.get('badge')
        tags = request.POST.get('tags')
        category_about_des = request.POST.get('category_about_des')
        banner_img = request.FILES.get('banner_image')
        category_about_img = request.FILES.get('category_about_img')

        Category.objects.create(
            icon=icon,
            title=title,
            description=description,
            badge=badge,
            tags=tags,
            category_about_des=category_about_des,
            category_about_img=category_about_img,
            banner_image=banner_img,
        )
        return redirect('list.category')


class UpdateCategory(View):

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        return render(request, 'pages/categories/update.html', {
            'category': category
        })

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)

        # Text fields
        category.title = request.POST.get('title')
        category.description = request.POST.get('description')
        category.badge = request.POST.get('badge')
        category.tags = request.POST.get('tags')
        category.category_about_des = request.POST.get('category_about_des')

        # Image fields (ONLY update if new file uploaded)
        if request.FILES.get('icon'):
            category.icon = request.FILES.get('icon')

        if request.FILES.get('category_about_img'):
            category.category_about_img = request.FILES.get(
                'category_about_img')

        if request.FILES.get('banner_image'):
            category.banner_image = request.FILES.get('banner_image')

        category.save()

        return redirect('list.category')


class DeleteCaregory(View):
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect('list.category')


class ListCategoryService(View):
    def get(self, request):
        categories = Category.objects.all()

        category_id = request.GET.get('category')
        services = None
        selected_category = None

        if category_id:
            selected_category = Category.objects.filter(id=category_id).first()
            services = CategoryService.objects.filter(category_id=category_id)

        return render(request, 'pages/categoryservice/list.html', {
            'categories': categories,
            'services': services,
            'selected_category': selected_category
        })


class CreateCategoryService(View):

    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'pages/categoryservice/create.html', {
            'categories': categories
        })

    def post(self, request):
        category_id = request.POST.get('category')

        if not category_id:
            return redirect('add.categories.service')

        category = get_object_or_404(Category, id=category_id)

        CategoryService.objects.create(
            category=category,
            s_tag=request.POST.get('s_tag'),
            s_title=request.POST.get('s_title'),
            s_desc=request.POST.get('s_desc'),
            image=request.FILES.get('image')
        )

        if 'save_add_more' in request.POST:
            return redirect('add.categories.service')

        return redirect('list.category.services')


class UpdateCategoryService(View):
    def get(self, request, id):
        services = get_object_or_404(CategoryService, id=id)
        return render(request, 'pages/categoryservice/update.html', {'services': services})

    def post(self, request, id):
        services = get_object_or_404(CategoryService, id=id)

        services.s_tag = request.POST.get('s_tag')
        services.s_title = request.POST.get('s_title')
        services.s_desc = request.POST.get('s_desc')
        image = request.FILES.get('image')
        if image:
            services.image = image
        services.save()
        return redirect('list.category.services')


class DeleteCategoryService(View):
    def get(self, request, id):
        service = get_object_or_404(CategoryService, id=id)
        service.delete()
        return redirect('list.category.services')


class ListServices(View):
    def get(self, request):
        services = ServicesCards.objects.all()
        return render(request, 'pages/services/list.html', {'services': services})


class CreateService(View):
    def get(self, request):
        return render(request, 'pages/services/create.html')

    def post(self, request):
        servicename = request.POST.get('servicename')
        serviceicon = request.FILES.get('serviceicon')
        service_image = request.FILES.get('service_image')

        ServicesCards.objects.create(
            servicename=servicename,
            serviceicon=serviceicon,
            service_image=service_image,
        )
        if 'save_add_more' in request.POST:
            return redirect('add.services')

        return redirect('services.list')


class UpdateServices(View):
    def get(self, request, id):
        services = get_object_or_404(ServicesCards, id=id)
        return render(request, 'pages/services/update.html', {'services': services})

    def post(self, request, id):
        services = get_object_or_404(ServicesCards, id=id)
        services.servicename = request.POST.get('servicename')

        if request.FILES.get('serviceicon'):
            services.serviceicon = request.FILES.get('serviceicon')
        if request.FILES.get('service_image'):
            services.service_image = request.FILES.get('service_image')
        services.save()
        return redirect('services.list')


class DeleteServices(View):
    def get(self, request, id):
        services = get_object_or_404(ServicesCards, id=id)
        services.delete()
        return redirect('services.list')


class ListJobs(View):
    def get(self, request):
        jobs = Job.objects.all().order_by('-created_at')
        return render(request, 'pages/jobs/list.html', {'jobs': jobs})


class CreateJob(View):

    def get(self, request):
        return render(request, 'pages/jobs/create.html')

    def post(self, request):
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        job_type = request.POST.get('job_type')
        work_mode = request.POST.get('work_mode')
        icon = request.FILES.get('icon')

        if not title or not description:
            messages.error(request, "Title and Description are required")
            return render(request, 'pages/jobs/create.html')

        Job.objects.create(
            title=title,
            description=description,
            status=status,
            job_type=job_type,
            work_mode=work_mode,
            icon=icon,
        )

        messages.success(request, "Job created successfully!")

        return redirect('list.jobs')


class UpdateJob(View):
    def get(self, request, id):
        job = get_object_or_404(Job, id=id)
        return render(request, 'pages/jobs/update.html', {'job': job})

    def post(self, request, id):
        job = get_object_or_404(Job, id=id)

        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.status = request.POST.get('status')
        job.job_type = request.POST.get('job_type')
        job.work_mode = request.POST.get('work_mode')

        if request.FILES.get('icon'):
            job.icon = request.FILES.get('icon')

        job.save()

        return redirect('list.jobs')


class DeleteJob(View):
    def get(self, request, id):
        job = get_object_or_404(Job, id=id)
        job.delete()
        return redirect('list.jobs')


class ListFooter(View):
    def get(self, request):
        footers = Footer.objects.all().order_by('-id')
        return render(request, 'pages/footer/list.html', {'footers': footers})


class CreateFooter(View):

    def get(self, request):
        return render(request, 'pages/footer/create.html')

    def post(self, request):
        logo_image = request.FILES.get('logo_image')
        footer_description = request.POST.get('footer_description')
        phone_num = request.POST.get('phone_num')
        whatsapp_num = request.POST.get('whatsapp_num')
        email = request.POST.get('email')
        address = request.POST.get('address')

        facebook = request.POST.get('facebook')
        instagram = request.POST.get('instagram')
        twitter = request.POST.get('twitter')
        whatsapp = request.POST.get('whatsapp')

        errors = []

        if not footer_description:
            errors.append("Footer description is required")

        if not phone_num:
            errors.append("Phone number is required")
        elif not phone_num.isdigit():
            errors.append("Phone number must contain only digits")

        if not whatsapp_num:
            errors.append("WhatsApp number is required")
        elif not whatsapp_num.isdigit():
            errors.append("WhatsApp number must contain only digits")

        if not email:
            errors.append("Email is required")

        if not address:
            errors.append("Address is required")

        if errors:
            for error in errors:
                messages.error(request, error)

            return render(request, 'pages/footer/create.html')

        Footer.objects.create(
            logo_image=logo_image,
            footer_description=footer_description,
            phone_num=phone_num,
            whatsapp_num=whatsapp_num,
            email=email,
            address=address,
            facebook=facebook,
            instagram=instagram,
            twitter=twitter,
            whatsapp=whatsapp,
        )

        messages.success(request, "Footer created successfully ")
        return redirect('list.footer')


class UpdateFooter(View):

    def get(self, request, id):
        footer = get_object_or_404(Footer, id=id)
        return render(request, 'pages/footer/update.html', {'footer': footer})

    def post(self, request, id):
        footer = get_object_or_404(Footer, id=id)

        logo_image = request.FILES.get('logo_image')
        footer_description = request.POST.get('footer_description')
        phone_num = request.POST.get('phone_num')
        whatsapp_num = request.POST.get('whatsapp_num')
        email = request.POST.get('email')
        address = request.POST.get('address')

        facebook = request.POST.get('facebook')
        instagram = request.POST.get('instagram')
        twitter = request.POST.get('twitter')
        whatsapp = request.POST.get('whatsapp')

        errors = []

        if not footer_description:
            errors.append("Footer description is required")

        if not phone_num:
            errors.append("Phone number is required")
        elif not phone_num.isdigit():
            errors.append("Phone number must contain only digits")
        elif len(phone_num) < 10 or len(phone_num) > 15:
            errors.append("Phone number must be 10–15 digits")

        if not whatsapp_num:
            errors.append("WhatsApp number is required")
        elif not whatsapp_num.isdigit():
            errors.append("WhatsApp number must contain only digits")

        if not email:
            errors.append("Email is required")

        if not address:
            errors.append("Address is required")

        if errors:
            for error in errors:
                messages.error(request, error)

            return render(request, 'pages/footer/update.html', {'footer': footer})

        footer.footer_description = footer_description
        footer.phone_num = phone_num
        footer.whatsapp_num = whatsapp_num
        footer.email = email
        footer.address = address

        footer.facebook = facebook
        footer.instagram = instagram
        footer.twitter = twitter
        footer.whatsapp = whatsapp

        if logo_image:
            footer.logo_image = logo_image

        footer.save()

        messages.success(request, "Footer updated successfully ")
        return redirect('list.footer')


class DeleteFooter(View):
    def get(self, request, id):
        footer = get_object_or_404(Footer, id=id)
        footer.delete()
        messages.success(request, 'footer item deleted successfully')
        return redirect('list.footer')
