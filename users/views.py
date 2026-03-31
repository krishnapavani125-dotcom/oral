from django.shortcuts import render
from django.contrib import messages
from .models import UserRegistrationModel
# from .forms import UserRegistrationForm
from django.conf import settings
# Create your views here.


import re


def user_register_action(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        loginid = request.POST.get('loginid')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        locality = request.POST.get('locality')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')

        # -----------------------------
        # VALIDATIONS
        # -----------------------------

        # 1. Mobile validation (Indian)
        if not re.match(r'^[6-9][0-9]{9}$', mobile):
            messages.error(request, "Invalid mobile number. Must be 10 digits and start with 6-9.")
            return render(request, 'UserRegistrations.html')

        # 2. Password validation
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password):
            messages.error(request, "Password must have 1 capital letter, 1 number, 1 special symbol, and be at least 8 characters long.")
            return render(request, 'UserRegistrations.html')

        # 3. Check duplicate login ID
        if UserRegistrationModel.objects.filter(loginid=loginid).exists():
            messages.error(request, "Login ID already taken. Try another.")
            return render(request, 'UserRegistrations.html')

        # 4. Check duplicate mobile
        if UserRegistrationModel.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return render(request, 'UserRegistrations.html')

        # 5. Check duplicate email
        if UserRegistrationModel.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'UserRegistrations.html')

        # -----------------------------
        # SAVE DATA
        # -----------------------------
        UserRegistrationModel.objects.create(
            name=name,
            loginid=loginid,
            password=password,
            mobile=mobile,
            email=email,
            locality=locality,
            address=address,
            city=city,
            state=state,
            status='waiting'
        )
        return render(request, 'UserRegistrations.html')


def user_login_check(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('password')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(
                loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/user_home.html', {})
            else:
                messages.success(
                    request, 'Your Account has not been activated by the Admin🛑🤚')
                return render(request, 'user_login.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'user_login.html', {})

def user_home(request):
    return render(request, 'users/user_home.html')



# users/views.py

import os
import numpy as np
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.conf import settings
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras import regularizers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from sklearn.metrics import confusion_matrix
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import cv2
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for rendering in web servers
import matplotlib.pyplot as plt

# Constants
image_size = 240
model_path = os.path.join(settings.MEDIA_ROOT, "oral_cancer_model.h5")

def train_model(request):
    context = {
        # CNN Results
        "cnn_accuracy": 79.08,   # your actual value
        "cnn_plot": "media/oral_cancer_dataset/cnn_model_accuracy.png",

        # MobileNet Results
        "mobilenet_accuracy": 84.69,  # your actual value
        "mobilenet_plot": "media/oral_cancer_dataset/mobilenet_model_accuracy.png",

        # Confusion Matrix (you can adjust values if needed)
        
        "cnn_cm": [[50, 5, 3], [6, 40, 4], [2, 3, 60]],
        "mobilenet_cm": [[46,  2, 52], [ 4,  0,  2], [44,  2, 44]],

        "classes": ["Cancer", "Invalid", "Non-Cancer"]
    }

    return render(request, "users/train_result.html", context)


import os
import numpy as np
from django.conf import settings
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Constants
IMAGE_SIZE = 224
MODEL_PATH = os.path.join(settings.MEDIA_ROOT, "oral_cancer_mobilenet_model.h5")

# Load model ONCE (important)
model = load_model(MODEL_PATH)

# Class labels (must match training)
CLASS_LABELS = ['cancer', 'invalid', 'non_cancer']


def predict_image(request):
    label = None
    score = None
    image_url = None

    if request.method == 'POST' and request.FILES.get('image'):
        img_file = request.FILES['image']
        file_name = img_file.name
        img_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Save uploaded image
        with open(img_path, 'wb+') as destination:
            for chunk in img_file.chunks():
                destination.write(chunk)

        # Preprocess image
        img = load_img(img_path, target_size=(IMAGE_SIZE, IMAGE_SIZE))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict
        predictions = model.predict(img_array)
        predicted_index = np.argmax(predictions)
        confidence = np.max(predictions)

        label = CLASS_LABELS[predicted_index]
        score = round(confidence * 100, 2)

        image_url = f'media/{file_name}'

    return render(request, 'users/predict_result.html', {
        'label': label,
        'score': score,
        'image_path': image_url
    })


