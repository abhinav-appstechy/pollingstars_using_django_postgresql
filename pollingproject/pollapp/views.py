from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from .models import UserRegisterModel, UserAccountVerificationModel, Poll, Choice, PollRecord
import bcrypt
from django.core.mail import send_mail
from django.template.loader import render_to_string
import datetime
import uuid
from django.utils import timezone
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SITE_URL= os.getenv("SITE_URL")

def send_email(user,email, token):
    url = f"{SITE_URL}/verify/{token}"
    subject = 'Activate Your Account'
    html_message = render_to_string('email_template.html', {'username': user, 'url':url})
    from_email = 'your_email'
    recipient_list = [email]

    send_mail(subject, '', from_email, recipient_list, html_message=html_message)

def hash_password(password):
    # Hash the password using bcrypt's hashpw function
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')  # Convert bytes to string

# Function to check if a provided password matches a hashed password using bcrypt
def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# Create your views here.
def home_page(request):
    all_polls = Poll.objects.all().order_by('-pub_date')
    print(all_polls)
    poll_status = {}
    for poll in all_polls:
        poll_status[poll.id] = "ongoing" if poll.due_date > timezone.now() else "closed"
    
    print(poll_status)
    context = {
        'user_login_status': request.session["user_status"] if "user_status" in request.session else "logged_out" ,
        "activeLink": "Home",
        "all_polls": all_polls,
        "poll_status": poll_status
    }
    return render(request, "homepage.html", context)

def login_page(request):
    return render(request, "login_page.html")


def single_poll_page(request, id):
    if(("user_status" in request.session and request.session["user_status"] == "logged_in") or request.user.is_staff):
        print(id)
        poll = Poll.objects.filter(id=id).first()
        options = Choice.objects.filter(poll_id = id)
        all_options = Choice.objects.filter(poll_id = id)
        is_poll_closed = False
        winner = ""
        max_vote = 0
        current_time = timezone.now()
        if poll.due_date < current_time:
            is_poll_closed = True
            for option in all_options:
                if option.votes > max_vote:
                    max_vote = option.votes
                    winner = option.choice_text
        print(winner)
        options1 = list(Choice.objects.filter(poll_id = id).values())
        poll1 = Poll.objects.filter(id=id).first()
        is_choice_selected = "no"
        if PollRecord.objects.filter(user_id_id=request.session["user_info"]["user_id"], poll_id=id).exists():
            poll_record = PollRecord.objects.filter(user_id_id=request.session["user_info"]["user_id"], poll_id=id).first()
            is_choice_selected = poll_record.choice_id

        print("is_choice_selected",is_choice_selected) 
        json_poll1 = json.dumps({
            "id": poll1.id,
            "question": poll1.question,
            "pub_date": poll1.pub_date.strftime('%Y-%m-%d %H:%M:%S'),
            "due_date": poll1.due_date.strftime('%Y-%m-%d %H:%M:%S')
        })

        context = {
            "poll": poll,
            "is_choice_selected": is_choice_selected,
            "choices": options,
            "choices1": json.dumps(options1),
            "poll_data":json_poll1,
            "is_poll_closed": is_poll_closed,
            "winner": winner,
            'user_login_status': request.session["user_status"] if "user_status" in request.session else "logged_out" ,
        }

        return render(request, "single_poll_page.html", context)
    else:
        return redirect("login_page")


