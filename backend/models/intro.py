import os
import json
from openai import OpenAI

# Configure the API client
token = os.environ.get("GITHUB_TOKEN")  # Ensure your GITHUB_TOKEN is properly set in the environment
endpoint = "https://models.inference.ai.azure.com"  # Replace with your endpoint if different
model_name = "gpt-4o-mini"  # Specify the model hosted in your setup

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)


def generate_audit_report(raw_text):
    """
    Generates a cybersecurity audit report using the GPT-4 model hosted on infrastructure.
    """
    try:
        # The enhanced prompt to instruct GPT-4 to generate a detailed and accurate report
        prompt = f"""
You are a professional cybersecurity analyst tasked with generating a comprehensive cybersecurity audit report based on the 
provided raw text from a cybersecurity document. The report should be tailored to the specific focus of the document, 
whether it be vulnerabilities, compliance issues, or other security concerns, vulnerability assessment, penetration test summary, 
compliance audit, malware analysis, or incident response reports.
Moreover, focus on getting correct dates and times for the report. Such as when was the test conducted, when was the report generated, etc.
Also Make sure to not repeat the same information in the report.

Please organize the report using the following sections:
1. Executive Summary:
   - Craft a detailed executive summary of the audit report, capturing its core findings, key insights, and major conclusions.
   - Ensure clarity and precision, making it accessible to readers who may not go through the full report.
   - Highlight critical observations, significant risks, key performance metrics, and major recommendations.
   - Maintain a professional and neutral tone, avoiding technical jargon where possible.
   - MAke sure to mention proper Dates and Times for the report.

2. Introduction:
   - craft a detailed introduction of the audit report, capturing its core findings, key insights, and major conclusions.
   - Develop a structured and engaging introduction that provides context for the audit.
   - Clearly define the audit’s purpose, objectives, and significance.
   - Outline the scope of the audit, specifying what was examined, the timeframe, and any limitations.
   - Briefly describe the methodology, including data sources, assessment techniques, and criteria used.
   - Establish the relevance of the audit by linking it to industry standards, regulations, or organizational goals.

3. Findings:

   - Detail the specific findings from the cybersecurity document in JSON format. Each finding should be an object with keys like "issue", "impact", and "details". Example:
     [
         {{
             "issue": "Insecure software configurations",
             "impact": "High",
             "details": "Multiple servers are configured with default settings, which may allow unauthorized access."
         }},
         {{
             "issue": "Lack of encryption",
             "impact": "Medium",
             "details": "Sensitive data is transmitted in plaintext over the network."
         }}
     ]
4. Results:
   - STRUCTURE THIS SECTION AS STRICTLY VALID JSON format with an array of objects for individual vulnerabilities, followed by a single object summarizing the overall result. Each vulnerability object should include keys like vulnerability, description, and severity. The overall result object should include keys for scope, security_level, and grade, where the grade is assigned based on the provided grading criteria. Example:
     "Ensure that the grade is 100% accurate and reflects the overall security posture based on the grading criteria: A (Excellent) : Security exceeds “Industry Best Practice” standards with only a few low-risk findings. B (Good) : Security meets accepted standards for “Industry Best Practice” with minor medium- and low-risk shortcomings. C (Fair) : Some areas are protected, but moderate changes are needed to meet best practices. D (Poor) : Significant security deficiencies exist, requiring major changes to address identified exposures. E (Inadequate) : Serious security deficiencies exist across most or all controls, requiring a major allocation of resources to improve.
     Also focus on the number of issues for each severity. Also focus on giving number of based on this criteria such as Severity scoring with descriptions: A. Critical – Immediate threat to key business processes. B. High – Direct threat to key business processes. C. Medium – No direct threat exists. The vulnerability may be exploited using other vulnerabilities. D. Low – No direct threat exists. The vulnerability may be exploited using other vulnerabilities. E. Informational – This finding does not indicate vulnerability but states a comment that notifies about design flaws and improper implementation that might cause a problem in the long run.
     [
        "overall_result": [
        {{
            "scope": "Network Infrastructure Audit",
            "security_level": "Poor",
            "grade": "D"
        }}
        ],
        "issues": [
            {{
            "Severity": "Critical",
            "issues": 0
            }},
            {{
            "Severity": "High",
            "issues": 0
            }},
            {{
            "Severity": "Medium",
            "issues": 5
            }},
            {{
            "Severity": "Low",
            "issues": 3
            }},
            {{
            "Severity": "Informational",
            "issues": 0
            }}
        ]
        "Vulnerabilities":[
         {{
             "vulnerability": "Outdated software",
             "description": "Critical patches are missing for key systems.",
             "severity": "High",
             
         }},
         {{
             "vulnerability": "Weak passwords",
             "description": "Password complexity requirements are not enforced.",
             "severity": "Medium",
         }}]
     ],


5. Recommendations:
   - Provide actionable recommendations based on the findings in JSON format. Each recommendation should be an object with keys like "action", "rationale", and "impact". Example:
     [
         {{
             "action": "Update software",
             "rationale": "To patch vulnerabilities in outdated systems",
             "impact": "High"
         }},
         {{
             "action": "Implement password policy",
             "rationale": "To enhance security by enforcing complexity requirements",
             "impact": "Medium"
         }}
     ]
6. Conclusion:
   - Craft a detailed conclusion for a cybersecurity audit report by summarizing the overall security posture of the system or network, highlighting critical vulnerabilities, risks, and compliance gaps while prioritizing issues based on their impact; evaluate the overall risk level, assess compliance with relevant regulations, and acknowledge both strengths and weaknesses in the current security measures; provide actionable, prioritized recommendations to mitigate risks and enhance security, along with clear warnings about potential consequences of inaction or emerging threats; and deliver a final assessment of the system's security health, using definitive language to convey whether it is secure, at risk, or critically vulnerable, ensuring the conclusion is evidence-based, well-structured, and focused on guiding decision-making for improving cybersecurity resilience.

Use the raw text below as input information for creating the report:

<<<START OF RAW TEXT>>>
{raw_text}
<<<END OF RAW TEXT>>>

Begin writing the report:
"""

        # Sending the enhanced prompt to the API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,  # Adjust creativity/randomness
            top_p=0.9,       # Maximum probability distribution
            max_tokens=4000,  # Max output tokens
            model=model_name,
        )

        # Extract the generated content
        report = response.choices[0].message.content
        return report

    except Exception as e:
        return f"An error occurred: {str(e)}"


