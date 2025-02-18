// frontend/src/components/OptimizationPanel.jsx
import React, { useState } from 'react';
import axios from 'axios';

// Loading state component for optimization processes
const LoadingState = () => (
  <div className="animate-pulse space-y-4 mt-4">
    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    <div className="space-y-3">
      <div className="h-3 bg-gray-200 rounded"></div>
      <div className="h-3 bg-gray-200 rounded w-5/6"></div>
      <div className="h-3 bg-gray-200 rounded w-4/6"></div>
    </div>
  </div>
);

// Component for displaying title suggestions with metrics
const SuggestionCard = ({ suggestion, onApply }) => (
  <div className="p-4 border rounded-lg hover:bg-gray-50 transition-all duration-200">
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <h4 className="font-medium text-lg text-gray-900">{suggestion.title}</h4>
        <p className="text-gray-600 text-sm mt-1">{suggestion.reasoning}</p>
        {suggestion.metrics && (
          <div className="flex flex-wrap gap-2 mt-2">
            {suggestion.metrics.recommended && (
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                Recommended Length
              </span>
            )}
            <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
              {suggestion.metrics.length} characters
            </span>
            <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
              {suggestion.metrics.word_count} words
            </span>
          </div>
        )}
      </div>
      <button
        onClick={() => onApply(suggestion.title)}
        className="ml-4 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
      >
        Apply
      </button>
    </div>
  </div>
);

// Component for displaying description suggestions
const DescriptionSuggestionCard = ({ suggestion, onApply }) => (
  <div className="p-4 border rounded-lg hover:bg-gray-50 transition-all duration-200">
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <pre className="whitespace-pre-wrap text-sm text-gray-900 font-normal">
          {suggestion.description}
        </pre>
        <p className="text-gray-600 text-sm mt-3">{suggestion.reasoning}</p>
        {suggestion.metrics && (
          <div className="flex flex-wrap gap-2 mt-2">
            <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
              {suggestion.metrics.word_count} words
            </span>
            <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
              {suggestion.metrics.line_count} lines
            </span>
            {suggestion.metrics.has_hashtags && (
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                Has Hashtags
              </span>
            )}
            {suggestion.metrics.has_links && (
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                Has Links
              </span>
            )}
          </div>
        )}
      </div>
      <button
        onClick={() => onApply(suggestion.description)}
        className="ml-4 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
      >
        Apply
      </button>
    </div>
  </div>
);

