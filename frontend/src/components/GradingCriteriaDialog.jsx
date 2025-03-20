import React, { useState, useRef, useEffect } from 'react';
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";
import { Shield, Info, ChevronRight, Lightbulb, Target, AlertTriangle, Search } from "lucide-react";

const gradingData = [
  {
    grade: "A",
    title: "Excellence in Security",
    description: "Excellent - The security exceeds 'Industry Best Practice' standards. The overall posture was found to be excellent with only a few low-risk findings identified.",
    color: "green",
    icon: "🏆",
    impact: "Minimal Risk",
    recommendations: [
      { title: "Maintain Standards", description: "Continue current security practices and monitoring" },
      { title: "Proactive Monitoring", description: "Regular security assessments and updates" },
      { title: "Innovation", description: "Explore emerging security technologies" }
    ]
  },
  {
    grade: "B",
    title: "Strong Security Stance",
    description: "Good - The security meets accepted standards for 'Industry Best Practice.' The overall posture was found to be strong with only a handful of medium- and low-risk shortcomings identified.",
    color: "blue",
    icon: "✨",
    impact: "Low Risk",
    recommendations: [
      { title: "Fine-tune Controls", description: "Address minor security gaps" },
      { title: "Enhance Monitoring", description: "Strengthen detection capabilities" },
      { title: "Training", description: "Regular security awareness programs" }
    ]
  },
  {
    grade: "C",
    title: "Moderate Security Status",
    description: "Fair - Current solutions protect some areas of the enterprise from security issues. Moderate changes are required to elevate the discussed areas to 'Industry Best Practice' standards.",
    color: "yellow",
    icon: "⚠️",
    impact: "Moderate Risk",
    recommendations: [
      { title: "Gap Analysis", description: "Identify and prioritize security gaps" },
      { title: "Implementation Plan", description: "Develop security improvement roadmap" },
      { title: "Resource Planning", description: "Allocate resources for improvements" }
    ]
  },
  {
    grade: "D",
    title: "Security Concerns Present",
    description: "Poor - Significant security deficiencies exist. Immediate attention should be given to the discussed issues to address the exposures identified. Major changes are required to elevate to 'Industry Best Practice' standards.",
    color: "orange",
    icon: "⚡",
    impact: "High Risk",
    recommendations: [
      { title: "Urgent Review", description: "Immediate security assessment needed" },
      { title: "Critical Fixes", description: "Address high-priority vulnerabilities" },
      { title: "Control Enhancement", description: "Implement missing security controls" }
    ]
  },
  {
    grade: "E",
    title: "Critical Security Issues",
    description: "Inadequate - Serious security deficiencies exist. Shortcomings were identified throughout most or even all of the security controls examined. Improving security will require a major allocation of resources.",
    color: "red",
    icon: "🚨",
    impact: "Critical Risk",
    recommendations: [
      { title: "Emergency Response", description: "Immediate security intervention required" },
      { title: "Complete Overhaul", description: "Comprehensive security restructuring" },
      { title: "Expert Consultation", description: "Engage security specialists" }
    ]
  }
];

const getGradeColor = (color, darkMode) => {
  const colors = {
    green: darkMode ? "bg-green-900/90 text-green-300 hover:bg-green-800/90" : "bg-green-100 text-green-700 hover:bg-green-200",
    blue: darkMode ? "bg-blue-900/90 text-blue-300 hover:bg-blue-800/90" : "bg-blue-100 text-blue-700 hover:bg-blue-200",
    yellow: darkMode ? "bg-yellow-900/90 text-yellow-300 hover:bg-yellow-800/90" : "bg-yellow-100 text-yellow-700 hover:bg-yellow-200",
    orange: darkMode ? "bg-orange-900/90 text-orange-300 hover:bg-orange-800/90" : "bg-orange-100 text-orange-700 hover:bg-orange-200",
    red: darkMode ? "bg-red-900/90 text-red-300 hover:bg-red-800/90" : "bg-red-100 text-red-700 hover:bg-red-200",
  };
  return colors[color];
};

