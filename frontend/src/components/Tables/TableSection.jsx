import React from 'react';

const TableSection = ({ tables, darkMode }) => {
  // Check if tables is defined and has length
  if (!tables || !Array.isArray(tables) || tables.length === 0) {
    return (
      <div className="mb-6">
        <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
          Extracted Tables
        </h2>
        <p className={`text-gray-500 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
          No tables found.
        </p>
      </div>
    );
  }

  return (
    <div className="mb-6">
      <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
        Extracted Tables ({tables.length})
      </h2>
      {tables.map((table, index) => (
        <div key={`table-${index}`} className="mb-4">
          <div
            className={`overflow-x-auto border rounded-lg ${
              darkMode ? 'border-gray-700' : 'border-gray-200'
            }`}
          >
            <table className="w-full text-sm">
              <thead
                className={`border-b ${
                  darkMode ? 'bg-gray-800 border-gray-700' : 'bg-gray-100 border-gray-200'
                }`}
              >
                <tr>
                  {table.data && table.data.length > 0 && Object.keys(table.data[0]).map((header, headerIndex) => (
                    <th
                      key={`header-${headerIndex}`}
                      className={`p-2 text-left ${
                        darkMode ? 'text-gray-300' : 'text-gray-700'
                      }`}
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className={darkMode ? 'bg-gray-900' : 'bg-white'}>
                {table.data && table.data.map((row, rowIndex) => (
                  <tr
                    key={`row-${rowIndex}`}
                    className={`border-b ${
                      darkMode ? 'border-gray-700' : 'border-gray-200'
                    }`}
                  >
                    {Object.values(row).map((cell, cellIndex) => (
                      <td
                        key={`cell-${rowIndex}-${cellIndex}`} // Ensure unique keys
                        className={`p-2 ${
                          darkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div
            className={`text-xs mt-1 ${
              darkMode ? 'text-gray-400' : 'text-gray-500'
            }`}
          >
            Page {table.pagenumber}, Table {index + 1}
          </div>
        </div>
      ))}
    </div>
  );
};

export default TableSection;