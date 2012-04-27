from django import forms

class FileCategorySearchForm(forms.Form):
    search_text = forms.CharField(max_length=35, label = '', widget=forms.TextInput(attrs={'placeholder': 'enter words or phrases separated by a commas'}), help_text='')