from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employe, Department, Attendance, LeaveRequest
from .form import EmployeForm, DepartmentForm, AttendanceForm, LeaveRequestForm
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .supabase_client import get_supabase_client
# pour recuperer la liste de tous les employe du site
def liste_employes(request):
    employes = Employe.objects.all()

    #retourner a une page html 
    return render(request, 'employe/list.html', {'employes' : employes})

#ajouter un employé
def ajouter_employe(request): 
    form = EmployeForm(request.POST or None)
    #verifier si le form est valide
    if form.is_valid():
        form.save()
        messages.success(request, "Employé ajouté avec succès.")
        return redirect('liste_employes')
    elif request.method == "POST":
        messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    return render(request, 'employe/formulaire.html', {'form': form})

def modifier_employe(request, id) :
    #recuper un objet dans la bd ou renvoie 404
    employe = get_object_or_404(Employe, id=id)
    form = EmployeForm(request.POST or None, instance=employe)
    if form.is_valid():
        form.save()
        messages.success(request, "Employé modifié avec succès.")
        return redirect('liste_employes')
    elif request.method == "POST":
        messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    return render(request, 'employe/formulaire.html', {'form': form})

def supprimer_employe(request, id):
    employe = get_object_or_404(Employe, id=id)
    if request.method == "POST":
        employe.delete()
        messages.success(request, "Employé supprimé avec succès.")
        return redirect('liste_employes')
    return render(request, 'employe/confirmer_suppression.html', {'employe': employe})

# Auth pages (frontend for Supabase Auth)
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        sb = get_supabase_client()
        if sb:
            try:
                res = sb.auth.sign_in_with_password({ 'email': email, 'password': password })
                if res and res.session:
                    request.session['sb_access_token'] = res.session.access_token
                    request.session['sb_user'] = res.user.id
                    messages.success(request, "Connexion réussie.")
                    return redirect('dashboard')
                messages.error(request, "Identifiants invalides.")
            except Exception:
                messages.error(request, "Connexion échouée. Vérifiez vos identifiants ou votre email.")
        else:
            # Fallback Django auth: try username directly, then by email lookup
            user = authenticate(request, username=email, password=password)
            if user is None:
                try:
                    u = User.objects.get(email=email)
                    user = authenticate(request, username=u.username, password=password)
                except User.DoesNotExist:
                    user = None
            if user is not None:
                login(request, user)
                messages.success(request, "Connexion réussie.")
                return redirect('dashboard')
            messages.error(request, "Identifiants invalides.")
    return render(request, 'auth/login.html')

def signup_page(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        sb = get_supabase_client()
        if sb:
            try:
                res = sb.auth.sign_up({ 'email': email, 'password': password, 'options': { 'data': { 'full_name': full_name } } })
                messages.success(request, "Compte créé. Vérifiez votre email pour confirmer.")
                return redirect('login')
            except Exception:
                messages.error(request, "Création du compte échouée. Essayez un autre email.")
        else:
            # Fallback: create Django user with username=email
            if User.objects.filter(username=email).exists():
                messages.error(request, "Un compte existe déjà avec cet email.")
                return render(request, 'auth/signup.html')
            user = User.objects.create_user(username=email, email=email, password=password)
            # Save full name if provided
            if full_name:
                parts = full_name.split(" ", 1)
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]
                user.save()
            messages.success(request, "Compte créé avec succès. Vous pouvez vous connecter.")
            return redirect('login')
    return render(request, 'auth/signup.html')

