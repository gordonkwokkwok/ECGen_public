import openai
from django.shortcuts import render, redirect
from .forms import ProfileForm
from django.http import FileResponse

# Create your views here.
from django.http import HttpResponse 
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
# for payment
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
import stripe
import logging

# how to initial the value MyModel(models.Model) once a new customer successfully registrated?
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import userModel
from django.utils import timezone

# Update model after confirmed payment
from datetime import datetime
from dateutil.relativedelta import relativedelta

# download the cover letter
from django.template.loader import get_template
from django.utils.encoding import smart_str

def home(request):
    return render(request, "home.html")

def tool(request):
    return render(request, "tool.html")

def price(request):
    return render(request, "price.html")

def blog(request):
    return render(request, "blog.html")

def contact(request):
    return render(request, "contact.html")

def signUpFormView(request):
    form = signUpForm()
    if request.method == 'POST':
        form = signUpForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    messages.success(request, "Hello, Cover Letter." )
    return render(request, "signUpForm.html", context)

@login_required
def user(request):
    user_model = userModel.objects.get(user=request.user)
    
    remaining_days = (user_model.serviceExpireDate - timezone.now().date()).days if user_model.serviceExpireDate else 0
    context = {
        'user_model': user_model,
        'remaining_days': remaining_days,
    }
    now = timezone.now().date()
    
    return render(request, "user/home.html", context)

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("/login/")  # pay attention
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = NewUserForm()
    return render (request=request, template_name="register.html", context={"register_form":form})

# 


# 
def login_request(request):
    if request.user.is_authenticated:
        return redirect("/user/")
    elif request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("/user/") # Go to user page
            else:messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	# success = messages.info(request, "You have successfully logged out.") 
	return redirect('home') # Back to home page

def about(request):
    return render(request, "about.html")

@login_required
def coverLetterAutoGenerator(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            openai.api_key = settings.OPENAI_API_KEY
            model_engine = "text-davinci-003"
            prompt = (f"Write a cover letter. I'm applying for the {profile.job_title} position at your company.\n"
                      f"Here is job description: {profile.job_description}")
            completions = openai.Completion.create(
                engine=model_engine,
                prompt=prompt,
                max_tokens=3800,
                n=1,
                stop=None,
                temperature=0.5,
            )
            message = completions.choices[0].text
            
            # Update freeTrial status
            user_model = userModel.objects.get(user=request.user)
            user_model.freeTrial = False
            user_model.save()
            
            return render(request, 'user/coverLetterAutoGeneratorOutput.html', {'message': message})
    else:
        form = ProfileForm()
    return render(request, 'user/coverLetterAutoGenerator.html', {'form': form})

def test(request):
    # form = 
    return render(request, 'coverLetterAutoGeneratorOutput.html')

# def download_cover_letter(request):
#     response = FileResponse(open('generated_cover_letter.txt', 'rb'))
#     response['content_type'] = 'application/txt'
#     response['Content-Disposition'] = 'attachment; filename="generated_cover_letter.txt"'
#     return response

@csrf_exempt
def download_cover_letter(request):
    # Your code to generate the message goes here
    message = "This is my cover letter."

    # Render the message as a file using a Django template
    template = get_template('cover_letter.txt')
    context = {'message': message}
    file_content = template.render(context)

    # Return a response with the file as a download attachment
    response = HttpResponse(smart_str(file_content), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="cover_letter.txt"'
    return response

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://3.112.60.141:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price': 'price_1MdvJrLFRjp8EjeDxDXQTss4',
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelledView(TemplateView):
    template_name = 'cancelled.html'

# One of the easiest ways to get notified when the payment goes through is to use a callback or so-called Stripe webhook.
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    logger = logging.getLogger(__name__)
    logger.info('Received Stripe webhook')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'charge.succeeded':
        charge_id = event['data']['object']['id']
        charge = stripe.Charge.retrieve(charge_id)
        customer_id = charge.customer

        # Retrieve all userModel objects associated with the customer who made the payment
        user_models = userModel.objects.filter(stripe_customer_id=customer_id)
        print(user_models)
        # Update the serviceExpireDate field to 1 month later from the current date for each user_model
        now = timezone.now().date()
        for user_model in user_models:
            user_model.serviceExpireDate = now + relativedelta(months=1)
            user_model.freeTrial = False
            user_model.save()

        return HttpResponse(status=200)


# how to initial the value MyModel(models.Model) once a new customer successfully registrated?
@receiver(post_save, sender=User)
def create_userModel(sender, instance, created, **kwargs):
    if created:
        # Create a new instance of MyModel with the desired initial values
        mymodel = userModel.objects.create(user=instance, serviceExpireDate=None)
        # ... set other initial values as needed ...  
