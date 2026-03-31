from django.urls import path
from users import views as users_views

urlpatterns = [
    path('user_register_action/', users_views.user_register_action,
         name='user_register_action'),
    path("user_login_check/", users_views.user_login_check, name="user_login_check"),
    path("user_home/", users_views.user_home, name="user_home"),
    path('predict/', users_views.predict_image, name='predict_image'),
    path('train/', users_views.train_model, name='train_model'),
    
]

