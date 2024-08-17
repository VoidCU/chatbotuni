from django import forms
from django.contrib import admin
from .models import Intent, Example, Conversation
from tinymce.widgets import TinyMCE
from django.db import models

class ExampleInline(admin.TabularInline):
    model = Example
    extra = 1

class IntentAdminForm(forms.ModelForm):
    response = forms.CharField(widget=TinyMCE(attrs={'cols': 50, 'rows': 10}))

    class Meta:
        model = Intent
        fields = '__all__'

class IntentAdmin(admin.ModelAdmin):
    inlines=[ExampleInline]
    form = IntentAdminForm
    list_display = ('name',)



admin.site.register(Intent, IntentAdmin)
admin.site.register(Conversation)
