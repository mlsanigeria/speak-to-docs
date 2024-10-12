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
        str: Transcription result text
    
    Raises:
        Exception: If the API request fails
    """
    if not SPEECH_KEY or not SPEECH_REGION:
        raise Exception("Azure Speech Service credentials are missing.")

    # Set up headers with subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': SPEECH_KEY,
        'Accept': 'application/json'
    }

    # Prepare the request data properly as JSON
    data = {
        'definition': '''
        {
            "locales": ["en-US"],
            "profanityFilterMode": "Masked"
        }
        '''
    }

    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            # Make the POST request to the API
            response = requests.post(STT_URL, headers=headers, files=files, data=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            result = response.json()
            # Extract transcription from the first speaker and handle errors
            transcription = result.get('combinedPhrases', [{}])[0].get('text', 'No transcription found.')
            
            return transcription

    except requests.exceptions.RequestException as e:
        error_message = f"Transcription failed: {str(e)}\nResponse: {response.text if 'response' in locals() else 'No response'}"
        raise Exception(error_message)

def synthesize_speech(text, output_file="output.wav", voice_name='en-NG-EzinneNeural', verbose=False):
    """
    Synthesize speech from text using Azure Speech Service.
    
    Args:
        text (str): Text to synthesize
        output_file (str): Path for the output audio file
        voice_name (str): Name of the voice to use for synthesis
    
    Returns:
        tuple: (bool, str) - True if synthesis was successful, False otherwise and a message
    """
    if not SPEECH_KEY or not SPEECH_REGION:
        return False, "Azure Speech Service credentials are missing."

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
            if verbose:
                print(f"Speech synthesized successfully for text: {text}")
            return True, "Speech synthesis completed successfully."
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_message = f"Speech synthesis canceled: {cancellation_details.reason}"
            if verbose:
                print(error_message)
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error and cancellation_details.error_details:
                error_message += f" Error details: {cancellation_details.error_details}."
                if verbose:
                    print("Did you set the speech resource key and region values?")
            
            return False, error_message
    
    except Exception as e:
        error_message = f"An error occurred during speech synthesis: {str(e)}"
        if verbose:
            print(error_message)
        return False, error_message

def main():
    # Example usage
    try:
        # Transcribe audio
        transcription = transcribe_audio("audio.wav")
        print(f"Transcription: {transcription}")
        
        # Synthesize speech with verbose output
        sample_text = "I love the AI Hacktoberfest challenge by MLSA Nigeria!"
        success, message = synthesize_speech(sample_text, verbose=True)
        print(message)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
