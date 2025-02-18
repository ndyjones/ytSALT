import { useState } from 'react'
import axios from 'axios'
import { ClipboardIcon, CheckIcon } from 'lucide-react'
import OptimizationPanel from './components/OptimizationPanel'

export default function App() {
  const [url, setUrl] = useState('')
  const [videoData, setVideoData] = useState(null)
  const [transcriptData, setTranscriptData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [copiedFields, setCopiedFields] = useState({})

  const handleContentUpdate = (field, value) => {
    setVideoData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCopy = async (text, field) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedFields({ ...copiedFields, [field]: true })
      setTimeout(() => {
        setCopiedFields({ ...copiedFields, [field]: false })
      }, 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setVideoData(null)
    setTranscriptData(null)
    setCopiedFields({})
    try {
      // Fetch video info
      const videoResponse = await axios.post('http://localhost:5000/api/video-info', {
        url: url
      }, {
        headers: { 'Content-Type': 'application/json' }
      })
      console.log('Video data:', videoResponse.data);  // Debug log
      setVideoData(videoResponse.data)
      // Try to fetch transcript
      try {
        const transcriptResponse = await axios.post('http://localhost:5000/api/transcript', {
          url: url
        }, {
          headers: { 'Content-Type': 'application/json' }
        })
        setTranscriptData(transcriptResponse.data)
      } catch (err) {
        console.error('Transcript error:', err.response?.data?.error)
        setTranscriptData({
          error: err.response?.data?.error || 'Unable to fetch transcript'
        })
      }
    } catch (err) {
      console.error('Error details:', err)
      if (err.response) {
        setError(err.response.data?.error || 'Server error')
      } else if (err.request) {
        setError('No response from server. Please check if backend is running.')
      } else {
        setError(err.message || 'An error occurred')
      }
    } finally {
      setLoading(false)
    }
  }

  const CopyButton = ({ text, field }) => (
    <button
      onClick={() => handleCopy(text, field)}
      className="p-1 bg-indigo-600 hover:bg-indigo-800 rounded transition-colors"
      title="Copy to clipboard"
    >
      {copiedFields[field] ? (
        <CheckIcon className="h-4 w-4 text-white" />
      ) : (
        <ClipboardIcon className="h-4 w-4 text-white hover:text-gray-100" />
      )}
    </button>
  )

  return (
    <div className="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            ytSALT - YouTube Content Optimizer
          </h1>
          <form onSubmit={handleSubmit} className="mt-8 max-w-xl mx-auto">
            <div className="flex gap-4">
              <input
                type="text"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1 rounded border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-gray-900 bg-white placeholder-gray-500"
                placeholder="Enter YouTube URL"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
              >
                {loading ? 'Processing...' : 'Analyze Video'}
              </button>
            </div>
          </form>
          {error && (
            <div className="mt-4 text-red-600">
              {error}
            </div>
          )}
        </div>
        {videoData && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Video Metadata Panel */}
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-4 py-5 sm:px-6">
                  <h2 className="text-lg font-medium text-gray-900">Video Information</h2>
                </div>
                {videoData.thumbnail_url && (
                  <div className="px-4 py-3 border-t border-gray-200">
                    <img
                      src={videoData.thumbnail_url}
                      alt="Video thumbnail"
                      className="w-full rounded-lg shadow-sm"
                    />
                  </div>
                )}
                <div className="border-t border-gray-200">
                  <dl>
                    <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500 flex items-center justify-between">
                        Title
                        <CopyButton text={videoData.title} field="title" />
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <div>{videoData.title}</div>
                        <div className="mt-1 text-xs text-gray-500">
                          Characters: {videoData.title_stats?.length || 0} · Words: {videoData.title_stats?.word_count || 0}
                        </div>
                      </dd>
                    </div>
                    <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500 flex items-center justify-between">
                        Channel
                        <CopyButton text={videoData.channel} field="channel" />
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {videoData.channel}
                      </dd>
                    </div>
                    <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500 flex items-center justify-between">
                        Description
                        <CopyButton text={videoData.description} field="description" />
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <div className="whitespace-pre-wrap">{videoData.description}</div>
                        <div className="mt-2 text-xs text-gray-500">
                          Characters: {videoData.description_stats?.length || 0} · Words: {videoData.description_stats?.word_count || 0}
                        </div>
                      </dd>
                    </div>
                    <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500 flex items-center justify-between">
                        Tags
                        <CopyButton text={videoData.tags?.join(', ')} field="tags" />
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <div>{videoData.tags?.join(', ') || 'No tags'}</div>
                        {videoData.tags_stats && (
                          <div className="mt-1 text-xs text-gray-500">
                            {videoData.tags_stats.count} tags · {videoData.tags_stats.total_length} total characters
                          </div>
                        )}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
              {/* Transcript Panel */}
              {transcriptData && (
                <div className="bg-white shadow rounded-lg overflow-hidden">
                  <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                    <h2 className="text-lg font-medium text-gray-900">Video Transcript</h2>
                    {!transcriptData.error && (
                      <button
                        onClick={() => handleCopy(transcriptData.transcript, 'fullTranscript')}
                        className="flex items-center px-3 py-1 text-sm text-white bg-indigo-600 hover:bg-indigo-800 rounded transition-colors"
                      >
                        {copiedFields['fullTranscript'] ? (
                          <>
                            <CheckIcon className="h-4 w-4 mr-1" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <ClipboardIcon className="h-4 w-4 mr-1" />
                            Copy Full Text
                          </>
                        )}
                      </button>
                    )}
                  </div>
                  <div className="border-t border-gray-200">
                    <div className="px-4 py-5 sm:px-6">
                      {transcriptData.error ? (
                        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                          <div className="flex">
                            <div className="flex-shrink-0">
                              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                              </svg>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm text-yellow-700">{transcriptData.error}</p>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          <div className="text-sm text-gray-900">
                            <div className="flex justify-between items-center mb-2">
                              <h3 className="font-medium text-gray-900">Full Transcript</h3>
                              <div className="text-xs text-gray-500">
                                {transcriptData.stats?.length || 0} characters · {transcriptData.stats?.word_count || 0} words · {transcriptData.stats?.segment_count || 0} segments
                              </div>
                            </div>
                            <div className="whitespace-pre-wrap max-h-[600px] overflow-y-auto p-4 bg-gray-50 rounded">
                              {transcriptData.transcript}
                            </div>
                          </div>
                          {Array.isArray(transcriptData.segments) && (
                            <div className="text-sm text-gray-900">
                              <h3 className="font-medium text-gray-900 mb-2">Timestamped Segments</h3>
                              <div className="max-h-[600px] overflow-y-auto space-y-2">
                                {transcriptData.segments.map((segment, idx) => {
                                  const minutes = Math.floor(segment.start / 60);
                                  const seconds = Math.floor(segment.start % 60);
                                  const timestamp = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                                  return (
                                    <div key={idx} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                      <span className="font-medium text-indigo-600 mr-3">{timestamp}</span>
                                      <span className="text-gray-800">{segment.text}</span>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
            {/* Optimization Panel */}
            <div className="mt-6">
              <OptimizationPanel 
                videoData={videoData} 
                transcriptData={transcriptData}
                onUpdate={handleContentUpdate}
              />
            </div>
          </>
        )}
      </div>
    </div>
  )
}