// Component for displaying tag suggestions
const TagSuggestionCard = ({ suggestion, onApply }) => (
  <div className={`p-4 border rounded-lg transition-all duration-200 ${
    suggestion.is_new ? 'bg-gradient-to-r from-blue-50 to-white' : 'hover:bg-gray-50'
  }`}>
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <h4 className="font-medium text-gray-900">{suggestion.tag}</h4>
          {suggestion.is_new && (
            <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
              New from Content
            </span>
          )}
          <span className={`text-xs px-2 py-1 rounded ${
            suggestion.category?.toLowerCase().includes('primary') ? 'bg-blue-100 text-blue-800' :
            suggestion.category?.toLowerCase().includes('long-tail') ? 'bg-green-100 text-green-800' :
            suggestion.category?.toLowerCase().includes('trending') ? 'bg-purple-100 text-purple-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {suggestion.category || 'General'}
          </span>
          <span className={`text-xs px-2 py-1 rounded ${
            suggestion.source === 'transcript' ? 'bg-yellow-100 text-yellow-800' :
            suggestion.source === 'both' ? 'bg-green-100 text-green-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {suggestion.source || 'metadata'}
          </span>
        </div>
        <p className="text-gray-600 text-sm mt-1">{suggestion.reasoning}</p>
        {suggestion.metrics && (
          <div className="flex flex-wrap gap-2 mt-2">
            <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
              {suggestion.metrics.length || 0} characters
            </span>
            {suggestion.metrics.is_recommended_length && (
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                Recommended Length
              </span>
            )}
          </div>
        )}
      </div>
      <button
        onClick={() => onApply(suggestion.tag)}
        className={`ml-4 px-3 py-1 rounded text-sm transition-colors duration-200 ${
          suggestion.is_new
            ? 'bg-blue-600 hover:bg-blue-700 text-white'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}
      >
        Add Tag
      </button>
    </div>
  </div>
);

// Thumbnail recommendation component
const ThumbnailSuggestionCard = ({ suggestion }) => (
    <div className="bg-white rounded-lg divide-y divide-gray-200">
        {suggestion.current_thumbnail_url && (
            <div className="p-4">
                <h4 className="font-medium text-lg text-gray-900 mb-2">Current Thumbnail</h4>
                <img 
                    src={suggestion.current_thumbnail_url} 
                    alt="Current thumbnail"
                    className="w-full max-w-md mx-auto rounded-lg shadow-md mb-4"
                />
            </div>
        )}
        <div className="p-4">
            <div className="flex justify-between items-center mb-4">
                <h4 className="font-medium text-lg text-gray-900">Thumbnail Design Guide</h4>
                {suggestion.content_type && (
                    <span className="text-sm px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
                        {suggestion.content_type} Content
                    </span>
                )}
            </div>
            {/* Current Analysis section */}
            {suggestion.current_analysis && (
                <div className="mt-4">
                    <h5 className="font-medium text-gray-800 mb-2">Current Thumbnail Analysis</h5>
                    <ul className="space-y-2 text-gray-600">
                        {suggestion.current_analysis.split('\n').map((rec, index) => (
                            rec.trim() && (
                                <li key={index} className="flex items-start">
                                    <span className="text-indigo-500 mr-2">•</span>
                                    <span>{rec.trim()}</span>
                                </li>
                            )
                        ))}
                    </ul>
                </div>
            )}
            {/* Existing recommendations sections */}
            {Object.entries(suggestion).map(([category, recommendations]) => (
                category !== 'current_thumbnail_url' && category !== 'content_type' && (
                    <div key={category} className="mt-4">
                        <h5 className="font-medium text-gray-800 mb-2">
                            {category.split('_').map(word =>
                                word.charAt(0).toUpperCase() + word.slice(1)
                            ).join(' ')}
                        </h5>
                        <ul className="space-y-2 text-gray-600">
                            {recommendations.split('\n').map((rec, index) => (
                                rec.trim() && (
                                    <li key={index} className="flex items-start">
                                        <span className="text-indigo-500 mr-2">•</span>
                                        <span>{rec.trim()}</span>
                                    </li>
                                )
                            ))}
                        </ul>
                    </div>
                )
            ))}
        </div>
    </div>
);

const KeyMomentCard = ({ moment, onApply }) => (
    <div className="p-4 border rounded-lg hover:bg-gray-50 transition-all duration-200">
        <div className="flex justify-between items-start">
            <div className="flex-1">
                <div className="flex items-center gap-2">
                    <span className="text-gray-600">{moment.timestamp}</span>
                    <h4 className="font-medium text-gray-900">{moment.title}</h4>
                </div>
            </div>
            <button
                onClick={() => onApply(moment)}
                className="ml-4 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
            >
                Add Chapter
            </button>
        </div>
    </div>
);

const OptimizationPanel = ({ videoData, transcriptData, onUpdate }) => {
  // State management
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('title');

  // Basic optimization states
  const [suggestions, setSuggestions] = useState(null);
  const [descriptionSuggestions, setDescriptionSuggestions] = useState(null);
  const [tagSuggestions, setTagSuggestions] = useState(null);
  const [thumbnailSuggestions, setThumbnailSuggestions] = useState(null);
  const [keyMoments, setKeyMoments] = useState(null);

  // Clear all suggestions and errors
  const clearSuggestions = () => {
    setSuggestions(null);
    setDescriptionSuggestions(null);
    setTagSuggestions(null);
    setThumbnailSuggestions(null);
    setKeyMoments(null);
    setError(null);
  };

  // Basic optimization handlers
  const handleOptimizeTitle = async () => {
    setActiveTab('title');
    setLoading(true);
    setError(null);
    clearSuggestions();
    try {
      const response = await axios.post('http://localhost:5000/api/optimize/title', videoData);
      if (response.data.success) {
        setSuggestions(response.data.suggestions);
      } else {
        setError(response.data.error || 'Failed to generate suggestions');
      }
    } catch (err) {
      console.error('Title optimization error:', err);
      setError(err.response?.data?.error || 'Failed to generate suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeDescription = async () => {
    setActiveTab('description');
    setLoading(true);
    setError(null);
    clearSuggestions();
    try {
      const response = await axios.post('http://localhost:5000/api/optimize/description', videoData);
      if (response.data.success) {
        setDescriptionSuggestions(response.data.suggestions);
      } else {
        setError(response.data.error || 'Failed to generate description suggestions');
      }
    } catch (err) {
      console.error('Description optimization error:', err);
      setError(err.response?.data?.error || 'Failed to generate description suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeTags = async () => {
    setActiveTab('tags');
    setLoading(true);
    setError(null);
    clearSuggestions();
    try {
      const dataWithTranscript = {
        ...videoData,
        transcript_data: {
          full_text: transcriptData?.transcript || '',
          segments: transcriptData?.segments || [],
        }
      };
      const response = await axios.post(
        'http://localhost:5000/api/optimize/tags',
        dataWithTranscript
      );
      if (response.data.success) {
        setTagSuggestions(response.data.suggestions);
      } else {
        setError(response.data.error || 'Failed to generate tag suggestions');
      }
    } catch (err) {
      console.error('Tag optimization error:', err);
      setError(err.response?.data?.error || 'Failed to generate tag suggestions');
    } finally {
      setLoading(false);
    }
  };

  // Thumbnail optimization handler
  const handleThumbnailOptimization = async () => {
      setActiveTab('thumbnail');
      setLoading(true);
      setError(null);
      clearSuggestions();
      try {
          if (!videoData.thumbnail_url) {
              throw new Error("No thumbnail URL available");
          }

          console.log("Processing thumbnail URL:", videoData.thumbnail_url);
          
          const response = await axios.post(
              'http://localhost:5000/api/optimize/thumbnail',
              {
                  ...videoData,
                  title: videoData.title || '',
                  description: videoData.description || '',
                  tags: videoData.tags || [],
                  thumbnail_url: videoData.thumbnail_url
              },
              {
                  headers: {
                      'Content-Type': 'application/json'
                  },
                  withCredentials: true
              }
          );
          
          console.log("Received response:", response.data);
          
          if (response.data.success) {
              setThumbnailSuggestions({
                  ...response.data.thumbnail_recommendations,
                  current_thumbnail_url: response.data.current_thumbnail_url
              });
          } else {
              throw new Error(response.data.error || 'Failed to generate thumbnail suggestions');
          }
      } catch (err) {
          console.error('Thumbnail optimization error:', err);
          setError(
              err.response?.data?.error || 
              err.message || 
              'Failed to generate thumbnail suggestions'
          );
      } finally {
          setLoading(false);
      }
  };

  // Key moment chapters optimization handler
const handleKeyMoments = async () => {
    setActiveTab('key-moments');
    setLoading(true);
    setError(null);
    clearSuggestions();
    try {
        if (!transcriptData?.transcript && !transcriptData?.full_text) {
            throw new Error("Transcript data is required for generating chapters");
        }
        
        const response = await axios.post(
            'http://localhost:5000/api/optimize/key-moments',
            {
                ...videoData,
                transcript_data: {
                    full_text: transcriptData.transcript || transcriptData.full_text,
                    segments: transcriptData.segments || []
                }
            }
        );
        
        if (response.data.success) {
            setKeyMoments(response.data.key_moments);
        } else {
            throw new Error(response.data.error || 'Failed to generate chapters');
        }
    } catch (err) {
        console.error('Key moments error:', err);
        setError(err.message || 'Failed to generate chapters. Please try again.');
    } finally {
        setLoading(false);
    }
};

//Add Chapters to description
const addChapterToDescription = (chapter) => {
    const currentDescription = videoData.description || '';
    const chapterLine = `${chapter.timestamp} ${chapter.title}`;
    
    // Check if description already has chapters
    const hasChapters = currentDescription.includes('0:00');
    
    let newDescription;
    if (hasChapters) {
        // Find the chapters section and add the new chapter
        const lines = currentDescription.split('\n');
        const chapterLines = lines.filter(line => /^\d{1,2}:\d{2}/.test(line));
        const nonChapterLines = lines.filter(line => !/^\d{1,2}:\d{2}/.test(line));
        
        // Add new chapter and sort all chapters
        chapterLines.push(chapterLine);
        const sortedChapters = chapterLines
            .map(line => {
                const [timestamp, ...titleParts] = line.split(' ');
                const [min, sec] = timestamp.split(':').map(Number);
                return {
                    time: min * 60 + sec,
                    line: line
                };
            })
            .sort((a, b) => a.time - b.time)
            .map(item => item.line);
        
        // Reconstruct description with sorted chapters at the top
        newDescription = [...sortedChapters, '', ...nonChapterLines].join('\n');
    } else {
        // Add chapters section at the top of the description
        newDescription = `${chapterLine}\n\n${currentDescription}`;
    }
    
    onUpdate('description', newDescription);
};

  const isTranscriptAvailable = Boolean(transcriptData?.transcript);
  const currentTagsStats = {
    count: videoData.tags?.length || 0,
    totalLength: videoData.tags?.join(',').length || 0
  };

  // Render component
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      {/* Header with Clear button */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl text-gray-700 font-bold">Content Optimization</h2>
        {(suggestions || descriptionSuggestions || tagSuggestions || thumbnailSuggestions || keyMoments) && (
          <button
            onClick={clearSuggestions}
            className="text-sm text-white bg-indigo-600 hover:bg-indigo-800 rounded transition-colors"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Optimization Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Title Optimization Group */}
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-medium text-gray-700">Title</h3>
          <button
            onClick={handleOptimizeTitle}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded
                       hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed
                       transition-colors duration-200"
          >
            {loading && activeTab === 'title' ? (
              <>
                <span className="animate-spin">⏳</span>
                Optimizing...
              </>
            ) : (
              'Generate Title Ideas'
            )}
          </button>
        </div>

        {/* Description Optimization Group */}
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-medium text-gray-700">Description</h3>
          <button
            onClick={handleOptimizeDescription}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded
                       hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed
                       transition-colors duration-200"
          >
            {loading && activeTab === 'description' ? (
              <>
                <span className="animate-spin">⏳</span>
                Optimizing...
              </>
            ) : (
              'Generate Description'
            )}
          </button>
          <button
              onClick={handleKeyMoments}
              disabled={loading || !isTranscriptAvailable}
              className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded
                       hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed
                       transition-colors duration-200"
              title={!isTranscriptAvailable ? "Transcript required for chapters" : ""}
            >
              {loading && activeTab === 'key-moments' ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Analyzing...
                </>
              ) : (
                'Generate Chapters'
              )}
            </button>
        </div>

        {/* Tags Optimization Group */}
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-medium text-gray-700">Tags</h3>
          <div className="flex flex-col gap-2">
            <button
              onClick={handleOptimizeTags}
              disabled={loading || !isTranscriptAvailable}
              className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded
                         hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed
                         transition-colors duration-200"
              title={!isTranscriptAvailable ? "Transcript required for tag optimization" : ""}
            >
              {loading && activeTab === 'tags' ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Generating...
                </>
              ) : (
                'Basic Tags'
              )}
            </button>
          </div>
        </div>

        {/* Additional Features Group */}
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-medium text-gray-700">Additional Features</h3>
          <div className="flex flex-col gap-2">
            <button
              onClick={handleThumbnailOptimization}
              disabled={loading}
              className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded
                       hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed
                       transition-colors duration-200"
            >
              {loading && activeTab === 'thumbnail' ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Analyzing...
                </>
              ) : (
                'Thumbnail Ideas'
              )}
            </button>
            
          </div>
        </div>
      </div>

      {/* Transcript Warning */}
      {!isTranscriptAvailable && (
        <div className="mb-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700">
          <p className="text-sm">
            Transcript data is required for enhanced optimizations. Please ensure the video has captions available.
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">⚠️</div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && <LoadingState />}

      {/* Results Display */}
      {/* Basic Optimization Results */}
      {suggestions && !loading && (
        <div className="mt-4">
          <h3 className="font-semibold text-gray-700 text-lg mb-4">Suggested Titles</h3>
          <div className="space-y-4">
            {suggestions.map((suggestion, index) => (
              <SuggestionCard
                key={index}
                suggestion={suggestion}
                onApply={(title) => onUpdate('title', title)}
              />
            ))}
          </div>
        </div>
      )}

      {descriptionSuggestions && !loading && (
        <div className="mt-4">
          <h3 className="font-semibold text-gray-700 text-lg mb-4">Suggested Descriptions</h3>
          <div className="space-y-4">
            {descriptionSuggestions.map((suggestion, index) => (
              <DescriptionSuggestionCard
                key={index}
                suggestion={suggestion}
                onApply={(description) => onUpdate('description', description)}
              />
            ))}
          </div>
        </div>
      )}

      {tagSuggestions && !loading && (
        <div className="mt-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-lg">Suggested Tags</h3>
            <span className="text-sm text-gray-600">
              Current Tags: {currentTagsStats.count}
              (Total: {currentTagsStats.totalLength}/500 characters)
            </span>
          </div>
          <div className="space-y-4">
            {tagSuggestions.map((suggestion, index) => (
              <TagSuggestionCard
                key={index}
                suggestion={suggestion}
                onApply={(tag) => {
                  const existingTags = videoData.tags || [];
                  const totalLength = existingTags.join(',').length;
                  if (totalLength + tag.length > 500) {
                    setError('Cannot add tag: would exceed YouTube\'s 500 character limit');
                    return;
                  }
                  if (!existingTags.some(t => t.toLowerCase() === tag.toLowerCase())) {
                    const newTags = [...existingTags, tag];
                    onUpdate('tags', newTags);
                  }
                }}
              />
            ))}
          </div>
        </div>
      )}


      {thumbnailSuggestions && !loading && (
        <div className="mt-4">
          <h3 className="font-semibold text-gray-700 text-lg mb-4">Thumbnail Optimization</h3>
          <ThumbnailSuggestionCard suggestion={thumbnailSuggestions} />
        </div>
      )}

      {keyMoments && !loading && (
        <div className="mt-4">
            <h3 className="font-semibold text-lg mb-4">Chapter Suggestions</h3>
            <div className="space-y-4">
                {keyMoments.map((moment, index) => (
                    <KeyMomentCard
                        key={index}
                        moment={moment}
                        onApply={(moment) => addChapterToDescription(moment)}
                    />
                ))}
            </div>
        </div>
    )}
    </div>
  );
};

export default OptimizationPanel;