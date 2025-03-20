// ReportComponents.js
import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
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
  AlertCircle
} from "lucide-react";

// Helper Components
const SectionCard = ({ title, content }) => (
  <Card className="mb-6">
    <CardHeader>
      <CardTitle className="text-xl">{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="text-gray-700 dark:text-gray-300 leading-relaxed">
        {content}
      </div>
    </CardContent>
  </Card>
);

const VulnerabilityCard = ({ vulnerability }) => {
  const severityColors = {
    Critical: "bg-red-100 text-red-800 border-red-200",
    High: "bg-orange-100 text-orange-800 border-orange-200",
    Medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
    Low: "bg-blue-100 text-blue-800 border-blue-200"
  };

  return (
    <div className={`p-4 rounded-lg mb-4 border ${severityColors[vulnerability.severity]}`}>
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-semibold">{vulnerability.vulnerability}</h4>
          <p className="mt-1 text-sm">{vulnerability.description}</p>
        </div>
        <Badge variant="outline" className={severityColors[vulnerability.severity]}>
          {vulnerability.severity}
        </Badge>
      </div>
    </div>
  );
};

const ReportSection = ({ report }) => {
  if (!report) return null;

  const sections = [
    {
      id: "executive-summary",
      title: "Executive Summary",
      content: report.ExecutiveSummary
    },
    {
      id: "introduction",
      title: "Introduction",
      content: report.Introduction
    },
    {
      id: "findings",
      title: "Findings",
      content: report.Findings
    },
    {
      id: "results",
      title: "Detailed Results",
      content: (
        <div className="space-y-4">
          {report.Results.sort((a, b) => {
            const severityOrder = { Critical: 0, High: 1, Medium: 2, Low: 3 };
            return severityOrder[a.severity] - severityOrder[b.severity];
          }).map((vulnerability, index) => (
            <VulnerabilityCard key={index} vulnerability={vulnerability} />
          ))}
        </div>
      )
    },
    {
      id: "recommendations",
      title: "Recommendations",
      content: report.Recommendations.split('\n').map((rec, index) => (
        <div key={index} className="flex items-start mb-2">
          {index > 0 && <div className="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0" />}
          <span>{rec}</span>
        </div>
      ))
    },
    {
      id: "conclusion",
      title: "Conclusion",
      content: report.Conclusion
    },
    {
      id: "metadata",
      title: "Metadata",
      content: (
        <div className="space-y-2 text-sm">
          <div className="flex justify-between border-b pb-2">
            <span className="font-medium">Processing Completed:</span>
            <span>{new Date(report.Metadata.processing_completed).toLocaleString()}</span>
          </div>
          <div className="flex justify-between border-b pb-2">
            <span className="font-medium">Text Length:</span>
            <span>{report.Metadata.text_length} characters</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">Timestamp:</span>
            <span>{new Date(report.Metadata.timestamp).toLocaleString()}</span>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6">
        <div className="flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-blue-700 dark:text-blue-300">
            Analysis Report
          </h3>
        </div>
        <p className="mt-2 text-sm text-blue-600 dark:text-blue-300">
          This report presents a comprehensive security analysis with findings and recommendations.
        </p>
      </div>

      {sections.map((section) => (
        <SectionCard
          key={section.id}
          title={section.title}
          content={section.content}
        />
      ))}

      <div className="flex justify-end mt-6">
        <Button 
          onClick={() => {
            const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'security-audit-report.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          }}
        >
          <Download className="mr-2 h-4 w-4" />
          Download Full Report
        </Button>
      </div>
    </div>
  );
};

export default { SectionCard, VulnerabilityCard, ReportSection };