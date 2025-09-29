# myApp/forms.py
from django import forms

SERVICE_CHOICES = [
    ("", "Select a service"),
    ("Landscape", "Landscape"),
    ("Interior", "Interior"),
    ("Joinery", "Joinery"),
    ("Marble", "Marble"),
    ("Facility Management", "Facility Management"),
]

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=40, required=False)
    service = forms.ChoiceField(choices=SERVICE_CHOICES, required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))
    consent = forms.BooleanField(required=False, initial=True, label="")

    # Simple honeypot (hidden in CSS via the template or your base)
    honeypot = forms.CharField(required=False, widget=forms.TextInput(attrs={"autocomplete":"off","tabindex":"-1","style":"position:absolute;left:-9999px;"}))

    def clean_honeypot(self):
        if self.cleaned_data.get("honeypot"):
            raise forms.ValidationError("Spam detected.")
        return ""
