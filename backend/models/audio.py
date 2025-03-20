import pyttsx3
import os
import uuid

# Initialize the TTS engine once
engine = pyttsx3.init()

def generate_audio(summary_text, output_dir="audio"):
    """
    Generate audio from summary text
    """
    os.makedirs(output_dir, exist_ok=True)
    unique_filename = f"summary_audio_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(output_dir, unique_filename)
    
    engine.save_to_file(summary_text, output_path)
    engine.runAndWait()

    return output_path
