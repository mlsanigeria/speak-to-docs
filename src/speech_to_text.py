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







## SPEECH SYNTHESIS - Speech Synthesis/Generation with Azure Speech Service

text = "I love the AI Hacktoberfest challenge by MLSA Nigeria!"

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=os.getenv("SPEECH_KEY"), region=os.getenv("SPEECH_REGION"))
# audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")
# audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")

# The neural multilingual voice can speak different languages based on the input text.
speech_config.speech_synthesis_voice_name='en-NG-EzinneNeural'


speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

speech_synthesis_result = speech_synthesizer.speak_text_async("Hiiiiii").get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
    
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")



def speech_to_text(audio_file: str) -> str:
    """
    Transcribe speech from an audio file using Azure Speech Service.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
    
    Returns:
        str: Transcription of the audio
    """
    # Define the endpoint and subscription key
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    result = speech_recognizer.recognize_once()

    # Check the result status
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
        
    return None
