# Does a conversion from mp4 to wav
# Input:
# SOURCE_DIR
# |- ABC
# ||- audio.mp4
# ||- caption-a-e.json
# |- BCD
# ||- audio.mp4
# ||- caption-a-e.json
#
# Output:
# OUTPUT_DIR
# |- ABC
# ||- audio.wav
# ||- caption-a-e.json
# |- BCD
# ||- audio.wav
# ||- caption-a-e.json

import sys
import os
import json
import shutil
import subprocess
import time
import random
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

def ffmpeg_encode_wav(file_to_encode):
    cmd = ['ffmpeg', '-y', '-i', file_to_encode[0], '-c:a', 'pcm_s16le', '-ar', '44100', '-ac', '1', file_to_encode[1]]
    print("Running", cmd)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Take input and output dirs from the command line as the first two arguments
SOURCE_DIR = os.path.abspath(sys.argv[1])
OUTPUT_DIR = os.path.abspath(sys.argv[2])

print(len(os.listdir(SOURCE_DIR)))
print(len(os.listdir(OUTPUT_DIR)))

start_time = time.time()
futures = []
with ThreadPoolExecutor(max_workers=48) as encode_exec:
    for folder in os.listdir(SOURCE_DIR):
        if os.path.exists(os.path.join(SOURCE_DIR, folder, "audio.mp4")) and os.path.exists(os.path.join(SOURCE_DIR, folder, "caption-a.en.json")):
            os.makedirs(os.path.join(OUTPUT_DIR, folder), exist_ok=True)
            shutil.copy(os.path.join(SOURCE_DIR, folder, "caption-a.en.json"), os.path.join(OUTPUT_DIR, folder, "caption-a.en.json"))
            futures.append(encode_exec.submit(ffmpeg_encode_wav, (os.path.join(SOURCE_DIR, folder, "audio.mp4"), os.path.join(OUTPUT_DIR, folder, "audio.wav"))))

end_time = time.time()
for future in as_completed(futures):
    result = future.result()
    print(result)
print("Total encoding time", (end_time - start_time))
