from django.contrib import admin
from .models import UploadedFile, ExtractedText

# Register your models here.
admin.site.register(UploadedFile)
admin.site.register(ExtractedText)