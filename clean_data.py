import os
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_file(file_path):
    """
    Process a single file to check if it's a valid FLAC file and delete it if not.
    Additionally, delete the file if its duration is over 20 seconds.
    """
    try:
        data, samplerate = sf.read(file_path)
        duration = len(data) / samplerate
        if duration > 20:
            os.remove(file_path)
            return f"Deleted file due to being over 20 seconds: {file_path}"
    except RuntimeError as e:
        if "psf_fseek()" in str(e) or "Failed to decode audio." in str(e):
            os.remove(file_path)
            return f"Deleted misformatted file due to error: {file_path}, Error: {e}"
        else:
            return f"Error reading {file_path}: {e}"
    except Exception as e:
        return f"Unhandled exception for {file_path}: {e}"
    return None

def check_and_delete_flac_files_concurrent(directory):
    """
    Check FLAC files in the given directory and delete those that cannot be decoded,
    using concurrency to speed up the process.
    """
    # List to hold the future results
    futures = []
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.flac'):
                    file_path = os.path.join(root, file)
                    # Submit the file processing task to the ThreadPoolExecutor
                    futures.append(executor.submit(process_file, file_path))

        # Iterate over the future results as they complete
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(result)

# Replace '/path/to/directory' with the actual directory path
directory_path = 'processed_dataset_3/'
check_and_delete_flac_files_concurrent(directory_path)

