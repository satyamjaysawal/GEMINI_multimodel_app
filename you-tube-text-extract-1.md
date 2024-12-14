# YouTube Transcript Fetcher

This Python script fetches the transcript of a YouTube video using its URL and saves it to a text file. It uses the `youtube-transcript-api` library to retrieve the transcript and provides error handling for invalid URLs or inaccessible videos.

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

