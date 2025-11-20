from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Event, EventImage
from .forms import EventForm, EventImageForm


def event_list(request):
    events = (
        Event.objects.select_related('created_by')
        .prefetch_related('images')
        .order_by('-created_at')
    )
    context = {
        'events': events,
        'current_page': 'Events',
    }

    return render(request, 'eventapp/event_list.html', context)


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
    }
    return render(request, 'eventapp/event_form.html', context)
