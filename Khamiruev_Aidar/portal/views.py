from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    AdminApplicationFilterForm,
    AdminLoginForm,
    ApplicationForm,
    LoginForm,
    RegistrationForm,
    ReviewForm,
)
from .models import Application, Review

ADMIN_LOGIN = 'Admin26'
ADMIN_PASSWORD = 'Demo20'
ADMIN_SESSION_KEY = 'portal_admin'


def index(request):
    if request.user.is_authenticated:
        return redirect('cabinet')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('cabinet')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
        return redirect('cabinet')
    return render(request, 'portal/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('cabinet')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Вы успешно вошли в систему.')
        return redirect('cabinet')
    return render(request, 'portal/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')


@login_required
def cabinet_view(request):
    applications = (
        Application.objects.filter(user=request.user)
        .select_related('course', 'review')
        .order_by('-created_at')
    )

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        application = get_object_or_404(
            Application, pk=app_id, user=request.user
        )
        if not application.can_leave_review():
            messages.error(
                request,
                'Отзыв можно оставить только после смены статуса заявки администратором.',
            )
            return redirect('cabinet')
        if hasattr(application, 'review'):
            messages.warning(request, 'Отзыв по этой заявке уже оставлен.')
            return redirect('cabinet')

        form = ReviewForm(request.POST, prefix=f'review_{application.pk}')
        if form.is_valid():
            review = form.save(commit=False)
            review.application = application
            review.user = request.user
            review.save()
            messages.success(request, 'Спасибо! Ваш отзыв сохранён.')
        else:
            messages.error(request, 'Проверьте текст отзыва.')
        return redirect('cabinet')

    return render(request, 'portal/cabinet.html', {'applications': applications})


@login_required
def application_create_view(request):
    form = ApplicationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        application = form.save(commit=False)
        application.user = request.user
        application.status = Application.STATUS_NEW
        application.save()
        messages.success(
            request,
            'Заявка отправлена на согласование администратору.',
        )
        return redirect('cabinet')
    return render(request, 'portal/application_form.html', {'form': form})


def _is_portal_admin(request):
    return request.session.get(ADMIN_SESSION_KEY) is True


def admin_login_view(request):
    if _is_portal_admin(request):
        return redirect('admin_panel')
    form = AdminLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if (
            form.cleaned_data['username'] == ADMIN_LOGIN
            and form.cleaned_data['password'] == ADMIN_PASSWORD
        ):
            request.session[ADMIN_SESSION_KEY] = True
            messages.success(request, 'Добро пожаловать в панель администратора.')
            return redirect('admin_panel')
        messages.error(request, 'Неверный логин или пароль администратора.')
    return render(request, 'portal/admin_login.html', {'form': form})


def admin_logout_view(request):
    request.session.pop(ADMIN_SESSION_KEY, None)
    messages.info(request, 'Вы вышли из панели администратора.')
    return redirect('admin_login')


def admin_panel_view(request):
    if not _is_portal_admin(request):
        return redirect('admin_login')

    filter_form = AdminApplicationFilterForm(request.GET)
    qs = Application.objects.select_related('user', 'course').all()

    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(user__username__icontains=search)
            | Q(user__full_name__icontains=search)
            | Q(course__title__icontains=search)
        )

    sort = request.GET.get('sort') or '-created_at'
    if sort in ('-created_at', 'created_at', 'status'):
        qs = qs.order_by(sort)

    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'portal/admin_panel.html',
        {
            'filter_form': filter_form,
            'page_obj': page_obj,
            'search': search,
            'status_choices': Application.STATUS_CHOICES,
        },
    )


@require_POST
def admin_change_status_view(request):
    if not _is_portal_admin(request):
        return redirect('admin_login')

    application = get_object_or_404(Application, pk=request.POST.get('application_id'))
    new_status = request.POST.get('status')
    valid_statuses = {s[0] for s in Application.STATUS_CHOICES}
    if new_status in valid_statuses:
        application.status = new_status
        application.save()
        messages.success(
            request,
            f'Статус заявки #{application.pk} изменён на «{application.get_status_display()}».',
        )
    return redirect('admin_panel')
