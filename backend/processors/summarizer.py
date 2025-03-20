from dataclasses import dataclass
import logging
from typing import Dict, List, Tuple

import numpy as np
import spacy
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
from rouge_score import rouge_scorer
import textstat
from nltk.tokenize import sent_tokenize

@dataclass
class SummaryMetrics:
    """Stores metrics for evaluating summary quality."""
    rouge_scores: Dict[str, float]
    coherence_score: float
    readability_score: float
    compression_ratio: float
    coverage_score: float

class OptimizedSummarizer:
    """A streamlined text summarization class using T5 and other NLP models."""
    
    def __init__(self):
        """Initialize models and tokenizers."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize core models
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        self.model = T5ForConditionalGeneration.from_pretrained('t5-base').to(self.device)
        self.nlp = spacy.load('en_core_web_sm')
        self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').to(self.device)
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        logging.info(f"Initialized OptimizedSummarizer using device: {self.device}")

    def preprocess_text(self, text: str) -> str:
        """Remove duplicates and normalize text."""
        # Split into sentences and get embeddings
        sentences = [sent.strip() for sent in self.nlp(text).sents]
        embeddings = self.sentence_transformer.encode(sentences)
        
        # Remove duplicate sentences based on semantic similarity
        unique_sentences = []
        seen_embeddings = []
        
        for sent, emb in zip(sentences, embeddings):
            # Skip very short sentences
            if len(sent.split()) < 4:
                continue
                
            # Check if sentence is semantically similar to any previous sentence
            if not any(np.dot(emb, seen_emb) / (np.linalg.norm(emb) * np.linalg.norm(seen_emb)) > 0.85 
                      for seen_emb in seen_embeddings):
                unique_sentences.append(str(sent))
                seen_embeddings.append(emb)
        
        return ' '.join(unique_sentences)

    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate a summary using T5 model."""
        try:
            # Prepare input
            input_text = f"summarize: {text}"
            inputs = self.tokenizer(
                input_text,
                max_length=1024,
                padding=True,
                truncation=True,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=max_length,
                    min_length=30,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3
                )
            
            # Decode and return summary
            return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
        except Exception as e:
            logging.error(f"Summary generation failed: {str(e)}")
            return ""

    def calculate_metrics(self, original_text: str, summary: str) -> SummaryMetrics:
        """Calculate various metrics for the summary."""
        # Calculate ROUGE scores
        rouge_scores = self.rouge_scorer.score(original_text, summary)
        rouge_dict = {
            'rouge1': rouge_scores['rouge1'].fmeasure,
            'rouge2': rouge_scores['rouge2'].fmeasure,
            'rougeL': rouge_scores['rougeL'].fmeasure
        }
        
        # Calculate other metrics
        coherence_score = self._calculate_coherence(summary)
        readability_score = textstat.flesch_reading_ease(summary) / 100  # Normalize to 0-1
        compression_ratio = len(summary.split()) / len(original_text.split())
        coverage_score = self._calculate_coverage(original_text, summary)
        
        return SummaryMetrics(
            rouge_scores=rouge_dict,
            coherence_score=coherence_score,
            readability_score=readability_score,
            compression_ratio=compression_ratio,
            coverage_score=coverage_score
        )

    def _calculate_coherence(self, text: str) -> float:
        """Calculate coherence score based on sentence similarity."""
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            return 1.0
            
        embeddings = self.sentence_transformer.encode(sentences)
        similarities = [
            np.dot(embeddings[i], embeddings[i + 1]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
            ) for i in range(len(embeddings) - 1)
        ]
        return float(np.mean(similarities))

    def _calculate_coverage(self, original: str, summary: str) -> float:
        """Calculate what proportion of original entities are covered in summary."""
        original_entities = set(ent.text.lower() for ent in self.nlp(original).ents)
        summary_entities = set(ent.text.lower() for ent in self.nlp(summary).ents)
        
        if not original_entities:
            return 1.0
            
        return len(summary_entities & original_entities) / len(original_entities)

    def summarize(self, text: str, max_length: int = 150) -> Tuple[str, SummaryMetrics]:
        """Main method to generate summary and calculate metrics."""
        # Preprocess text
        cleaned_text = self.preprocess_text(text)
        
        # Generate summary
        summary = self.generate_summary(cleaned_text, max_length)
        
        # Calculate metrics
        metrics = self.calculate_metrics(text, summary)
        
        return summary, metrics
    
