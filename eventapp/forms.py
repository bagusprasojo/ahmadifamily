from django import forms
from .models import Event



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


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }


class EventImageForm(forms.Form):
    images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={'multiple': True})
    )
