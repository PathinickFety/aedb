from django import forms
from .models import Program, Beneficiary


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'program_type', 'date', 'time', 'place', 'responsible', 'beneficiaries', 'notes', 'is_finished']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Program Name'}),
            'program_type': forms.Select(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'place': forms.TextInput(attrs={'placeholder': 'Location'}),
            'responsible': forms.TextInput(attrs={'placeholder': 'Responsible Person'}),
            'beneficiaries': forms.SelectMultiple(attrs={
                'class': 'beneficiaries-select2',
                'style': 'width: 100%;',
                'data-ajax--url': '/search-beneficiaries/',
                'data-ajax--type': 'GET',
                'data-ajax--cache': 'true',
                'data-placeholder': 'Search beneficiary by name, phone, or category...',
                'data-allow-clear': 'true',
                'data-minimum-input-length': '1',
            }),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Notes (optional)'}),
            'is_finished': forms.CheckboxInput(),
        }


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ['full_name', 'date_of_birth', 'age', 'phone1', 'phone2', 'phone3', 'address', 'family_size', 'photo', 'category', 'remarks', 'is_needed_person', 'is_serious']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age (optional)', 'min': '0'}),
            'phone1': forms.TextInput(attrs={'placeholder': 'Phone 1', 'type': 'tel'}),
            'phone2': forms.TextInput(attrs={'placeholder': 'Phone 2 (optional)', 'type': 'tel'}),
            'phone3': forms.TextInput(attrs={'placeholder': 'Phone 3 (optional)', 'type': 'tel'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Address'}),
            'family_size': forms.NumberInput(attrs={'placeholder': 'Family Size (optional)', 'min': '1'}),
            'photo': forms.FileInput(),
            'category': forms.Select(),
            'remarks': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Remarks (optional)'}),
            'is_needed_person': forms.CheckboxInput(),
            'is_serious': forms.CheckboxInput(),
        }
