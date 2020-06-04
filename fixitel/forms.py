from django import forms
from .models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm




class TicketsForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'clientName', 'clientPhone', 'clientAdress', 'body', 'status', 'master', 'fullprice', 'price', 'priceDetails']
    def __init__(self, *args, **kwargs):
        super(TicketsForm, self).__init__(*args, **kwargs)
        self.fields['master'].empty_label = "Мастер не назначен"


class TicketsSimpleForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']





class UserForm(UserCreationForm):
    first_name = forms.CharField(label='Ф.И.О мастера')
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'email', 'password1', 'password2')


class MasterEditForm(forms.ModelForm):
    first_name = forms.CharField(label='Ф.И.О мастера')
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')


class MasterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('specialty', 'role', 'cash', 'findata')



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)



class TransactForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('transact_type', 'name', 'total')

