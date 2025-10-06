# myApp/forms.py
from django import forms
from .models import Service, Insight, ServiceProjectImage, CaseStudy

# -----------------------------
# Existing contact form (unchanged)
# -----------------------------
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
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"autocomplete": "off", "tabindex": "-1", "style": "position:absolute;left:-9999px;"}
        ),
    )

    def clean_honeypot(self):
        if self.cleaned_data.get("honeypot"):
            raise forms.ValidationError("Spam detected.")
        return ""


# -----------------------------
# New helpers for media uploads
# -----------------------------
class _URLOrFileBaseForm(forms.Form):
    """
    Base: allow either a pasted URL or a file upload.
    The view will:
      - If `file` present: upload to Cloudinary, use returned secure_url
      - Else: use the pasted `url`
    """
    url = forms.URLField(required=False, label="Cloudinary URL (optional)")
    file = forms.ImageField(required=False, label="Or upload file")

    def clean(self):
        cleaned = super().clean()
        url = cleaned.get("url")
        file = cleaned.get("file")

        if not url and not file:
            raise forms.ValidationError("Provide a URL or upload a file.")
        # Optional lightweight guard: if URL is provided, ensure it's https
        if url and not url.startswith("http"):
            self.add_error("url", "URL must start with http(s)://")
        return cleaned


class EditorialUploadForm(_URLOrFileBaseForm):
    """
    For ServiceEditorialImage (image_url + caption)
    """
    caption = forms.CharField(max_length=120, required=False)


class ProjectImageUploadForm(_URLOrFileBaseForm):
    """
    For ServiceProjectImage (thumb_url + full_url + caption)
    By default, we’ll save the same URL to both fields;
    later you can render Cloudinary thumb transforms in templates.
    """
    caption = forms.CharField(max_length=140, required=False)


# -----------------------------
# ModelForms for dashboard CRUD
# -----------------------------
from django import forms
from django.utils.text import slugify
from django.forms import inlineformset_factory
from .models import Service, ServiceCapability, ServiceEditorialImage

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "title","slug","eyebrow",
            "hero_headline","hero_subcopy","hero_media_url",
            "stat_projects","stat_years","stat_specialists",
            "pinned_heading","pinned_title","pinned_body_1","pinned_body_2",
            "insights_heading","insights_subcopy",
            "is_active","sort_order",
            "seo_meta_title","seo_meta_description","canonical_path",
        ]
        widgets = {
            "hero_subcopy": forms.Textarea(attrs={"rows":3}),
            "pinned_body_1": forms.Textarea(attrs={"rows":3}),
            "pinned_body_2": forms.Textarea(attrs={"rows":3}),
            "insights_subcopy": forms.Textarea(attrs={"rows":2}),
            "seo_meta_description": forms.Textarea(attrs={"rows":2}),
        }
        help_texts = {
            "slug": "Lowercase, hyphen-separated (auto-filled from title).",
            "canonical_path": "Optional. Example: /services/ai-consulting",
        }

    def clean_slug(self):
        s = self.cleaned_data.get("slug") or self.cleaned_data.get("title") or ""
        s = slugify(s)[:80]
        if not s:
            raise forms.ValidationError("Slug cannot be empty.")
        return s

    def clean_seo_meta_title(self):
        t = (self.cleaned_data.get("seo_meta_title") or "").strip()
        if len(t) > 70:
            raise forms.ValidationError("Keep meta title concise (≤ 70 chars recommended).")
        return t

    def clean_seo_meta_description(self):
        d = (self.cleaned_data.get("seo_meta_description") or "").strip()
        if len(d) > 180:
            raise forms.ValidationError("Keep meta description concise (≤ 180 chars).")
        return d



class InsightForm(forms.ModelForm):
    class Meta:
        model = Insight
        fields = [
            "service",
            "title",
            "cover_image_url", 
            "blocks",
            "published",
        ]
        widgets = {
            "blocks": forms.HiddenInput(),
        }


# -----------------------------
# Inline Formsets for Service Management
# -----------------------------

class ServiceCapabilityForm(forms.ModelForm):
    class Meta:
        model = ServiceCapability
        fields = ['title', 'blurb', 'icon_class', 'sort_order']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Design Studio'}),
            'blurb': forms.TextInput(attrs={'placeholder': 'Brief description...'}),
            'icon_class': forms.TextInput(attrs={'placeholder': 'e.g., fa-solid fa-palette'}),
            'sort_order': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition'})


class ServiceEditorialImageForm(forms.ModelForm):
    class Meta:
        model = ServiceEditorialImage
        fields = ['image_url', 'caption', 'sort_order']
        widgets = {
            'image_url': forms.URLInput(attrs={'placeholder': 'https://res.cloudinary.com/...'}),
            'caption': forms.TextInput(attrs={'placeholder': 'Image caption...'}),
            'sort_order': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition'})


class ServiceProjectImageForm(forms.ModelForm):
    class Meta:
        model = ServiceProjectImage
        fields = ['thumb_url', 'full_url', 'caption', 'sort_order']
        widgets = {
            'thumb_url': forms.URLInput(attrs={'placeholder': 'https://res.cloudinary.com/.../w_400,h_auto,c_fill'}),
            'full_url': forms.URLInput(attrs={'placeholder': 'https://res.cloudinary.com/.../w_2400,h_auto,c_fill'}),
            'caption': forms.TextInput(attrs={'placeholder': 'Project image caption...'}),
            'sort_order': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition'})


class CaseStudyForm(forms.ModelForm):
    class Meta:
        model = CaseStudy
        fields = ['title', 'hero_image_url', 'summary', 'scope', 'size_label', 'timeline_label', 'status_label', 'tags_csv', 'is_featured', 'sort_order', 'cta_url']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Case study title...'}),
            'hero_image_url': forms.URLInput(attrs={'placeholder': 'https://res.cloudinary.com/.../w_1600,h_900,c_fill'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief summary of the project...'}),
            'scope': forms.TextInput(attrs={'placeholder': 'e.g., Design + Build'}),
            'size_label': forms.TextInput(attrs={'placeholder': 'e.g., 5,000 sq ft'}),
            'timeline_label': forms.TextInput(attrs={'placeholder': 'e.g., 6 months'}),
            'status_label': forms.TextInput(attrs={'placeholder': 'e.g., Completed'}),
            'tags_csv': forms.TextInput(attrs={'placeholder': 'e.g., Architecture, Interior Fit-Out, Joinery, Landscape'}),
            'cta_url': forms.URLInput(attrs={'placeholder': 'https://... (optional detail page)'}),
            'sort_order': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full rounded-xl border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-400 transition'})


# Create the inline formsets
ServiceCapabilityFormSet = inlineformset_factory(
    Service, 
    ServiceCapability, 
    form=ServiceCapabilityForm,
    extra=1, 
    can_delete=True,
    min_num=0,
    validate_min=False
)

ServiceEditorialImageFormSet = inlineformset_factory(
    Service, 
    ServiceEditorialImage, 
    form=ServiceEditorialImageForm,
    extra=1, 
    can_delete=True,
    min_num=0,
    validate_min=False
)

ServiceProjectImageFormSet = inlineformset_factory(
    Service, 
    ServiceProjectImage, 
    form=ServiceProjectImageForm,
    extra=1, 
    can_delete=True,
    min_num=0,
    validate_min=False
)

CaseStudyFormSet = inlineformset_factory(
    Service, 
    CaseStudy, 
    form=CaseStudyForm,
    extra=1, 
    can_delete=True,
    min_num=0,
    validate_min=False
)
