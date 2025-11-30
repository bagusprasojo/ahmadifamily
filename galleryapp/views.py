from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Gallery, GalleryImage
from .forms import GalleryForm, GalleryImageForm


def _base_gallery_queryset():
    return Gallery.objects.select_related('created_by').prefetch_related('images')


def _user_gallery_queryset(user):
    queryset = _base_gallery_queryset()
    if user.is_staff or user.is_superuser:
        return queryset
    return queryset.filter(created_by=user)


def gallery_list(request):
    galleries = _base_gallery_queryset().order_by('-created_at')
    return render(request, 'galleryapp/gallery_list.html', {'galleries': galleries, 'current_page': 'Gallery'})


def gallery_detail(request, pk):
    gallery = get_object_or_404(_base_gallery_queryset(), pk=pk)
    return render(request, 'galleryapp/gallery_detail.html', {'gallery': gallery, 'current_page': gallery.title})


@login_required
def gallery_manage_list(request):
    galleries = _user_gallery_queryset(request.user).order_by('-created_at')
    context = {
        'galleries': galleries,
        'current_page': 'Galeri Saya',
    }
    return render(request, 'galleryapp/gallery_manage_list.html', context)


@login_required
def gallery_create(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        images_form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            gallery = form.save(commit=False)
            gallery.created_by = request.user
            gallery.save()
            for image_file in request.FILES.getlist('images'):
                GalleryImage.objects.create(gallery=gallery, image=image_file)
            return redirect('gallery_detail', pk=gallery.pk)
    else:
        form = GalleryForm()
        images_form = GalleryImageForm()

    return render(
        request,
        'galleryapp/gallery_form.html',
        {
            'form': form,
            'images_form': images_form,
            'current_page': 'Tambah Galeri',
            'is_edit': False,
            'gallery': None,
        },
    )


@login_required
def gallery_update(request, pk):
    gallery = get_object_or_404(_user_gallery_queryset(request.user), pk=pk)
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=gallery)
        images_form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            form.save()
            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                GalleryImage.objects.filter(id__in=delete_ids, gallery=gallery).delete()
            for image_file in request.FILES.getlist('images'):
                GalleryImage.objects.create(gallery=gallery, image=image_file)
            return redirect('gallery_manage_list')
    else:
        form = GalleryForm(instance=gallery)
        images_form = GalleryImageForm()

    context = {
        'form': form,
        'images_form': images_form,
        'current_page': 'Edit Galeri',
        'is_edit': True,
        'gallery': gallery,
    }
    return render(request, 'galleryapp/gallery_form.html', context)


@login_required
def gallery_delete(request, pk):
    gallery = get_object_or_404(_user_gallery_queryset(request.user), pk=pk)
    if request.method == 'POST':
        gallery.delete()
        return redirect('gallery_manage_list')
    return redirect('gallery_manage_list')
