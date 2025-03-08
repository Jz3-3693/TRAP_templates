from http.client import HTTPResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import contact
import numpy as np
import joblib
from.models import AccidentPrediction
import folium

#load pickle files

kmeans=joblib.load("new_app/dataset/kmeans_model_cldtst.pkl")
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


  
# def predict_future_hotspot(request):
#     if request.method == 'POST':
#         if request.POST.get('form_type') == 'predict_future_hotspot':
            
#             longitude = float(request.POST.get('longitude'))
#             latitude = float(request.POST.get('latitude'))
#             Noofvehicle_involved=int(request.POST.get('Noofvehicle_involved'))
#             Severity_Fatal=int(request.POST.get('Severity_Fatal'))
#             Severity_Grievous_Injury=int(request.POST.get('Severity_Grievous_Injury'))
#             Weather_Clear=int(request.POST.get('Weather_Clear'))
#             Weather_Cloudy=int(request.POST.get('Weather_Cloudy'))
#             Weather_Heavy_Rain=int(request.POST.get('Weather_Heavy_Rain'))
#             Weather_Light_Rain=int(request.POST.get('Weather_Light_Rain'))
#             Road_Type_NH=int(request.POST.get('Road_Type_NH'))
#             Road_Type_Residential_Street=int(request.POST.get('Road_Type_Residential_Street'))
            
#             new_input = np.array([[ longitude,latitude,Noofvehicle_involved,
#                            Severity_Fatal, Severity_Grievous_Injury, 
#                            Weather_Clear, Weather_Cloudy, Weather_Heavy_Rain, 
#                            Weather_Light_Rain, Road_Type_NH, Road_Type_Residential_Street]])
#             new_input_scaled = scaler.transform(new_input)
#             predicted_cluster = kmeans.predict(new_input_scaled)[0]
            
#             hotspot = AccidentPrediction(latitude=latitude, longitude=longitude, cluster=predicted_cluster)    
#             hotspot.save()
            
            
#             return redirect('prediction result')
#     return render(request, 'index.html')


def predict_future_hotspot(request):
    context = {"cluster": None, "latitude": None, "longitude": None}

    if request.method == "POST":
        latitude = float(request.POST.get("latitude"))
        longitude = float(request.POST.get("longitude"))
        no_of_vehicles = int(request.POST.get("no_of_vehicles"))
        
        severity_fatal = int(request.POST.get("severity_fatal"))
        severity_grievous = int(request.POST.get("severity_grievous"))
        
        road_type_nh = int(request.POST.get("road_type_nh"))
        road_type_residential = int(request.POST.get("road_type_residential"))
        
        weather_clear = int(request.POST.get("weather_clear"))
        weather_cloudy = int(request.POST.get("weather_cloudy"))
        weather_heavy_rain = int(request.POST.get("weather_heavy_rain"))
        weather_light_rain = int(request.POST.get("weather_light_rain"))
        
        # Prepare input data
        new_input = np.array([[latitude, longitude, no_of_vehicles, severity_fatal, 
                               severity_grievous, road_type_nh, road_type_residential, 
                               weather_clear, weather_cloudy, weather_heavy_rain, weather_light_rain]])

        # Scale the input data
        new_input_scaled = scaler.transform(new_input)

        # Predict the cluster
        predicted_cluster = kmeans.predict(new_input_scaled)[0]

        # Save to database
        hotspot = AccidentPrediction(latitude=latitude, longitude=longitude, cluster=predicted_cluster)
        hotspot.save()

        # Update context to show results on the same page
        context.update({"cluster": predicted_cluster, "latitude": latitude, "longitude": longitude})

    return render(request, "index.html", context)
 
def prediction_result(request):
    latest_prediction= AccidentPrediction.objects.latest('timestamp') if AccidentPrediction.objects.exists() else None
    
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


def map_view(request):

    latitude = request.GET.get("latitude")
    longitude = request.GET.get("longitude")
    cluster = request.GET.get("cluster")  # Get predicted cluster from URL parameters

    if not latitude or not longitude:
        return HttpResponse("Latitude and Longitude are required.", status=400)

    # Get all past accident locations except the latest one
    past_hotspots = AccidentPrediction.objects.exclude(latitude=latitude, longitude=longitude)

    return render(request, "result.html", {
        "latitude": latitude,
        "longitude": longitude,
        "cluster": cluster,
        "past_hotspots": past_hotspots
    })
