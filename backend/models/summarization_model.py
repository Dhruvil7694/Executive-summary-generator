import unicodedata
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import os
import logging
import re
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
import asyncio  # Add this import

class SummarizationModel:
    def __init__(self, model_name: str = "google/flan-t5-large", local_path: str = "./models/flan-t5-large"):
        """Initialize the summarization model with local caching."""
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.local_path = Path(local_path)
        self.model_name = model_name

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        try:
            self._setup_model()
        except Exception as e:
            self.logger.error(f"Model initialization failed: {str(e)}")
            raise

    def _setup_model(self):
        """Setup model with local caching."""
        try:
            # Create local directory if it doesn't exist
            self.local_path.parent.mkdir(parents=True, exist_ok=True)

            # Load or download model and tokenizer
            if self.local_path.exists():
                self.logger.info("Loading model from local cache...")
                self.tokenizer = T5Tokenizer.from_pretrained(self.local_path)
                self.model = T5ForConditionalGeneration.from_pretrained(self.local_path)
            else:
                self.logger.info("Downloading model...")
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
                
                # Save model locally
                self.logger.info("Saving model to local cache...")
                self.tokenizer.save_pretrained(self.local_path)
                self.model.save_pretrained(self.local_path)

            # Move model to device
            self.model.to(self.device)
            self.logger.info(f"Model loaded successfully on {self.device}")

        except Exception as e:
            self.logger.error(f"Model setup failed: {str(e)}")
            raise

    def _clean_output(self, text: str) -> str:
        """Enhanced cleaning of generated output text."""
        try:
            # Remove noise and format issues
            noise_patterns = {
                r'\s*\.\s*\.\s*\.': '...',  # Fix ellipsis
                r'­+': '',                   # Remove soft hyphens
                r'_{2,}': '',                # Remove multiple underscores
                r'\?{3,}': '?',              # Fix multiple question marks
                r'-{3,}': '--',              # Standardize long dashes
                r'\s{2,}': ' ',              # Remove multiple spaces
                r'[\(\)\/]{2,}': '',         # Remove multiple parentheses/slashes
                r'(?i)true:\s*': '',         # Remove True: prefix
                r'(?i)false:\s*': '',        # Remove False: prefix
                r'(?i)null:\s*': '',         # Remove Null: prefix
                r'back to mail:.*': '',      # Remove mail references
                r'http[s]?://\S+': '',       # Remove URLs
                r'\d+\.\s*\d+\.\s*\d+\.': lambda m: m.group(0).replace(' ', ''),  # Fix version numbers
            }
            
            for pattern, replacement in noise_patterns.items():
                text = re.sub(pattern, replacement, text)

            # Enhance formatting of security-specific content
            security_formatting = {
                # Format CVE references
                r'(?i)\b(cve-\d{4}-\d+)\b': lambda m: m.group(1).upper(),
                
                # Format CVSS scores
                r'(?i)cvss(?:\s+score)?:\s*(\d+\.?\d*)': r'CVSS Score: \1',
                
                # Format severity levels
                r'(?i)\b(critical|high|medium|low)\s+severity\b': 
                    lambda m: m.group(1).upper() + ' Severity',
                
                # Format vulnerability counts
                r'(\d+)\s+vulnerabilities': r'\1 Vulnerabilities',
                
                # Format risk levels
                r'(?i)\b(critical|high|medium|low)\s+risk\b':
                    lambda m: m.group(1).upper() + ' Risk',
            }
            
            for pattern, replacement in security_formatting.items():
                text = re.sub(pattern, replacement, text)

            # Clean up sentences and structure
            sentences = text.split('.')
            cleaned_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                # Keep only meaningful sentences
                if (len(sentence) > 10 and 
                    not any(x in sentence.lower() for x in ['...', '___', '???']) and
                    not re.match(r'^[^a-zA-Z]*$', sentence)):
                    
                    # Capitalize first letter if needed
                    if sentence and sentence[0].isalpha():
                        sentence = sentence[0].upper() + sentence[1:]
                    
                    cleaned_sentences.append(sentence)

            # Join sentences and fix final formatting
            text = '. '.join(cleaned_sentences)
            
            # Final cleanup
            text = re.sub(r'\s*\.\s*', '. ', text)  # Fix spacing around periods
            text = re.sub(r'\s*,\s*', ', ', text)   # Fix spacing around commas
            text = re.sub(r'\s*:\s*', ': ', text)   # Fix spacing around colons
            text = re.sub(r'\s*;\s*', '; ', text)   # Fix spacing around semicolons
            text = re.sub(r'\s*\(\s*', ' (', text)  # Fix spacing around parentheses
            text = re.sub(r'\s*\)\s*', ') ', text)
            
            # Ensure proper paragraph separation
            text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', text)
            
            # Remove any remaining excessive whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Output cleaning failed: {str(e)}")
            return text

    def _preprocess_text(self, text: str) -> str:
        """Advanced preprocessing of input text."""
        try:
            # Initial cleanup
            text = unicodedata.normalize('NFKC', text)
            
            # Remove common document artifacts
            artifacts = [
                r'I\s*P\s*age',                    # Page markers
                r'Page\s*\d+\s*of\s*\d+',          # Page numbers
                r'Table\s+of\s+Contents.*?(?=\d+\.)', # Table of contents
                r'©.*?(?=\d{4})',                  # Copyright notices
                r'Confidential[^\n]*',             # Confidentiality notices
                r'Draft\s+Version[^\n]*',          # Draft markers
                r'Document\s+Status[^\n]*',        # Status headers
                r'Last\s+Updated[^\n]*',           # Update timestamps
                r'Generated\s+by[^\n]*',           # Generation notices
                r'\[+\s*\]+',                      # Empty brackets
                r'_{3,}',                          # Horizontal lines
                r'-{3,}',                          # Dash lines
            ]
            
            for pattern in artifacts:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

            # Normalize security-related terms
            security_terms = {
                r'(?i)cve-\d{4}-\d+': lambda m: m.group(0).upper(),  # CVE IDs
                r'(?i)cvss\s*:?\s*(\d+\.?\d*)': r'CVSS Score: \1',   # CVSS scores
                r'(?i)severity\s*:?\s*(critical|high|medium|low)': lambda m: f"Severity: {m.group(1).upper()}", # Severity levels
                r'(?i)risk\s*:?\s*(critical|high|medium|low)': lambda m: f"Risk Level: {m.group(1).upper()}"    # Risk levels
            }
            
            for pattern, replacement in security_terms.items():
                text = re.sub(pattern, replacement, text)

            # Fix version numbers and technical specifications
            text = re.sub(r'(\d+)\s*\.\s*(\d+)\s*\.\s*(\d+)', r'\1.\2.\3', text)  # Version numbers
            text = re.sub(r'v(\d)', r'version \1', text, flags=re.IGNORECASE)      # Version indicators
            
            # Normalize IP addresses and network ranges
            text = re.sub(r'(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?', 
                         lambda m: m.group(0).strip(), text)  # IP addresses
            
            # Fix list formatting
            text = re.sub(r'(?m)^\s*[-•]\s*', '\n• ', text)  # Bullet points
            text = re.sub(r'(?m)^\s*(\d+)\.\s+', r'\n\1. ', text)  # Numbered lists
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            # Ensure proper section separation
            text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', text)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Text preprocessing failed: {str(e)}")
            return text

    async def generate_section(self, text: str, section: str, prompt: str = None) -> str:
        try:
            # Ensure text length is within model limits
            max_length = 1024  # Adjust based on your model's limits
            text = text[:max_length]  # Truncate if too long
            
            # Convert any numeric values in prompt to strings
            if prompt:
                prompt = self._sanitize_prompt(prompt)
            
            # Generate the section content
            response = await self._generate(text, section, prompt)
            return response
            
        except Exception as e:
            logging.error(f"Section generation failed: {str(e)}")
            raise RuntimeError(f"Error generating section: {str(e)}")
    async def _generate(self, text: str, section: str, prompt: str = None) -> str:
        """Generate content for a specific section using the summarization model."""
        try:
            # Construct the input prompt
            section_prompt = f"Section: {section}\n"
            if prompt:
                section_prompt += f"Instructions: {prompt}\n"
            section_prompt += f"Content: {text}\n\nGenerate a detailed {section} section:"

            # Generate response using transformers
            inputs = self.tokenizer(section_prompt, return_tensors="pt", truncation=True, max_length=1024)
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=512,
                min_length=100,
                num_beams=4,
                temperature=0.7,
                no_repeat_ngram_size=3,
                early_stopping=True
            )
            
            # Decode and clean the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = self._clean_response(response)
            
            return response

        except Exception as e:
            logging.error(f"Generation failed for section {section}: {str(e)}")
            return f"Error generating {section}: {str(e)}"

    def _clean_response(self, text: str) -> str:
        """Clean and format the generated response."""
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        # Remove any repeated newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Ensure proper sentence capitalization
        sentences = re.split(r'([.!?]+)', text)
        text = ''.join(s.capitalize() if i % 2 == 0 else s
                    for i, s in enumerate(sentences))
        
        return text
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt by converting all numeric values to strings."""
        try:
            # Replace numeric patterns with their string representations
            pattern = r'\b\d+\b'
            return re.sub(pattern, lambda m: f'"{m.group(0)}"', prompt)
        except Exception:
            return prompt

    def _extract_total_hosts(self, text: str) -> int:
        """Extract total number of hosts from text."""
        try:
            match = re.search(r'(\d+)\s+hosts identified', text)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0

    def _extract_scanned_hosts(self, text: str) -> int:
        """Extract number of scanned hosts from text."""
        try:
            match = re.search(r'(\d+)\s+systems were found to be active', text)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0

    def _extract_vulnerability_counts(self, text: str) -> dict:
        """Extract vulnerability counts by severity."""
        try:
            counts = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            # Try to find counts in format "Critical Severity: X"
            for severity in counts.keys():
                match = re.search(rf'{severity.title()}\s+Severity\s+(\d+)', text, re.IGNORECASE)
                if match:
                    counts[severity] = int(match.group(1))
            
            return counts
        except Exception:
            return {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
    def summarize(self, text: str) -> Dict[str, Any]:
        """Generate a complete cybersecurity audit report."""
        try:
            sections = {
                "executive_summary": {
                    "prompt": (
                        "Create a clear, professional executive summary that addresses:\n"
                        "• Assessment Overview: Scope, objectives, and methodology\n"
                        "• Key Statistics: {scanned} out of {total} hosts scanned\n"
                        "• Critical Findings: {vuln_counts} total vulnerabilities found\n"
                        "• Risk Overview: Primary areas of concern and business impact\n\n"
                        "Focus on business impact and clarity. Avoid technical jargon."
                    ),
                    "max_length": 400,
                    "min_length": 200
                },
                "key_findings": {
                    "prompt": (
                        "Present the top 5 most critical security findings:\n\n"
                        "For each finding, structure as:\n"
                        "FINDING #[number]: [Vulnerability Name]\n"
                        "• Severity: [Rating] (CVSS: [Score])\n"
                        "• Affected Systems: [Count]\n"
                        "• Business Impact: [Clear description]\n"
                        "• Remediation Priority: [Immediate/High/Medium]\n"
                        "• Recommended Action: [Clear action item]\n\n"
                        "Focus on clarity and actionable insights."
                    ),
                    "max_length": 500,
                    "min_length": 250
                },
                "risk_assessment": {
                    "prompt": (
                        "Structure the risk assessment as follows:\n\n"
                        "CRITICAL RISKS ({critical_count} findings):\n"
                        "• Key Vulnerabilities:\n"
                        "• Business Impact:\n"
                        "• Required Actions:\n\n"
                        "HIGH RISKS ({high_count} findings):\n"
                        "• Key Vulnerabilities:\n"
                        "• Business Impact:\n"
                        "• Required Actions:\n\n"
                        "MEDIUM RISKS ({medium_count} findings):\n"
                        "• Key Vulnerabilities:\n"
                        "• Business Impact:\n"
                        "• Required Actions:\n\n"
                        "Focus on clear categorization and business context."
                    ),
                    "max_length": 600,
                    "min_length": 300
                },
                "recommendations": {
                    "prompt": (
                        "Structure recommendations as:\n\n"
                        "IMMEDIATE ACTIONS (0-7 days):\n"
                        "1. [Action Item]\n"
                        "   • Implementation Steps:\n"
                        "   • Required Resources:\n"
                        "   • Expected Impact:\n\n"
                        "SHORT-TERM ACTIONS (8-30 days):\n"
                        "1. [Action Item]\n"
                        "   • Implementation Steps:\n"
                        "   • Required Resources:\n"
                        "   • Expected Impact:\n\n"
                        "LONG-TERM ACTIONS (30+ days):\n"
                        "1. [Action Item]\n"
                        "   • Implementation Steps:\n"
                        "   • Required Resources:\n"
                        "   • Expected Impact:\n\n"
                        "Focus on practical, prioritized actions."
                    ),
                    "max_length": 800,
                    "min_length": 400
                }
            }

            # Generate each section
            report_sections = {}
            for section_name, config in sections.items():
                # Format prompt with actual data
                formatted_prompt = config["prompt"].format(
                    scanned=self._extract_scanned_hosts(text),
                    total=self._extract_total_hosts(text),
                    vuln_counts=sum(self._extract_vulnerability_counts(text).values()),
                    **self._extract_vulnerability_counts(text)
                )
                
                self.logger.info(f"Generating {section_name}...")
                section_content = self.generate_section(
                    text,
                    formatted_prompt,
                    config["max_length"],
                    config["min_length"]
                )
                report_sections[section_name] = section_content


            return {
                "sections": report_sections,
                "metadata": {
                    "model_info": {
                        "name": self.model_name,
                        "device": str(self.device)
                    },
                    "timestamp": datetime.now().isoformat(),
                    "text_length": len(text),
                    "scan_summary": {
                        "total_hosts": self._extract_total_hosts(text),
                        "scanned_hosts": self._extract_scanned_hosts(text),
                        "vulnerability_counts": self._extract_vulnerability_counts(text)
                    }
                }
            }

        except Exception as e:
            self.logger.error(f"Summarization failed: {str(e)}")
            return {"error": str(e)}

def main():
    """Test the summarization model."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample text for testing
    test_text = """
            2025-01-24 13:38:47,529 - INFO - Starting extraction of ../sample/sample.pdf
        2025-01-24 13:38:47,535 - INFO - Processing 5 pages
        2025-01-24 13:38:47,998 - INFO - Text extraction and cleaning completed successfully

        Extraction successful!

        Document Sections:
        ==================================================

        Sample Network Vulnerability Assessment Report I P age Table of Contents 1. Executive Summary 2 2. Scan Results 2 3. Our Findings 2 4. Risk Assessment 2 Critical Severity Vulnerability 2 High Severity Vulnerability 3 Medium Severity Vulnerability 3 Low Severity Vulnerability 3 5. Recommendations 3 Remediation 4 I P age 1. Executive Summary The purpose of this vulnerability scan is to gather data on Windows and third-party software patch levels on hosts in the SAMPLE-INC domain in the 00.00.00.0/01 subnet. Of the 300 hosts identified by SAMPLE- INC, 100 systems were found to be active and were scanned. 2. Scan Results The raw scan results will be provided upon delivery. 3. Our Findings The results from the credentialed patch audit are listed below. It is important to note that not all identified hosts were able to be scanned during this assessment – of the 300 hosts identified as belonging to the SAMPLE-INC domain, only 100 were successfully scanned. In addition, some of the hosts that were successfully scanned were not included in the host list provided. 4. Risk Assessment This report identifies security risks that could have significant impact on mission-critical applications used for day-to-day business operations. Critical Severity High Severity Medium Severity Low Severity 286 171 116 0 Critical Severity Vulnerability 286 were unique critical severity vulnerabilities. Critical vulnerabilities require immediate attention. They are relatively easy for attackers to exploit and may provide them with full control of the affected systems. A table of the top critical severity vulnerabilities is provided below: PLUGIN NAME DESCRIPTION SOLUTION COUNT Mozilla Firefox < 65.0 The version of Firefox installed on the remote Windows host is prior to 65.0. It is therefore affected by multiple vulnerabilities as referenced in the mfsa2019-01 advisory. Upgrade to Mozilla Firefox version 65.0 or later. 22 Mozilla Foundation Unsupported Application Detection According to its version there is at least one unsupported Mozilla application (FirefoxI ThunderbirdI and/or SeaMonkey) installed on the remote host. This version of the software is no longer actively maintained. Upgrade to a version that is currently supported. 16 I P age High Severity Vulnerability 171 were unique high severity vulnerabilities. High severity vulnerabilities are often harder to exploit and may not provide the same access to affected systems. A table of the top high severity vulnerabilities is provided below: PLUGIN NAME DESCRIPTION SOLUTION COUNT MS15-124: Cumulative Security Update for Internet Explorer (3116180) The version of Internet Explorer installed on the remote host is missing Cumulative Security Update 3116180. It is therefore affected by multiple vulnerabilities the majority of which are remote code execution vulnerabilities. Microsoft has released a set of patches for Windows Vista, 2008, 7, 2008 R2, 8, RT 2012, 8.1, RT 8.1, 2012 R2, and 10. 24 Mozilla Firefox < 64.0 Multiple Vulnerabilities The version of Mozilla Firefox installed on the remote Windows host is prior to 64.0. It is therefore affected by multiple vulnerabilities as noted in Mozilla Firefox stable channel update release notes for 2018/12/11. Upgrade to Mozilla Firefox version 64.0 or later. 22 Medium Severity Vulnerability 116 were unique medium severity vulnerabilities. These vulnerabilities often provide information to attackers that may assist them in mounting subsequent attacks on your network. These should also be fixed in a timely manner but are not as urgent as the other vulnerabilities. A table of the top high severity vulnerabilities is provided below: PLUGIN NAME DESCRIPTION SOLUTION COUNT Mozilla Firefox < 62.0.2 Vulnerability The version of Mozilla Firefox installed on the remote Windows host is prior to 62.0.2. It is therefore affected by a vulnerability as noted in Mozilla Firefox stable channel update release notes for 2018/09/21. Upgrade to Mozilla Firefox version 62.0.2 or later. 17 Mozilla Firefox < 57.0.4 Speculative Execution Side-Channel Attack Vulnerability (Spectre) The version of Mozilla Firefox installed on the remote Windows host is prior to 57.0.4. It is therefore vulnerable to a speculative execution side-channel attack. Code from a malicious web page could read data from other web sites or private data from the browser itself. Upgrade to Mozilla Firefox version 57.0.4 or later. 15 Low Severity Vulnerability No low severity vulnerabilities were found during this scan. I P age 5. Recommendations Recommendations in this report are based on the available findings from the credentialed patch audit. Vulnerability scanning is only one tool to assess the security posture of a network. The results should not be interpreted as definitive measurement of the security posture of the SAMPLE-INC network. Other elements used to assess the current security posture would include policy review, a review of internal security controls and procedures, or internal red teaming/penetration testing. Remediation Taking the following actions across all hosts will resolve 96% of the vulnerabilities on the network: ACTION TO TAKE VULNS HOSTS Mozilla Firefox < 65.0: Upgrade to Mozilla Firefox version 65.0 or later. 82 3 Adobe Acrobat <= 10.1.15 / 11.0.12 / 2015.006.30060 / 2015.008.20082 Multiple Vulnerabilities (APSB15-24): Upgrade to Adobe Acrobat 10.1.16 / 11.0.13 / 2015.006.30094 / 2015.009.20069 or later. 16 10 Oracle Java SE 1.7.x < 1.7.0_211 / 1.8.x < 1.8.0_201 / 1.11.x < 1.11.0_2 Multiple Vulnerabilities (January 2019 CPU): Upgrade to Oracle JDK / JRE 11 Update 2, 8 Update 201 / 7 Update 211 or later. If necessary, remove any affected versions. 7 6 Adobe AIR <= 22.0.0.153 Android Applications Runtime Analytics MitM (APSB16-31): Upgrade to Adobe AIR version 23.0.0.257 or later. 8 3.

        Full Text Preview:
        ==================================================
        Sample Network Vulnerability Assessment Report I P age Table of Contents 1. Executive Summary 2 2. Scan Results 2 3. Our Findings 2 4. Risk Assessment 2 Critical Severity Vulnerability 2 High Severity Vulnerability 3 Medium Severity Vulnerability 3 Low Severity Vulnerability 3 5. Recommendations 3 Remediation 4 I P age 1. Executive Summary The purpose of this vulnerability scan is to gather data on Windows and third-party software patch levels on hosts in the SAMPLE-INC domain in the 00.00.00.0/01 subnet. Of the 300 hosts identified by SAMPLE- INC, 100 systems were found to be active and were scanned. 2. Scan Results The raw scan results will be provided upon delivery. 3. Our Findings The results from the credentialed patch audit are listed below. It is important to note that not all identified hosts were able to be scanned during this assessment – of the 300 hosts identified as belonging to the SAMPLE-INC domain, only 100 were successfully scanned. In addition, some of the hosts that
        ==================================================

        Full text saved to 'extracted_text.txt'
    """

    try:
        # Initialize model
        model = SummarizationModel()
        
        # Generate report
        result = model.summarize(test_text)
        
        # Print results
        print("\n=== Cybersecurity Audit Report ===\n")
        
        for section_name, content in result["sections"].items():
            print(f"\n{section_name.upper()}")
            print("=" * len(section_name))
            print(content)
            print("\n" + "-" * 50)
        
        print(f"\nModel Info: {result['metadata']['model_info']}")

    except Exception as e:
        logging.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main()