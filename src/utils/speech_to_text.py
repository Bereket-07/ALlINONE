from google.cloud import speech

def transcribe_audio(file_path):
    client = speech.SpeechClient()

    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # change based on file type
        sample_rate_hertz=16000,  # adjust to your audio file
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    full_text = ""
    for result in response.results:
        full_text += result.alternatives[0].transcript + " "

    return full_text.strip()