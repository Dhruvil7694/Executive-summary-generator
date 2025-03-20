from transformers import pipeline

def format_findings_and_vulnerabilities_free(raw_text):
    """
    Function to structure extracted raw text into a well-formatted 'Findings and Vulnerabilities' section
    using a free Hugging Face model.
    """
    # Load a summarization pipeline with a free Hugging Face model
    summarizer = pipeline("summarization", model="google/flan-t5-base", tokenizer="google/flan-t5-base")

    # Prompt to organize findings
    prompt = f"""
    You are a cybersecurity expert. The following text is extracted from a document and contains findings and vulnerabilities.
    Your task is to:
    1. Summarize and organize the findings into clear, concise bullet points.
    2. Present vulnerabilities in a table with columns: 'Vulnerability ID', 'Description', 'Impact', and 'Recommendation'.
    3. Ensure professional formatting and readability.

    Raw Text:
    {raw_text}

    Provide the formatted output.
    """

    # Generate the summary using the model
    summary = summarizer(prompt, max_length=512, min_length=100, do_sample=False)

    # Extract and return the summary text
    return summary[0]['summary_text']


# Example usage
if __name__ == "__main__":
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
        sales@purplesec.us...
    """

    formatted_section = format_findings_and_vulnerabilities_free(raw_text)
    print(formatted_section)
