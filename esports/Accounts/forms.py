from django.forms import fields, forms, models
from django.contrib.auth.forms import UserCreationForm
from . models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model =User
        fields=('email','phone', 'username')

 