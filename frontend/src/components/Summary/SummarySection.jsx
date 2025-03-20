import React, { useState, useEffect } from 'react';
import { 
  BookOpen, Brain, ChevronDown, ChevronUp, Copy, 
  Loader2, Tag, Clock, CheckCircle, XCircle,
  AlertCircle, RefreshCw, FileText, BarChart2,
  Download, Share2, Printer, PieChart, 
  BrainCircuit, Sparkles, ArrowUpRight, Shield
} from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const SummarySection = ({ data, loading, error, onRetry }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copyStatus, setCopyStatus] = useState('idle');
  const [activeTab, setActiveTab] = useState('summary');
  const [progress, setProgress] = useState(0);
  const [processingState, setProcessingState] = useState({
    stage: '',
    message: '',
    progress: 0
  });

  const handleProgress = (progress) => {
    setProcessingState({
      stage: progress.stage,
      message: progress.message,
      progress: progress.progress
    });
  };

  const processDocument = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/process-pdf', {
        method: 'POST',
        body: formData,
        onProgress: handleProgress
      });
      
      const result = await response.json();
      if (!result.summary) {
        throw new Error('No summary generated');
      }
      
      return result;
    } catch (error) {
      console.error('Processing error:', error);
      throw error;
    }
  };

  const getSeverityColor = (severity) => ({
    critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    high: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    low: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
  }[severity.toLowerCase()] || '');

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setProgress(prev => prev < 90 ? prev + 10 : prev);
      }, 1000);
      return () => clearInterval(interval);
    } else {
      setProgress(100);
    }
  }, [loading]);

  const handleCopy = async () => {
    if (!data?.summary) return;
    setCopyStatus('loading');
    try {
      await navigator.clipboard.writeText(data.summary);
      setCopyStatus('success');
    } catch {
      setCopyStatus('error');
    } finally {
      setTimeout(() => setCopyStatus('idle'), 2000);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Document Summary',
          text: data.summary
        });
      } catch (err) {
        console.error('Share failed:', err);
      }
    }
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'summary-report.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (error) {
    return (
      <Alert variant="destructive" className="max-w-4xl mx-auto">
        <AlertCircle className="h-5 w-5" />
        <AlertTitle>Processing Error</AlertTitle>
        <AlertDescription className="flex items-center justify-between">
          <span>{error}</span>
          {onRetry && (
            <Button variant="outline" size="sm" onClick={onRetry}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  if (loading) {
    return (
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            Processing Document
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Progress value={45} className="h-2" />
            <p className="text-sm text-muted-foreground">
              Analyzing document content...
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data?.summary) {
    return null;
  }

    if (!data?.summary) {
      return null;
    }

    const metrics = {
      wordCount: data.summary?.split(/\s+/).length || 0,
      readingTime: Math.ceil((data.summary?.split(/\s+/).length || 0) / 200),
      vulnerabilities: Object.values(data.vulnerabilities || {}).flat().length,
      keyTopics: (data.document_structure?.key_concepts || []).length
    };

    const chartData = Object.entries(data.vulnerabilities || {}).map(([severity, items]) => ({
      name: severity.charAt(0).toUpperCase() + severity.slice(1),
      count: items.length
    }));

    return (
      <Card className="max-w-4xl mx-auto">
        <CardHeader className="border-b space-y-4">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <CardTitle className="text-2xl font-bold flex items-center gap-2">
                <BrainCircuit className="h-6 w-6 text-primary" />
                Document Analysis Report
              </CardTitle>
              <p className="text-muted-foreground mt-1 flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Generated {new Date().toLocaleString()}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={handleShare}>
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button variant="default" size="sm" onClick={handleCopy}>
                {copyStatus === 'idle' && <Copy className="h-4 w-4 mr-2" />}
                {copyStatus === 'loading' && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                {copyStatus === 'success' && <CheckCircle className="h-4 w-4 mr-2" />}
                {copyStatus === 'error' && <XCircle className="h-4 w-4 mr-2" />}
                {copyStatus === 'idle' ? 'Copy' : 
                copyStatus === 'loading' ? 'Copying...' : 
                copyStatus === 'success' ? 'Copied!' : 'Failed'}
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard 
              icon={Clock} 
              title="Reading Time" 
              value={metrics.readingTime} 
              unit=" min"
            />
            <MetricCard 
              icon={BookOpen} 
              title="Word Count" 
              value={metrics.wordCount}
            />
            <MetricCard 
              icon={Shield} 
              title="Vulnerabilities" 
              value={metrics.vulnerabilities}
            />
            <MetricCard 
              icon={Tag} 
              title="Key Topics" 
              value={metrics.keyTopics}
            />
          </div>
        </CardHeader>

        <Tabs defaultValue="summary" className="w-full">
          <TabsList className="grid w-full grid-cols-4 px-6 pt-6">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="vulnerabilities">Security</TabsTrigger>
            <TabsTrigger value="structure">Structure</TabsTrigger>
            <TabsTrigger value="topics">Topics</TabsTrigger>
          </TabsList>

          <TabsContent value="summary" className="p-6">
            <div className="space-y-6">
              <div className="prose dark:prose-invert max-w-none">
                <div className={`${isExpanded ? '' : 'line-clamp-3'} text-lg leading-relaxed`}>
                  {data.summary}
                </div>
                <Button
                  variant="ghost"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="mt-4 flex items-center gap-2"
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="h-4 w-4" />
                      Show Less
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-4 w-4" />
                      Read More
                    </>
                  )}
                </Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="vulnerabilities" className="p-6">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Vulnerability Distribution</CardTitle>
                </CardHeader>
                <CardContent className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#2563eb" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Severity</TableHead>
                    <TableHead className="text-right">Count</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(data.vulnerabilities || {}).map(([severity, items]) => (
                    <TableRow key={severity}>
                      <TableCell>
                        <Badge className={getSeverityColor(severity)}>
                          {severity.charAt(0).toUpperCase() + severity.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-bold">{items.length}</TableCell>
                      <TableCell>
                        <ul className="list-disc pl-4">
                          {items.slice(0, 3).map((item, index) => (
                            <li key={index} className="text-sm">{item}</li>
                          ))}
                          {items.length > 3 && (
                            <li className="text-sm text-muted-foreground">
                              +{items.length - 3} more...
                            </li>
                          )}
                        </ul>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="structure" className="p-6">
            <div className="space-y-6">
              {Object.entries(data.document_structure || {}).map(([section, items]) => {
                if (!Array.isArray(items) || !items.length) return null;
                
                return (
                  <Card key={section}>
                    <CardHeader>
                      <CardTitle className="capitalize">
                        {section.replace(/_/g, ' ')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-3">
                        {items.map((item, index) => (
                          <li key={index} className="flex items-start gap-2 text-muted-foreground">
                            <ArrowUpRight className="h-5 w-5 mt-1 flex-shrink-0" />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          <TabsContent value="topics" className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.document_structure?.key_concepts?.map((topic, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Tag className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{topic}</p>
                        <p className="text-sm text-muted-foreground">Topic {index + 1}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    );
  };

  const MetricCard = ({ icon: Icon, title, value, unit = '' }) => (
    <Card className="bg-secondary/50">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <Icon className="h-5 w-5 text-primary" />
          <div>
            <p className="text-sm font-medium">{title}</p>
            <p className="text-2xl font-bold">
              {typeof value === 'number' ? value.toLocaleString() : value}
              {unit}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );


export default SummarySection;