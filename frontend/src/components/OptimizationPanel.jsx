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
        className="ml-4 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded
                   text-sm transition-colors duration-200"
      >
        Apply
      </button>
    </div>
  </div>
);

// Component for displaying description suggestions with formatting and metrics
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
        className="ml-4 bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded
                   text-sm transition-colors duration-200"
      >
        Apply
      </button>
    </div>
  </div>
);

// Component for displaying tag suggestions with source indicators and metrics
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
            suggestion.category.toLowerCase().includes('primary') ? 'bg-blue-100 text-blue-800' :
            suggestion.category.toLowerCase().includes('long-tail') ? 'bg-green-100 text-green-800' :
            suggestion.category.toLowerCase().includes('trending') ? 'bg-purple-100 text-purple-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {suggestion.category}
          </span>
          <span className={`text-xs px-2 py-1 rounded ${
            suggestion.source === 'transcript' ? 'bg-yellow-100 text-yellow-800' :
            suggestion.source === 'both' ? 'bg-green-100 text-green-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {suggestion.source}
          </span>
        </div>
        <p className="text-gray-600 text-sm mt-1">{suggestion.reasoning}</p>
        <div className="flex flex-wrap gap-2 mt-2">
          <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">
            {suggestion.metrics.length} characters
          </span>
          {suggestion.metrics.is_recommended_length && (
            <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
              Recommended Length
            </span>
          )}
        </div>
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

// Main optimization panel component
const OptimizationPanel = ({ videoData, transcriptData, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState(null);
  const [error, setError] = useState(null);
  const [tagSuggestions, setTagSuggestions] = useState(null);
  const [descriptionSuggestions, setDescriptionSuggestions] = useState(null);
  const [activeTab, setActiveTab] = useState('title');

  // Clear all suggestions and errors
  const clearSuggestions = () => {
    setSuggestions(null);
    setDescriptionSuggestions(null);
    setTagSuggestions(null);
    setError(null);
  };

  // Handle title optimization request
  const handleOptimizeTitle = async () => {
    setActiveTab('title');
    setLoading(true);
    setError(null);
    setDescriptionSuggestions(null);
    setTagSuggestions(null);
    try {
      const response = await axios.post('http://localhost:5000/api/optimize/title', videoData, {
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.data.success) {
        setSuggestions(response.data.suggestions);
      } else {
        setError(response.data.error || 'Failed to generate suggestions');
      }
    } catch (err) {
      console.error('Optimization error:', err);
      setError(
        err.response?.data?.error ||
        'Failed to generate suggestions. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Handle description optimization request
  const handleOptimizeDescription = async () => {
    setActiveTab('description');
    setLoading(true);
    setError(null);
    setSuggestions(null);
    setTagSuggestions(null);
    try {
      const response = await axios.post('http://localhost:5000/api/optimize/description', videoData, {
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.data.success) {
        setDescriptionSuggestions(response.data.suggestions);
      } else {
        setError(response.data.error || 'Failed to generate description suggestions');
      }
    } catch (err) {
      console.error('Description optimization error:', err);
      setError(
        err.response?.data?.error ||
        'Failed to generate description suggestions. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Handle tag optimization request
  const handleOptimizeTags = async () => {
    setActiveTab('tags');
    setLoading(true);
    setError(null);
    setSuggestions(null);
    setDescriptionSuggestions(null);
    try {
      // Format the transcript data properly
      const dataWithTranscript = {
        ...videoData,
        transcript_data: {
          full_text: transcriptData?.transcript || '',
          segments: transcriptData?.segments || [],
        }
      };

      console.log('Sending data for tag optimization:', dataWithTranscript); // Debug log

      const response = await axios.post(
        'http://localhost:5000/api/optimize/tags',
        dataWithTranscript,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.data.success) {
        setTagSuggestions(response.data.suggestions);
      } else {
        setError(response.data.error || 'Failed to generate tag suggestions');
      }
    } catch (err) {
      console.error('Tag optimization error:', err);
      setError(
        err.response?.data?.error ||
        'Failed to generate tag suggestions. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Check if transcript is available for tag optimization
  const isTranscriptAvailable = Boolean(transcriptData?.transcript);

  // Calculate current tags statistics
  const currentTagsStats = {
    count: videoData.tags?.length || 0,
    totalLength: videoData.tags?.join(',').length || 0
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">Content Optimization</h2>
        {(suggestions || descriptionSuggestions || tagSuggestions) && (
          <button
            onClick={clearSuggestions}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Clear Suggestions
          </button>
        )}
      </div>

      {/* Optimization Controls */}
      <div className="flex flex-wrap gap-4 mb-6">
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
            'Optimize Title'
          )}
        </button>
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
            'Optimize Description'
          )}
        </button>
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
              Optimizing...
            </>
          ) : (
            'Optimize Tags'
          )}
        </button>
      </div>

      {/* Transcript Warning */}
      {!isTranscriptAvailable && (
        <div className="mb-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700">
          <p className="text-sm">
            Transcript data is required for optimal tag suggestions. Please ensure the video has captions available.
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              ⚠️
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && <LoadingState />}

      {/* Title Suggestions Display */}
      {suggestions && !loading && (
        <div className="mt-4">
          <h3 className="font-semibold text-lg mb-4">Suggested Titles</h3>
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

      {/* Description Suggestions Display */}
      {descriptionSuggestions && !loading && (
        <div className="mt-4">
          <h3 className="font-semibold text-lg mb-4">Suggested Descriptions</h3>
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

      {/* Tag Suggestions Display */}
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
                  
                  // Check for tag limit
                  if (totalLength + tag.length > 500) {
                    setError('Cannot add tag: would exceed YouTube\'s 500 character limit');
                    return;
                  }

                  // Check for duplicates (case-insensitive)
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
    </div>
  );
};

export default OptimizationPanel;