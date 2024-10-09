import os
import requests
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants for Azure Speech Services
SPEECH_REGION = os.getenv("SPEECH_REGION")
SPEECH_KEY = os.getenv("SPEECH_KEY")

# API endpoint for speech-to-text
STT_URL = f"https://eastus.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-05-15-preview"

def transcribe_audio(audio_file_path):
    """
    Transcribe audio using Azure Speech Service.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
    
    Returns:
        dict: Transcription result
    
    Raises:
        Exception: If the API request fails
    """
    # Set up headers with subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': SPEECH_KEY,
        'Accept': 'application/json'
    }

    # Prepare the request data
    
        
    data = {
        'definition': '''
        {
            "locales": ["en-US"],
            "profanityFilterMode": "Masked"
        }
        '''
    }
    # Note: Uncomment below line to specify audio channels if needed
    # "channels": [0, 1]

    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            # Make the POST request to the API
            response = requests.post(STT_URL, headers=headers, files=files, data=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            result = response.json()
            transcription = result['combinedPhrases'][0]['text']
            
            audio_file.close()
            return transcription

    except requests.exceptions.RequestException as e:
        error_message = f"Transcription failed: {str(e)}\nResponse: {response.text if 'response' in locals() else 'No response'}"
        raise Exception(error_message)

def synthesize_speech(text, output_file="output.wav", voice_name='en-NG-EzinneNeural'):
    """
    Synthesize speech from text using Azure Speech Service.
    
    Args:
        text (str): Text to synthesize
        output_file (str): Path for the output audio file
        voice_name (str): Name of the voice to use for synthesis
    
    Returns:
        bool: True if synthesis was successful, False otherwise
    """
    try:
        # Configure speech service
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        
        # Set the voice for synthesis
        speech_config.speech_synthesis_voice_name = voice_name
        
        # Create synthesizer and generate speech
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = speech_synthesizer.speak_text_async(text).get()
        
        # Handle the result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized successfully for text: {text}")
            return True
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(f"Error details: {cancellation_details.error_details}")
                    print("Did you set the speech resource key and region values?")
            return False
    
    except Exception as e:
        print(f"An error occurred during speech synthesis: {str(e)}")
        return False

def main():
    # Example usage
    try:
        # Transcribe audio
        transcription = transcribe_audio("audio.wav")
        print(f"Transcription: {transcription}")
        
        # Synthesize speech
        sample_text = "I love the AI Hacktoberfest challenge by MLSA Nigeria!"
        synthesize_speech(sample_text)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()