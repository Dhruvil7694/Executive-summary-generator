import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Search, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Findings = ({ findings }) => {
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  if (!Array.isArray(findings)) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Unable to load findings</AlertDescription>
      </Alert>
    );
  }

  const filteredFindings = findings.filter(finding =>
    finding.issue.toLowerCase().includes(searchTerm.toLowerCase()) ||
    finding.details.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getImpactStyles = (impact) => {
    const baseStyles = "inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold";
    switch (impact) {
      case 'High':
        return `${baseStyles} bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200`;
      case 'Medium':
        return `${baseStyles} bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-200`;
      case 'Low':
        return `${baseStyles} bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200`;
      case 'Very Low':
        return `${baseStyles} bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200`;
      default:
        return `${baseStyles} bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-200`;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-800">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          {/* <h3 className="flex items-center gap-2 text-xl font-semibold text-gray-900 dark:text-gray-100">
            <AlertCircle className="h-5 w-5 text-red-500" />
            Findings
          </h3> */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search findings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-64 rounded-md border border-gray-200 dark:border-gray-700 
                bg-gray-50 dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100
                focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            />
          </div>
        </div>
        
        <div className="space-y-4">
          {filteredFindings.map((finding, index) => (
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
                    {finding.issue}
                  </p>
                  <span className={getImpactStyles(finding.impact)}>
                    {finding.impact} Impact
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
                    {finding.details}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>

        {filteredFindings.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">No findings match your search</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Findings;