from django.http import HttpResponse
from openai import OpenAI
import base64
from pdf2image import convert_from_path
from pathlib import Path
from .models import UploadedFile, ExtractedText

def generateMessages(prompts, imageUrls):
    messages = []
    finalContent = []

    finalPrompt = "Get the following information from all the images together - "
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
        uploadedFileInstance = UploadedFile(file=uploadedFile)
        uploadedFileInstance.save()
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
        if image.size[0] * image.size[1] > 518400:
            image.save(imagePath, 'JPEG', optimize = True, quality=20)
        else:
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
        max_tokens=500,
    )

    return response.choices[0].message.content

def saveExtractedText(extractedText, uploadedFile):
    extractedTextInstance = ExtractedText(file=uploadedFile, text=extractedText)
    extractedTextInstance.save()