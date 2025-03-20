import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Import components
from extractors.text_extractor import TextExtractor
from backend.models.intro import generate_audit_report, save_report_to_advanced_json, load_json_data  # Use load_json_data for accessing saved file

class DocumentProcessor:
    def __init__(self):
        self.text_extractor = TextExtractor()

    async def process_document(self, pdf_path):
        """
        Main document processing workflow:
        1. Extract text from PDF
        2. Generate cybersecurity report
        3. Save results in a structured JSON format
        4. Access saved file and display its contents
        """
        try:
            # Step 1: Extract text from PDF
            print(f"Extracting text from: {pdf_path}")
            extracted_text = self.text_extractor.extract(pdf_path)
            print("Extracted text:", extracted_text[:500])  # Display a snippet of extracted text for debug
            
            if len(extracted_text.strip()) == 0:
                raise ValueError("No text could be extracted from the provided PDF file.")

            # Step 2: Generate cybersecurity report
            print("Generating cybersecurity report...")
            report = generate_audit_report(extracted_text)
            print("Generated report:", report)

            if "An error occurred" in report:
                raise RuntimeError("Error while generating the report: " + report)

            # Step 3: Save the report in structured JSON format and get the saved file path
            report_file_path = self._save_report(report, pdf_path)
           
            # Step 4: Access saved file and load data
            print("Accessing saved report...")
            saved_data = load_json_data(report_file_path)

            # Display the saved JSON data
            if saved_data:
                print("\n--- SAVED REPORT CONTENTS ---")
                print(json.dumps(saved_data, indent=4))
            else:
                print("Could not access saved JSON file content.")

            return saved_data

        except Exception as e:
            print(f"Processing error: {e}")
            return {"error": str(e)}

    def _save_report(self, report, pdf_path):
        """
        Save processing results to structured JSON and return the saved file path
        """
        filename = Path(pdf_path).stem  # Get the name of the PDF file (minus extension)
        report_file = f"{filename}_cybersecurity_report.json"

        # Save the report in structured format
        saved_file_path = save_report_to_advanced_json(report, filename=report_file)

        print(f"Cybersecurity report saved to: {saved_file_path}")
        return saved_file_path  # Return the saved filepath to be used later


async def main():
    # Update this with your own sample PDF path
    pdf_path = "sample/sample.pdf"  # Replace with the actual path to your PDF

    processor = DocumentProcessor()

    print("Starting document processing...")
    result = await processor.process_document(pdf_path)

    # Display the final result or error
    if result and "error" not in result:
        print("\n--- PROCESSING COMPLETED SUCCESSFULLY ---")
        print(json.dumps(result, indent=4))
    elif "error" in result:
        print("\n--- ERROR ---")
        print(result["error"])


if __name__ == "__main__":
    asyncio.run(main())