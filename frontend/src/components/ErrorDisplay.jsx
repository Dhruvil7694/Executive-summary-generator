import React from 'react';

const ErrorDisplay = ({ error, darkMode }) => {
  if (!error) return null;
  
  return (
    <div className={`mt-4 p-4 rounded-lg text-sm ${
      darkMode ? 'bg-red-900 text-red-300' : 'bg-red-100 text-red-700'
    }`}>
      {error}
    </div>
  );
};

export default ErrorDisplay;
