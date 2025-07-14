"""
PDF processing utilities for extracting content from PDF files.
"""
import io
import logging
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
from src.domain.models.llm_selection import ProcessedFileContent
from src.utils.constants import ALLOWED_DOCUMENT_EXTENSIONS

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Utility class for processing PDF files.
    """
    
    # Maximum file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file to validate
            
        Raises:
            HTTPException: If file validation fails
        """
        # Check if file is provided
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if f".{file_extension}" not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed types: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
            )
        
        # Check file size (this is a rough check, actual size check happens during read)
        if hasattr(file, 'size') and file.size and file.size > PDFProcessor.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {PDFProcessor.MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    @staticmethod
    async def extract_pdf_content(file: UploadFile) -> ProcessedFileContent:
        """
        Extract text content from PDF file.
        
        Args:
            file: Uploaded PDF file
            
        Returns:
            ProcessedFileContent with extracted text and metadata
            
        Raises:
            HTTPException: If PDF processing fails
        """
        try:
            # Validate file first
            PDFProcessor.validate_file(file)
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Check actual file size
            if file_size > PDFProcessor.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large. Maximum size: {PDFProcessor.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Reset file pointer and create PDF reader
            file_stream = io.BytesIO(file_content)
            pdf_reader = PdfReader(file_stream)
            
            # Extract text from all pages
            extracted_text = ""
            page_count = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                except Exception as page_error:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {page_error}")
                    continue
            
            # Clean up extracted text
            extracted_text = extracted_text.strip()
            
            if not extracted_text:
                raise HTTPException(
                    status_code=400, 
                    detail="No text content could be extracted from the PDF file"
                )
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF: {file.filename}")
            
            return ProcessedFileContent(
                filename=file.filename,
                content=extracted_text,
                file_type="pdf",
                file_size=file_size,
                page_count=page_count
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error processing PDF file {file.filename}: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to process PDF file: {str(e)}"
            )
        finally:
            # Reset file pointer for potential future use
            if hasattr(file, 'seek'):
                try:
                    await file.seek(0)
                except:
                    pass
    
    @staticmethod
    def generate_file_insights_prompt(file_content: ProcessedFileContent, user_query: Optional[str] = None) -> str:
        """
        Generate appropriate prompt for LLM based on file content and optional query.
        
        Args:
            file_content: Processed file content
            user_query: Optional user query
            
        Returns:
            Formatted prompt for LLM
        """
        if user_query and user_query.strip():
            # User provided both file and query
            prompt = f"""I have uploaded a {file_content.file_type.upper()} file named "{file_content.filename}" ({file_content.page_count} pages, {file_content.file_size} bytes) and have a specific question about it.

File Content:
{file_content.content}

My Question: {user_query.strip()}

Please analyze the file content and provide a comprehensive answer to my question based on the information in the document."""
        else:
            # Only file provided, generate insights
            prompt = f"""I have uploaded a {file_content.file_type.upper()} file named "{file_content.filename}" ({file_content.page_count} pages, {file_content.file_size} bytes). Please analyze this document and provide comprehensive insights.

File Content:
{file_content.content}

Please provide:
1. A summary of the document's main content and purpose
2. Key topics, themes, or subjects covered
3. Important findings, conclusions, or recommendations (if any)
4. Notable data, statistics, or facts mentioned
5. The document's structure and organization
6. Any action items, next steps, or implications mentioned
7. Overall assessment of the document's significance or value

Provide a detailed and insightful analysis that would help someone understand the essence and importance of this document."""
        
        return prompt
    
    @staticmethod
    def summarize_file_for_history(file_content: ProcessedFileContent) -> str:
        """
        Create a concise summary of file content for conversation history.
        
        Args:
            file_content: Processed file content
            
        Returns:
            Concise summary for history storage
        """
        # Truncate content for history (first 500 chars + metadata)
        content_preview = file_content.content[:500]
        if len(file_content.content) > 500:
            content_preview += "... [content truncated]"
        
        return f"[FILE: {file_content.filename} ({file_content.page_count} pages)] {content_preview}" 