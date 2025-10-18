"""
PDF Text Extraction Service
Handles text extraction from PDF files for audiobook generation
"""

import logging
from typing import Optional
import PyPDF2
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFService:
    """Service for extracting text from PDF files"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if failed
        """
        try:
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return None
            
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    logger.warning("PDF is encrypted, attempting to decrypt with empty password")
                    try:
                        pdf_reader.decrypt("")
                    except Exception as e:
                        logger.error(f"Failed to decrypt PDF: {str(e)}")
                        return None
                
                text = ""
                total_pages = len(pdf_reader.pages)
                logger.info(f"Processing {total_pages} pages from PDF")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        logger.info(f"Extracted text from page {page_num + 1}/{total_pages}")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                        continue
                
                if text.strip():
                    logger.info(f"Successfully extracted {len(text)} characters from PDF")
                    return text.strip()
                else:
                    logger.warning("No text could be extracted from PDF")
                    return None
                    
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def clean_extracted_text(self, text: str) -> str:
        """
        Clean and format extracted text for better audiobook generation
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize line breaks
        import re
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newlines (paragraph breaks)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove page numbers and headers/footers (simple patterns)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up common PDF extraction artifacts
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\/]', '', text)
        
        return text.strip()
    
    def get_pdf_info(self, pdf_path: str) -> Optional[dict]:
        """
        Get basic information about a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF info or None if failed
        """
        try:
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                return None
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info = {
                    'pages': len(pdf_reader.pages),
                    'file_size': pdf_file.stat().st_size,
                    'encrypted': pdf_reader.is_encrypted,
                    'title': None,
                    'author': None,
                    'subject': None
                }
                
                # Try to get metadata
                if pdf_reader.metadata:
                    info['title'] = pdf_reader.metadata.get('/Title')
                    info['author'] = pdf_reader.metadata.get('/Author')
                    info['subject'] = pdf_reader.metadata.get('/Subject')
                
                return info
                
        except Exception as e:
            logger.error(f"Error getting PDF info: {str(e)}")
            return None
