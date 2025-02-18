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
    /api/optimize/tags (POST) - Generates optimized tag suggestions
    /api/optimize/thumbnail (POST) - Generates thumbnail optimization suggestions
    /api/optimize/key-moments (POST) - Generates chapter suggestions
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
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

def create_options_response():
    """Helper function to create OPTIONS response"""
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Add explicit OPTIONS handlers for active routes
@app.route('/api/optimize/thumbnail', methods=['OPTIONS'])
def thumbnail_options():
    return create_options_response()

@app.route('/api/optimize/key-moments', methods=['OPTIONS'])
def key_moments_options():
    return create_options_response()

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

@app.route('/api/optimize/key-moments', methods=['POST', 'OPTIONS'])
def generate_key_moments():
    if request.method == 'OPTIONS':
        return create_options_response()
    try:
        data = request.get_json()
        if not data or not data.get('transcript_data'):
            return jsonify({
                "success": False,
                "error": "Missing transcript data"
            }), 400
        result = ai_service.generate_key_moments(data)
        return jsonify(result)
    except Exception as e:
        print(f"Error generating key moments: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/optimize/thumbnail', methods=['POST', 'OPTIONS'])
def optimize_thumbnail():
    if request.method == 'OPTIONS':
        return create_options_response()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        print("Received data for thumbnail optimization:", data)
        result = ai_service.optimize_thumbnail(data)
        print("Thumbnail optimization result:", result)
        return jsonify(result)
    except Exception as e:
        print(f"Error in thumbnail optimization route: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)