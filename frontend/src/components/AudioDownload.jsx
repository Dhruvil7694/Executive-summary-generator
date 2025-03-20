import React from 'react';

const AudioDownload = ({ audioPath, darkMode }) => {
  if (!audioPath) return null;

  return (
    <div className="mb-4">
      <a
        href={`http://localhost:5000${audioPath}`}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-block px-4 py-2 rounded-lg font-medium ${
          darkMode 
            ? 'bg-green-700 text-white hover:bg-green-600' 
            : 'bg-green-600 text-white hover:bg-green-700'
        }`}
      >
        Download Audio Summary
      </a>
    </div>
  );
};

export default AudioDownload;