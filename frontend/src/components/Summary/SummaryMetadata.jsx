import React from 'react';

const SummaryMetadata = ({ summary, darkMode }) => {
  if (!summary) return null;

  const metrics = [
    {
      label: 'Word Count',
      value: summary.word_count || 0
    },
    {
      label: 'Reading Time',
      value: `${Math.ceil(summary.reading_time_minutes || 0)} min`
    },
    {
      label: 'Quality Score',
      value: `${((summary.quality_metrics?.semantic_similarity || 0) * 100).toFixed(1)}%`
    }
  ];

  return (
    <div className="border-t pt-4 mt-4">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {metrics.map((metric, index) => (
          <div key={index} className="text-center">
            <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              {metric.label}
            </p>
            <p className={`text-lg font-semibold ${
              darkMode ? 'text-gray-200' : 'text-gray-800'
            }`}>
              {metric.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SummaryMetadata;