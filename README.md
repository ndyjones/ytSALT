# ytSALT - YouTube SALT - A content SEO optimization tool

## Overview
ytSALT (YouTube Salt) is an AI-powered tool for optimizing YouTube video metadata. It uses GPT-4 to analyze video content and generate SEO-optimized suggestions for titles, descriptions, and tags.

## Features
- Video metadata extraction
- Transcript analysis
- Thumbnail analysis
- AI-powered optimization for:
  - Video titles
  - Video descriptions
  - Tags (with transcript-aware suggestions)
- Character limit monitoring
- Duplicate tag prevention
- Copy-to-clipboard functionality

## Tech Stack
### Backend
- Python 3.x
- Flask
- OpenAI GPT-4o, GPT-4o-mini (for image analysis)
- yt-dlp
- youtube-transcript-api
- Pillow
- requests

### Frontend
- React
- Tailwind CSS
- Axios
- Vite
- Lucide React (icons)

## Setup
1. Clone the repository
2. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Install frontend dependencies:
```bash
cd frontend
npm install
```
4. Set up environment variables:
Create a .env file in the backend directory with:
```plaintext
OPENAI_API_KEY=your_api_key_here
```


## Running the application
1. Start the backend server:
```bash
cd backend
python app.py 
```
2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

## Current status
- Implemented core optimization features for titles and descriptions
- Tag optimization with transcript analysis
- Thumbnail optimization recommendations
- Timestamp/chapter suggestions

- Working on enhanced optimization features:
  - Keyword research integration

## Development roadmap
- Analytics support
- Batch video optimization
- Custom optimization templates (demos, explainers, product showcases)
- Youtube API integration
- Historical optimization tracking

## Author
NC Jones @ndyjones

