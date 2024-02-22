import os
import json
import re
import requests

dataset = "dataset-dummy/"
os.listdir(dataset)

# TODO: Check it has an mp4 and a caption
path = dataset + "D3owqp72SJE/caption-a.en.json"
with open(path, 'r') as caption_file:
    caption = json.load(caption_file)
print(caption.keys())

# Everything is in events
events = caption['events']

print(len(events)) # 1460 events

raw_text = ""
all_words = []
all_timestamps = []

for event in events:
    if 'segs' not in event:
        continue
    if event['segs'][0]['utf8'] == '\n':
        continue
    
    words = [x['utf8'].strip(' ') for x in event['segs']]
    timestamps = [event['tStartMs'] + (x['tOffsetMs'] if 'tOffsetMs' in x else 0) for x in event['segs']]

    all_words += words
    all_timestamps += timestamps
    
    for word in words:
        raw_text += word + " "
        
print(all_words)
print(all_timestamps)
print(len(all_words))
print(len(all_timestamps))

all_segments = []

for event in events:
    if 'segs' not in event:
        continue
    if event['segs'][0]['utf8'] == '\n':
        all_segments.append("\n")  # Preserving paragraph breaks
        continue
    
    segment_text = " ".join([seg['utf8'].strip() for seg in event['segs']])
    all_segments.append(segment_text)

# Joining all segments into a single string, ready for punctuation processing
raw_text = " ".join(all_segments)

print("Prepared Text for Punctuation Processing:")
print(raw_text)

def call_gpt_4(messages):
    # Call GPT-4 API
    headers = {'Authorization': 'Bearer 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', 'Content-Type': 'application/json'}
    url = 'https://api.openai.com/v1/chat/completions'

    response = requests.post(url, headers=headers, data=json.dumps(messages))
    print(response)
    content = response.json()["choices"][0]["message"]["content"]
    return content

data = {
    'model': 'gpt-3.5-turbo-16k',
    "messages": [{"role": "system", "content": "You are a professional transcript punctuator. You recite the transcript EXACTLY as provided to you, but with proper punctuation added. You do not deviate from the transcript in any way."}, 
                {"role": "user", "content": "Transcript provided: " + raw_text}],
}

punctuated_text = call_gpt_4(data)
print(punctuated_text)

from Levenshtein import distance

def align_timestamps(original_words, timestamps, punctuated_words):
  # Initialize DP table
  dp = [[float('inf')] * (len(punctuated_words) + 1) for _ in range(len(original_words) + 1)]
  for i in range(len(original_words) + 1):
    dp[i][0] = i

  # Fill DP table using Levenshtein distance and timestamps
  for i in range(1, len(original_words) + 1):
    for j in range(1, len(punctuated_words) + 1):
      dist = distance(original_words[i-1], punctuated_words[j-1])
      costs = [dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + dist]
      dp[i][j] = min(costs)
      if costs[2] == min(costs) and i > 0 and j > 0:
        prev_timestamp = timestamps[i-2] if abs(timestamps[i-2] - timestamps[i-1]) > 1000 else timestamps[i-1]
        timestamps[i-1] = max(timestamps[i-1], prev_timestamp)

  # Backtrack to find optimal alignment
  alignment = []
  i, j = len(original_words), len(punctuated_words)
  while i > 0 or j > 0:
    if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + distance(original_words[i-1], punctuated_words[j-1]):
      alignment.append((original_words[i-1], timestamps[i-1], punctuated_words[j-1]))
      i -= 1
      j -= 1
    elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
      alignment.append((original_words[i-1], timestamps[i-1], None))
      i -= 1
    else:
      alignment.append((None, None, punctuated_words[j-1]))
      j -= 1

  return alignment[::-1]

punctuated_words = re.findall(r"\b\w+(?:'\w+)?", punctuated_text)

alignment = align_timestamps(all_words, all_timestamps, punctuated_words)
for original_word, timestamp, punctuated_word in alignment:
  print(f"{original_word} ({timestamp}) -> {punctuated_word}")

sentences = []
current_sentence = ""
current_start_timestamp = None

for original_word, timestamp, punctuated_word in alignment:
    if current_sentence and (punctuated_word in [".", "!"]):
        # Sentence ends here
        sentence_duration = estimate_duration(current_sentence)
        if sentence_duration < 8:
            # Merge with next sentence if too short
            current_sentence += " " + next(alignment)[2]
            current_end_timestamp = next(alignment)[1]
        else:
            # Add complete sentence and reset
            sentences.append((current_sentence, current_start_timestamp, current_end_timestamp))
            current_sentence = ""
            current_start_timestamp = None
    else:
        # Accumulate words for the current sentence
        current_sentence += " " + punctuated_word
        if not current_start_timestamp:
            current_start_timestamp = timestamp

# Handle the last sentence if not merged
if current_sentence:
    sentence_duration = estimate_duration(current_sentence)
    sentences.append((current_sentence, current_start_timestamp, current_end_timestamp))

# Print final sentences and durations
for sentence_text, start_timestamp, end_timestamp in sentences:
    duration = (end_timestamp - start_timestamp) / 1000  # Convert milliseconds to seconds
    print(f"Sentence: {sentence_text}")
    print(f"Duration: {duration:.2f} seconds")