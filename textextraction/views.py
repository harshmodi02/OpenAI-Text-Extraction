from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path
from .models import UploadedFile, ExtractedText
from .helper import saveFile, convertPdfToJpg, extractText, saveExtractedText

# Create your views here.

def home(request):
    finalOutput = ""
    uploadedFiles = UploadedFile.objects.all()

    if request.method == 'POST':
        if 'uploadFile' in request.FILES:
            uploadedFile = saveFile(request.FILES['uploadFile'])
            pdfPath = uploadedFile.file.name

            imagePaths = convertPdfToJpg("media/" + pdfPath)

            prompts = []
            selectedPrompts = request.POST.getlist('parameter')

            if 'owner' in selectedPrompts:
                prompts.append('Account Owner Name')
            if 'portfolio-value' in selectedPrompts:
                prompts.append('Portfolio Value')
            if 'cost-basis' in selectedPrompts:
                prompts.append('Name and Cost Basis of Each Holding')
            if request.POST.get('customParameter').strip():
                prompts.append(request.POST.get('customParameter').strip())

            finalOutput = extractText(prompts, imagePaths)

            saveExtractedText(finalOutput,uploadedFile)


    return render(request, 'textextraction/dashboard.html', {'finalOutput': finalOutput, 'uploadedFiles': uploadedFiles})

def previouslyExtractedText(request):
    if request.method == 'GET':
        fileId = request.GET.get("file")
        fileObj = UploadedFile.objects.get(id=fileId)

        extractedTextObj = ExtractedText.objects.get(file=fileObj)

    return HttpResponse(extractedTextObj.text)
