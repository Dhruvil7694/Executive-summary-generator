import React from 'react';

const ProgressBar = ({ progress, stage, message, status, darkMode }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'error':
        return 'bg-red-500';
      case 'complete':
        return 'bg-green-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="mb-6">
      <div className="flex justify-between mb-1">
        <span
          className={`text-sm font-medium ${
            darkMode ? 'text-gray-300' : 'text-gray-700'
          }`}
        >
          {stage.charAt(0).toUpperCase() + stage.slice(1)}
        </span>
        <span
          className={`text-sm font-medium ${
            darkMode ? 'text-gray-300' : 'text-gray-700'
          }`}
        >
          {Math.round(progress)}%
        </span>
      </div>
      <div
        className={`w-full h-2.5 rounded-full ${
          darkMode ? 'bg-gray-700' : 'bg-gray-200'
        }`}
      >
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${getStatusColor()}`}
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p
        className={`mt-2 text-sm ${
          darkMode ? 'text-gray-400' : 'text-gray-600'
        }`}
      >
        {message}
      </p>
    </div>
  );
};

export default ProgressBar;