import json

def parse_results(results_content):
    """
    Parse the Results section as JSON. If it fails, log the error and return an empty structure.
    """
    try:
        # Remove potential markdown-style code block indicators (```json ... ```)
        if results_content.startswith("```json"):
            results_content = results_content.strip("```json").strip("```").strip()
        
        # Attempt to parse the results content as JSON
        return json.loads(results_content)
    except json.JSONDecodeError as e:
        print(f"Error parsing Results section as JSON: {e}")
        print("Problematic Results content:\n", results_content)
        
        # Return a default/fallback structure in case of error
        return {
            "error": "Failed to parse Results content as valid JSON.",
            "content": results_content
        }

def save_report_to_advanced_json(report, filename="Updated_cybersecurity_audit_report.json"):
    """
    Saves the generated cybersecurity audit report to an advanced JSON file format 
    and returns the path of the saved file.
    """
    try:
        # Split the report into sections using double newlines (ensuring we avoid breaking structured content)
        sections = report.split("\n\n")

        # Initialize the structured JSON data
        report_data = {
            "ExecutiveSummary": "",
            "Introduction": "",
            "Findings": "",
            "Results": [],
            "Recommendations": "",
            "Conclusion": ""
        }

        for section in sections:
            # Extract section title and content
            lines = section.split("\n", 1)  # Split section into title and content
            if len(lines) == 2:
                title = lines[0].strip().lower()
                content = lines[1].strip()

                # Map each section to the structured JSON keys
                if "executive summary" in title:
                    report_data["ExecutiveSummary"] = content
                elif "introduction" in title:
                    report_data["Introduction"] = content
                elif "findings" in title:
                    report_data["Findings"] = parse_results(content)
                elif "results" in title:
                    # Parse JSON content from the Results section
                    report_data["Results"] = parse_results(content)
                elif "recommendations" in title:
                    report_data["Recommendations"] = parse_results(content)
                elif "conclusion" in title:
                    report_data["Conclusion"] = content

        # Save the structured report as a JSON file with UTF-8 encoding
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(report_data, json_file, indent=4, ensure_ascii=False)
        print(f"Report successfully saved to {filename}")
        return filename  # Return the saved file path
    except Exception as e:
        print(f"An error occurred while saving the report: {str(e)}")
        return None  # Return None if there was an error
    

