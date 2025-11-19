from django.contrib import admin
from .models import Person, Marriage, Child, VisitorLog, AppConfig, ImageCarousel, AboutArticle

from django.utils.timezone import localtime
from django import forms
from ckeditor.widgets import CKEditorWidget

class AboutArticleAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = AboutArticle
        fields = '__all__'

class MarriageInline(admin.ModelAdmin):
    list_display = ('husband', 'wife', 'date_of_marriage')
    search_fields = ('husband__name', 'wife__name')

class ChildInline(admin.ModelAdmin):
    list_display = ('person', 'marriage')
    search_fields = ('person__name', 'marriage__husband__name', 'marriage__wife__name')
    
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name','gender','birth_date', 'user', 'created_at', 'updated_at', 'is_root')
    search_fields = ('name',)
    readonly_fields = ('user',)

class AppConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name',)

class ImageCarouselAdmin(admin.ModelAdmin):
    list_display = ('image', 'caption', 'order')
    search_fields = ('caption',)
    ordering = ('order',)



@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    # local_time = localtime(log.timestamp)
    list_display = ('ip_address', 'path', 'timestamp')
    search_fields = ('ip_address', 'path', 'user_agent')
    list_filter = ('timestamp',)

admin.site.register(Person, PersonAdmin)
admin.site.register(Marriage, MarriageInline)
admin.site.register(Child, ChildInline)
admin.site.register(AppConfig, AppConfigAdmin)
admin.site.register(ImageCarousel, ImageCarouselAdmin)

@admin.register(AboutArticle)
class AboutArticleAdmin(admin.ModelAdmin):
    form = AboutArticleAdminForm
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

