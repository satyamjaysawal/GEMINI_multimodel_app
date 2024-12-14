# YouTube Transcript Fetcher

This Python script fetches the transcript of a YouTube video using its URL and saves it to a text file. It uses the `youtube-transcript-api` library to retrieve the transcript and provides error handling for invalid URLs or inaccessible videos.

****

```python
from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_video_id(youtube_url):
    """
    Extracts the video ID from a YouTube URL.
    """
    match = re.search(r"v=([a-zA-Z0-9_-]+)", youtube_url)
    return match.group(1) if match else None

def fetch_transcript(video_url):
    """
    Fetches the transcript of a YouTube video using its URL.
    """
    video_id = get_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL. Please provide a valid one."
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine the transcript into a single string
        text = " ".join([item['text'] for item in transcript])
        return text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def save_to_file(file_name, content):
    """
    Saves the provided content to a file.
    """
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Transcript saved to {file_name}")

# Input YouTube video URL
# Predefined YouTube video URL
youtube_url = "https://www.youtube.com/watch?v=TtvytXHLAsc&t=3023s"
print(f"Using predefined URL: {youtube_url}")

# Fetch transcript
transcript = fetch_transcript(youtube_url)

# Check if the transcript was fetched successfully
if "Error" not in transcript:
    print("\nTranscript fetched successfully!")
    print("\nTranscript Preview:\n")
    print(transcript[:500])  # Display the first 500 characters of the transcript

    # Save the transcript to a file
    save_to_file("youtube_transcript.txt", transcript)
else:
    print(transcript)
```

This script accomplishes the following:

1. **Extracts the YouTube video ID** from a given URL using a regular expression.
2. **Fetches the transcript** of the video using the `youtube_transcript_api` library.
3. **Displays a preview** of the transcript if it is fetched successfully.
4. **Saves the transcript** to a file named `youtube_transcript.txt`.

## Features

- Extracts the video ID from a YouTube URL.
- Retrieves the transcript of a YouTube video.
- Saves the transcript to a text file.
- Displays a preview of the transcript in the console.

## Requirements

- Python 3.7 or higher
- The `youtube-transcript-api` library

## Installation

1. Clone or download this repository.
2. Install the required Python library:

   ```bash
   pip install youtube-transcript-api
   ```

## Usage

1. Open the script in your preferred code editor.
2. Replace the predefined YouTube URL with your desired video URL:

   ```python
   youtube_url = "https://www.youtube.com/watch?v=your_video_id"
   ```

3. Run the script:

   ```bash
   python script_name.py
   ```

4. If the transcript is successfully fetched, it will:
   - Display a preview (first 500 characters) of the transcript in the console.
   - Save the full transcript to a file named `youtube_transcript.txt`.

## Functions

### `get_video_id(youtube_url)`
Extracts the video ID from the provided YouTube URL using a regular expression.

- **Parameters**: `youtube_url` (str) - The YouTube video URL.
- **Returns**: `str` - The extracted video ID or `None` if the URL is invalid.

### `fetch_transcript(video_url)`
Fetches the transcript of the video using the video ID.

- **Parameters**: `video_url` (str) - The YouTube video URL.
- **Returns**: `str` - The transcript text or an error message.

### `save_to_file(file_name, content)`
Saves the provided content to a text file.

- **Parameters**:
  - `file_name` (str) - The name of the file.
  - `content` (str) - The text content to save.

## Example Output

If the script runs successfully, you will see the following:

```plaintext
Using predefined URL: https://www.youtube.com/watch?v=TtvytXHLAsc&t=3023s

Transcript fetched successfully!

Transcript Preview:
[Transcript text preview here]

Transcript saved to youtube_transcript.txt
```

## Error Handling

- If the URL is invalid or the video ID cannot be extracted, you will see:

  ```plaintext
  Invalid YouTube URL. Please provide a valid one.
  ```

- If the transcript cannot be fetched due to any issue (e.g., video has no transcript, API issues), you will see an error message like:

  ```plaintext
  Error fetching transcript: [Error details]
  ```

