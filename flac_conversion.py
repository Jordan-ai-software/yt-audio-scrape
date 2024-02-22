from pydub import AudioSegment
import os

def convert_mp4_to_flac(folder_path):
    # Traverse the directory tree
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the current file is an MP4 file
            if file.endswith(".mp4"):
                full_path = os.path.join(root, file)
                # Define the output path with the same name but with a .flac extension
                output_path = full_path.rsplit('.', 1)[0] + '.flac'
                
                try:
                    # Load the MP4 file
                    audio = AudioSegment.from_file(full_path, "mp4")
                    # Set the frame rate to 44100
                    audio = audio.set_frame_rate(44100)
                    # Export the audio to FLAC
                    audio.export(output_path, format="flac")
                    print(f"Converted {file} to FLAC.")
                except Exception as e:
                    print(f"Failed to convert {file}: {e}")

folder_path = 'dataset-dummy'
convert_mp4_to_flac(folder_path)
