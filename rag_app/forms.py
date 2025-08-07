
from django import forms

class FolderSelectionForm(forms.Form):
    topic = forms.CharField(
        label="Literature Review Topic",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. Deep Learning for Medical Imaging (optional)",
            "class": "form-control"
        })
    )
    folder_path = forms.CharField(
        label="Folder Path",
        max_length=500,
        widget=forms.TextInput(attrs={
            "placeholder": "/path/to/your/pdf/folder",
            "class": "form-control"
        })
    )
