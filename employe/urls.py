from django.contrib import admin
from django.urls import path 
from . import views

urlpatterns = [
    path('', views.dashboard , name='dashboard'),
    path('employes/', views.liste_employes , name='liste_employes'),
    path('ajouter/', views.ajouter_employe , name='ajouter_employe'),
    path('modifier/<int:id>/', views.modifier_employe , name='modifier_employe'),
    path('supprimer/<int:id>/', views.supprimer_employe , name='supprimer_employe'),
    # Dashboard explicit route
    path('dashboard/', views.dashboard, name='dashboard'),
    # Auth routes (frontend pages)
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('verify-email/', views.verify_email_page, name='verify_email'),
    path('logout/', views.logout_page, name='logout'),
    # Departments
    path('departements/', views.liste_departements, name='liste_departements'),
    path('departements/ajouter/', views.ajouter_departement, name='ajouter_departement'),
    path('departements/modifier/<int:id>/', views.modifier_departement, name='modifier_departement'),
    path('departements/supprimer/<int:id>/', views.supprimer_departement, name='supprimer_departement'),
    # Attendance
    path('attendance/', views.attendance_dashboard, name='attendance_dashboard'),
    path('attendance/list/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/edit/<int:id>/', views.attendance_edit, name='attendance_edit'),
    path('attendance/delete/<int:id>/', views.attendance_delete, name='attendance_delete'),
    path('attendance/clock-in/<int:employee_id>/', views.clock_in, name='clock_in'),
    path('attendance/clock-out/<int:employee_id>/', views.clock_out, name='clock_out'),
    # Leave
    path('leave/', views.leave_list, name='leave_list'),
    path('leave/create/', views.leave_create, name='leave_create'),
    path('leave/edit/<int:id>/', views.leave_edit, name='leave_edit'),
    path('leave/delete/<int:id>/', views.leave_delete, name='leave_delete'),
    path('leave/approve/<int:id>/', views.leave_approve, name='leave_approve'),
    path('leave/reject/<int:id>/', views.leave_reject, name='leave_reject'),
]