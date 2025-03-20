import React from 'react';

const SummaryText = ({ summary, darkMode }) => {
  if (!summary?.text) return null;

  return (
    <div className={`mb-6 ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
      <p className="text-lg leading-relaxed text-justified ">{summary.text}</p>
    </div>
  );
};

export default SummaryText;
