from django.db import models

# Create your models here.

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')

class ExtractedText(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    parameter = models.CharField(max_length=100)
    value = models.TextField()