from django import forms
from .models import Gallery


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    def to_python(self, data):
        # data = list of InMemoryUploadedFile
        if not data:
            return []
        return data

    def validate(self, data):
        # Override: validasi setiap file
        if self.required and not data:
            raise forms.ValidationError("This field is required.")
        for file in data:
            super(MultiFileField, self).validate(file)


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class GalleryImageForm(forms.Form):
    images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={'multiple': True})
    )


