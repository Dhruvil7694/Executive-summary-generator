import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertTriangle, Info } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Recommendations = ({ recommendations }) => {
  const [expandedIndex, setExpandedIndex] = useState(null);

  if (!Array.isArray(recommendations)) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>Unable to load recommendations</AlertDescription>
      </Alert>
    );
  }

  const getImpactStyles = (impact) => {
    const baseStyles = "inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold";
    switch (impact) {
      case 'High':
        return `${baseStyles} bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200`;
      case 'Medium':
        return `${baseStyles} bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-200`;
      default:
        return `${baseStyles} bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200`;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
      <div className="p-6">
        {/* <h3 className="flex items-center gap-2 text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
          <Info className="h-5 w-5 text-blue-500" />
          Recommendations
        </h3> */}
        
        <div className="space-y-4">
          {recommendations.map((recommendation, index) => (
            <div
              key={index}
              className="group rounded-lg border border-gray-200 dark:border-gray-800 transition-all duration-200 hover:border-blue-500 dark:hover:border-blue-400"
            >
              <button
                onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                className="w-full p-4 flex items-start justify-between gap-4 text-left"
              >
                <div className="space-y-2 flex-1">
                  <p className="font-medium text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                    {recommendation.action}
                  </p>
                  <span className={getImpactStyles(recommendation.impact)}>
                    {recommendation.impact} Impact
                  </span>
                </div>
                {expandedIndex === index ? (
                  <ChevronUp className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-500" />
                )}
              </button>
              
              {expandedIndex === index && (
                <div className="px-4 pb-4 pt-2">
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {recommendation.rationale}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Recommendations;