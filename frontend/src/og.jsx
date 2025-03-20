import { useState } from 'react';
import axios from 'axios';
import jsPDF from "jspdf";

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPasswordInfo, setShowPasswordInfo] = useState(false); // State for the popup

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setData(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordInfo = () => setShowPasswordInfo(!showPasswordInfo);

  const handleDownload = (format) => {
    if (format === "txt") {
      const element = document.createElement("a");
      const file = new Blob([data.summary], { type: "text/plain" });
      element.href = URL.createObjectURL(file);
      element.download = "summary.txt";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } else if (format === "pdf") {
      const doc = new jsPDF();
      const lines = doc.splitTextToSize(data.summary, 180); // Wrap text for the page width
      doc.text(lines, 10, 10);
      doc.save("summary.pdf");
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-blue-100 p-6 ">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8 items-center">
        <h1 className="text-3xl font-bold text-blue-700 mb-6 text-center">PDF Analyzer</h1>

        {/* File Upload Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Upload your PDF</label>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0 file:text-sm file:font-medium hover:cursor-pointer
              file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={loading}
          className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-blue-700  disabled:bg-gray-400"
        >
          {loading ? 'Processing...' : 'Upload & Analyze'}
        </button>

        {/* Button to Show Password Info */}
        <div className="mt-6 text-center">
          <button
            onClick={togglePasswordInfo}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-300"
          >
            Need Help with Password?
          </button>
        </div>

        {/* Popup Component */}
        {showPasswordInfo && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 w-96">
              <h2 className="text-lg font-bold text-gray-700 mb-4">Password Information</h2>
              <p className="text-md text-gray-600 text-justify">
                If your PDF is password-protected, please ensure you have the correct password handy. 
                You can also remove the password using tools like Adobe Acrobat before uploading.
              </p>
              <div className="mt-4 text-right">
                <button
                  onClick={togglePasswordInfo}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Results Display */}
        {data && (
          <div className="mt-6">
           {/* Summary Section */}
          <div className="mb-6">
            <h2 className="flex items-center text-2xl font-bold text-gray-800 mb-4 border-b-2 border-gray-300 pb-2">
              Summary
            </h2>
            <div className="bg-white shadow-lg p-6 rounded-lg">
              <div className="grid md:grid-cols-[auto_1fr] gap-4">
                {/* Dynamically Render Summary Paragraphs */}
                <div className="text-justify leading-relaxed text-gray-700 space-y-4">
                  {data && data.summary && data.summary.split('\n').map((paragraph, index) => (
                    paragraph.trim() !== '' && (
                      <div 
                        key={`paragraph-${index}`} 
                        className="bg-gray-50 p-4 rounded-lg border-l-4 border-blue-500"
                      >
                        <p className="text-gray-700">{paragraph.trim()}</p>
                      </div>
                    )
                  ))}
                </div>
              </div>
              
              {/* Download Buttons */}
              <div className="mt-6 flex justify-center space-x-4">
                <button
                  className="flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                  onClick={() => handleDownload("txt")}
                >
                  Download as TXT
                </button>
                <button
                  className="flex items-center px-4 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
                  onClick={() => handleDownload("pdf")}
                >
                  Download as PDF
                </button>
              </div>
            </div>
          </div>


            {/* Metadata and Content Stats Section */}
            <div className="mb-6 grid md:grid-cols-2 gap-4">
              {/* Document Details */}
              <div>
                <h2 className="text-xl font-semibold text-gray-700 mb-4">Document Details</h2>
                <div>
                  <strong>Title:</strong> {data.title}
                  <br />
                  <strong>Producer:</strong> {data.producer}
                  <br />
                  <strong>Language:</strong> {data.language}
                  <br />
                  <strong>Keywords:</strong>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {data.keywords && data.keywords.length > 0 ? (
                      data.keywords.map((keyword, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium shadow-sm hover:bg-blue-200 transition duration-200"
                        >
                          {keyword}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-500 text-sm">No keywords available</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Document Statistics */}
              <div>
                <h2 className="text-xl font-semibold text-gray-700 mb-4">Document Statistics</h2>
                <div>
                  <strong>Word Count:</strong> {data.word_count}
                  <br />
                  <strong>Reading Time:</strong> {data.reading_time} minutes
                  <br />
                  <strong>Images Found:</strong> {data.images ? data.images.length : 0}
                  <br />
                  <strong>Tables Found:</strong> {data.tables ? data.tables.length : 0}
                </div>
              </div>
            </div>

           {/* Images Section */}
              {data && data.images && data.images.length > 0 && (
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-700 mb-4">
                    Extracted Images ({data.images.length})
                  </h2>
                  <div className="grid grid-cols-2 gap-4">
                    {data.images.map((img, index) => (
                      <div key={index} className="border rounded-lg p-2">
                        <img
                          src={`data:image/png;base64,${img.base64_image}`}
                          alt={`Extracted image from page ${img.page_number}`}
                          className="w-full h-48 object-cover cursor-pointer"
                        />
                        <div className="mt-2">
                          {img.description && (
                            <div className="text-sm text-gray-600 mb-2">
                              <strong>OCR Text:</strong> {img.description || 'No text detected'}
                            </div>
                          )}
                          <div className="text-xs text-gray-500">
                            Page {img.page_number}, Image {index + 1}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            {/* Tables Section */}
              {data && data.tables && data.tables.length > 0 && (
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-700 mb-4">
                    Extracted Tables ({data.tables.length})
                  </h2>
                  {data.tables.map((table, index) => (
                    <div key={index} className="mb-4">
                      <div className="overflow-x-auto border rounded-lg">
                        <table className="w-full text-sm">
                          <thead className="bg-gray-100 border-b">
                            <tr>
                              {Object.keys(table.data[0] || {}).map(header => (
                                <th key={header} className="p-2 text-left">{header}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {table.data.map((row, rowIndex) => (
                              <tr key={rowIndex} className="border-b">
                                {Object.values(row).map((cell, cellIndex) => (
                                  <td key={cellIndex} className="p-2">{cell}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Page {table.page_number}, Table {table.table_index + 1}
                      </div>
                    </div>
                  ))}
                </div>
              )}


            {/* Audio Download */}
             <div className="mb-4">
              <a
                href={`http://localhost:5000${data.audio_path}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700"
              >
                Download Audio Summary
              </a>
            </div> 
          </div>
        )}
      </div>
    </div>
  );
}

export default App;