def verify_email_page(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        sb = get_supabase_client()
        if sb:
            try:
                sb.auth.resend({ 'type': 'signup', 'email': email })
                messages.success(request, "Email de vérification renvoyé si le compte existe.")
                return redirect('login')
            except Exception:
                messages.error(request, "Echec de l'envoi de l'email de vérification.")
        else:
            messages.info(request, "La vérification par email nécessite Supabase. Fonction non disponible.")
    return render(request, 'auth/verify_email.html')

def logout_page(request):
    request.session.pop('sb_access_token', None)
    request.session.pop('sb_user', None)
    logout(request)
    messages.success(request, "Déconnecté.")
    return redirect('login')

# Dashboard
def dashboard(request):
    total_employees = Employe.objects.count()
    total_departments = Department.objects.count()
    recent_employees = Employe.objects.order_by('-id')[:5]
    today = timezone.localdate()
    today_att = Attendance.objects.filter(work_date=today)
    present_count = today_att.exclude(check_in__isnull=True).values('employee').distinct().count()
    attendance_rate = (present_count / total_employees * 100) if total_employees else 0
    avg_hours = today_att.aggregate(avg=Avg('worked_hours'))['avg'] or 0
    total_hours = today_att.aggregate(sum=Sum('worked_hours'))['sum'] or 0
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    return render(request, 'employe/dashboard.html', {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'recent_employees': recent_employees,
        'attendance_rate': round(attendance_rate, 2),
        'avg_hours': avg_hours,
        'total_hours': total_hours,
        'pending_leaves': pending_leaves,
    })

# Department Management
def liste_departements(request):
    departements = Department.objects.annotate(employee_count=Count('employees')).order_by('name')
    return render(request, 'departments/list.html', {'departements': departements})

def ajouter_departement(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('liste_departements')
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Département ajouté avec succès.")
        return redirect('liste_departements')
    elif request.method == "POST":
        messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    return render(request, 'departments/form.html', {'form': form})

def modifier_departement(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('liste_departements')
    departement = get_object_or_404(Department, id=id)
    form = DepartmentForm(request.POST or None, instance=departement)
    if form.is_valid():
        form.save()
        messages.success(request, "Département modifié avec succès.")
        return redirect('liste_departements')
    elif request.method == "POST":
        messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    return render(request, 'departments/form.html', {'form': form})

def supprimer_departement(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('liste_departements')
    departement = get_object_or_404(Department, id=id)
    if request.method == "POST":
        departement.delete()
        messages.success(request, "Département supprimé avec succès.")
        return redirect('liste_departements')
    return render(request, 'departments/confirm_delete.html', {'departement': departement})

# Attendance
def attendance_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, "Veuillez vous connecter.")
        return redirect('login')
    today = timezone.localdate()
    total_employees = Employe.objects.count()
    qs = Attendance.objects.filter(work_date=today)
    present_count = qs.exclude(check_in__isnull=True).values('employee').distinct().count()
    attendance_rate = (present_count / total_employees * 100) if total_employees else 0
    avg_hours = qs.aggregate(avg=Avg('worked_hours'))['avg'] or 0
    total_hours = qs.aggregate(sum=Sum('worked_hours'))['sum'] or 0
    records = qs.select_related('employee').order_by('employee__nom')
    return render(request, 'attendance/dashboard.html', {
        'today': today,
        'records': records,
        'attendance_rate': round(attendance_rate, 2),
        'avg_hours': avg_hours,
        'total_hours': total_hours,
    })

def attendance_list(request):
    if not request.user.is_authenticated:
        messages.error(request, "Veuillez vous connecter.")
        return redirect('login')
    records = Attendance.objects.select_related('employee').order_by('-work_date', 'employee__nom')
    return render(request, 'attendance/list.html', {'records': records})

def attendance_create(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('attendance_list')
    form = AttendanceForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Attendance créé.")
        return redirect('attendance_list')
    return render(request, 'attendance/form.html', {'form': form})

def attendance_edit(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('attendance_list')
    rec = get_object_or_404(Attendance, id=id)
    form = AttendanceForm(request.POST or None, instance=rec)
    if form.is_valid():
        form.save()
        messages.success(request, "Attendance modifié.")
        return redirect('attendance_list')
    return render(request, 'attendance/form.html', {'form': form})

def attendance_delete(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('attendance_list')
    rec = get_object_or_404(Attendance, id=id)
    if request.method == 'POST':
        rec.delete()
        messages.success(request, "Attendance supprimé.")
        return redirect('attendance_list')
    return render(request, 'attendance/confirm_delete.html', {'record': rec})

def clock_in(request, employee_id):
    if not request.user.is_authenticated:
        messages.error(request, "Veuillez vous connecter.")
        return redirect('login')
    employee = get_object_or_404(Employe, id=employee_id)
    today = timezone.localdate()
    rec, _ = Attendance.objects.get_or_create(employee=employee, work_date=today)
    if rec.check_in:
        messages.info(request, "Déjà pointé pour aujourd'hui.")
    else:
        rec.check_in = timezone.now()
        rec.save()
        messages.success(request, "Pointage d'entrée enregistré.")
    return redirect('attendance_dashboard')

def clock_out(request, employee_id):
    if not request.user.is_authenticated:
        messages.error(request, "Veuillez vous connecter.")
        return redirect('login')
    employee = get_object_or_404(Employe, id=employee_id)
    today = timezone.localdate()
    rec = get_object_or_404(Attendance, employee=employee, work_date=today)
    if rec.check_out:
        messages.info(request, "Déjà sorti aujourd'hui.")
    else:
        rec.check_out = timezone.now()
        rec.save()
        messages.success(request, "Pointage de sortie enregistré.")
    return redirect('attendance_dashboard')

# Leave Management
def leave_list(request):
    if not request.user.is_authenticated:
        messages.error(request, "Veuillez vous connecter.")
        return redirect('login')
    leaves = LeaveRequest.objects.select_related('employee').order_by('-created_at')
    return render(request, 'leave/list.html', {'leaves': leaves})

def leave_create(request):
    if not request.user.is_authenticated:
        messages.error(request, "Veuillez vous connecter.")
        return redirect('login')
    form = LeaveRequestForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Demande de congé créée.")
        return redirect('leave_list')
    return render(request, 'leave/form.html', {'form': form})

def leave_edit(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('leave_list')
    lr = get_object_or_404(LeaveRequest, id=id)
    form = LeaveRequestForm(request.POST or None, instance=lr)
    if form.is_valid():
        form.save()
        messages.success(request, "Demande de congé mise à jour.")
        return redirect('leave_list')
    return render(request, 'leave/form.html', {'form': form})

def leave_delete(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('leave_list')
    lr = get_object_or_404(LeaveRequest, id=id)
    if request.method == 'POST':
        lr.delete()
        messages.success(request, "Demande de congé supprimée.")
        return redirect('leave_list')
    return render(request, 'leave/confirm_delete.html', {'leave': lr})

def leave_approve(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('leave_list')
    lr = get_object_or_404(LeaveRequest, id=id)
    lr.status = 'approved'
    lr.approved_by = request.user.get_username()
    lr.save()
    messages.success(request, "Demande de congé approuvée.")
    return redirect('leave_list')

def leave_reject(request, id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Accès refusé: réservé aux administrateurs/gestionnaires.")
        return redirect('leave_list')
    lr = get_object_or_404(LeaveRequest, id=id)
    lr.status = 'rejected'
    lr.approved_by = request.user.get_username()
    lr.save()
    messages.success(request, "Demande de congé rejetée.")
    return redirect('leave_list')
