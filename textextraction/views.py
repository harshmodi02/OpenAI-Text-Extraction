from django.shortcuts import render
from django.http import HttpResponse
from openai import OpenAI
import base64
import requests
from pdf2image import convert_from_path
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
import tempfile
import os
from .models import UploadedFile, ExtractedText


# Create your views here.

def generateMessages(prompts, imageUrls):
    messages = []
    finalContent = []

    finalPrompt = "Get the following information from the images - "
    for prompt in prompts:
        finalPrompt += prompt + ", "

    finalTextContent = {
        "type": "text",
        "text": finalPrompt
    }

    finalContent.append(finalTextContent)

    finalImageContents = []
    for url in imageUrls:
        currContent = {
            "type": "image_url",
            "image_url": {
                "url": url,
            }
        }
        finalImageContents.append(currContent)

    for content in finalImageContents:
        finalContent.append(content)

    messages = [
         {
             "role": "user",
             "content": finalContent,
         }
    ]

    return messages

def saveFile(uploadedFile):
    try:
        uploaded_file_instance = UploadedFile(file=uploadedFile)
        uploaded_file_instance.save()
        return uploaded_file_instance
    except Exception as e:
        return HttpResponse("An error occurred while saving the file: {}".format(str(e)))

def convertPdfToJpg(pdfPath):
    outputDirectory = Path('media/images')
    outputDirectory.mkdir(parents=True, exist_ok=True)

    fileName = Path(pdfPath).name

    images = convert_from_path(pdfPath)

    imagePaths = []
    for i, image in enumerate(images):
        imagePath = outputDirectory / f'{fileName}-page{i}.jpg'
        image.save(imagePath, 'JPEG')
        pathString = ""
        with open(imagePath, "rb") as imageFile:
            base64Image = base64.b64encode(imageFile.read()).decode('utf-8')
            pathString = f"data:image/jpeg;base64,{base64Image}"

        imagePaths.append(pathString)

    return imagePaths

def extractText(inputPrompts, inputImagePaths):
    client = OpenAI()

    messages = generateMessages(inputPrompts, inputImagePaths)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=messages,
        max_tokens=300,
    )

    return response.choices[0].message.content

def saveExtractedText(extractedText, uploadedFile):
    extractedTextInstance = ExtractedText(file=uploadedFile, text=extractedText)
    extractedTextInstance.save()

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
            print(request.POST.get('customParameter'))

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