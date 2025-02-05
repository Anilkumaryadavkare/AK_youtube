from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

def get_video_id(url):
    if 'youtu.be' in url:
        return url.split('/')[-1]
    return url.split('v=')[-1].split('&')[0]

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, preserve_formatting=True)
        return [{'text': entry['text'], 'start': entry['start']} for entry in transcript]
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")

def search_youtube_videos(query, max_results=5):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True
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
