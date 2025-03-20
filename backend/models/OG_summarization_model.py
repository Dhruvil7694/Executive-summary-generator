from transformers import T5ForConditionalGeneration, T5Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize
import re
import spacy
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import networkx as nx
import pandas as pd

class SummarizationModel:
    def __init__(self, model_name="t5-small", local_path="./models/t5_model"):
        self.local_path = local_path
        self.model_name = model_name

        # Load the T5 model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

        # Save locally (optional)
        self.tokenizer.save_pretrained(local_path)
        self.model.save_pretrained(local_path)

        # Load spaCy model for Named Entity Recognition
        self.nlp = spacy.load("en_core_web_sm")

        # Load Sentence-BERT model for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_main_idea(self, text, title):
        if title:
            return title.strip()
        
        # Fallback to extracting keywords from text
        doc = self.nlp(text)
        keywords = [chunk.text for chunk in doc.noun_chunks]
        return ' '.join(set(keywords))[:100]  # Return unique keywords as main idea

    def preprocess_text(self, text):
        """
        Advanced text cleaning to handle special characters, abbreviations, and typos.
        """
        text = text.lower()
        text = re.sub(r'http\S+|www\.\S+', '', text)  # Remove URLs
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)  # Remove special characters

        # Correct common typos (example replacements)
        corrections = {
            "th": "the",
            "recieve": "receive",
            "adress": "address"
        }

        for typo, correction in corrections.items():
            text = re.sub(r'\b' + typo + r'\b', correction, text)

        doc = self.nlp(text)
        words = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]

        return ' '.join(words)

    def extract_key_sentences(self, text, num_sentences=5):
        """
        Extract key sentences using BERT embeddings and TextRank.
        """
        sentences = sent_tokenize(text)
        unique_sentences = list(set(sentences))  # Remove duplicates

        if len(unique_sentences) < num_sentences:
            return unique_sentences

        # Create a similarity matrix using BERT embeddings
        embeddings = self.sentence_model.encode(unique_sentences)
        similarity_matrix = np.inner(embeddings, embeddings)

        # Create a graph from the similarity matrix
        nx_graph = nx.from_numpy_array(similarity_matrix)

        # Use PageRank algorithm to rank sentences
        scores = nx.pagerank(nx_graph)

        # Get indices of top sentences based on PageRank scores
        top_sentence_indices = sorted(scores, key=scores.get, reverse=True)[:num_sentences]

        return [unique_sentences[i] for i in sorted(top_sentence_indices)]

    def summarize(self, text, title=None, max_length=200, min_length=50):
        """
        Summarize the given text using a hybrid approach with structured output.
        """
        # Step 1: Extract main idea
        main_idea = self.extract_main_idea(text, title)

        # Step 2: Extract key sentences (Extractive Summarization)
        key_sentences = self.extract_key_sentences(text)

        # Combine key sentences into a single context for abstractive summarization
        extractive_summary_text = ' '.join(key_sentences)

        # Step 3: Generate an abstractive summary from the extractive summary
        inputs = self.tokenizer.encode(
            "summarize: " + extractive_summary_text,
            return_tensors="pt",
            max_length=1024,
            truncation=True,
            padding=True
        )

        summary_ids = self.model.generate(
            inputs,
            max_length=max_length,
            min_length=min_length,
            length_penalty=2.0,
            num_beams=5,
            early_stopping=True
        )

        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        # Step 4: Enhance the summary with structured formatting
        return self.format_summary(main_idea, summary)

    def format_summary(self, main_idea, summary):
        """
        Format the summary with the main idea and structured paragraphs.
        """
        if not summary:
            return ""

        # Split summary into key points
        summary_points = summary.split('. ')
        
        formatted_summary = f"Main Idea: {main_idea}\n\nSummary Points:\n"

        for point in summary_points:
            if point.strip():
                formatted_summary += f"{point.strip()}.\n"

        return formatted_summary.strip()

    def enhance_summary(self, summary):
        """
        Enhance the summary with structured formatting in paragraphs and bullet points where relevant.
        """
        if not summary:
            return ""

        sentences = sent_tokenize(summary)
        
        bullet_points = []
        
        for sentence in sentences:
            if any(word in sentence.lower() for word in ["train", "use", "apply", "recommend"]):
                bullet_points.append(f"- {sentence.strip()}")
            else:
                bullet_points.append(sentence.strip())

        return '\n\n'.join(bullet_points)

    def feedback_loop(self, user_feedback):
        feedback_file = "feedback_data.json"

        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                feedback_data = json.load(f)
                feedback_data.append(user_feedback)  # Append new feedback

                with open(feedback_file, 'w') as f:
                    json.dump(feedback_data, f, indent=4)

                self.analyze_feedback(feedback_data)  # Analyze updated feedback

    def analyze_feedback(self, feedback_data):
         if not feedback_data:
             print("No feedback data available for analysis.")
             return

         total_rating = sum(entry.get('rating', 0) for entry in feedback_data)
         average_rating = total_rating / len(feedback_data) if feedback_data else 0
         print(f"Average Rating: {average_rating:.2f} based on {len(feedback_data)} feedback entries.")

    def summarize_numerical_results(self, results):
         """
         Format numerical results into a table.
         """
         df = pd.DataFrame(results)
         
         return df.to_string(index=False)  # Convert DataFrame to string representation

    def segment_findings(self, findings):
         """
         Segment findings into logical categories.
         """
         categorized_findings = {
             "Introduction": [],
             "Key Findings": [],
             "Methodology": [],
             "Results": [],
             "Conclusion": []
         }

         for finding in findings:
             category = finding.get('category', 'General')
             if category in categorized_findings:
                 categorized_findings[category].append(finding['text'])

         return categorized_findings

