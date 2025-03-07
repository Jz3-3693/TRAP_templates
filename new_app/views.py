from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import contact
import numpy as np
import joblib
from.models import AccidentPrediction

#load pickle files

kmeans=joblib.load("new_app/dataset/kmeans_label_cldtst.pkl")
scaler=joblib.load("new_app/dataset/kmeans_scaler_cldtst.pkl")

# Login page view
def login(request):
    return render(request, 'login.html')

# Home page view
def home(request):
    return render(request, 'home.html')

# Index page view
def index(request):
    return render(request, 'index.html')

# Register view
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('rusnm')
        email = request.POST.get('remail')
        password = request.POST.get('regpass')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_view')
        else:
            # Create user and save to db
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account successfully created. Please login!')
            return redirect('login_view')
    
    return render(request, 'login.html', {'form_type': 'register'})

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate User
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Incorrect username or password')
    
    return render(request, 'login.html', {'form_type': 'login'})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('login')
#contact Us view
def contact_us(request):
    if request.method == 'POST':
       if request.POST.get('form_type') == 'contact_view':
    
         email = request.POST.get('email')
         name = request.POST.get('name')
         message = request.POST.get('message')
         if not name or not email or not message:
             messages.error(request,'Please fill all filds')
         else:
            info=contact.objects.create(name=name, email=email, message=message)
            info.save()
            messages.success(request, 'Message uploaded')
            return redirect('contact_us') 
    return render(request, 'home.html')


  
def predict_future_hotspot(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'accident_prediction':
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            Noofvehicle_involved=int(request.POST.get('Noofvehicle_involved'))
            Severity_Fatal=int(request.POST.get('Severity_Fatal'))
            Severity_Grievous_Injury=int(request.POST.get('Severity_Grievous_Injury'))
            Weather_Clear=int(request.POST.get('Weather_Clear'))
            Weather_Cloudy=int(request.POST.get('Weather_Cloudy'))
            Weather_Heavy_Rain=int(request.POST.get('Weather_Heavy_Rain'))
            Weather_Light_Rain=int(request.POST.get('Weather_Light_Rain'))
            Road_Type_NH=int(request.POST.get('Road_Type_NH'))
            Road_Type_Residential_Street=int(request.POST.get('Road_Type_Residential_Street'))
            
            new_input = np.array([[latitude, longitude, Noofvehicle_involved,
                           Severity_Fatal, Severity_Grievous_Injury, 
                           Weather_Clear, Weather_Cloudy, Weather_Heavy_Rain, 
                           Weather_Light_Rain, Road_Type_NH, Road_Type_Residential_Street]])
            new_input_scaled = scaler.transform(new_input)
            predicted_cluster = kmeans.predict(new_input_scaled)[0]
            
            hotspot = AccidentPrediction(latitude=latitude, longitude=longitude, cluster=predicted_cluster)    
            hotspot.save()
            
            
            return redirect('prediction result')
    return render(request, 'index.html')
 
def prediction_result(request):
    latest_prediction=Acdident_Prediction.objects.latest('timestamp') if Accident_Prediction.objects.exists() else None
    
    if latest_prediction:
        context
        {
            'latitude':latest_prediction.latitude,
            'longitude':latest_prediction.longitude,
            'cluster':latest_prediction.cluster
        }
    else:
        context={"error:""No predictionns availabe yet."}
    return render(request,"index.html",context)