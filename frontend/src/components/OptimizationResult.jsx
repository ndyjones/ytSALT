// frontend/src/components/OptimizationResult.jsx
import React from 'react';

const OptimizationResult = ({ suggestions, onApply, currentValue }) => {
  return (
    <div className="space-y-4">
      {suggestions.map((suggestion, index) => (
        <div 
          key={index}
          className="border rounded-lg p-4 hover:bg-gray-50 transition-colors duration-200"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h4 className="font-medium text-lg text-gray-900">{suggestion.title}</h4>
              <p className="text-gray-600 text-sm mt-1">{suggestion.reasoning}</p>
              
              <div className="flex gap-2 mt-2">
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
      ))}
    </div>
  );
};

export default OptimizationResult;