const GradingCriteriaDialog = ({ open, onClose, darkMode }) => {
  const [selectedGrade, setSelectedGrade] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const cardRefs = useRef({});

  const handleGradeClick = (grade) => {
    setSelectedGrade(selectedGrade === grade ? null : grade);
    if (selectedGrade !== grade && cardRefs.current[grade]) {
      cardRefs.current[grade].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const filteredGrades = gradingData.filter(grade =>
    grade.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    grade.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <AlertDialog open={open} onOpenChange={onClose}>
      <AlertDialogContent className={`max-w-5xl max-h-[90vh] overflow-y-auto transform transition-all duration-500 ${
        darkMode ? "bg-slate-950 text-blue-200" : "bg-white text-blue-900"
      } rounded-xl shadow-2xl border border-opacity-20 ${
        darkMode ? "border-slate-800" : "border-blue-200"
      }`}>
        <AlertDialogHeader className="sticky top-0 z-20 backdrop-blur-xl bg-opacity-90">
          <AlertDialogTitle className={`flex items-center justify-between px-6 py-4 text-xl font-bold rounded-t-xl ${
            darkMode
              ? "text-blue-100 bg-slate-950/90 border-b border-slate-800/50"
              : "text-blue-900 bg-white/90 border-b border-blue-100/50"
          }`}>
            <div className="flex items-center gap-3 group">
              <Shield className={`w-8 h-8 transition-all duration-300 group-hover:rotate-12 ${
                darkMode ? "text-blue-300" : "text-blue-600"
              }`} />
              <div className="flex flex-col">
                <span className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 dark:from-blue-300 dark:via-blue-400 dark:to-blue-500">
                  Security Grading Criteria
                </span>
                <span className={`text-sm ${darkMode ? "text-blue-400" : "text-blue-600"}`}>
                  Comprehensive Security Assessment Criteria List
                </span>
              </div>
            </div>
            <AlertDialogCancel className={`group relative inline-flex items-center justify-center w-12 h-12 rounded-full transition-all duration-300 hover:scale-110 ${
              darkMode
                ? "bg-slate-800/50 hover:bg-slate-700/50"
                : "bg-blue-50/50 hover:bg-blue-100/50"
            } shadow-lg hover:shadow-xl`}>
              <span className={`absolute inset-0 rounded-full transition-opacity duration-300 opacity-0 group-hover:opacity-100 ${
                darkMode ? "bg-red-500/20" : "bg-red-100/30"
              }`} />
              <svg className={`w-6 h-6 transition-all duration-300 group-hover:rotate-90 ${
                darkMode
                  ? "text-blue-300 group-hover:text-red-300"
                  : "text-blue-700 group-hover:text-red-600"
              }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </AlertDialogCancel>
          </AlertDialogTitle>

          <div className={`px-6 py-4 ${
            darkMode ? "bg-slate-950/80" : "bg-white/80"
          }`}>
            <div className="flex items-center gap-4 mb-4">
              <div className={`relative flex-1 ${
                darkMode ? "text-blue-300" : "text-blue-700"
              }`}>
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 opacity-60" />
                <input
                  type="text"
                  placeholder="Search grades or descriptions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className={`w-full pl-10 pr-4 py-2 rounded-lg outline-none transition-all duration-300 ${
                    darkMode
                      ? "bg-slate-800 border-slate-700 focus:border-blue-500 text-blue-200"
                      : "bg-blue-50 border-blue-200 focus:border-blue-500 text-blue-900"
                  } border`}
                />
              </div>
            </div>

            {/* <div className="flex gap-4 border-b border-opacity-20">
              {['overview', 'recommendations', 'impact'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 text-sm font-medium transition-all duration-300 ${
                    activeTab === tab
                      ? darkMode
                        ? "text-blue-300 border-b-2 border-blue-500"
                        : "text-blue-700 border-b-2 border-blue-500"
                      : darkMode
                      ? "text-blue-400/60 hover:text-blue-300"
                      : "text-blue-600/60 hover:text-blue-700"
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div> */}
          </div>
        </AlertDialogHeader>

        <div className="px-6 py-4 space-y-4">
          {filteredGrades.map((grade) => (
            <div
              key={grade.grade}
              ref={el => cardRefs.current[grade.grade] = el}
              className={`transform transition-all duration-300 ${
                selectedGrade === grade.grade ? 'scale-102' : 'hover:scale-101'
              }`}
              onClick={() => handleGradeClick(grade.grade)}
            >
              <div className={`rounded-xl p-5 cursor-pointer transition-all duration-300 ${
                darkMode
                  ? `bg-slate-900/90 hover:bg-slate-800 border-slate-700 ${
                      selectedGrade === grade.grade ? 'ring-2 ring-blue-500/50' : ''
                    }`
                  : `bg-white hover:bg-blue-50 border-blue-200 ${
                      selectedGrade === grade.grade ? 'ring-2 ring-blue-500/30' : ''
                    }`
              } border shadow-lg hover:shadow-xl`}>
                <div className="flex items-start gap-4">
                  <div className={`p-4 rounded-xl shadow-lg transition-all duration-300 ${getGradeColor(grade.color, darkMode)}`}>
                    <div className="flex flex-col items-center">
                      <span className="text-3xl font-bold">{grade.grade}</span>
                      <span className="text-2xl mt-2">{grade.icon}</span>
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className={`text-lg font-semibold ${
                        darkMode ? "text-blue-200" : "text-blue-800"
                      }`}>
                        {grade.title}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-sm ${getGradeColor(grade.color, darkMode)}`}>
                        {grade.impact}
                      </span>
                    </div>
                    
                    <p className={`text-sm leading-relaxed ${
                      darkMode ? "text-blue-100/90" : "text-blue-900"
                    }`}>
                      {grade.description}
                    </p>

                    {selectedGrade === grade.grade && (
                      <div className={`mt-4 rounded-lg overflow-hidden ${
                        darkMode ? "bg-slate-800/50" : "bg-blue-50/50"
                      }`}>
                        <div className="flex border-b border-opacity-20">
                          {activeTab === 'recommendations' && (
                            <div className="p-4 space-y-3 w-full">
                              {grade.recommendations.map((rec, idx) => (
                                <div key={idx} className={`p-3 rounded-lg ${
                                  darkMode ? "bg-slate-700/50" : "bg-blue-100/50"
                                }`}>
                                  <div className="flex items-center gap-2">
                                    <Lightbulb className="w-4 h-4" />
                                    <h4 className="font-medium">{rec.title}</h4>
                                  </div>
                                  <p className="mt-1 text-sm opacity-90">{rec.description}</p>
                                </div>
                              ))}
                            </div>
                          )}

                          {activeTab === 'impact' && (
                            <div className="p-4 space-y-3 w-full">
                              <div className={`p-3 rounded-lg ${
                                darkMode ? "bg-slate-700/50" : "bg-blue-100/50"
                              }`}>
                                <div className="flex items-center gap-2">
                                  <AlertTriangle className="w-4 h-4" />
                                  <h4 className="font-medium">Impact Level: {grade.impact}</h4>
                                </div>
                                <p className="mt-2 text-sm">
                                  {grade.grade === "A" && "Minimal impact on security posture. Regular monitoring sufficient."}
                                  {grade.grade === "B" && "Low impact with some areas requiring attention."}
                                  {grade.grade === "C" && "Moderate impact requiring planned improvements."}
                                  {grade.grade === "D" && "High impact requiring immediate attention and resource allocation."}
                                  {grade.grade === "E" && "Critical impact necessitating emergency intervention and complete security overhaul."}
                                </p>
                                <div className="mt-3 space-y-2">
                                  <div className={`p-2 rounded-lg ${
                                    darkMode ? "bg-slate-800/50" : "bg-white/50"
                                  }`}>
                                    <h5 className="font-medium">Business Impact</h5>
                                    <p className="text-sm mt-1">
                                      {grade.grade === "A" && "Minimal business risk with strong security posture supporting operations."}
                                      {grade.grade === "B" && "Minor operational adjustments may be needed to address security gaps."}
                                      {grade.grade === "C" && "Moderate business risk requiring planned security improvements."}
                                      {grade.grade === "D" && "Significant business risk requiring immediate mitigation strategies."}
                                      {grade.grade === "E" && "Severe business risk demanding urgent executive attention and resources."}
                                    </p>
                                  </div>
                                  <div className={`p-2 rounded-lg ${
                                    darkMode ? "bg-slate-800/50" : "bg-white/50"
                                  }`}>
                                    <h5 className="font-medium">Timeline</h5>
                                    <p className="text-sm mt-1">
                                      {grade.grade === "A" && "Maintain current practices with regular reviews."}
                                      {grade.grade === "B" && "Address findings within 3-6 months."}
                                      {grade.grade === "C" && "Implement improvements within 1-3 months."}
                                      {grade.grade === "D" && "Urgent attention required within 2-4 weeks."}
                                      {grade.grade === "E" && "Immediate action required within 1 week."}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}

                          {activeTab === 'overview' && (
                            <div className="p-4 space-y-3 w-full">
                              <div className={`p-3 rounded-lg ${
                                darkMode ? "bg-slate-700/50" : "bg-blue-100/50"
                              }`}>
                                <h4 className="font-medium flex items-center gap-2">
                                  <Target className="w-4 h-4" />
                                  Key Characteristics
                                </h4>
                                <ul className="mt-2 space-y-2 text-sm">
                                  {grade.grade === "A" && (
                                    <>
                                      <li>• Exceptional security controls</li>
                                      <li>• Proactive threat management</li>
                                      <li>• Industry-leading practices</li>
                                    </>
                                  )}
                                  {grade.grade === "B" && (
                                    <>
                                      <li>• Strong security foundation</li>
                                      <li>• Minor improvements needed</li>
                                      <li>• Good risk management</li>
                                    </>
                                  )}
                                  {grade.grade === "C" && (
                                    <>
                                      <li>• Basic security measures</li>
                                      <li>• Several improvements needed</li>
                                      <li>• Moderate risk exposure</li>
                                    </>
                                  )}
                                  {grade.grade === "D" && (
                                    <>
                                      <li>• Significant vulnerabilities</li>
                                      <li>• Immediate action required</li>
                                      <li>• High risk exposure</li>
                                    </>
                                  )}
                                  {grade.grade === "E" && (
                                    <>
                                      <li>• Critical security gaps</li>
                                      <li>• Emergency intervention needed</li>
                                      <li>• Severe risk exposure</li>
                                    </>
                                  )}
                                </ul>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredGrades.length === 0 && (
          <div className={`p-8 text-center ${
            darkMode ? "text-blue-300" : "text-blue-700"
          }`}>
            <div className="flex justify-center mb-4">
              <Search className="w-12 h-12 opacity-50" />
            </div>
            <h3 className="text-lg font-medium">No matching grades found</h3>
            <p className="mt-2 text-sm opacity-70">Try adjusting your search terms</p>
          </div>
        )}
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default GradingCriteriaDialog;