def user_vote_logic(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            print(data.get("option_id"))
            id = data.get("option_id")
            poll_id = data.get("poll_id")
            poll = Poll.objects.filter(id=poll_id).first()
            current_time = timezone.now()
            if poll.due_date < current_time:
                return JsonResponse({'message':'Poll Closed!', 'status': 400}, status = 400)

            print(request.session["user_info"], poll_id)
            if PollRecord.objects.filter(user_id_id=request.session["user_info"]["user_id"], poll_id=poll_id).exists():
                poll_record = PollRecord.objects.filter(user_id_id=request.session["user_info"]["user_id"], poll_id=poll_id).first()
                if poll_record.choice_id == id:
                    return JsonResponse({'message':'Already voted!', 'status': 400}, status = 400)
                else:
                    poll_record.choice_id = id
                    poll_record.save()
            else:
                new_poll_record = PollRecord(choice_id=id, poll_id=poll_id, user_id_id=request.session["user_info"]["user_id"])
                new_poll_record.save()
            if data.get("prevOptionId")!= "no_id":
                prevOptionId = data.get("prevOptionId")
                prevChoice = Choice.objects.filter(id=prevOptionId).first()
                prev_count = prevChoice.votes - 1
                prevChoice.votes-=1
                prevChoice.save()

                choice = Choice.objects.filter(id=id).first()
                count = choice.votes + 1
                choice.votes+=1
                choice.save()
                return JsonResponse({'message':'success', 'status':200, 'new_count':count, 'prev_count':prev_count}, status=200)

            else:
                choice = Choice.objects.filter(id=id).first()
                count = choice.votes + 1
                choice.votes+=1
                choice.save()
                return JsonResponse({'message':'success', 'status':200, 'new_count':count}, status=200)

            
        
    except Exception as e:
        print(e)
        return JsonResponse({'message':'exception', 'status':400}, status=400)

def signup_page(request):
    return render(request, "signup_page.html")

def user_register_logic(request):
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")

            # input validation 
            if not username:
                return JsonResponse({'message': 'Username is required!', 'status': 400}, status=400)
            
            if not email:
                return JsonResponse({'message': 'Email is required!', 'status': 400}, status=400)
            
            if not '@' in email or not '.' in email:
                return JsonResponse({'message': 'Invalid email format', 'status': 400}, status=400)
            
            if UserRegisterModel.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Email already exists', 'status': 400}, status=400)
            
            if not password:
                return JsonResponse({'message': 'Password is required', 'status': 400}, status=400)
            if not (6 <= len(password) <= 128):
                return JsonResponse({'message': 'Password must be between 6 and 128 characters','status': 400}, status=400)

            # end input validation 
            hash_pwd = hash_password(password)
            new_user = UserRegisterModel(username=username, email=email, password=hash_pwd)
            new_user.save()

            unique_id = uuid.uuid4()

            new_token = UserAccountVerificationModel(email=email, token=unique_id)
            new_token.save()
            send_email(username, email, unique_id)
            

            return JsonResponse({'message':'User registered successfully. Please check your email for verification!', 'status':200}, status=200)
        
        else:
            return JsonResponse({'message':'error!', 'status':400}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({'message':'exception', 'status':400}, status=400)


def user_signin_logic(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            # input validation 

            if not email:
                return JsonResponse({'message': 'Email is required!', 'status': 400}, status=400)
            
            if not '@' in email or not '.' in email:
                return JsonResponse({'message': 'Invalid email format', 'status': 400}, status=400)
            
            if not password:
                return JsonResponse({'message': 'Password is required', 'status': 400}, status=400)
            if not (6 <= len(password) <= 128):
                return JsonResponse({'message': 'Password must be between 6 and 128 characters','status': 400}, status=400)

            # end input validation 


            if UserRegisterModel.objects.filter(email=email).exists():
                hash_password = UserRegisterModel.objects.filter(email=email).first().password
                user_info = UserRegisterModel.objects.filter(email=email).first()
                user_status = UserRegisterModel.objects.filter(email=email).first().user_status
                if check_password(password, hash_password):
                    if user_status:
                        request.session["user_status"] = "logged_in"
                        request.session["user_info"] = {
                            "user_id": user_info.id,
                            "username": user_info.username,
                            "email": user_info.email
                        }
                        return JsonResponse({'message': 'User Logged-in Successfully!', 'status': 200}, status=200)
                    else:
                        return JsonResponse({'message': 'Please first verify your account!', 'status': 400}, status=400)
                else:
                    return JsonResponse({'message': 'Password does not mached!', 'status': 400}, status=400)
            else:
                return JsonResponse({'message': 'User not found!', 'status': 400}, status=400)
            
            

        else:
            return JsonResponse({'message':'error!', 'status':400}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({'message':'exception', 'status':400}, status=400)


def verify_user_logic(request, token):
    print(token)
    if UserAccountVerificationModel.objects.filter(token=token).exists():
        data = UserAccountVerificationModel.objects.filter(token=token).first()
        email = data.email
        print(data.created_at)
        created_at = data.created_at

        # Add 5 minutes to the created_at timestamp
        expiration_time = created_at + timedelta(minutes=5)

        # Get the current time in the UTC timezone
        current_time = timezone.now()

        # Check if the expiration time is greater than the current time
        if expiration_time > current_time:
            print("Token is valid. Proceed with verification.")
            user = UserRegisterModel.objects.filter(email=email).first()
            if user.user_status:
                context = {
                    "message": "Already verified"
                }
                return render(request, "verification_status.html", context)
            else:
                user.user_status = True
                user.save()
                context = {
                    "message": "Verified successfully"
                }
                return render(request, "verification_status.html", context)


            # Further logic for token verification...
        else:
            print("Token has expired.")
            context = {
                    "message": "Token expired"
                }
            return render(request, "verification_status.html", context)
            # Handle token expiration...

        
    return JsonResponse({'message':'success', 'status':200}, status=200)


def resend_verification_email(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            token = data.get("old_token")
            if UserAccountVerificationModel.objects.filter(token=token).exists():
                email = UserAccountVerificationModel.objects.filter(token=token).first().email
                username = UserRegisterModel.objects.filter(email=email).first().username
                unique_id = uuid.uuid4()

                new_token = UserAccountVerificationModel(email=email, token=unique_id)
                new_token.save()
                send_email(username, email, unique_id)
                return JsonResponse({'message':'Successfully Resent Verification Email!', 'status':200}, status=200)
            return JsonResponse({'message':'Invalid Token!', 'status':400}, status=400)
        
    except Exception as e:
        print(e)
        return JsonResponse({'message':'exception', 'status':400}, status=400)



def logout_view(request):
    if request.method == "POST":     
        logout(request)
        request.session["user_status"] = "logged_out"
        if "user_info" in request.session:
            del request.session["user_info"]
        return redirect("homepage")

def about_us(request):
    context = {
        "array": [1,1,1,1],
        "activeLink": "AboutUs",
        'user_login_status': request.session["user_status"] if "user_status" in request.session else "logged_out" ,
    }
    return render(request, "aboutus.html", context)

def contact_us(request):
    context = {
        "activeLink": "ContactUs",
        'user_login_status': request.session["user_status"] if "user_status" in request.session else "logged_out" ,
    }
    return render(request, "contactus.html", context)
