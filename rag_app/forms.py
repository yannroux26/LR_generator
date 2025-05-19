# rag_app/forms.py

from django import forms

class FolderSelectionForm(forms.Form):
    folder_path = forms.CharField(
        label="Folder Path",
        max_length=500,
        widget=forms.TextInput(attrs={
            "placeholder": "/path/to/your/pdf/folder",
            "class": "form-control"
        })
    )