def load_json_data(file_path):
    """
    Load and parse JSON data from a file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # Load JSON content into a Python dictionary
            print(f"Successfully loaded data from: {file_path}")
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Sample raw text extracted from a cybersecurity document
    raw_text = """
        Sample Network Vulnerability Assessment Report
        sales@purplesec.usTable of Contents
        1. Executive Summary ................................................................................................................................... 2
        2. Scan Results .............................................................................................................................................. 2
        3. Our Findings .............................................................................................................................................. 2
        4. Risk Assessment ........................................................................................................................................ 2
        Critical Severity Vulnerability .................................................................................................................... 2
        High Severity Vulnerability ........................................................................................................................ 3
        Medium Severity Vulnerability ................................................................................................................. 3
        Low Severity Vulnerability ........................................................................................................................ 3
        5. Recommendations .................................................................................................................................... 3
        Remediation .............................................................................................................................................. 4
        1 | P age
        sales@purplesec.us1. Executive Summary
        The purpose of this vulnerability scan is to gather data on Windows and third-party software patch levels
        on hosts in the SAMPLE-INC domain in the 00.00.00.0/01 subnet. Of the 300 hosts identified by SAMPLE-
        INC, 100 systems were found to be active and were scanned.
        2. Scan Results
        The raw scan results will be provided upon delivery.
        3. Our Findings
        The results from the credentialed patch audit are listed below. It is important to note that not all
        identified hosts were able to be scanned during this assessment – of the 300 hosts identified as belonging
        to the SAMPLE-INC domain, only 100 were successfully scanned. In addition, some of the hosts that were
        successfully scanned were not included in the host list provided.
        4. Risk Assessment
        This report identifies security risks that could have significant impact on mission-critical applications used
        for day-to-day business operations.
        Critical Severity High Severity Medium Severity Low Severity
        286 171 116 0
        Critical Severity Vulnerability
        286 were unique critical severity vulnerabilities. Critical vulnerabilities require immediate attention. They
        are relatively easy for attackers to exploit and may provide them with full control of the affected systems.
        A table of the top critical severity vulnerabilities is provided below:
        PLUGIN NAME DESCRIPTION SOLUTION COUNT
        The version of Firefox installed on the
        Upgrade to Mozilla
        remote Windows host is prior to 65.0. It is
        Mozilla Firefox < 65.0 Firefox version 65.0 or 22
        therefore affected by multiple vulnerabilities
        later.
        as referenced in the mfsa2019-01 advisory.
        According to its version there is at least one
        Mozilla Foundation unsupported Mozilla application (Firefox| Upgrade to a version
        Unsupported Thunderbird| and/or SeaMonkey) installed that is currently 16
        Application Detection on the remote host. This version of the supported.
        software is no longer actively maintained.
        2 | P age
        sales@purplesec.usHigh Severity Vulnerability
        171 were unique high severity vulnerabilities. High severity vulnerabilities are often harder to exploit and
        may not provide the same access to affected systems.
        A table of the top high severity vulnerabilities is provided below:
        PLUGIN NAME DESCRIPTION SOLUTION COUNT
        The version of Internet Explorer installed on Microsoft has released
        MS15-124: Cumulative the remote host is missing Cumulative a set of patches for
        Security Update for Security Update 3116180. It is therefore Windows Vista, 2008,
        24
        Internet Explorer affected by multiple vulnerabilities the 7, 2008 R2, 8, RT 2012,
        (3116180) majority of which are remote code execution 8.1, RT 8.1, 2012 R2,
        vulnerabilities. and 10.
        The version of Mozilla Firefox installed on the
        remote Windows host is prior to 64.0. It is Upgrade to Mozilla
        Mozilla Firefox < 64.0
        therefore affected by multiple vulnerabilities Firefox version 64.0 or 22
        Multiple Vulnerabilities
        as noted in Mozilla Firefox stable channel later.
        update release notes for 2018/12/11.
        Medium Severity Vulnerability
        116 were unique medium severity vulnerabilities. These vulnerabilities often provide information to
        attackers that may assist them in mounting subsequent attacks on your network. These should also be
        fixed in a timely manner but are not as urgent as the other vulnerabilities.
        A table of the top high severity vulnerabilities is provided below:
        PLUGIN NAME DESCRIPTION SOLUTION COUNT
        The version of Mozilla Firefox installed on the
        remote Windows host is prior to 62.0.2. It is Upgrade to Mozilla
        Mozilla Firefox < 62.0.2
        therefore affected by a vulnerability as noted Firefox version 62.0.2 17
        Vulnerability
        in Mozilla Firefox stable channel update or later.
        release notes for 2018/09/21.
        The version of Mozilla Firefox installed on the
        remote Windows host is prior to 57.0.4. It is
        Mozilla Firefox < 57.0.4
        therefore vulnerable to a speculative Upgrade to Mozilla
        Speculative Execution
        execution side-channel attack. Code from a Firefox version 57.0.4 15
        Side-Channel Attack
        malicious web page could read data from or later.
        Vulnerability (Spectre)
        other web sites or private data from the
        browser itself.
        Low Severity Vulnerability
        No low severity vulnerabilities were found during this scan.
        3 | P age
        sales@purplesec.us5. Recommendations
        Recommendations in this report are based on the available findings from the credentialed patch audit.
        Vulnerability scanning is only one tool to assess the security posture of a network. The results should not
        be interpreted as definitive measurement of the security posture of the SAMPLE-INC network. Other
        elements used to assess the current security posture would include policy review, a review of internal
        security controls and procedures, or internal red teaming/penetration testing.
        Remediation
        Taking the following actions across all hosts will resolve 96% of the vulnerabilities on the network:
        ACTION TO TAKE VULNS HOSTS
        Mozilla Firefox < 65.0: Upgrade to Mozilla Firefox version 65.0 or later. 82 3
        Adobe Acrobat <= 10.1.15 / 11.0.12 / 2015.006.30060 / 2015.008.20082 Multiple
        Vulnerabilities (APSB15-24): Upgrade to Adobe Acrobat 10.1.16 / 11.0.13 / 16 10
        2015.006.30094 / 2015.009.20069 or later.
        Oracle Java SE 1.7.x < 1.7.0_211 / 1.8.x < 1.8.0_201 / 1.11.x < 1.11.0_2 Multiple
        Vulnerabilities (January 2019 CPU): Upgrade to Oracle JDK / JRE 11 Update 2, 8 7 6
        Update 201 / 7 Update 211 or later. If necessary, remove any affected versions.
        Adobe AIR <= 22.0.0.153 Android Applications Runtime Analytics MitM (APSB16-31):
        8 3
        Upgrade to Adobe AIR version 23.0.0.257 or later.
        4 | P age
        sales@purplesec.us
    """

    # Generate the cybersecurity audit report
    report = generate_audit_report(raw_text)

    if "An error occurred" not in report:
        # Print the generated report
        print("Generated Cybersecurity Audit Report:\n")
        print(report)

        # Save the report in JSON format with proper structure
        save_report_to_advanced_json(report)
        load_json_data(report)
    else:
        print(report)