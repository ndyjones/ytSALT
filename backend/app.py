#!/usr/bin/env python3
"""
ytsALT - YouTube Salt Content Optimization Tool
A Flask application that generates optimized meta text for YouTube videos using AI.
This module serves as the main entry point for the application, handling HTTP requests
and coordinating between various services for video information extraction and processing.

Version: 1.0.0
Author: NC Jones @ndyjones
License: MIT
Created: February 2025

Routes:
    /api/video-info (POST) - Fetches metadata for a given YouTube video
    /api/transcript (POST) - Retrieves and processes video transcript
    /api/optimize/title (POST) - Generates optimized title suggestions
    /api/optimize/description (POST) - Generates optimized description suggestions

Dependencies:
    - Flask
    - flask-cors
    - yt-dlp
    - youtube-transcript-api
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from services.video_service import VideoService
from services.transcript_service import TranscriptService
from services.ai_service import AIService

# Initialize the services
video_service = VideoService()
transcript_service = TranscriptService()
ai_service = AIService()

app = Flask(__name__)

# Configure CORS with specific settings
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],  # frontend URL
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

def create_options_response():
    """Helper function to create OPTIONS response"""
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

@app.route('/api/video-info', methods=['POST', 'OPTIONS'])
def fetch_video_info():
    if request.method == 'OPTIONS':
        return create_options_response()

    try:
        data = request.get_json()
        video_url = data.get('url')
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400

        print(f"Processing URL: {video_url}")
        video_info = video_service.get_video_info(video_url)
        print("Successfully processed video")
        return jsonify(video_info)
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/transcript', methods=['POST', 'OPTIONS'])
def fetch_transcript():
    if request.method == 'OPTIONS':
        return create_options_response()

    try:
        data = request.get_json()
        video_url = data.get('url')
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400

        print(f"Fetching transcript for URL: {video_url}")
        transcript_data = transcript_service.get_transcript(video_url)
        print("Successfully fetched transcript")
        return jsonify(transcript_data)
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimize/title', methods=['POST', 'OPTIONS'])
def optimize_title():
    if request.method == 'OPTIONS':
        return create_options_response()

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        result = ai_service.optimize_title(data)
        return jsonify(result)
    except Exception as e:
        print(f"Error in optimize_title route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/optimize/description', methods=['POST', 'OPTIONS'])
def optimize_description():
    if request.method == 'OPTIONS':
        return create_options_response()

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        result = ai_service.optimize_description(data)
        return jsonify(result)
    except Exception as e:
        print(f"Error in optimize_description route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/optimize/tags', methods=['POST', 'OPTIONS'])
def optimize_tags():
    if request.method == 'OPTIONS':
        return create_options_response()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        result = ai_service.optimize_tags(data)
        return jsonify(result)
    except Exception as e:
        print(f"Error in optimize_tags route: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)