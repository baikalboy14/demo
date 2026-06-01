import re
from datetime import datetime

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Application, Review

User = get_user_model()

LOGIN_PATTERN = re.compile(r'^[a-zA-Z0-9]{6,}$')


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label='ФИО',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
    )
    phone = forms.CharField(
        label='Контактный телефон',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'user@mail.ru'}),
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'full_name', 'phone', 'email')
        labels = {'username': 'Логин'}
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'login123'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Минимум 8 символов'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Повторите пароль'}
        )
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def clean_username(self):
        login = self.cleaned_data['username']
        if not LOGIN_PATTERN.match(login):
            raise ValidationError(
                'Логин должен содержать только латинские буквы и цифры, минимум 6 символов.'
            )
        if User.objects.filter(username=login).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return login

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        if len(password) < 8:
            raise ValidationError('Пароль должен содержать не менее 8 символов.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш логин'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ваш пароль'}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        login = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if login and password:
            self.user_cache = authenticate(
                self.request, username=login, password=password
            )
            if self.user_cache is None:
                raise ValidationError('Неверный логин или пароль.')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ApplicationForm(forms.ModelForm):
    start_date = forms.CharField(
        label='Дата начала (ДД.ММ.ГГГГ)',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '01.09.2026'}
        ),
    )

    class Meta:
        model = Application
        fields = ('course', 'start_date', 'payment_method')
        labels = {
            'course': 'Курс',
            'payment_method': 'Способ оплаты',
        }
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_start_date(self):
        value = self.cleaned_data['start_date'].strip()
        try:
            parsed = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError as exc:
            raise ValidationError('Введите дату в формате ДД.ММ.ГГГГ.') from exc
        if parsed < datetime.now().date():
            raise ValidationError('Дата начала не может быть в прошлом.')
        return parsed


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('text',)
        labels = {'text': 'Ваш отзыв'}
        widgets = {
            'text': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опишите впечатления от курса'}
            ),
        }


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class AdminApplicationFilterForm(forms.Form):
    status = forms.ChoiceField(
        label='Статус',
        required=False,
        choices=[('', 'Все статусы')] + list(Application.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    sort = forms.ChoiceField(
        label='Сортировка',
        required=False,
        choices=[
            ('-created_at', 'Сначала новые'),
            ('created_at', 'Сначала старые'),
            ('status', 'По статусу (А-Я)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
