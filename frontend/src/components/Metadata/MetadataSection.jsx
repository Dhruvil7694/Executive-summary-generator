import React from 'react';

const MetadataSection = ({ metadata, darkMode }) => {
  return (
    <div className="mb-6">
      <h2
        className={`text-xl font-semibold mb-4 ${
          darkMode ? 'text-gray-300' : 'text-gray-700'
        }`}
      >
        Document Metadata
      </h2>
      <div
        className={`shadow-lg p-6 rounded-lg ${
          darkMode ? 'bg-gray-800' : 'bg-white'
        }`}
      >
        <ul
          className={`list-disc pl-6 space-y-1 ${
            darkMode ? 'text-gray-300' : 'text-gray-700'
          }`}
        >
          {metadata &&
            Object.entries(metadata).map(([key, value], index) => (
              <li key={`metadata-${index}`}>
                <strong>{key.replace(/_/g, ' ')}:</strong> {value || 'N/A'}
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
};

export default MetadataSection;