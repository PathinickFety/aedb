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
        fields = [
            'full_name',
            'date_of_birth',
            'age',
            'gender',
            'national_id',
            'phone1',
            'phone2',
            'phone3',
            'address',
            'village',
            'district',
            'region',
            'family_size',
            'monthly_income',
            'occupation',
            'photo',
            'id_document',
            'category',
            'remarks',
            'is_needed_person',
            'is_serious',
            'is_muslim',
            'is_verified',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age (optional)', 'min': '0'}),
            'gender': forms.Select(),
            'national_id': forms.TextInput(attrs={'placeholder': 'National ID (optional)'}),
            'phone1': forms.TextInput(attrs={'placeholder': 'Phone 1', 'type': 'tel'}),
            'phone2': forms.TextInput(attrs={'placeholder': 'Phone 2 (optional)', 'type': 'tel'}),
            'phone3': forms.TextInput(attrs={'placeholder': 'Phone 3 (optional)', 'type': 'tel'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Address'}),
            'village': forms.TextInput(attrs={'placeholder': 'Village (optional)'}),
            'district': forms.TextInput(attrs={'placeholder': 'District (optional)'}),
            'region': forms.TextInput(attrs={'placeholder': 'Region (optional)'}),
            'family_size': forms.NumberInput(attrs={'placeholder': 'Family Size', 'min': '1'}),
            'monthly_income': forms.NumberInput(attrs={'placeholder': 'Monthly Income (optional)', 'step': '0.01'}),
            'occupation': forms.TextInput(attrs={'placeholder': 'Occupation (optional)'}),
            'photo': forms.FileInput(),
            'id_document': forms.FileInput(),
            'category': forms.Select(),
            'remarks': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Remarks (optional)'}),
            'is_needed_person': forms.CheckboxInput(),
            'is_serious': forms.CheckboxInput(),
            'is_muslim': forms.CheckboxInput(),
            'is_verified': forms.CheckboxInput(),
        }


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    photo = forms.FileField(required=False)

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            max_size = 5 * 1024 * 1024  # 5MB
            if photo.size > max_size:
                raise forms.ValidationError('Uploaded image is too large (max 5MB).')
            content_type = photo.content_type
            if not content_type.startswith('image/'):
                raise forms.ValidationError('Only image files are allowed for avatar.')
        return photo
