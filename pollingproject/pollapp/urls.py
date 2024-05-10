from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name="homepage"),
    path('poll/<int:id>/', views.single_poll_page, name="single_poll_page"),
    path('about-us', views.about_us, name="about_us"),
    path('contact-us', views.contact_us, name="contact_us"),
    path('logout', views.logout_view , name="logout"),
    path('login', views.login_page , name="login_page"),
    path('signup', views.signup_page , name="signup_page"),
    path('user-register', views.user_register_logic , name="user_register"),
    path('user-signin', views.user_signin_logic , name="user_login"),
    path('verify/<str:token>/', views.verify_user_logic , name="verify_user"),
    path('resend-verification-email', views.resend_verification_email , name="resend_verification_email"),
    path('user-vote-logic', views.user_vote_logic , name="user_vote"),
    
    
    
]