from django import forms

from .models import FloorPlan

from django.core.exceptions import ValidationError

class PlanForm(forms.ModelForm):

    # title = forms.CharField(max_length=50)
    # slug = forms.CharField(max_length=50)
    # body = forms.CharField(max_length=240)
    # image = forms.ImageField()
    class Meta:
        model = FloorPlan
        fields = ['title', 'slug', 'body', 'image']

        widgets =  {
            'title':forms.TextInput(attrs={'class': 'form-control'}),
            'slug':forms.TextInput(attrs={'class': 'form-control'}),
            'body':forms.TextInput(attrs={'class': 'form-control'}),
        }





    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()
        if FloorPlan.objects.filter(slug__iexact = new_slug).count():
            raise ValidationError('Slug must be unique. slug: "{}" - exist'.format(new_slug) )
        return new_slug

    def save(self):
        new_plan = FloorPlan.objects.create(title = self.cleaned_data['title'],
        slug = self.cleaned_data['slug'],
        body = self.cleaned_data['body'],
        image = self.cleaned_data['image'])
        return new_plan