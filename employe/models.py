from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

#une classe qui herite de models
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Employe(models.Model):
    #cree un champ de chain de charactere
    nom = models.CharField(max_length=100)
    #preciser que un employer a un email
    email = models.EmailField()
    poste = models.CharField(max_length=100)
    salaire = models.DecimalField(max_digits=10 , decimal_places=2)
    # optional link to Department to align with HR structure
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='employees')
    hire_date = models.DateField(default=timezone.now)

    #fonction(constructeur) 
    def __str__(self):
        return self.nom


class Attendance(models.Model):
    employee = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='attendance_records')
    work_date = models.DateField(default=timezone.localdate)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    worked_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('employee', 'work_date')
        ordering = ['-work_date', '-check_in']

    def __str__(self):
        return f"{self.employee.nom} - {self.work_date}"

    def save(self, *args, **kwargs):
        # Auto derive work_date from check_in if missing
        if not self.work_date and self.check_in:
            self.work_date = self.check_in.date()
        # Compute worked hours when both timestamps present
        if self.check_in and self.check_out and self.check_out > self.check_in:
            total_seconds = (self.check_out - self.check_in).total_seconds()
            hours = Decimal(total_seconds / 3600).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.worked_hours = hours
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    LEAVE_TYPES = (
        ('annual', 'Congé annuel'),
        ('sick', 'Maladie'),
        ('unpaid', 'Sans solde'),
        ('other', 'Autre'),
    )
    STATUS = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
    )

    employee = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    approved_by = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.nom} {self.start_date} → {self.end_date} ({self.get_status_display()})"

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            from django.core.exceptions import ValidationError
            raise ValidationError('La date de fin doit être postérieure à la date de début.')
