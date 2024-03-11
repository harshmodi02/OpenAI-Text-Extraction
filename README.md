# OpenAI-Text-Extraction
Django project that takes in a PDF file and uses OpenAI’s vision model to extract a few pieces of structured information from the file.

Users has 2 options for selecting the file to transcribe:
1. Upload a new file: <br>
In this scenario, user uploads a new file, selects and/or add and custom information that they want to extract. On clicking submit, the extracted information
is displayed to the user.
2. Select an existing file: <br>
If the user had previously uploaded and transcribed a file, they can simply select the same file and see the earlier transcribed result hence saving the wait time and the cost
involved with re-transcribing. If they want more information, they can still go ahead and submit the form with the information required to get the new transcribed result.
