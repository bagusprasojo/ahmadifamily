from django.db import models
from django.utils.timezone import now
from ckeditor.fields import RichTextField
from collections import defaultdict
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

class AboutArticle(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()
    image = models.ImageField(upload_to='family_articles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "About Article"
        verbose_name_plural = "About Articles"


class ImageCarousel(models.Model):
    image = models.ImageField(upload_to='carousel_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image {self.order} - {self.caption or 'No Caption'}"

    class Meta:
        ordering = ['order']
        verbose_name = "Image Carousel"
        verbose_name_plural = "Image Carousels"

class AppConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "App Configuration"
        verbose_name_plural = "App Configurations"

class VisitorLog(models.Model):
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referer = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.ip_address} - {self.path} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
class Person(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_root = models.BooleanField(default=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='person_profile'
    )

    def get_parents(self):
        try:
            child = self.child
        except Child.DoesNotExist:
            return []
        m = child.marriage
        return [m.husband, m.wife]

    def get_children(self):
        marriages = list(self.marriages_as_husband.all()) + \
                    list(self.marriages_as_wife.all())
        return [c.person for m in marriages for c in m.children.all()]

    def get_spouses(self):
        return [m.wife for m in self.marriages_as_husband.all()] + \
               [m.husband for m in self.marriages_as_wife.all()]

    def _traverse(self, sequence):
        """
        Jalankan sequence of relations, 
        misal ['parent','child'] untuk mencari siblings.
        """
        funcs = {
            'parent': Person.get_parents,
            'child':  Person.get_children,
            'spouse': Person.get_spouses,
        }
        results = [self]
        for step in sequence:
            next_gen = []
            for p in results:
                next_gen.extend(funcs[step](p))
            results = next_gen
        # buang duplikat & diri sendiri
        return {p for p in results if p.pk != self.pk}

    def get_mahram(self):
        # mapping path → (kategori dalam BI, jenis hubungan)
        mapping = {
            ('parent',):               ('orang_tua',        'darah'),            
            ('parent',)*2:             ('kakek_nenek',      'darah'),
            ('parent',)*3:             ('buyut',            'darah'),            
            ('child',):                ('anak',             'darah'),
            ('child',)*2:              ('cucu',             'darah'),
            ('child',)*3:              ('cicit',            'darah'),
            ('parent','child'):        ('saudara',          'darah'),
            ('child','parent'):        ('saudara',          'darah'),
            ('parent','parent','child'): ('paman_bibi', 'darah'),
            ('spouse',):               ('pasangan',         'perkawinan'),
            ('spouse','parent'):       ('mertua',           'perkawinan'),
            ('spouse','child'):        ('menantu',          'perkawinan'),
            ('child','spouse'):        ('menantu',          'perkawinan'),
        }

        # kumpulkan hasil
        result = {'darah': defaultdict(list),
                  'perkawinan': defaultdict(list)}
        for path, (kategori, jenis) in mapping.items():
            orang = self._traverse(path)
            if kategori == 'paman_bibi':
                orang -= set(self.get_parents())
            elif kategori == 'menantu':
                orang -= set(self.get_children())
            elif kategori == 'saudara':
                orang -= {self, *self.get_spouses()}

            result[jenis][kategori].extend(sorted(orang, key=lambda p: p.pk))
        return result
    
    def get_mahram_for_template(self):
        """
        Mengubah output get_mahram() jadi list of dict dengan label BI
        siap dirender di template.
        """
        raw = self.get_mahram()
        LABEL_JENIS = {
            'darah':      'Mahram karena Darah',
            'perkawinan': 'Mahram karena Perkawinan',
        }
        LABEL_KAT = {
            'orang_tua':   'Orang Tua',
            'kakek_nenek': 'Kakek & Nenek',
            'buyut':       'Buyut',
            'anak':        'Anak',
            'cucu':        'Cucu',
            'cicit':       'Cicit',
            'saudara':     'Saudara Kandung',
            'paman_bibi':  'Paman & Bibi',
            'pasangan':    'Pasangan',
            'mertua':      'Mertua',
            'menantu':     'Menantu',
        }

        display = []
        for jenis, cats in raw.items():
            for kat, people in cats.items():
                if not people:
                    continue
                display.append({
                    'jenis_label':    LABEL_JENIS[jenis],
                    'kategori_label': LABEL_KAT[kat],
                    'persons':        [{'id': p.pk, 'name': p.name} for p in people],
                })
        return display

    def __str__(self):
        return self.name

class Marriage(models.Model):
    husband = models.ForeignKey(Person, related_name='marriages_as_husband', on_delete=models.CASCADE)
    wife = models.ForeignKey(Person, related_name='marriages_as_wife', on_delete=models.CASCADE)
    date_of_marriage = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.husband.name} + {self.wife.name}"

class Child(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    marriage = models.ForeignKey(Marriage, on_delete=models.CASCADE, related_name='children')

    def __str__(self):
        return self.person.name


def _generate_unique_username(full_name):
    """
    Build a slug-based username and make sure it is unique.
    """
    UserModel = get_user_model()
    base_username = slugify(full_name) or 'person'
    candidate = base_username
    suffix = 1
    while UserModel.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = f"{base_username}{suffix}"
    return candidate


@receiver(post_save, sender=Person)
def create_user_for_person(sender, instance, created, **kwargs):
    """
    Automatically create a Django auth user for every new Person so the
    individual can log in later. Admins can set/reset passwords as needed.
    """
    if not created or instance.user_id:
        return

    UserModel = get_user_model()
    username = _generate_unique_username(instance.name)
    user = UserModel.objects.create_user(username=username)
    instance.user = user
    instance.save(update_fields=['user'])
