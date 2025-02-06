from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import webvtt
import os

def get_video_id(url):
    if 'youtu.be' in url:
        return url.split('/')[-1]
    return url.split('v=')[-1].split('&')[0]

def get_transcript(video_id, download_subtitles=True):
    try:
        # Try fetching the transcript using YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return [{'text': entry['text'], 'start': entry['start']} for entry in transcript]
    except Exception as e:
        # If transcript fetch fails, check if we need to download the subtitles and parse them
        if download_subtitles:
            print(f"Error fetching transcript from API: {str(e)}. Trying to download subtitles...")
            return download_and_parse_subtitles(video_id)
        else:
            raise Exception(f"Error fetching transcript: {str(e)}")

def download_and_parse_subtitles(video_id):
    # Download subtitles using yt-dlp and parse them
    ydl_opts = {
        'quiet': True,
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'skip_download': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
        if 'subtitles' in result and 'en' in result['subtitles']:
            subtitle_file = result['subtitles']['en'][0]['url']
            # Read the subtitle file directly
            subtitle_data = ydl.urlopen(subtitle_file).read().decode('utf-8')
            return parse_vtt(subtitle_data)
        else:
            raise Exception("No subtitles available for this video.")

def parse_vtt(vtt_data):
    captions = []
    vtt = webvtt.read_buffer(vtt_data)
    for caption in vtt:
        captions.append({
            'text': caption.text,
            'start': caption.start
        })
    return captions

def get_youtube_cookies_path():
    return os.getenv("YOUTUBE_COOKIES_PATH", "default_path_to_cookies")  # Indented correctly
  
def search_youtube_videos(query, max_results=5):
    cookies_path = get_youtube_cookies_path()  # Get cookies path dynamically

ydl_opts = {
    'quiet': True,
    'extract_flat': True,
    'force_generic_extractor': True,
    'cookies': cookies_path  # Use dynamic cookies path
}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        return [{
            'title': entry['title'],
            'url': entry['url'],
            'duration': entry.get('duration', 0),
            'views': entry.get('view_count', 0)
        } for entry in result['entries']]

def chunk_transcript(transcript, chunk_size=300):  # Reduced from 500
    chunks = []
    current_chunk = []
    current_length = 0
    
    for entry in transcript:
        if current_length + len(entry['text']) > chunk_size:
            chunks.append({
                'text': ' '.join(current_chunk),
                'start': chunks[-1]['start'] if chunks else entry['start']
            })
            current_chunk = []
            current_length = 0
            
        current_chunk.append(entry['text'])
        current_length += len(entry['text'])
        
    if current_chunk:
        chunks.append({
            'text': ' '.join(current_chunk),
            'start': entry['start']
        })
        
    return chunks
