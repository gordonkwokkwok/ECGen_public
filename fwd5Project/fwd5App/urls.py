from django.urls import path 
from . import views 

urlpatterns = [ 
    path('', views.home, name='home'), 
    path('signup/', views.signUpFormView, name='forms'), 
    path('user/', views.user, name='user interface'), 
    path('register/', views.register_request, name='register'), 
    path('login/', views.login_request, name='login'), 
    path('logout/', views.logout_request, name='logout'), 
    path('about/', views.about, name='about'), 
    path('tools/', views.tool, name='tools'), 
    path('price/', views.price, name='price'), 
    path('blog/', views.blog, name='blog'), 
    path('contact/', views.contact, name='contact'), 
    path('cover-letter-auto-generator/', views.coverLetterAutoGenerator, name='cover letter auto generator'), 
    path('test/', views.test, name='test'), 
    path('download-cover-letter/', views.download_cover_letter, name='download_cover_letter'),
    path('config/', views.stripe_config, name='stripe config'),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.SuccessView.as_view()),
    path('cancelled/', views.CancelledView.as_view()),
    path('webhook/', views.stripe_webhook),
    #path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
]
