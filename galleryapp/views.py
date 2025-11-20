from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Gallery, GalleryImage
from .forms import GalleryForm, GalleryImageForm


def gallery_list(request):
    galleries = Gallery.objects.select_related('created_by').all().order_by('-created_at')
    return render(request, 'galleryapp/gallery_list.html', {'galleries': galleries, 'current_page': 'Gallery'})


def gallery_detail(request, pk):
    gallery = get_object_or_404(Gallery.objects.select_related('created_by'), pk=pk)
    return render(request, 'galleryapp/gallery_detail.html', {'gallery': gallery, 'current_page': gallery.title})


@login_required
def gallery_create(request):
    print("Sebelum pengecekan metode")
    print("FILES:", request.FILES)
    print("POST:", request.POST)
    print("FILES.getlist('images'):", request.FILES.getlist('images'))
    print("FILES.keys():", request.FILES.keys())

    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        images_form = GalleryImageForm(request.POST, request.FILES)
        
        print(request.FILES)
        if form.is_valid() and images_form.is_valid():
            print("Form valid")
            gallery = form.save(commit=False)
            gallery.created_by = request.user
            gallery.save()
            for image_file in request.FILES.getlist('images'):
                GalleryImage.objects.create(gallery=gallery, image=image_file)
            return redirect('gallery_detail', pk=gallery.pk)
        else:
            print("Form tidak valid")
            print("Form utama errors:", form.errors)
            print("Form images errors:", images_form.errors)
            print("Non-field form errors:", form.non_field_errors())
            print("Non-field image errors:", images_form.non_field_errors())
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
        },
    )
