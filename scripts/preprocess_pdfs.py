#!/usr/bin/env python3
"""
PDF to Markdown Preprocessing Script for RAG

This script converts PDF documents to markdown files using the marker API endpoint.
The converted markdown files are stored in rag_data/processed/ for RAG integration.

Usage:
    python scripts/preprocess_pdfs.py
    python scripts/preprocess_pdfs.py --input-dir documents --output-dir rag_data/processed
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


class PDFPreprocessor:
    """Handles PDF to markdown conversion using marker API."""

    def __init__(
        self,
        api_url: str = "http://10.26.1.11:8701/analyze",
        input_dir: str = "documents",
        output_dir: str = "rag_data/processed"
    ):
        self.api_url = api_url
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.metadata_file = self.output_dir.parent / "metadata.json"

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_api_health(self) -> bool:
        """Check if the API is accessible."""
        try:
            health_url = self.api_url.replace("/analyze", "/health")
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"❌ API health check failed: {e}")
            return False

    def find_pdfs(self) -> List[Path]:
        """Find all PDF files in the input directory."""
        if not self.input_dir.exists():
            print(f"❌ Input directory not found: {self.input_dir}")
            return []

        pdfs = list(self.input_dir.glob("**/*.pdf"))
        print(f"📄 Found {len(pdfs)} PDF file(s) in {self.input_dir}")
        return pdfs

    def convert_pdf_to_markdown(self, pdf_path: Path) -> Optional[Dict]:
        """
        Convert a single PDF to markdown using the API.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing markdown content and metadata, or None if failed
        """
        print(f"\n🔄 Processing: {pdf_path.name}")

        try:
            with open(pdf_path, 'rb') as f:
                files = {'files': (pdf_path.name, f, 'application/pdf')}
                response = requests.post(
                    self.api_url,
                    files=files,
                    timeout=300  # 5 minute timeout for large PDFs
                )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully converted: {pdf_path.name}")
                return result
            else:
                print(f"❌ Failed to convert {pdf_path.name}: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return None

        except requests.RequestException as e:
            print(f"❌ Error converting {pdf_path.name}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error with {pdf_path.name}: {e}")
            return None

    def save_markdown(self, pdf_path: Path, api_response: Dict) -> Optional[Path]:
        """
        Save the converted markdown to a file.

        Args:
            pdf_path: Original PDF path
            api_response: Response from the API

        Returns:
            Path to saved markdown file, or None if failed
        """
        # Create markdown filename from PDF name
        md_filename = pdf_path.stem + ".md"
        output_path = self.output_dir / md_filename

        try:
            # Extract markdown content from API response
            # API returns: {"results": [{"file_name": "...", "content": "..."}]}
            content = None

            if isinstance(api_response, dict):
                # Check for results array (marker API format)
                if 'results' in api_response and isinstance(api_response['results'], list):
                    if len(api_response['results']) > 0:
                        first_result = api_response['results'][0]
                        if isinstance(first_result, dict) and 'content' in first_result:
                            content = first_result['content']
                # Direct content field
                elif 'content' in api_response:
                    content = api_response['content']
                # Direct markdown field
                elif 'markdown' in api_response:
                    content = api_response['markdown']

            # Fallback if no content found
            if content is None:
                print(f"⚠️  Warning: Unexpected API response format for {pdf_path.name}")
                content = json.dumps(api_response, indent=2)

            # Ensure content is a string
            if not isinstance(content, str):
                content = str(content)

            # Write markdown file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"💾 Saved markdown: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error saving markdown for {pdf_path.name}: {e}")
            return None

    def update_metadata(self, pdf_path: Path, md_path: Optional[Path], success: bool):
        """Update metadata file with processing information."""
        # Load existing metadata
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {"processed_files": []}

        # Add/update entry
        entry = {
            "pdf_file": str(pdf_path),
            "pdf_name": pdf_path.name,
            "markdown_file": str(md_path) if md_path else None,
            "success": success,
            "processed_at": datetime.now().isoformat(),
            "file_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0
        }

        # Remove old entry if exists
        metadata["processed_files"] = [
            f for f in metadata["processed_files"]
            if f.get("pdf_name") != pdf_path.name
        ]

        # Add new entry
        metadata["processed_files"].append(entry)
        metadata["last_updated"] = datetime.now().isoformat()
        metadata["total_processed"] = len(metadata["processed_files"])
        metadata["successful"] = sum(1 for f in metadata["processed_files"] if f["success"])

        # Save metadata
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, indent=2, fp=f)

    def process_all(self) -> Dict[str, int]:
        """
        Process all PDFs in the input directory.

        Returns:
            Dictionary with statistics (total, successful, failed)
        """
        print("=" * 60)
        print("PDF to Markdown Preprocessing Pipeline")
        print("=" * 60)
        print(f"Input directory:  {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"API endpoint:     {self.api_url}")
        print("=" * 60)

        # Check API health
        if not self.check_api_health():
            print("\n⚠️  Warning: API health check failed. Proceeding anyway...")
        else:
            print("✅ API is healthy")

        # Find PDFs
        pdfs = self.find_pdfs()
        if not pdfs:
            print("\n⚠️  No PDF files found to process.")
            return {"total": 0, "successful": 0, "failed": 0}

        # Process each PDF
        stats = {"total": len(pdfs), "successful": 0, "failed": 0}

        for pdf_path in pdfs:
            # Convert to markdown
            api_response = self.convert_pdf_to_markdown(pdf_path)

            if api_response:
                # Save markdown
                md_path = self.save_markdown(pdf_path, api_response)

                if md_path:
                    stats["successful"] += 1
                    self.update_metadata(pdf_path, md_path, True)
                else:
                    stats["failed"] += 1
                    self.update_metadata(pdf_path, None, False)
            else:
                stats["failed"] += 1
                self.update_metadata(pdf_path, None, False)

        # Print summary
        print("\n" + "=" * 60)
        print("Processing Complete!")
        print("=" * 60)
        print(f"Total PDFs:       {stats['total']}")
        print(f"✅ Successful:    {stats['successful']}")
        print(f"❌ Failed:        {stats['failed']}")
        print(f"\nMarkdown files saved to: {self.output_dir}")
        print(f"Metadata saved to: {self.metadata_file}")
        print("=" * 60)

        return stats


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert PDF documents to markdown for RAG integration"
    )
    parser.add_argument(
        '--input-dir',
        default='documents',
        help='Directory containing PDF files (default: documents)'
    )
    parser.add_argument(
        '--output-dir',
        default='rag_data/processed',
        help='Directory to save markdown files (default: rag_data/processed)'
    )
    parser.add_argument(
        '--api-url',
        default='http://10.26.1.11:8701/analyze',
        help='API endpoint URL (default: http://10.26.1.11:8701/analyze)'
    )

    args = parser.parse_args()

    # Create preprocessor and run
    preprocessor = PDFPreprocessor(
        api_url=args.api_url,
        input_dir=args.input_dir,
        output_dir=args.output_dir
    )

    stats = preprocessor.process_all()

    # Exit with error code if any failures
    if stats["failed"] > 0:
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
