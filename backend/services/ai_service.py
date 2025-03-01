# backend/services/ai_service.py
from openai import OpenAI
from typing import Dict, List
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import base64
import requests
from PIL import Image  # for thumbnail processing
import io
from io import BytesIO

load_dotenv()

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def _determine_content_type(self, video_data: Dict) -> str:
        """
        Analyze video metadata to determine the content type
        """
        try:
            title = video_data.get('title', '').lower()
            description = video_data.get('description', '').lower()
            tags = [tag.lower() for tag in video_data.get('tags', [])]
            
            # Define content type indicators
            content_types = {
                'tutorial': ['how to', 'tutorial', 'guide', 'learn', 'step by step'],
                'review': ['review', 'hands on', 'unboxing', 'testing'],
                'vlog': ['vlog', 'day in', 'daily', 'life'],
                'entertainment': ['fun', 'funny', 'comedy', 'prank', 'challenge'],
                'gaming': ['gameplay', 'playthrough', 'gaming', 'game'],
                'educational': ['explained', 'understanding', 'education', 'learn'],
                'news': ['news', 'update', 'latest', 'breaking'],
                'commentary': ['reaction', 'thoughts on', 'discussing', 'opinion']
            }
            
            # Check content against indicators
            content_scores = {ctype: 0 for ctype in content_types}
            
            for ctype, indicators in content_types.items():
                # Check title
                if any(indicator in title for indicator in indicators):
                    content_scores[ctype] += 2
                
                # Check description
                if any(indicator in description for indicator in indicators):
                    content_scores[ctype] += 1
                    
                # Check tags
                if any(indicator in ' '.join(tags) for indicator in indicators):
                    content_scores[ctype] += 1
            
            # Get the content type with highest score
            max_score = max(content_scores.values())
            if max_score > 0:
                content_type = max(content_scores.items(), key=lambda x: x[1])[0]
            else:
                content_type = 'general'
                
            return content_type.capitalize()
            
        except Exception as e:
            print(f"Error determining content type: {str(e)}")
            return 'General'

    def optimize_title(self, video_data: Dict) -> Dict:
        """
        Generate optimized title suggestions based on video metadata
        Note: Removed async since OpenAI's Python client handles async internally
        """
        try:
            prompt = self._create_title_optimization_prompt(video_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are a YouTube SEO expert.
                    Analyze the provided video metadata and suggest 5 optimized titles
                    that will improve CTR while maintaining content accuracy."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            # Debug logging
            print("OpenAI Response received")
            print(f"Response content: {response.choices[0].message.content[:100]}...")

            suggestions = self._parse_title_suggestions(response.choices[0].message.content)
            
            return {
                "success": True,
                "suggestions": suggestions,
                "reasoning": response.choices[0].message.content
            }
        except Exception as e:
            print(f"Error in optimize_title: {str(e)}")  # Debug logging
            return {
                "success": False,
                "error": f"Failed to generate suggestions: {str(e)}"
            }

    def _create_title_optimization_prompt(self, video_data: Dict) -> str:
        """
        Creates a structured prompt for title optimization
        """
        return f"""
        Analyze the following video metadata and suggest 5 optimized titles:

        Current Title: {video_data.get('title', 'No title provided')}
        Description: {video_data.get('description', 'No description provided')}
        Tags: {', '.join(video_data.get('tags', []) or ['No tags provided'])}

        Please provide 5 optimized titles in the following format:
        1. [Suggested Title]
           [Explanation of why this title would perform better]
        2. [Suggested Title]
           [Explanation of why this title would perform better]

        Requirements for each title:
        - Must maintain the core message
        - Should improve CTR (Click-Through Rate)
        - Follow YouTube best practices
        - Include relevant keywords
        - Stay within 70 characters
        - Be engaging and searchable

        Provide each title with a clear explanation of its benefits.
        """

    def _parse_title_suggestions(self, response_text: str) -> List[Dict]:
        """
        Parse GPT's response text into structured title suggestions.
        Returns a list of dictionaries containing title and reasoning.
        """
        try:
            suggestions = []
            # Split the response into lines and clean them
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            current_title = None
            current_reasoning = []
            
            for line in lines:
                # Check if line starts with a number or bullet point
                if (line[0].isdigit() and '. ' in line) or line.startswith(('•', '-', '*')):
                    # If we have a previous title, save it before starting new one
                    if current_title is not None:
                        suggestions.append({
                            'title': current_title,
                            'reasoning': ' '.join(current_reasoning),
                            'metrics': self._analyze_title_metrics(current_title)
                        })
                    
                    # Extract new title
                    title_text = line.split('. ', 1)[-1] if '. ' in line else line[1:].strip()
                    current_title = title_text
                    current_reasoning = []
                
                # If not a new title, add to reasoning
                elif current_title is not None:
                    current_reasoning.append(line)
            
            # Add the last title if exists
            if current_title is not None:
                suggestions.append({
                    'title': current_title,
                    'reasoning': ' '.join(current_reasoning),
                    'metrics': self._analyze_title_metrics(current_title)
                })
            
            # If no suggestions were parsed, try alternate parsing method
            if not suggestions:
                suggestions = self._alternate_parse_method(response_text)
            
            return suggestions
        except Exception as e:
            print(f"Error parsing suggestions: {str(e)}")  # Debug logging
            return []

    def _analyze_title_metrics(self, title: str) -> Dict:
        """
        Analyze title metrics for additional insights
        """
        return {
            'length': len(title),
            'word_count': len(title.split()),
            'has_number': any(char.isdigit() for char in title),
            'character_limit_ok': len(title) <= 70,
            'recommended': len(title) >= 30 and len(title) <= 70
        }

    def _alternate_parse_method(self, response_text: str) -> List[Dict]:
        """
        Fallback parsing method for different response formats
        """
        try:
            # Split by common title indicators
            possible_titles = re.split(r'\n(?=Title |Suggestion |Option |\d+[\)\.] )', response_text)
            suggestions = []
            
            for title_block in possible_titles:
                if not title_block.strip():
                    continue
                    
                # Try to separate title from reasoning
                parts = title_block.split('\n', 1)
                if len(parts) >= 1:
                    title = parts[0]
                    # Clean the title of common prefixes
                    title = re.sub(r'^(Title |Suggestion |Option |\d+[\)\.] )', '', title).strip()
                    reasoning = parts[1].strip() if len(parts) > 1 else "No reasoning provided"
                    
                    suggestions.append({
                        'title': title,
                        'reasoning': reasoning,
                        'metrics': self._analyze_title_metrics(title)
                    })
            
            return suggestions
        except Exception as e:
            print(f"Error in alternate parse method: {str(e)}")  # Debug logging
            return []


    def _create_description_optimization_prompt(self, video_data: Dict) -> str:
        """
        Creates a structured prompt for description optimization
        """
        return f"""
        Analyze the following video metadata and create 3 optimized descriptions:

        Current Title: {video_data.get('title', 'No title provided')}
        Current Description: {video_data.get('description', 'No description provided')}
        Tags: {', '.join(video_data.get('tags', []) or ['No tags provided'])}

        For each suggestion, please use this exact format:
        1.
        Description: [Your suggested description here]
        Explanation: [Why this description would perform better]

        2.
        Description: [Your suggested description here]
        Explanation: [Why this description would perform better]

        3.
        Description: [Your suggested description here]
        Explanation: [Why this description would perform better]

        Requirements for each description:
        - Include relevant keywords naturally
        - Start with a compelling hook
        - Include clear call-to-actions (CTAs)
        - Use proper formatting and line breaks
        - Include relevant hashtags
        - Optimize for both viewer engagement and SEO
        - Maximum 5000 characters
        - Include timestamps for longer videos
        - Include relevant links and social media
        """

    def _analyze_description_metrics(self, description: str) -> Dict:
        """
        Analyze description metrics for additional insights
        """
        if not description:
            return {
                'word_count': 0,
                'line_count': 0,
                'has_hashtags': False,
                'has_links': False,
                'character_limit_ok': True
            }
            
        lines = description.split('\n')
        words = description.split()
        
        return {
            'word_count': len(words),
            'line_count': len(lines),
            'has_hashtags': '#' in description,
            'has_links': 'http' in description.lower() or 'www.' in description.lower(),
            'character_limit_ok': len(description) <= 5000,
            'length': len(description)
        }

    def optimize_description(self, video_data: Dict) -> Dict:
        """
        Generate optimized description suggestions based on video metadata
        """
        try:
            prompt = self._create_description_optimization_prompt(video_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are a YouTube SEO expert. 
                    Analyze the video metadata and suggest 3 optimized descriptions 
                    that will improve searchability and engagement while maintaining 
                    content accuracy."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return {
                "success": True,
                "suggestions": self._parse_description_suggestions(response.choices[0].message.content),
                "reasoning": response.choices[0].message.content
            }
        except Exception as e:
            print(f"Error in optimize_description: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate description suggestions: {str(e)}"
            }

    def _parse_description_suggestions(self, response_text: str) -> List[Dict]:
        """
        Parse GPT's response text into structured description suggestions.
        Returns a list of dictionaries containing description and reasoning.
        """
        try:
            suggestions = []
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            current_description = None
            current_reasoning = []
            
            for i, line in enumerate(lines):
                # Check if line starts with a number followed by a period
                if re.match(r'^\d+\.', line):
                    # If we have a previous description, save it
                    if current_description is not None:
                        suggestions.append({
                            'description': current_description,
                            'reasoning': ' '.join(current_reasoning),
                            'metrics': self._analyze_description_metrics(current_description)
                        })
                    
                    # Start new description
                    current_description = ''
                    current_reasoning = []
                    continue
                
                # If line starts with "Description:" or similar, it's the description
                if any(line.lower().startswith(prefix) for prefix in ['description:', 'suggested description:']):
                    current_description = line.split(':', 1)[1].strip()
                # If line starts with "Explanation:" or similar, it's the reasoning
                elif any(line.lower().startswith(prefix) for prefix in ['explanation:', 'reasoning:', 'why:']):
                    current_reasoning.append(line.split(':', 1)[1].strip())
                # If we have a current description but no reasoning prefix, add to description
                elif current_description is not None and not current_reasoning:
                    current_description += '\n' + line
                # If we have reasoning started, add to reasoning
                elif current_reasoning:
                    current_reasoning.append(line)
            
            # Add the last description if exists
            if current_description is not None:
                suggestions.append({
                    'description': current_description,
                    'reasoning': ' '.join(current_reasoning),
                    'metrics': self._analyze_description_metrics(current_description)
                })
            
            return suggestions
        except Exception as e:
            print(f"Error parsing description suggestions: {str(e)}")
            return []

    def _analyze_description_metrics(self, description: str) -> Dict:
        """
        Analyze description metrics for additional insights
        """
        lines = description.split('\n')
        words = description.split()
        
        return {
            'length': len(description),
            'word_count': len(words),
            'line_count': len(lines),
            'has_links': 'http' in description.lower(),
            'has_hashtags': '#' in description,
            'character_limit_ok': len(description) <= 5000
        }

    def optimize_tags(self, video_data: Dict) -> Dict:
        """
        Generate optimized tag suggestions based on video metadata and transcript
        """
        try:
            # Input validation
            if not isinstance(video_data, dict):
                raise ValueError("Invalid video data format")
            # Debug logging
            print(f"Received video data with keys: {video_data.keys()}")
            
            # Extract existing keywords from current tags and description
            existing_keywords = set()
            if video_data.get('tags'):
                existing_keywords.update([tag.lower() for tag in video_data['tags']])
            if video_data.get('description'):
                # Extract meaningful words from description (excluding common words)
                desc_words = set(word.lower() for word in video_data['description'].split()
                               if len(word) > 3 and word.isalnum())
                existing_keywords.update(desc_words)
            
            # Create prompt with transcript data
            prompt = self._create_tag_optimization_prompt(video_data, existing_keywords)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are a YouTube SEO expert.
                    Analyze the video metadata and transcript to suggest optimized tags.
                    Pay special attention to key topics and terms mentioned in the transcript
                    that aren't already covered in existing tags. Include:
                    - Primary keywords from video content
                    - Long-tail variations based on context
                    - Related terms from transcript
                    - Trending topics that relate to the content
                    Maximum 500 characters total for all tags combined."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            suggestions = self._parse_tag_suggestions(
                response.choices[0].message.content,
                existing_keywords
            )
            
            return {
                "success": True,
                "suggestions": suggestions,
                "reasoning": response.choices[0].message.content
            }
        except Exception as e:
            print(f"Error in optimize_tags: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate tag suggestions: {str(e)}"
            }

    def _create_tag_optimization_prompt(self, video_data: Dict, existing_keywords: set) -> str:
        """
        Creates a structured prompt for tag optimization including transcript analysis
        """
        # Safely extract transcript text
        transcript_text = ''
        if isinstance(video_data.get('transcript_data'), dict):
            transcript_text = video_data['transcript_data'].get('full_text', '')
        
        # Debug logging
        print(f"Creating prompt with transcript length: {len(transcript_text)}")
        
        return f"""
        Analyze this video's content and metadata to suggest optimized tags:
        
        Title: {video_data.get('title', 'No title provided')}
        Description: {video_data.get('description', 'No description provided')}
        Current Tags: {', '.join(video_data.get('tags', []) or ['No tags provided'])}
        
        Transcript Content:
        {transcript_text[:1500]}... [truncated]
        
        Existing Keywords: {', '.join(existing_keywords)}
        
        Please provide:
        1. A list of 15-20 optimized tags
        2. Categories for each tag (primary keyword, long-tail, related term, trending)
        3. Explanation of why each tag was chosen
        4. Indicate if the tag is newly discovered from transcript content
        
        Format each tag suggestion as:
        Tag: [tag]
        Category: [category]
        Source: [metadata/transcript/both]
        Reasoning: [brief explanation]
        
        Remember:
        - Prioritize terms found in the transcript that aren't in existing tags
        - Keep individual tags under 100 characters
        - Total tags combined should not exceed 500 characters
        - Include a mix of specific and broad terms
        - Consider search volume and competition
        - Maintain relevance to video content
        """

    def _parse_tag_suggestions(self, response_text: str, existing_keywords: set) -> List[Dict]:
        """
        Parse GPT's response text into structured tag suggestions
        """
        try:
            suggestions = []
            current_tag = {}
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            for line in lines:
                if line.lower().startswith('tag:'):
                    if current_tag:
                        suggestions.append(current_tag)
                    tag_text = line.split(':', 1)[1].strip()
                    current_tag = {
                        'tag': tag_text,
                        'is_new': tag_text.lower() not in existing_keywords
                    }
                elif line.lower().startswith('category:'):
                    current_tag['category'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('source:'):
                    current_tag['source'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('reasoning:'):
                    current_tag['reasoning'] = line.split(':', 1)[1].strip()
                    current_tag['metrics'] = self._analyze_tag_metrics(current_tag['tag'])
            
            if current_tag:
                # Make sure the last tag has metrics if it wasn't added
                if 'metrics' not in current_tag and 'tag' in current_tag:
                    current_tag['metrics'] = self._analyze_tag_metrics(current_tag['tag'])
                suggestions.append(current_tag)
            
            # Sort suggestions to prioritize new tags from transcript
            suggestions.sort(key=lambda x: (
                not x.get('is_new'),  # New tags first
                x.get('source') != 'transcript',  # Transcript sources second
                x.get('category') != 'primary keyword'  # Primary keywords third
            ))
            
            return suggestions
        except Exception as e:
            print(f"Error parsing tag suggestions: {str(e)}")
            return []

    def _analyze_tag_metrics(self, tag: str) -> Dict:
        """
        Analyze tag metrics for additional insights
        """
        return {
            'length': len(tag),
            'word_count': len(tag.split()),
            'has_numbers': any(char.isdigit() for char in tag),
            'is_recommended_length': 10 <= len(tag) <= 30
        }

    def optimize_thumbnail(self, video_data: Dict) -> Dict:
        """
        Generate thumbnail optimization suggestions based on video content type, metadata, and current thumbnail
        """
        try:
            # Debug print
            # print("Video data:", video_data)
            
            content_type = self._determine_content_type(video_data)
            title = video_data.get('title', '')
            thumbnail_url = video_data.get('thumbnail_url', '')

            if not thumbnail_url:
                raise ValueError("No thumbnail URL provided")

            # Download the image from the URL
            response = requests.get(thumbnail_url)
            if response.status_code != 200:
                raise ValueError(f"Failed to download thumbnail image: {response.status_code}")

            # Convert WebP to JPEG
            image = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary (in case of RGBA WebP)
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Save as JPEG in memory
            jpeg_buffer = io.BytesIO()
            image.save(jpeg_buffer, format='JPEG', quality=95)
            jpeg_buffer.seek(0)
            
            # Encode the JPEG image
            encoded_image = base64.b64encode(jpeg_buffer.getvalue()).decode('utf-8')

            prompt = f"""
            Analyze this YouTube video thumbnail and provide specific optimization recommendations.
            
            Video Context:
            Title: {title}
            Content Type: {content_type}
            Description: {video_data.get('description', '')}

            Please provide detailed recommendations for:

            1. Visual Analysis:
            - Current thumbnail strengths and weaknesses
            - Main focal points and their effectiveness
            - Image composition and layout
            - Visual hierarchy

            2. Improvement Recommendations:
            - Text overlay suggestions (placement, style, size)
            - Color scheme optimization
            - Composition adjustments
            - Attention-grabbing elements
            - CTR optimization tips

            3. Technical Specifications:
            - Resolution and quality assessment
            - Safe zone compliance
            - Mobile viewing optimization
            - Platform-specific considerations
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            parsed_recommendations = self._parse_thumbnail_recommendations(
                response.choices[0].message.content
            )

            return {
                "success": True,
                "thumbnail_recommendations": parsed_recommendations,
                "content_type": content_type,
                "current_thumbnail_url": thumbnail_url
            }
        except Exception as e:
            print(f"Error in thumbnail optimization: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }

    def _download_and_encode_image(self, image_url: str) -> str:
        """
        Download image from URL and return base64 encoded string
        """
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

    def _parse_thumbnail_recommendations(self, response_text: str) -> Dict:
        """
        Parse the thumbnail optimization response into structured recommendations
        """
        try:
            recommendations = {
                'current_analysis': [],
                'visual_elements': [],
                'text_overlay': [],
                'color_scheme': [],
                'composition': [],
                'technical_specs': [],
                'additional_recommendations': []
            }

            current_section = None
            lines = response_text.split('\n')
            
            section_mapping = {
                'current thumbnail analysis': 'current_analysis',
                'visual elements': 'visual_elements',
                'text overlay': 'text_overlay',
                'color scheme': 'color_scheme',
                'composition': 'composition',
                'technical specs': 'technical_specs',
                'additional recommendations': 'additional_recommendations'
            }

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for section headers
                lower_line = line.lower()
                for key, value in section_mapping.items():
                    if key in lower_line:
                        current_section = value
                        break

                # Add content to current section
                if current_section and (line[0] in ['-', '•', '*'] or line[0].isdigit()):
                    cleaned_line = re.sub(r'^[-•*\d]+\.?\s*', '', line).strip()
                    if cleaned_line:
                        recommendations[current_section].append(cleaned_line)

            # Format the output
            return {
                key: '\n• ' + '\n• '.join(value) if value else 'No specific recommendations'
                for key, value in recommendations.items()
            }
        except Exception as e:
            print(f"Error parsing thumbnail recommendations: {str(e)}")
            return {
                'error': f"Failed to parse recommendations: {str(e)}"
            }

    def _parse_key_moments(self, response_text: str) -> List[Dict]:
        """
        Parse the key moments response into structured data
        """
        try:
            moments = []
            current_moment = None
            lines = response_text.split('\n')
            timestamp = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for new moment indicators (numbered points)
                if re.match(r'^\d+[\.\)]', line):
                    # Save previous moment if exists
                    if current_moment:
                        moments.append(current_moment)
                        timestamp += 120  # Add 2 minutes for each section
                    
                    # Extract title (remove number and period/parenthesis)
                    title = re.sub(r'^\d+[\.\)]\s*', '', line)
                    
                    current_moment = {
                        'title': title,
                        'time': timestamp,
                        'type': 'topic_change',
                        'description': ''
                    }
                # Add description to current moment
                elif current_moment and not line.lower().startswith(('chapter', 'section', 'part')):
                    if current_moment['description']:
                        current_moment['description'] += ' ' + line
                    else:
                        current_moment['description'] = line
            
            # Add the last moment if exists
            if current_moment:
                moments.append(current_moment)
            
            return moments
        except Exception as e:
            print(f"Error parsing key moments: {str(e)}")
            return []

    def generate_thumbnail_optimization(self, video_data: Dict) -> Dict:
        """
        Generate comprehensive thumbnail optimization suggestions
        """
        try:
            prompt = f"""
            Based on this video content:
            Title: {video_data.get('title')}
            Description: {video_data.get('description')}
            
            Provide specific thumbnail recommendations including:
            1. Main visual elements to include
            2. Text overlay suggestions
            3. Color scheme recommendations
            4. Composition tips
            5. Emotional triggers to incorporate
            
            For each category, provide specific, actionable recommendations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a YouTube thumbnail optimization expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            parsed_elements = self._parse_thumbnail_elements(response.choices[0].message.content)
            
            return {
                "success": True,
                "thumbnail_suggestions": {
                    "suggestions": response.choices[0].message.content,
                    "elements": parsed_elements
                }
            }
        except Exception as e:
            print(f"Error generating thumbnail suggestions: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate thumbnail suggestions: {str(e)}"
            }

    def generate_key_moments(self, video_data: Dict) -> Dict:
        """
        Generate concise chapter markers from transcript with SEO optimization
        """
        try:
            transcript_text = video_data.get('transcript_data', {}).get('full_text', '')
            if not transcript_text:
                return {
                    "success": False,
                    "error": "No transcript data available for chapter generation"
                }

            prompt = f"""
            Generate SEO-optimized chapter titles for this video transcript.
            Format each chapter with its timestamp in this exact format:
            [timestamp] [brief chapter title]

            Critical Requirements:
            1. Timing Rules:
               - Must start with "0:00" for the first chapter
               - Minimum 10 seconds between chapters (YouTube requirement)
               - Space chapters logically throughout the video
               - Use proper timestamp format (M:SS or MM:SS)

            2. Title Format Rules:
               - Keep titles extremely concise (2-5 words)
               - Must be clear and descriptive
               - Use action words when possible
               - Make titles scannable
               - Capitalize key words

            3. SEO Optimization:
               - Use search-friendly keywords
               - Match user search intent
               - Include relevant topic terms
               - Maintain natural language flow
               - Consider common search phrases

            4. Structure Requirements:
               - Include introduction chapter
               - Break into clear content segments
               - Mark major transitions
               - Note key demonstrations or examples
               - Include conclusion/summary if applicable

            Example Format:
            0:00 Introduction
            0:45 Project Overview
            2:15 Main Demonstration
            5:30 Key Results
            8:45 Final Tips

            Current Video Context:
            Title: {video_data.get('title', '')}
            Description: {video_data.get('description', '')}

            Generate chapters based on this transcript:
            {transcript_text[:2000]}...
            """

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at creating YouTube chapters that maximize SEO and user engagement.
                        Focus on creating chapters that:
                        1. Help viewers navigate the content effectively
                        2. Improve search visibility
                        3. Maintain professional formatting
                        4. Use strategic keywords"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            chapters = self._parse_chapters(response.choices[0].message.content)
            
            # Validate chapter timing
            validated_chapters = self._validate_chapters(chapters)
            
            return {
                "success": True,
                "key_moments": validated_chapters
            }
        except Exception as e:
            print(f"Error generating chapters: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate chapters: {str(e)}"
            }

    def _validate_chapters(self, chapters: List[Dict]) -> List[Dict]:
        """
        Validate chapters meet YouTube requirements
        """
        validated_chapters = []
        previous_time = -10  # Initialize to ensure first chapter can be 0:00
        
        for chapter in chapters:
            current_time = chapter['time']
            
            # Ensure minimum 10-second gap between chapters
            if (current_time - previous_time) >= 10:
                validated_chapters.append(chapter)
                previous_time = current_time
            else:
                print(f"Skipping chapter at {chapter['timestamp']} due to insufficient time gap")
        
        # Ensure first chapter starts at 0:00
        if validated_chapters and validated_chapters[0]['time'] != 0:
            print("Adding 0:00 Introduction chapter")
            validated_chapters.insert(0, {
                'time': 0,
                'timestamp': '0:00',
                'title': 'Introduction',
                'type': 'chapter'
            })
        
        return validated_chapters

    def _parse_chapters(self, response_text: str) -> List[Dict]:
        """
        Parse chapter markers from response with enhanced validation
        """
        chapters = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for timestamp pattern (M:SS or MM:SS)
            match = re.match(r'(\d{1,2}:\d{2})\s+(.*)', line)
            if match:
                timestamp, title = match.groups()
                
                # Convert timestamp to seconds for sorting
                minutes, seconds = map(int, timestamp.split(':'))
                time_in_seconds = minutes * 60 + seconds
                
                # Basic title validation
                title = title.strip()
                words = title.split()
                if len(words) > 4:  # If title too long, truncate to 4 words
                    title = ' '.join(words[:4])
                
                # Capitalize key words
                title = ' '.join(word.capitalize() if len(word) > 3 else word 
                               for word in title.split())
                
                chapters.append({
                    'time': time_in_seconds,
                    'timestamp': timestamp,
                    'title': title,
                    'type': 'chapter'
                })
        
        # Sort chapters by time
        chapters.sort(key=lambda x: x['time'])
        
        return chapters