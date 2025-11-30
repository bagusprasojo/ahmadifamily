from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Event, EventImage
from .forms import EventForm, EventImageForm


def _base_event_queryset():
    return Event.objects.select_related('created_by').prefetch_related('images')


def _user_event_queryset(user):
    queryset = _base_event_queryset()
    if user.is_staff or user.is_superuser:
        return queryset
    return queryset.filter(created_by=user)


def event_public_list(request):
    events = _base_event_queryset().order_by('-created_at')
    context = {
        'events': events,
        'current_page': 'Events',
    }
    return render(request, 'eventapp/event_list.html', context)


@login_required
def event_manage_list(request):
    events = _user_event_queryset(request.user).order_by('-created_at')
    context = {
        'events': events,
        'current_page': 'Event Saya',
    }
    return render(request, 'eventapp/event_manage_list.html', context)

def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('created_by').prefetch_related('images'), pk=pk)
    return render(request, 'eventapp/event_detail.html', {'event': event})


@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        images_form = EventImageForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            for image_file in request.FILES.getlist('images'):
                EventImage.objects.create(event=event, image=image_file)
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
        images_form = EventImageForm()

    context = {
        'form': form,
        'images_form': images_form,
        'current_page': 'Tambah Event',
        'is_edit': False,
    }
    return render(request, 'eventapp/event_form.html', context)


@login_required
def event_update(request, pk):
    event = get_object_or_404(_user_event_queryset(request.user), pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        images_form = EventImageForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            event = form.save()
            for image_file in request.FILES.getlist('images'):
                EventImage.objects.create(event=event, image=image_file)
            return redirect('event_manage_list')
    else:
        form = EventForm(instance=event)
        images_form = EventImageForm()

    context = {
        'form': form,
        'images_form': images_form,
        'current_page': 'Edit Event',
        'is_edit': True,
        'event': event,
    }
    return render(request, 'eventapp/event_form.html', context)


@login_required
def event_delete(request, pk):
    event = get_object_or_404(_user_event_queryset(request.user), pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_manage_list')
    return redirect('event_manage_list')
