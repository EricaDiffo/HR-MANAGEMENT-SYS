from django import forms
from .models import Employe, Department, Attendance, LeaveRequest


class EmployeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre visuel le caractère requis dans le HTML et faciliter le style d'erreurs
        for field_name, field in self.fields.items():
            field.required = True
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{css_classes} input w-full".strip()
        # Ajouter la classe d'erreur si le formulaire est lié et invalide
        if self.is_bound:
            for field_name, field in self.fields.items():
                if self.errors.get(field_name):
                    existing = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f"{existing} is-invalid".strip()

    class Meta:
        model = Employe
        fields = ['nom', 'email', 'poste', 'salaire', 'department', 'hire_date']
        labels = {
            'nom': 'Nom',
            'email': 'Email',
            'poste': 'Poste',
            'salaire': 'Salaire',
            'department': 'Département',
            'hire_date': "Date d'embauche",
        }
        help_texts = {
            'email': "Exemple: nom@domaine.com",
            'salaire': "Utilisez un nombre positif (ex: 150000.00)",
        }
        error_messages = {
            'nom': {
                'required': "Le nom est obligatoire.",
                'max_length': "Le nom est trop long.",
            },
            'email': {
                'required': "L'email est obligatoire.",
                'invalid': "Format d'email invalide.",
            },
            'poste': {
                'required': "Le poste est obligatoire.",
                'max_length': "Le poste est trop long.",
            },
            'salaire': {
                'required': "Le salaire est obligatoire.",
                'invalid': "Entrez un nombre valide pour le salaire.",
            },
        }
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Nom',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'required': 'required',
            }),
            'poste': forms.TextInput(attrs={
                'placeholder': 'Poste',
                'required': 'required',
            }),
            'salaire': forms.NumberInput(attrs={
                'placeholder': 'Salaire',
                'step': '0.01',
                'min': '0',
                'required': 'required',
            }),
            'department': forms.Select(attrs={
                'class': 'input w-full',
            }),
            'hire_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input w-full',
            }),
        }

    def clean_nom(self):
        nom = self.cleaned_data.get('nom', '').strip()
        if not nom:
            raise forms.ValidationError("Le nom ne peut pas être vide.")
        return nom

    def clean_poste(self):
        poste = self.cleaned_data.get('poste', '').strip()
        if not poste:
            raise forms.ValidationError("Le poste ne peut pas être vide.")
        return poste

    def clean_salaire(self):
        salaire = self.cleaned_data.get('salaire')
        if salaire is None:
            return salaire
        if salaire <= 0:
            raise forms.ValidationError("Le salaire doit être un nombre positif.")
        return salaire


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        labels = {
            'name': 'Nom du département',
            'description': 'Description',
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'work_date', 'check_in', 'check_out']
        labels = {
            'employee': 'Employé',
            'work_date': 'Date',
            'check_in': 'Heure d\'arrivée',
            'check_out': 'Heure de départ',
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['employee', 'type', 'start_date', 'end_date', 'reason']
        labels = {
            'employee': 'Employé',
            'type': 'Type de congé',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'reason': 'Motif',
        }
        widgets = {
            'employee': forms.Select(attrs={'class': 'input w-full'}),
            'type': forms.Select(attrs={'class': 'input w-full'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'input w-full'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'input w-full'}),
            'reason': forms.Textarea(attrs={'class': 'input w-full', 'rows': 4, 'placeholder': 'Motif (optionnel)'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', "La date de fin doit être postérieure à la date de début.")
        return cleaned
        widgets = {
            'employee': forms.Select(attrs={'class': 'input w-full'}),
            'work_date': forms.DateInput(attrs={'type': 'date', 'class': 'input w-full'}),
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'input w-full'}),
            'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'input w-full'}),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input w-full',
                'placeholder': 'Nom du département',
                'required': 'required',
            }),
            'description': forms.Textarea(attrs={
                'class': 'input w-full',
                'placeholder': 'Description (optionnel)',
                'rows': 4,
            }),
        }