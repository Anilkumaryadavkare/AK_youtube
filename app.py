from flask import Flask, request, render_template
from utils import *
from prompts import *
import ollama
import json
from pyngrok import ngrok

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        question = request.form.get('question')
        video_id = get_video_id(url)
        
        try:
            # Attempt to fetch the transcript with fallback to download and parse subtitles if needed
            transcript = get_transcript(video_id, download_subtitles=True)
            chunks = chunk_transcript(transcript)
            
            response = ollama.generate(
                model='deepseek-llm:7b-chat-q4_0',
                options={
                    'num_gpu': 0,
                    'num_threads': 4,
                    'num_ctx': 2048
                },
                prompt=QA_PROMPT.format(
                    chunks=json.dumps(chunks[:3]),
                    question=question
                )
            )
            
            answer, timestamps = parse_response(response['response'])
            return render_template('index.html', 
                                answer=answer,
                                timestamps=timestamps,
                                video_id=video_id)
            
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

def parse_response(response):
    answer = response.split('Timestamps:')[0].replace('Answer:', '').strip()
    timestamps = []
    if 'Timestamps:' in response:
        timestamps = [ts.strip() for ts in response.split('Timestamps:')[1].split(',')]
    return answer, timestamps

if __name__ == '__main__':
    # Start ngrok tunnel
    public_url = ngrok.connect(5000).public_url
    print(f" * Public URL: {public_url}")
    
    try:
        # Start Flask application
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        # Clean up ngrok tunnel on exit
        ngrok.kill()
