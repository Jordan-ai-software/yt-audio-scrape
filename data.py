import os
import json
from pydub import AudioSegment
import concurrent.futures

def extract_words_and_timestamps(caption_file_path):
    with open(caption_file_path, 'r') as caption_file:
        caption = json.load(caption_file)
        events = caption['events']
        all_words = []
        all_timestamps = []
        for event in events:
            if 'segs' not in event or event['segs'][0]['utf8'] == '\n':
                continue
            words = [x['utf8'].strip(' ') for x in event['segs']]
            timestamps = [event['tStartMs'] + (x.get('tOffsetMs', 0)) for x in event['segs']]
            all_words += words
            all_timestamps += timestamps
    return all_words, all_timestamps

def process_folder(folder):
    print(folder)
    dataset = "dataset-4/"
    processed_dataset = "processed_dataset_3/"
    path = os.path.join(dataset, folder)
    files = os.listdir(path)
    
    mp4_file = [f for f in files if f.endswith('.mp4')]
    json_file = [f for f in files if f == 'caption-a.en.json']
    
    if mp4_file and json_file:
        mp4_path = os.path.join(path, mp4_file[0])
        json_path = os.path.join(path, json_file[0])
        all_words, all_timestamps = extract_words_and_timestamps(json_path)
        
        processed_segment_path = os.path.join(processed_dataset, folder, "segments")
        os.makedirs(processed_segment_path, exist_ok=True)
        
        audio = AudioSegment.from_file(mp4_path)
        segment_start = all_timestamps[0]
        segment_index = 0
        segment_words = []
        
        i = 0
        transcript_text = ""
        
        while i < len(all_words):
            word_start = all_timestamps[i]
            if word_start - segment_start > 8000 or i == len(all_words) - 1:
                if i == len(all_words) - 1:
                    i += 1
                
                segment_name = f"segment_{segment_index}.flac"
                segment_file = os.path.join(processed_segment_path, segment_name)
                
                segment_end = all_timestamps[i-1] if i > 0 else segment_start + 8000
                segment_audio = audio[segment_start:segment_end]
                segment_audio = segment_audio.set_frame_rate(44100)
                segment_audio.export(segment_file, format="flac")
                
                segment_text = segment_name + " " + " ".join(segment_words) + "\n"
                transcript_text += segment_text
                
                segment_start = word_start
                segment_index += 1
                segment_words = []
            else:
                segment_words.append(all_words[i])
                i += 1
        
        with open(os.path.join(processed_segment_path, "segment_transcript.txt"), 'w') as transcript_file:
            transcript_file.write(transcript_text)

if __name__ == "__main__":
    dataset = "dataset-4/"
    folders = os.listdir(dataset)
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(process_folder, folders)