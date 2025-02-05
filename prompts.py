QA_PROMPT = """Analyze this video transcript and answer the question. Include exact timestamps from the video where this information is discussed.

Transcript chunks with timestamps:
{chunks}

Question: {question}

Answer in this format:
Answer: [your answer]
Timestamps: [comma-separated list of seconds]

If the answer isn't found, respond with:
Answer: The information is not available in the video.
Timestamps: """

SEARCH_PROMPT = """Analyze these YouTube video results for the query "{query}" and recommend the 3 most relevant videos. 

Format your response as:
1. [Video Title] - [Duration] - [URL]
2. ..."""