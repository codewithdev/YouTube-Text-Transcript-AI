from pydub import AudioSegment
from openai import OpenAI
import yt_dlp
import os

# Set your OpenAI API key
openai_api_key = "apikey"

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=openai_api_key)

# Function to download YouTube video and convert to mp3
def download_yt_video_to_mp3(yt_url, output_filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_filename.replace('.mp3', '')  # Remove .mp3 extension
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])

# Download the YouTube video and save as mp3 in the current working directory
yt_url = "yturl"  # Replace with the actual YouTube URL
output_filename = "downloaded_audio.mp3"
download_yt_video_to_mp3(yt_url, output_filename)

# Load the downloaded audio file
audio_path = os.path.join(os.getcwd(), output_filename)
try:
    audio = AudioSegment.from_mp3(audio_path)
except FileNotFoundError:
    print(f"Error: Audio file not found at {audio_path}")
    print("Available files in the current directory:")
    print(os.listdir())
    exit(1)

# Length of audio in milliseconds
length_audio = len(audio)

# Open the transcript file in write mode
with open("transcript.md", "w") as transcript_file:
    # Split audio into 10 min (600000 ms) chunks
    for i in range(0, length_audio, 600000):
        # Calculate the start and end of the chunk
        start = i
        end = min(i + 600000, length_audio)  # Ensure end does not exceed audio length

        # Extract the chunk of audio
        chunk = audio[start:end]

        # Export the chunk to an mp3 file
        chunk_filename = f"chunk{i//600000}.mp3"
        chunk.export(chunk_filename, format="mp3")
        
        # Open the exported chunk to send for transcription
        with open(chunk_filename, "rb") as audio_file:
            # Call the updated transcription API
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )

        # Access the transcription text directly from the '.text' attribute
        transcription_text = transcript_response.text

        # Write the transcription text to the .md file
        transcript_file.write(transcription_text + "\n\n")

        # Print the transcription text
        print(transcription_text)
