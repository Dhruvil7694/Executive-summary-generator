import torch
from transformers import BartTokenizer, BartForConditionalGeneration
import language_tool_python  # For grammar and spelling correction
from sklearn.feature_extraction.text import CountVectorizer  # For keyword extraction
from textblob import TextBlob  # For sentiment analysis

def generate_cybersecurity_summary(report_text):
    
    # Load the pre-trained BART model and tokenizer
    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    # Preprocess the input text
    inputs = tokenizer(report_text, max_length=1024, truncation=True, return_tensors="pt")

    # Fine-tuning instructions for better summary generation
    summary_ids = model.generate(
        inputs['input_ids'],
        num_beams=6,  # Increase beam search for better quality
        length_penalty=1.2,  # Slightly reduce penalty to allow more details
        max_length=300,  # Allow longer summaries
        min_length=100,  # Ensure sufficient content
        no_repeat_ngram_size=3,  # Avoid repetitive phrases
        early_stopping=True  # Stop generation when the summary is complete
    )

    # Decode the generated summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # Grammar and spelling correction
    tool = language_tool_python.LanguageTool('en-US')
    corrected_summary = tool.correct(summary)

    # Refine the summary to ensure it is cybersecurity-specific and flows logically
    refined_summary = refine_cybersecurity_summary(corrected_summary, report_text)

    # Perform keyword extraction to highlight vulnerabilities or attack vectors
    keywords = extract_keywords(report_text)

    # Perform sentiment analysis to assess the severity of risks
    sentiment = analyze_sentiment(report_text)

    # Append keywords and sentiment analysis results to the summary
    if keywords:
        refined_summary += f" Key vulnerabilities or attack vectors identified include: {', '.join(keywords)}."
    if sentiment:
        refined_summary += f" Sentiment analysis indicates that the overall risk level is {sentiment}."

    return refined_summary


def refine_cybersecurity_summary(summary, report_text):
   
    # Split the summary into sentences
    sentences = summary.split(". ")

    # Improve the introduction
    if sentences[0].startswith("Of the") or sentences[0].startswith("The"):
        sentences[0] = "This cybersecurity report evaluates key findings and identifies critical risks."

    # Add context about vulnerabilities and risks
    if "vulnerability" in report_text.lower() or "risk" in report_text.lower():
        sentences.insert(1, "The report highlights significant vulnerabilities and risks that require immediate attention.")

    # Include cybersecurity-specific keywords if missing
    critical_keywords = [
        "multi-factor authentication", "unauthorized access", "vulnerability", "exploit",
        "patch", "mitigation", "risk assessment", "incident response", "data breach",
        "phishing", "malware", "ransomware", "firewall", "intrusion detection", "encryption",
        "password policy", "software update", "security training", "zero-day", "attack vector",
        "threat actor", "compliance", "network security", "endpoint protection", "access control"
    ]

    missing_keywords = [keyword for keyword in critical_keywords if keyword in report_text.lower() and keyword not in summary.lower()]
    if missing_keywords:
        keyword_sentence = f"Key factors highlighted in the report include {', '.join(missing_keywords[:-1])}, and {missing_keywords[-1]}."
        sentences.append(keyword_sentence)

    # Simplify and format recommendations
    if "recommendations" in report_text.lower():
        sentences.append("To mitigate identified risks, the report recommends implementing robust security measures, including software updates, employee training, and enhanced access controls.")

    # Remove redundant phrases
    sentences = [sentence for sentence in sentences if "Recommendations in this report" not in sentence]

    # Join the refined sentences back into a single summary
    refined_summary = ". ".join(sentences).strip().replace("..", ".")

    return refined_summary


def extract_keywords(text):
    
    # Define a custom list of cybersecurity-related terms to prioritize
    cybersecurity_terms = [
        "vulnerability", "exploit", "attack vector", "threat actor", "phishing",
        "malware", "ransomware", "data breach", "unauthorized access", "zero-day",
        "firewall", "intrusion detection", "encryption", "multi-factor authentication",
        
        # Additional terms:
        "adversary", "APT (Advanced Persistent Threat)", "backdoor", "botnet", 
        "brute force attack", "credential stuffing", "cross-site scripting (XSS)",
        "denial of service (DoS)", "distributed denial of service (DDoS)", 
        "endpoint security", "honeypot", "incident response", "keylogger", 
        "man-in-the-middle (MitM) attack", "patch management", "payload", 
        "penetration testing", "privilege escalation", "rootkit", "sandbox", 
        "social engineering", "spyware", "SQL injection", "threat intelligence", 
        "two-factor authentication (2FA)", "virtual private network (VPN)", 
        "virus", "worm", "whaling", "watering hole attack", "white hat", 
        "black hat", "gray hat", "red team", "blue team", "purple team", 
        "security information and event management (SIEM)", 
        "security operations center (SOC)", "zero trust architecture", 
        "biometric authentication", "blockchain", "cloud security", 
        "cryptocurrency", "dark web", "digital certificate", "digital forensics", 
        "DNS spoofing", "fileless malware", "hash function", "insider threat", 
        "least privilege", "logic bomb", "macro virus", "network segmentation", 
        "obfuscation", "open redirect", "password cracking", "password spraying", 
        "port scanning", "protocol", "quantum cryptography", "risk assessment", 
        "rogue software", "secure socket layer (SSL)", "session hijacking", 
        "sniffing", "spoofing", "supply chain attack", "threat hunting", 
        "tokenization", "Trojan horse", "USB drop attack", "web application firewall (WAF)", 
        "wireless security", "zero knowledge proof"
    ]

    # Use CountVectorizer to extract top keywords
    vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
    X = vectorizer.fit_transform([text])
    feature_array = vectorizer.get_feature_names_out()
    word_counts = X.toarray().flatten()

    # Combine term frequency with custom prioritization
    keyword_scores = {}
    for term, count in zip(feature_array, word_counts):
        if term in cybersecurity_terms:
            keyword_scores[term] = count * 2  # Prioritize cybersecurity terms
        else:
            keyword_scores[term] = count

    # Sort keywords by score and return top 5
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return [kw for kw, _ in sorted_keywords]


def analyze_sentiment(text):
    
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity < -0.5:
        return "high risk"
    elif polarity < 0:
        return "moderate risk"
    else:
        return "low risk"



def main():
    # Example input text (can be replaced with any type of document)
    input_text = """
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

    # Generate the summary
    summary = generate_cybersecurity_summary(input_text)

    # Print the generated summary
    print("Summary:")
    print(summary)


if __name__ == "__main__":
    main()