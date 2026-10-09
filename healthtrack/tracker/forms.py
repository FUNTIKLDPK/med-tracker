from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Measurement


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['measured_at', 'systolic', 'diastolic', 'pulse', 'note']
        widgets = {
            'measured_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M',
            ),
            'systolic': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '120', 'min': 50, 'max': 300
            }),
            'diastolic': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '80', 'min': 30, 'max': 200
            }),
            'pulse': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '70', 'min': 30, 'max': 220
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Например: после прогулки'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['measured_at'].input_formats = ['%Y-%m-%dT%H:%M']
        if not self.instance.pk and not self.initial.get('measured_at'):
            self.fields['measured_at'].initial = timezone.localtime().strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned = super().clean()
        systolic = cleaned.get('systolic')
        diastolic = cleaned.get('diastolic')

        if systolic and diastolic and systolic <= diastolic:
            raise forms.ValidationError('Верхнее давление должно быть больше нижнего.')

        measured_at = cleaned.get('measured_at')
        if measured_at and measured_at > timezone.now():
            raise forms.ValidationError('Дата измерения не может быть в будущем.')

        return cleaned


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = 'Латиница, цифры и @/./+/-/_ — до 150 символов.'
        self.fields['password1'].help_text = 'Минимум 8 символов, не только цифры.'
        self.fields['password2'].help_text = 'Повторите пароль.'