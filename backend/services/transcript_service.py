#!/usr/bin/env python3
"""
ytsALT Transcript Service Module
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