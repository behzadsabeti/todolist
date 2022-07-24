from django import forms
from todolist.models import Task


# Create the form class.
class CreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'text', 'tags']
