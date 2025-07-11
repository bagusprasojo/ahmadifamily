from django.shortcuts import render, redirect, get_object_or_404
from .models import Person, Marriage, Child
from django import forms
from datetime import date
from django.urls import reverse
from operator import itemgetter
from itertools import groupby

# ----- FORM -----
class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'gender', 'birth_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama lengkap'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class MarriageForm(forms.Form):
    husband = forms.ModelChoiceField(
        queryset=Person.objects.filter(gender='M'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    wife = forms.ModelChoiceField(
        queryset=Person.objects.filter(gender='F'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_of_marriage = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Tanggal Pernikahan (opsional)'
        })
    )
class ChildForm(forms.Form):
    person = forms.ModelChoiceField(queryset=Person.objects.all())
    marriage = forms.ModelChoiceField(queryset=Marriage.objects.all())

# ----- VIEWS -----

def input_data(request):
    person_form = PersonForm(request.POST or None, prefix='person')
    marriage_form = MarriageForm(request.POST or None, prefix='marriage')
    child_form = ChildForm(request.POST or None, prefix='child')

    if request.method == 'POST':
        if 'add_person' in request.POST and person_form.is_valid():
            person_form.save()
            return redirect('input')
        elif 'add_marriage' in request.POST and marriage_form.is_valid():
            husband = marriage_form.cleaned_data['husband']
            wife = marriage_form.cleaned_data['wife']
            date = marriage_form.cleaned_data['date_of_marriage']
            Marriage.objects.create(husband=husband, wife=wife, date_of_marriage=date)
            return redirect('input')
        elif 'add_child' in request.POST and child_form.is_valid():
            person = child_form.cleaned_data['person']
            marriage = child_form.cleaned_data['marriage']
            Child.objects.create(person=person, marriage=marriage)
            return redirect('input')

    context = {
        'person_form': person_form,
        'marriage_form': marriage_form,
        'child_form': child_form,
        'persons': Person.objects.all(),
        'current_page': 'Input Person',
    }

    return render(request, 'treeapp/input.html', context)

def build_person_node(person):
        
        # Ambil semua pernikahan sebagai suami atau istri
        if person.gender == 'M':
            marriages = Marriage.objects.filter(husband=person)
        else:
            marriages = Marriage.objects.filter(wife=person)

        marriage_data = []
        for marriage in marriages:
            spouse = marriage.wife if person.gender == 'M' else marriage.husband
            children = Child.objects.filter(marriage=marriage)

            child_nodes = []
            for child in children:
                child_nodes.append(build_person_node(child.person))  # rekursif!

            marriage_data.append({
                'spouse': {
                    'name': spouse.name,
                    'class': 'man' if spouse.gender == 'M' else 'woman',
                    "textClass": "node-text",
                    "HTMLclass": "clickable-node",
                    "extra": {
                        "person_id": spouse.id,
                        "href": reverse('person_detail', args=[spouse.id])
                    }
                },
                'children': child_nodes
            })

        return {
            'name': person.name,            
            'class': 'man' if person.gender == 'M' else 'woman',
            'marriages': marriage_data,
            "textClass": "node-text",
            "HTMLclass": "clickable-node",
            "extra": {
                "person_id": person.id,
                "href": reverse('person_detail', args=[person.id])
            }
        }



def family_tree(request, husband_id):
    persons = Person.objects.all().order_by('name')
    try:
        person = Person.objects.get(pk=husband_id)
    except Person.DoesNotExist:
        return render(request, 'treeapp/tree.html', {
            'tree_data': [],
            'error': 'Data tidak ditemukan',
            'current_page': 'Family Tree',
            'persons': persons,
        })

    tree_data = [build_person_node(person)]
    # print(tree_data)

    context = {
        'tree_data': tree_data,
        'current_page': 'Family Tree',
        'husband_id': husband_id,
        'persons': persons,
    }
    return render(request, 'treeapp/tree.html', context)

def person_detail(request, person_id):
    person = get_object_or_404(Person, pk=person_id)

    # Hitung umur
    def hitung_umur(birth_date):
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    umur = hitung_umur(person.birth_date) if person.birth_date else None


    # Cari pasangan (suami/istri)
    if person.gender == 'M':
        marriage = Marriage.objects.filter(husband=person).first()
        spouse = marriage.wife if marriage else None
    else:
        marriage = Marriage.objects.filter(wife=person).first()
        spouse = marriage.husband if marriage else None

    # Cari anak (jika dia orang tua)
    marriages_as_parent = Marriage.objects.filter(husband=person) | Marriage.objects.filter(wife=person)
    children = Person.objects.filter(child__marriage__in=marriages_as_parent)

    # Cari orang tua (jika dia anak)
    child_record = None
    try:
        child_record = Child.objects.get(person=person)
        father = child_record.marriage.husband
        mother = child_record.marriage.wife
    except Child.DoesNotExist:
        father = None
        mother = None

    # Cari saudara kandung (anak-anak dari pernikahan yang sama)
    siblings = Person.objects.none()
    if child_record:
        siblings = Person.objects.filter(child__marriage=child_record.marriage).exclude(id=person.id)

    flat = person.get_mahram_for_template()
    # urut dulu supaya groupby berjalan
    flat = sorted(flat, key=itemgetter('jenis_label'))
    grouped = [
        {
          'jenis_label': jenis,
          'categories': list(items)
        }
        for jenis, items in groupby(flat, key=itemgetter('jenis_label'))
    ]

    context = {
        'person': person,
        'spouse': spouse,
        'children': children,
        'father': father,
        'mother': mother,
        'siblings': siblings,
        'umur': umur,
        'mahram_grouped': grouped,
        'current_page': f'Profil {person.name}',
    }

    return render(request, 'treeapp/person_detail.html', context)

