import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Button } from "@/components/ui/button";
import { Info } from "lucide-react";
import SeverityInfoDialog from './SeverityInfoDialog';

const IssuesTable = ({ sectionValue , darkmode}) => {
  const [isDialogbox, setIsDialogbox] = useState(false);


  const totalIssues = sectionValue?.issues?.reduce((acc, curr) => acc + (curr.issues || 0), 0) || 0;

  // Calculate percentages for progress bars
  const getPercentage = (value) => ((value / totalIssues) * 100).toFixed(1);

  return (
    <>
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span>Security Issues Summary</span>
              <Button
                variant="ghost"
                size="sm"
                className="p-2 hover:bg-blue-100 dark:hover:bg-slate-800 rounded-full"
                onClick={() => setIsDialogbox(true)}
              >
                <Info className="w-5 h-5" />
              </Button>
            </div>
            <span className="text-sm font-normal">
              Total Issues: <span className="font-bold">{totalIssues}</span>
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Table Section */}
            <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Issues
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Distribution
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
                  {sectionValue?.issues?.map((item, index) => (

                    <tr
                      key={index}
                      className="hover:bg-blue-100/50 dark:hover:bg-slate-700/50 transition duration-150"
                    >
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold tracking-wide ${
                            item.Severity === 'Critical'
                              ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                              : item.Severity === 'High'
                              ? 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
                              : item.Severity === 'Medium'
                              ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                              : item.Severity === 'Low'
                              ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                              : 'bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-300'
                          }`}
                        >
                          {item.Severity === 'Critical' && <span>🔴</span>}
                          {item.Severity === 'High' && <span>🟠</span>}
                          {item.Severity === 'Medium' && <span>🟡</span>}
                          {item.Severity === 'Low' && <span>🟢</span>}
                          {item.Severity}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-blue-900 dark:text-blue-100">
                        {item.issues}
                      </td>
                      <td className="px-6 py-4 w-64">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                            <div
                              className={`h-full rounded-full ${
                                item.Severity === 'Critical'
                                  ? 'bg-red-500'
                                  : item.Severity === 'High'
                                  ? 'bg-orange-500'
                                  : item.Severity === 'Medium'
                                  ? 'bg-yellow-500'
                                  : item.Severity === 'Low'
                                  ? 'bg-green-500'
                                  : 'bg-gray-500'
                              }`}
                              style={{
                                width: `${item.issues ? getPercentage(item.issues) : 0}%`
                              }}
                            />
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400 w-12">
                            {item.issues ? getPercentage(item.issues) : 0}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Chart Section */}
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={sectionValue.issues}
                  margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
                >
                  <XAxis dataKey="Severity" />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="issues"
                    fill="#3b82f6"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </CardContent>
      </Card>

      <SeverityInfoDialog 
        open={isDialogbox} 
        onClose={() => setIsDialogbox(false)}
        darkMode={darkmode}
      />
    </>
  );
};

export default IssuesTable;