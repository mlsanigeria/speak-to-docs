import os
import requests
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
load_dotenv()

# Define the endpoint and subscription key
url = f"https://eastus.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-05-15-preview"
subscription_key = os.getenv('SUBSCRIPTION_KEY')


## TRANSCRIPTION - Fast Transcription with Azure Speech Service

# Set up headers with your subscription key
# subscription_key = 'YourSubscriptionKey'
headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Accept': 'application/json'
}

# Define the files and data for the request
files = {
    'audio': open("audio.wav", 'rb')  # Replace with your audio file path
}
data = {
    'definition': '''
    {
        "locales": ["en-US"],
        "profanityFilterMode": "Masked"
    }
    '''
}
# "channels": [0, 1]

# Make the POST request
response = requests.post(url, headers=headers, files=files, data=data)

# Check the response
if response.status_code == 200:
    print('Success!')
    print(response.json())
    print(response.json()['combinedPhrases'][0]['text'])
else:
    print('Error:', response.status_code)
    print("\n" + response.text)
    error_message = "Error: " + str(response.status_code) + "\n" + response.text
    raise Exception(error_message)






## SPEECH SYNTHESIS - Speech Synthesis/Generation with Azure Speech Service

text = "I love the AI Hacktoberfest challenge by MLSA Nigeria!"

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=os.getenv("SPEECH_KEY"), region=os.getenv("SPEECH_REGION"))
audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")
# audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")

# The neural multilingual voice can speak different languages based on the input text.
speech_config.speech_synthesis_voice_name='en-NG-EzinneNeural'

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

speech_synthesis_result = speech_synthesizer.speak_text_async().get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
    
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