def main():
    # Usage example
    summarizer = OptimizedSummarizer()
    
    text = """Sample Network Vulnerability Assessment Report sales purplesec.us 1. Executive Summary The purpose of this vulnerability scan is to gather data on Windows and third-party software patch levels on hosts in the SAMPLE-INC domain in the 00.00.00.0 01 subnet. Of the 300 hosts identified by SAMPLE- INC, 100 systems were found to be active and were scanned. 2. Scan Results The raw scan results will be provided upon delivery. 3. Our Findings The results from the credentialed patch audit are listed below. It is important to note that not all identified hosts were able to be scanned during this assessment of the 300 hosts identified as belonging to the SAMPLE-INC domain, only 100 were successfully scanned. In addition, some of the hosts that were successfully scanned were not included in the host list provided. 4. Risk Assessment This report identifies security risks that could have significant impact on mission-critical applications used for day-to-day business operations. Critical Severity High Severity Medium Severity Low Severity 286 171 116 0 Critical Severity Vulnerability 286 were unique critical severity vulnerabilities. Critical vulnerabilities require immediate attention. They are relatively easy for attackers to exploit and may provide them with full control of the affected systems. A table of the top critical severity vulnerabilities is provided below: PLUGIN NAME DESCRIPTION SOLUTION COUNT The version of Firefox installed on the Upgrade to Mozilla remote Windows host is prior to 65.0. It is Mozilla Firefox 65.0 Firefox version 65.0 or 22 therefore affected by multiple vulnerabilities later. as referenced in the mfsa2019-01 advisory. According to its version there is at least one Mozilla Foundation unsupported Mozilla application (Firefox Upgrade to a version Unsupported Thunderbird and or SeaMonkey) installed that is currently 16 Application Detection on the remote host. This version of the supported. software is no longer actively maintained. 2 P age sales purplesec.us 5. Recommendations in this report are based on the available findings from the credentialed patch audit. Vulnerability scanning is only one tool to assess the security posture of a network. The results should not be interpreted as definitive measurement of the security posture of the SAMPLE-INC network. Other elements used to assess the current security posture would include policy review, a review of internal security controls and procedures, or internal red teaming penetration testing. Remediation Taking the following actions across all hosts will resolve 96 of the vulnerabilities on the network: ACTION TO TAKE VULNS HOSTS Mozilla Firefox 65.0: Upgrade to Mozilla Firefox version 65.0 or later. 82 3 Adobe Acrobat 10.1.15 11.0.12 2015.006.30060 2015.008.20082 Multiple Vulnerabilities (APSB15-24) : Upgrade to Adobe Acrobat 10.1.16 11.0.13 16 10 2015.006.30094 2015.009.20069 or later. Oracle Java SE 1.7.x 1.7.0_211 1.8.x 1.8.0_201 1.11.x 1.11.0_2 Multiple Vulnerabilities (January 2019 CPU) : Upgrade to Oracle JDK JRE 11 Update 2, 8 7 6 Update 201 7 Update 211 or later. If necessary, remove any affected versions. Adobe AIR 22.0.0.153 Android Applications Runtime Analytics MitM (APSB16-31) : 8 3 Upgrade to Adobe AIR version 23.0.0.257 or later. 4 P age sales purplesec.us"""
    
    summary, metrics = summarizer.summarize(text)
    print(f"Summary: {summary}\n")
    print(f"Metrics: {metrics}")

if __name__ == "__main__":
    main()