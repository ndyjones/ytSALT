#!/usr/bin/env python3
"""
ytSALT Transcript Service Module
This module handles the extraction and processing of YouTube video transcripts.
It provides functionality to fetch and format transcript data, supporting both
automatic and manual captions when available.

Classes:
    TranscriptService: Handles transcript extraction and processing operations

Dependencies:
    - youtube_transcript_api
    - urllib.parse

Version: 1.0.0
Author: NC Jones @ndyjones
License: MIT
Created: February 2025
"""

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

class TranscriptService:
    def __init__(self):
        """Initialize TranscriptService"""
        pass

    def extract_video_id(self, url):
        """
        Extract video ID from YouTube URL.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            str: Video ID if found, None otherwise
        """
        try:
            parsed_url = urlparse(url)
            if parsed_url.hostname == 'youtu.be':
                return parsed_url.path[1:]
            if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
                if parsed_url.path == '/watch':
                    return parse_qs(parsed_url.query)['v'][0]
            return None
        except Exception as e:
            print(f"Error extracting video ID: {str(e)}")
            return None

    def get_transcript(self, url):
        """
        Retrieve transcript for a YouTube video.
        Returns both the full transcript and individual segments with timestamps.

        Args:
            url (str): YouTube video URL

        Returns:
            dict: Dictionary containing:
                - transcript: str (full concatenated transcript)
                - segments: List[dict] (individual transcript segments with timestamps)
                - stats: dict (transcript statistics)

        Raises:
            Exception: If transcript cannot be fetched or processed
        """
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")

            print(f"Fetching transcript for video ID: {video_id}")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine transcript pieces into a single text
            full_transcript = ' '.join(
                item['text'] for item in transcript_list
            )

            # Calculate transcript stats
            transcript_stats = {
                'length': len(full_transcript),
                'word_count': len(full_transcript.split()),
                'segment_count': len(transcript_list)
            }

            return {
                'transcript': full_transcript,
                'segments': transcript_list,
                'stats': transcript_stats
            }

        except TranscriptsDisabled:
            raise Exception("This video does not have subtitles or closed captions enabled.")
        except NoTranscriptFound:
            raise Exception("No transcript was found for this video.")
        except Exception as e:
            print(f"Error in get_transcript: {str(e)}")
            if "Subtitles are disabled" in str(e):
                raise Exception("This video does not have subtitles or closed captions enabled.")
            raise Exception(f"Could not fetch transcript: {str(e)}")

    def generate_timestamps(self, transcript_data):
        """
        Generate intelligent timestamps from transcript data
        """
        try:
            if not transcript_data or 'segments' not in transcript_data:
                raise ValueError("Invalid transcript data provided")

            segments = transcript_data.get('segments', [])
            if not segments:
                raise ValueError("No transcript segments available")

            timestamps = []
            current_segment_buffer = []
            current_start_time = 0
            min_segment_duration = 60  # Minimum 1 minute per segment
            
            for i, segment in enumerate(segments):
                current_segment_buffer.append(segment['text'])
                
                # Check for natural breaks or minimum duration
                if (i > 0 and (
                    segment['start'] - current_start_time >= min_segment_duration or 
                    self._is_topic_break(segment['text']) or 
                    i == len(segments) - 1  # Include last segment
                )):
                    # Create chapter from buffer
                    chapter_text = ' '.join(current_segment_buffer)
                    
                    # Format timestamp
                    minutes = int(current_start_time // 60)
                    seconds = int(current_start_time % 60)
                    timestamp_str = f"{minutes}:{seconds:02d}"
                    
                    timestamps.append({
                        'time': current_start_time,
                        'timestamp': timestamp_str,
                        'title': self._generate_topic_title(chapter_text[:200]),  # Limit text length
                        'text': chapter_text
                    })
                    
                    # Reset buffer
                    current_segment_buffer = []
                    current_start_time = segment['start']
            
            return timestamps

        except Exception as e:
            print(f"Error generating timestamps: {str(e)}")
            return []

    def _is_topic_break(self, text):
        """
        Enhanced detection of topic transitions
        """
        transition_phrases = [
            "moving on", "next", "now let's", "turning to",
            "another", "additionally", "furthermore", "however",
            "meanwhile", "in contrast", "on the other hand",
            "first", "second", "third", "finally", "lastly",
            "to begin", "in conclusion"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in transition_phrases)

    def _generate_topic_title(self, text):
        """
        Generate a concise topic title from segment text
        """
        try:
            # Remove common filler words
            filler_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
            words = [w for w in text.split() if w.lower() not in filler_words]
            
            # Take first 4-5 significant words
            title_words = words[:5]
            title = ' '.join(title_words)
            
            # Add ellipsis if truncated
            if len(words) > 5:
                title += "..."
                
            return title.capitalize()
        except Exception as e:
            print(f"Error generating topic title: {str(e)}")
            return "Untitled Section"