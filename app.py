import gradio as gr
import os
import speech_recognition as sr
import whisper  
import time
import pyttsx3
from pydub import AudioSegment
from gtts import gTTS

class PigLatinVoiceAgent:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = whisper.load_model("medium")  
        self.engine = pyttsx3.init()
        
    # Methods to Handle UI Settings - START #
    
    #Apply Voice Gender using pyttsx3 Engine
    def set_voice_gender(self, gender):
        voices = self.engine.getProperty('voices')
        if gender == "male":
            self.engine.setProperty('voice', voices[0].id)  
        elif gender == "female":
            self.engine.setProperty('voice', voices[1].id)  
    
    #Apply Voice Speed using pyttsx3 Engine
    def set_speed(self, speed):
        if speed == "slow":
            self.engine.setProperty('rate', 100)  
        else:
            self.engine.setProperty('rate', 150)  
    
    #Apply Voice Tone using pyttsx3 Engine    
    def set_tone(self, tone):
        # Map the slider value (0 to 100) to a pitch range (0.5 to 2.0)
        pitch = 0.5 + (tone / 100) * 1.5
        self.engine.setProperty('pitch', pitch)    
        
    # Mix Background Noise file Based on User Selection    
    def add_background_noise(self, audio_file, noise_file):
        main_audio = AudioSegment.from_file(audio_file)
        noise_audio = AudioSegment.from_file(noise_file)
        noise_audio = noise_audio - abs(-20)
        mixed_audio = main_audio.overlay(noise_audio)
        mixed_audio.export("mixed_response.mp3", format="mp3")
        return "mixed_response.mp3"    
     # Methods to Handle UI Settings - END #    
        
    def to_pig_latin(self, text):
        print("to_pig_latin enter") 
        vowels = "aeiou"
        pig_latin_text = []
        for word in text.split():
            if word[0].lower() in vowels:
                pig_latin_text.append(word + "yay")
            else:
                pig_latin_text.append(word[1:] + word[0] + "ay")
        return ' '.join(pig_latin_text)

    def from_pig_latin(self, text):
        words = text.split()
        english_text = []
        for word in words:
            if word[-3:] == 'yay':
                english_text.append(word[:-3])
            else:
                english_text.append(word[-2] + word[:-2])
        return ' '.join(english_text)
    
    def audio_to_text(self, audio_file):
        print("enter audio_to_text:")
        result = self.whisper_model.transcribe(audio_file, language="en",temperature=0.0,fp16=False) 
        print("exit audio_to_text:")
        return result["text"] if result["text"].strip() else "Could not understand audio"    
                
    def audio_to_text_SR(self, audio_file):
        with sr.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Could not understand audio"
    
    def respond(self, input_audio, voice, speed, tone, background_noise):
        print("enter respond")
        # Convert recorded audio to text
        if input_audio is None:
            print("input audi is none return:")
            return "response.mp3"  
        
        print("respond input_audio:",input_audio)
        input_text = self.audio_to_text(input_audio)
        piglatinFound = True
        for word in input_text.split():
            if "ay" in word[-3:]:
                print("input_text:",word[-3:]);  
            else:
                piglatinFound = False
    
        if piglatinFound:
           response_text = self.to_pig_latin("I understand your Pig Latin!")
        else:
           response_text = "orrysay , easeplay eakspay inyay igpay atinlay, iyay annotcay understandyay otherwiseyay"
            
        self.set_voice_gender(voice)
        self.set_speed(speed)
        self.set_tone(tone)
        
        # Generate speech using pyttsx3
        self.engine.save_to_file(response_text, "response.mp3")
        self.engine.runAndWait()
                
        # Add background noise if selected
        if background_noise != "None":
            noise_file = f"{background_noise.lower()}.mp3"  # Assume noise files are in an 'assets' folder
            print("background_noise file path:",noise_file);
            if os.path.exists(noise_file):
                response_audio = self.add_background_noise("response.mp3", noise_file)
            else:
                response_audio = "response.mp3"
        else:
            response_audio = "response.mp3"
        
        print("exit respond")
        return response_audio
 
 # Initialize the Pig Latin Voice Agent
voiceAgent = PigLatinVoiceAgent()

# Function to reset inputs
def reset():
    return None, None, "male", "normal", 1.0, "None"
    
# Gradio interface
with gr.Blocks() as voiceagentdemo:
    gr.HTML("<h1 style='text-align: center; font-size: 40px; font-weight: bold; color: #007BFF;'>PigLatin Voice Agent</h1>")  
    gr.HTML("<p style='text-align: center; font-size: 20px;'>Speak in Pig Latin using your microphone and adjust the voice settings using UI.</p>")

    with gr.Row():
        mic_input = gr.Audio(sources=["microphone"], type="numpy", label="Record your voice", interactive=True)
        output_audio = gr.Audio(label="Response")

    with gr.Row():
        voice = gr.Radio(["male", "female"], label="Voice", value="male")
        speed = gr.Radio(["normal", "slow"], label="Speed", value="normal")

    with gr.Row():
        tone = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, label="Tone")
        background_noise = gr.Radio(["None", "Nature", "Rain"], label="Background Noise", value="None")

    submit_btn = gr.Button("Submit")
    reset_btn = gr.Button("Reset")

    submit_btn.click(
        voiceAgent.respond,
        inputs=[mic_input, voice, speed, tone, background_noise],
        outputs=output_audio
    )

    reset_btn.click(
        reset,
        inputs=[],
        outputs=[mic_input, output_audio, voice, speed, tone, background_noise]
    )

# Launch the app
voiceagentdemo.launch(share=True)
