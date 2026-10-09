import csv

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import MeasurementForm, SignUpForm
from .models import Measurement


@login_required
def measurement_list(request):
    qs = Measurement.objects.filter(user=request.user)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        d = parse_date(date_from)
        if d:
            qs = qs.filter(measured_at__date__gte=d)
    if date_to:
        d = parse_date(date_to)
        if d:
            qs = qs.filter(measured_at__date__lte=d)

    chart_qs = qs.order_by('measured_at')
    chart_data = {
        'labels': [timezone.localtime(m.measured_at).strftime('%d.%m %H:%M') for m in chart_qs],
        'systolic': [m.systolic for m in chart_qs],
        'diastolic': [m.diastolic for m in chart_qs],
        'pulse': [m.pulse for m in chart_qs],
    }

    total = qs.count()
    high_count = sum(1 for m in qs if m.is_high)

    context = {
        'measurements': qs[:200],
        'chart_data': chart_data,
        'date_from': date_from or '',
        'date_to': date_to or '',
        'total': total,
        'high_count': high_count,
    }
    return render(request, 'tracker/measurement_list.html', context)


@login_required
def measurement_add(request):
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()

            if m.is_high:
                messages.warning(request, f'⚠️ Внимание! Давление {m.systolic}/{m.diastolic} повышено.')
            else:
                messages.success(request, 'Измерение сохранено.')

            return redirect('measurement_list')
    else:
        form = MeasurementForm()

    return render(request, 'tracker/measurement_form.html', {'form': form})


@login_required
def measurement_delete(request, pk):
    m = Measurement.objects.filter(pk=pk, user=request.user).first()
    if not m:
        messages.error(request, 'Измерение не найдено.')
        return redirect('measurement_list')

    if request.method == 'POST':
        m.delete()
        messages.success(request, 'Измерение удалено.')
        return redirect('measurement_list')

    return render(request, 'tracker/measurement_confirm_delete.html', {'measurement': m})


@login_required
def export_csv(request):
    qs = Measurement.objects.filter(user=request.user)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        d = parse_date(date_from)
        if d:
            qs = qs.filter(measured_at__date__gte=d)
    if date_to:
        d = parse_date(date_to)
        if d:
            qs = qs.filter(measured_at__date__lte=d)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="healthtrack_export.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Дата', 'Верхнее', 'Нижнее', 'Пульс', 'Статус', 'Заметка'])

    for m in qs.order_by('-measured_at'):
        writer.writerow([
            timezone.localtime(m.measured_at).strftime('%d.%m.%Y %H:%M'),
            m.systolic,
            m.diastolic,
            m.pulse,
            m.status_label,
            m.note,
        ])

    return response


def signup(request):
    if request.user.is_authenticated:
        return redirect('measurement_list')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('measurement_list')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})