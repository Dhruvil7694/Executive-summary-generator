import React, { useState } from 'react';
import GradingCriteriaDialog from './GradingCriteriaDialog';
import IssuesTable from './IssuesTable';

const ResultsSection = ({ sectionValue, darkMode }) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <div className="space-y-6">
      {/* Overall Result Table with Grading Criteria Button */}
      {sectionValue?.overall_result && sectionValue.overall_result.length > 0 && (
        <div className="relative">
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-lg font-semibold text-blue-900 dark:text-blue-100">Overall Assessment</h4>
            <button
              onClick={() => setIsDialogOpen(true)}
              className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 rounded-md hover:bg-blue-100 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800 transition-colors"
            >
              View Grading Criteria
            </button>
          </div>
          
          <div className="overflow-x-auto shadow-md border border-blue-200 dark:border-slate-700 rounded-lg">
            <table className="min-w-full divide-y divide-blue-200 dark:divide-slate-700">
              <thead className="bg-blue-50/70 dark:bg-slate-900/70 backdrop-blur-md">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                    Grade
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                    Security Level
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                    Scope
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-slate-900 divide-y divide-blue-200 dark:divide-slate-700">
                {sectionValue.overall_result.map((result, index) => (
                  <tr key={index} className="hover:bg-blue-100/50 dark:hover:bg-slate-700/50 transition duration-150">
                    <td className="px-6 py-4 text-sm">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                        {result.grade}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-blue-900 dark:text-blue-100">
                      {result.security_level}
                    </td>
                    <td className="px-6 py-4 text-sm text-blue-900 dark:text-blue-100">
                      {result.scope}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Issues Table */}
      <IssuesTable sectionValue={sectionValue} />

      {/* Vulnerabilities Table */}
      {sectionValue.Vulnerabilities && sectionValue.Vulnerabilities.length > 0 && (
        <div className="relative overflow-x-auto shadow-md border border-blue-200 dark:border-slate-700 rounded-lg">
          <table className="min-w-full divide-y divide-blue-200 dark:divide-slate-700">
            <thead className="bg-blue-50/70 dark:bg-slate-900/70 backdrop-blur-md sticky top-0 z-10">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                  Vulnerability
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-blue-700 dark:text-blue-200 uppercase tracking-wider">
                  Description
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-slate-900 divide-y divide-blue-200 dark:divide-slate-700">
              {sectionValue.Vulnerabilities.map((item, index) => (
                <tr
                  key={index}
                  className="hover:bg-blue-100/50 dark:hover:bg-slate-700/50 transition duration-150"
                >
                  <td className="px-6 py-4 text-sm text-blue-900 dark:text-blue-100">{item.vulnerability}</td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold tracking-wide ${
                        item.severity === 'Critical'
                          ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                          : item.severity === 'High'
                          ? 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
                          : item.severity === 'Medium'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                          : item.severity === 'Low'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-300'
                      }`}
                    >
                      {item.severity === 'Critical' && <span>🔴</span>}
                      {item.severity === 'High' && <span>🟠</span>}
                      {item.severity === 'Medium' && <span>🟡</span>}
                      {item.severity === 'Low' && <span>🟢</span>}
                      {item.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-blue-900 dark:text-blue-100">{item.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {/* Optional Scroll Indicators */}
          <div className="absolute inset-y-0 right-0 bg-gradient-to-l from-blue-50/80 dark:from-slate-900/80 w-6 pointer-events-none"></div>
          <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-50/80 dark:from-slate-900/80 w-6 pointer-events-none"></div>
        </div>
      )}

      {/* Grading Criteria Dialog */}
      <GradingCriteriaDialog 
        open={isDialogOpen} 
        onClose={() => setIsDialogOpen(false)} 
        darkMode={darkMode}
      />
    </div>
  );
};

export default ResultsSection;