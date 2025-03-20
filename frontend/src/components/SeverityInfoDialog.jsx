import React from 'react';
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel } from "@/components/ui/alert-dialog";
import { AlertCircle, AlertTriangle, AlertOctagon, Info, Shield } from "lucide-react";

const severityData = [
  {
    level: 'Critical',
    description: 'Immediate threat to key business processes.',
    icon: AlertOctagon,
    color: 'red'
  },
  {
    level: 'High',
    description: 'Direct threat to key business processes.',
    icon: AlertTriangle,
    color: 'orange'
  },
  {
    level: 'Medium',
    description: 'No direct threat exists. The vulnerability may be exploited using other vulnerabilities.',
    icon: AlertCircle,
    color: 'yellow'
  },
  {
    level: 'Low',
    description: 'No direct threat exists. The vulnerability may be exploited using other vulnerabilities.',
    icon: AlertCircle,
    color: 'green'
  },
  {
    level: 'Informational',
    description: 'This finding does not indicate vulnerability but states a comment that notifies about design flaws and improper implementation that might cause a problem in the long run.',
    icon: Info,
    color: 'gray'
  }
];

const getSeverityColor = (color, darkMode) => {
  const colors = {
    red: darkMode ? 'bg-red-900 text-red-300' : 'bg-red-100 text-red-700',
    orange: darkMode ? 'bg-orange-900 text-orange-300' : 'bg-orange-100 text-orange-700',
    yellow: darkMode ? 'bg-yellow-900 text-yellow-300' : 'bg-yellow-100 text-yellow-700',
    green: darkMode ? 'bg-green-900 text-green-300' : 'bg-green-100 text-green-700',
    gray: darkMode ? 'bg-gray-900 text-gray-300' : 'bg-gray-100 text-gray-700'
  };
  return colors[color];
};

const SeverityInfoDialog = ({ open, onClose, darkMode }) => {
  return (
    <AlertDialog open={open} onOpenChange={onClose}>
      <AlertDialogContent className={`max-w-4xl max-h-[90vh] overflow-y-auto transform transition-all duration-300 scale-100 ${darkMode ? 'bg-slate-950' : 'bg-white'}`}>
      <AlertDialogHeader className="sticky top-0 z-10 backdrop-blur-md bg-opacity-80">
        <AlertDialogTitle 
            className={`flex items-center justify-between px-6 py-4 text-xl font-bold
            ${darkMode 
            ? 'text-blue-100 bg-slate-950/70 border-b border-slate-800/50' 
            : 'text-blue-900 bg-white/70 border-b border-blue-100/50'
            } backdrop-blur-lg`}
        >
            <div className="flex items-center gap-2">
            <Shield className={`w-6 h-6 ${darkMode ? 'text-blue-300' : 'text-blue-600'}`} />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-blue-700 dark:from-blue-300 dark:to-blue-500">
                Severity Levels Description
            </span>
            </div>
            <AlertDialogCancel 
            className={`group relative inline-flex items-center justify-center w-10 h-10 
            overflow-hidden rounded-full transition-all duration-300 hover:scale-110
            ${darkMode 
                ? 'bg-slate-800/50 hover:bg-slate-700/50' 
                : 'bg-blue-50/50 hover:bg-blue-100/50'
            } backdrop-blur-sm shadow-lg hover:shadow-xl`}
            >
            <span className={`absolute inset-0 transition-opacity duration-300 opacity-0 group-hover:opacity-100
                ${darkMode ? 'bg-red-500/20' : 'bg-red-100/30'}`}
            />
            <svg 
                className={`w-5 h-5 transition-all duration-300 group-hover:rotate-90
                ${darkMode ? 'text-blue-300 group-hover:text-red-300' : 'text-blue-700 group-hover:text-red-600'}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
            >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            </AlertDialogCancel>
        </AlertDialogTitle>
        
        <AlertDialogDescription 
            className={`px-6 text-lg backdrop-blur-sm
            ${darkMode ? 'text-blue-300/90 bg-slate-950/30' : 'text-blue-700/90 bg-white/30'}`}
        >
            Understanding security issue severity levels and their implications
        </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="px-6 py-4 space-y-4">
          {severityData.map((severity, index) => {
            const IconComponent = severity.icon;
            return (
              <div 
                key={index}
                className={`rounded-lg p-4 transition-all duration-200 hover:transform hover:scale-[1.01] ${
                  darkMode ? 'bg-slate-900 hover:bg-slate-800' : 'bg-white hover:bg-blue-50'
                } border ${darkMode ? 'border-slate-800' : 'border-blue-200'}`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-full ${getSeverityColor(severity.color, darkMode)}`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${getSeverityColor(severity.color, darkMode)}`}>
                        {severity.level}
                      </span>
                    </div>
                    <p className={`text-sm leading-relaxed ${darkMode ? 'text-blue-100' : 'text-blue-900'}`}>
                      {severity.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default SeverityInfoDialog;