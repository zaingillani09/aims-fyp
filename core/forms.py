from django import forms
from issues.models import Issue

class IssueSubmitForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'department', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title of the issue...'}),
            'department': forms.Select(),
            'description': forms.Textarea(attrs={'placeholder': 'Detailed description of the issue...', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['department'].queryset = self.user.departments.all()
            if self.fields['department'].queryset.count() == 1:
                self.fields['department'].initial = self.fields['department'].queryset.first()
