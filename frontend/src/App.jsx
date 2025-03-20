import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import 'jspdf-autotable';
import { 
  Cloud,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Upload,
  FileText,
  Download,
  Sun,
  Moon,
  RefreshCw,
  Server,
  RotateCcw,
  Clock
} from "lucide-react";
import ResultsSection from './components/ResultsSection';

import Findings from './components/Findings';
import Recommendations from './components/Recommendations';



const App = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileId, setFileId] = useState(null);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [serverStatus, setServerStatus] = useState({ status: "checking", lastChecked: null });
  

  // Add drag and drop handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file && file.type !== "application/pdf") {
      setError("Please select a valid PDF file");
      return;
    }
    setError(null);
    setSelectedFile(file);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setFileId(null);
    setStatus(null);
    setProgress(0);
    setReport(null);
    setError(null);
    setIsLoading(false);
    // Reset file input
    const fileInput = document.getElementById('file-upload');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  // Server status check function
  const checkServerStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/test");
      const isOnline = response.status === 200;
      setServerStatus({
        status: isOnline ? "online" : "offline",
        lastChecked: new Date().toLocaleTimeString()
      });
    } catch {
      setServerStatus({
        status: "offline",
        lastChecked: new Date().toLocaleTimeString()
      });
    }
  };

  // Add a new useEffect to handle server status checking
  useEffect(() => {
    // No server status checks if report is generated
    if (report) return;
  
    checkServerStatus();
    const interval = setInterval(checkServerStatus, 30000);
    
    // Cleanup function to clear the interval
    return () => clearInterval(interval);
  }, [report, checkServerStatus]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type !== "application/pdf") {
      setError("Please select a valid PDF file");
      setSelectedFile(null);
      return;
    }
    setError(null);
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a PDF file first");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setProgress(0);
    setReport(null);
    
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        setFileId(data.fileId);
        setStatus("Processing started");
        // Remove simulated progress, rely on actual backend status
      } else {
        throw new Error("Upload failed");
      }
    } catch (err) {
      setError("Failed to upload file. Please try again.");
      setIsLoading(false);
    }
  };

  

  const getStatusColor = (stage) => {
    switch (stage) {
      case 'upload':
        return 'text-blue-600 dark:text-blue-400';
      case 'processing':
        return 'text-amber-600 dark:text-amber-400';
      case 'completed':
        return 'text-green-600 dark:text-green-400';
      case 'failed':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const orderedSections = [
    'ExecutiveSummary',
    'Introduction',
    'Findings',
    'Results',
    'Recommendations',
    'Conclusion',
    'Metadata'
  ];

  // Update the status checking effect
  useEffect(() => {
    if (!fileId) return;

    const checkStatus = async () => {
      try {
        const statusResponse = await fetch(`http://localhost:8000/api/status/${fileId}`);
        const statusData = await statusResponse.json();
        
        setProgress(statusData.progress);
        setStatus(statusData.message);

        if (statusData.stage === 'completed') {
          setReport(statusData.results);
          setIsLoading(false);
        } else if (statusData.stage === 'failed') {
          setError(statusData.message);
          setIsLoading(false);
        }
      } catch (err) {
        setError("Failed to check status");
        setIsLoading(false);
      }
    };

    const interval = setInterval(checkStatus, 1000); // Check more frequently (every second)
    return () => clearInterval(interval);
  }, [fileId]);
  

  const handleDownloadResults = async () => {
    if (!fileId) return;

    try {
      const response = await fetch(`http://localhost:8000/api/download/${fileId}`);
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'cybersecurity_report.json';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setError('Failed to download report');
    }
  };

  const getServerStatusBadge = () => {
    const statusColors = {
      checking: "bg-yellow-100 text-yellow-800",
      online: "bg-green-100 text-green-800",
      offline: "bg-red-100 text-red-800"
    };

    return (
      <div className="flex flex-col space-y-2 p-4 rounded-lg border border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Badge variant={serverStatus.status} className={`${statusColors[serverStatus.status]} px-3 py-1`}>
              <Server className="w-4 h-4 mr-2" />
              {serverStatus.status.charAt(0).toUpperCase() + serverStatus.status.slice(1)}
            </Badge>
            <span className="text-sm text-gray-600 dark:text-gray-300 font-medium ">
              System Status
            </span>
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
            <Clock className="w-3 h-3 mr-1 ml-2" />
            Last checked: {serverStatus.lastChecked}
          </span>
        </div>
        {serverStatus.message && (
          <p className="text-sm text-gray-600 dark:text-gray-300">
            {serverStatus.message}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className={`min-h-screen ${darkMode ? "dark" : ""}`}>
      <div className="bg-gradient-to-br from-blue-100 via-blue-50 to-indigo-50 dark:from-blue-950 dark:via-slate-900 dark:to-blue-900 min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header Card */}
          <Card className="mb-8 shadow-lg border-0 bg-white/80 dark:bg-slate-900/50 backdrop-blur-lg backdrop-saturate-150">
            <CardHeader className="flex flex-row items-center justify-between bg-transparent p-6">
              <div className="flex items-center space-x-3">
                <FileText className="h-7 w-7 text-blue-600 dark:text-blue-400" />
                <div className="flex flex-col">
                  <CardTitle className="text-xl font-medium text-blue-900 dark:text-blue-100">
                    Security Audit Generator
                  </CardTitle>
                  <p className="text-sm text-blue-600/80 dark:text-blue-300/80 mt-0.5">
                    Generate comprehensive security reports
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="hidden sm:block">
                  {getServerStatusBadge()}
                </div>
                <div className="flex items-center">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setDarkMode(!darkMode)}
                    className="hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                    title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                  >
                    {darkMode ? (
                      <Sun className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                    ) : (
                      <Moon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                    )}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <div className="block sm:hidden px-4 pb-4 bg-white dark:bg-gray-900">
              {getServerStatusBadge()}
            </div>
          </Card>

          {/* File Upload Card */}
          <Card className="mb-8 bg-white/80 dark:bg-slate-900/50 backdrop-blur-lg backdrop-saturate-150 shadow-lg border border-blue-100/50 dark:border-blue-500/20">
            <CardContent className="pt-6">
              <div
                onDragEnter={handleDragIn}
                onDragLeave={handleDragOut}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative flex flex-col items-center justify-center p-8 border-2 ${
                  isDragging
                    ? "border-blue-400 bg-blue-50/50 dark:bg-blue-900/20"
                    : "border-dashed border-blue-200 dark:border-blue-700/50"
                } rounded-lg transition-all duration-200 ease-in-out group hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-900/20 backdrop-blur-sm`}
              >
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  onChange={handleFileChange}
                  accept="application/pdf"
                />
                
                <div className="flex flex-col items-center text-center">
                  <Cloud className={`mb-4 h-12 w-12 ${
                    isDragging ? "text-blue-500" : "text-blue-400/60"
                  } group-hover:text-blue-500 transition-colors duration-200`} />
                  
                  <div className="space-y-2">
                    <div className="flex flex-col items-center gap-2">
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        <span className="font-semibold text-blue-600 dark:text-blue-400">
                          Click to upload
                        </span>{" "}
                        or drag and drop
                      </p>
                      <p className="text-xs text-blue-600/70 dark:text-blue-400/70">
                        PDF files up to 10MB
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {selectedFile && (
                <div className="mt-4">
                  <Alert className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                    <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                    <AlertTitle className="text-green-800 dark:text-green-200">File Ready</AlertTitle>
                    <AlertDescription className="text-green-700 dark:text-green-300">
                      {selectedFile.name} ({Math.round(selectedFile.size / 1024)} KB)
                    </AlertDescription>
                  </Alert>
                </div>
              )}

              {error && (
                <Alert variant="destructive" className="mt-4 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                  <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                  <AlertTitle className="text-red-800 dark:text-red-200">Error</AlertTitle>
                  <AlertDescription className="text-red-700 dark:text-red-300">{error}</AlertDescription>
                </Alert>
              )}

              {status && (
                <div className="mt-4 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {isLoading && (
                        <RefreshCw 
                          className={`w-4 h-4 animate-spin ${getStatusColor(status.stage)}`} 
                        />
                      )}
                      <span className={`text-sm font-medium ${getStatusColor(status.stage)}`}>
                        {status}
                      </span>
                      <div className="ml-2 px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/50">
                        <span className="text-xs font-medium text-blue-700 dark:text-blue-300">
                          {progress < 100 ? 'Processing' : 'Complete'}
                        </span>
                      </div>
                    </div>
                    <span className="text-sm font-semibold bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded-md text-blue-600 dark:text-blue-400">
                      {progress}%
                    </span>
                  </div>
                  <div className="relative">
                    <Progress 
                      value={progress} 
                      className="w-full h-3 bg-blue-100 dark:bg-blue-900 rounded-full"
                    />
                    <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center pointer-events-none">
                      <div className="w-full h-full absolute">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <div
                            key={i}
                            className="absolute h-full w-px bg-blue-200 dark:bg-blue-800"
                            style={{ left: `${(i + 1) * 20}%` }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-between text-xs text-blue-500 dark:text-blue-400">
                    <span>Start</span>
                    <span>Processing</span>
                    <span>Analyzing</span>
                    <span>Finalizing</span>
                    <span>Complete</span>
                  </div>
                </div>
              )}

              <div className="mt-6 flex justify-end gap-3">
                <Button
                  onClick={handleReset}
                  variant="outline"
                  disabled={isLoading}
                  className="w-full sm:w-auto border-2 border-blue-200 dark:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                >
                  <RotateCcw className="mr-2 h-4 w-4" />
                  Reset
                </Button>
                <Button
                  onClick={handleUpload}
                  disabled={!selectedFile || isLoading}
                  className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 dark:bg-blue-600/80 dark:hover:bg-blue-700/80"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload and Analyze
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results Section */}
          {report && (
            <Card className="bg-white/80 dark:bg-slate-900/50 backdrop-blur-lg backdrop-saturate-150 shadow-lg border border-blue-100/50 dark:border-blue-500/20">
              <CardHeader className="flex flex-row justify-between items-center">
                <CardTitle className="text-blue-900 dark:text-blue-100">Comprehensive Analysis Report</CardTitle>
                <Button 
                  variant="outline" 
                  onClick={handleDownloadResults}
                  disabled={!fileId}
                  className="border-blue-200 dark:border-blue-800 hover:bg-blue-50 dark:hover:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download Report
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-8 text-justify">
                {orderedSections.map((sectionKey) => {
                  const sectionValue = report[sectionKey];
                  
                  if (!sectionValue) return null;

                  return (
                    <div key={sectionKey}>
                      <h3 className="font-bold text-lg mb-4 text-blue-900 dark:text-blue-100">
                        {sectionKey.replace(/_/g, ' ')}
                      </h3>
                      
                      {sectionKey === 'Results' ? (
                        <ResultsSection sectionValue={sectionValue} darkMode={darkMode} />
                      ) : sectionKey === 'Findings' ? (
                        <Findings findings={report.Findings} />
                      ) : sectionKey === 'Recommendations' ? (
                        <Recommendations recommendations={report.Recommendations} />
                        ) : sectionKey === 'Metadata' && typeof sectionValue === 'object' ? (
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-blue-200 dark:divide-blue-800 rounded-full">
                              <thead className="bg-blue-50/70 dark:bg-blue-900/30 backdrop-blur-sm">
                                <tr>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-blue-700 dark:text-blue-300 uppercase tracking-wider">Property</th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-blue-700 dark:text-blue-300 uppercase tracking-wider">Value</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white/50 dark:bg-slate-900/50 divide-y divide-blue-200 dark:divide-blue-800">
                                {Object.entries(sectionValue).map(([metaKey, metaValue]) => (
                                  <tr key={metaKey} className="hover:bg-blue-50 dark:hover:bg-slate-800">
                                    <td className="px-6 py-4 text-sm font-medium text-blue-900 dark:text-blue-100">
                                      {metaKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-blue-900 dark:text-blue-100">
                                      {typeof metaValue === 'string' && metaValue.includes('T') 
                                        ? new Date(metaValue).toLocaleString()
                                        : metaValue}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <p className="text-blue-500 dark:text-blue-400">{sectionValue}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;