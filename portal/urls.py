from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cabinet/', views.cabinet_view, name='cabinet'),
    path('application/new/', views.application_create_view, name='application_new'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin/', views.admin_panel_view, name='admin_panel'),
    path('admin/status/', views.admin_change_status_view, name='admin_change_status'),
]
