from django import forms
from django.core.exceptions import ValidationError

from idea_jet_business.models import Waitlist


class WaitlistForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'placeholder': 'Your email', 'class': 'form-input block w-2/3 p-3'}
        ),
        label=''
    )

    class Meta:
        model = Waitlist
        fields = ['email']


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Waitlist.objects.filter(email=email).exists():
            raise ValidationError("You are already in the WaitList!")
        return email

