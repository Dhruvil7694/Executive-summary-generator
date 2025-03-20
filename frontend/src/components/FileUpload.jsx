import React from 'react';
import Loader from './Loader.jsx'; // Correct import for FileUpload and Loader in the same folder

// In FileUpload.jsx, add disabled prop
const FileUpload = ({ handleFileChange, handleUpload, loading, darkMode, disabled }) => {
  return (
    <div className="space-y-4">
      <input
        type="file"
        onChange={handleFileChange}
        accept=".pdf"
        disabled={disabled || loading}
        className={`block w-full text-sm ${
          darkMode ? 'text-gray-300' : 'text-gray-900'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      />
      <button
        onClick={handleUpload}
        disabled={disabled || loading}
        className={`w-full px-4 py-2 rounded-lg ${
          darkMode
            ? 'bg-blue-600 hover:bg-blue-700'
            : 'bg-blue-500 hover:bg-blue-600'
        } text-white font-medium transition-colors ${
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        {loading ? 'Processing...' : 'Upload PDF'}
      </button>
    </div>
  );
};

export default FileUpload;


