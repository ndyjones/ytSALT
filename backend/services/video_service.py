#!/usr/bin/env python3
"""
ytsALT Video Service Module
This module handles the extraction of metadata from YouTube videos using yt-dlp.
It provides functionality to fetch comprehensive video information without requiring
the YouTube API, including title, description, tags, and engagement metrics.

Classes:
    VideoService: Handles video metadata extraction operations

Dependencies:
    - yt-dlp

Version: 1.0.0
Author: NC Jones @ndyjones
License: MIT
Created: February 2025
"""

import yt_dlp

class VideoService:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }

    def get_video_info(self, url):
        """
        Extracts metadata from a YouTube video URL

        Args:
            url (str): YouTube video URL

        Returns:
            dict: Dictionary containing video metadata including:
                - title: str
                - description: str
                - tags: List[str]
                - duration: int (in seconds)
                - view_count: int
                - like_count: int
                - channel: str
                - upload_date: str (YYYYMMDD format)
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get base data
                title = info.get('title', '')
                description = info.get('description', '')
                tags = info.get('tags', [])
                
                # Calculate stats
                title_stats = {
                    'length': len(title),
                    'word_count': len(title.split())
                }
                
                description_stats = {
                    'length': len(description),
                    'word_count': len(description.split())
                }
                
                tags_stats = {
                    'count': len(tags),
                    'total_length': sum(len(tag) for tag in tags)
                }
                
                # Get thumbnail URL (prefer high quality)
                thumbnails = info.get('thumbnails', [])
                thumbnail_url = thumbnails[-1]['url'] if thumbnails else None
                
                return {
                    'title': title,
                    'title_stats': title_stats,
                    'description': description,
                    'description_stats': description_stats,
                    'tags': tags,
                    'tags_stats': tags_stats,
                    'thumbnail_url': thumbnail_url,
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'channel': info.get('channel'),
                    'upload_date': info.get('upload_date')
                }
                
        except Exception as e:
            print(f"Error fetching video info: {str(e)}")  # Debug log
            raise Exception(f"Error fetching video info: {str(e)}")