import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, AlertCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';

const ProcessingStatus = ({ fileId, onComplete }) => {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/status/${fileId}`);
        const data = await response.json();
        
        setStatus(data);
        
        if (data.stage === 'completed') {
          onComplete(data.results);
          return; // Stop polling
        }
        
        // Continue polling if not complete
        setTimeout(checkStatus, 1000);
      } catch (err) {
        setError('Failed to fetch status');
        console.error('Status check failed:', err);
      }
    };

    checkStatus();
  }, [fileId]);

  if (error) {
    return (
      <Card className="bg-red-50">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!status) return null;

  const getStageIcon = () => {
    switch (status.stage) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      default:
        return <Activity className="h-5 w-5 text-blue-500 animate-pulse" />;
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getStageIcon()}
              <span className="font-medium capitalize">{status.stage}</span>
            </div>
            <span className="text-sm text-gray-500">{status.progress}%</span>
          </div>
          
          <Progress value={status.progress} className="h-2" />
          
          <p className="text-sm text-gray-600">{status.message}</p>
          
          {status.stage === 'completed' && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg">
              <p className="text-green-600 text-sm">
                Analysis completed successfully! Viewing results...
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProcessingStatus;