"""
Utility functions to convert Word documents and PDFs to Editor.js blocks format.
"""
import re
import uuid
from typing import Dict, Any
from django.utils import timezone

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def extract_text_from_docx(file) -> str:
    """
    Extract text from a Word document (.docx file).
    
    Args:
        file: Django uploaded file object
        
    Returns:
        str: Extracted text content
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx is not installed. Please install it: pip install python-docx")
    
    doc = Document(file)
    paragraphs = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    
    return "\n".join(paragraphs)


def extract_text_from_pdf(file) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file: Django uploaded file object
        
    Returns:
        str: Extracted text content
    """
    if not PDF_AVAILABLE:
        raise ImportError("PyMuPDF is not installed. Please install it: pip install PyMuPDF")
    
    # Read file content
    file.seek(0)  # Reset file pointer
    pdf_bytes = file.read()
    
    # Open PDF with PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_parts = []
    
    for page in doc:
        text = page.get_text()
        if text.strip():
            text_parts.append(text.strip())
    
    doc.close()
    return "\n\n".join(text_parts)


def text_to_editorjs_blocks(text: str) -> Dict[str, Any]:
    """
    Convert plain text to Editor.js blocks format.
    Intelligently detects headings, lists, and paragraphs.
    
    Args:
        text: Plain text content
        
    Returns:
        dict: Editor.js blocks format
    """
    if not text or not text.strip():
        return {
            "time": int(timezone.now().timestamp() * 1000),
            "blocks": [],
            "version": "2.28.2"
        }
    
    lines = text.split('\n')
    blocks = []
    current_list_items = []
    current_list_style = None
    
    def flush_list():
        """Add accumulated list items as a list block."""
        nonlocal current_list_items, current_list_style
        if current_list_items:
            blocks.append({
                "id": str(uuid.uuid4()),
                "type": "list",
                "data": {
                    "style": current_list_style or "unordered",
                    "items": current_list_items
                }
            })
            current_list_items = []
            current_list_style = None
    
    for line in lines:
        line = line.strip()
        if not line:
            # Empty line - flush any pending list
            flush_list()
            continue
        
        # Detect headings (lines that are short and end without punctuation, or start with #)
        # Heading patterns:
        # 1. Lines starting with # (Markdown style)
        # 2. Short lines (less than 80 chars) that are all caps or title case
        # 3. Lines that look like section headers (short, no ending punctuation)
        
        if line.startswith('#'):
            # Markdown-style heading
            flush_list()
            level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('#').strip()
            if heading_text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {
                        "text": heading_text,
                        "level": min(level, 6)  # Cap at level 6
                    }
                })
            continue
        
        # Detect list items (lines starting with -, *, •, or numbers)
        list_match = re.match(r'^([-*•]|\d+[.)])\s+(.+)$', line)
        if list_match:
            flush_list()  # Flush previous list if style changes
            marker = list_match.group(1)
            item_text = list_match.group(2).strip()
            
            if item_text:
                # Determine list style
                if marker in ['-', '*', '•']:
                    current_list_style = "unordered"
                else:
                    current_list_style = "ordered"
                
                current_list_items.append(item_text)
            continue
        
        # If we have accumulated list items and hit a non-list line, flush the list
        if current_list_items:
            flush_list()
        
        # Detect if line looks like a heading (short, title case, no ending punctuation)
        is_short = len(line) < 80
        is_title_case = line.istitle() or line.isupper()
        no_ending_punct = not line.rstrip().endswith(('.', '!', '?', ':', ';'))
        
        if is_short and (is_title_case or no_ending_punct) and len(line.split()) <= 10:
            # Likely a heading
            flush_list()
            blocks.append({
                "id": str(uuid.uuid4()),
                "type": "header",
                "data": {
                    "text": line,
                    "level": 2  # Default to H2
                }
            })
        else:
            # Regular paragraph
            flush_list()
            blocks.append({
                "id": str(uuid.uuid4()),
                "type": "paragraph",
                "data": {
                    "text": line
                }
            })
    
    # Flush any remaining list items
    flush_list()
    
    # If no blocks were created, create at least one paragraph with the text
    if not blocks:
        blocks.append({
            "id": str(uuid.uuid4()),
            "type": "paragraph",
            "data": {
                "text": text.strip()
            }
        })
    
    return {
        "time": int(timezone.now().timestamp() * 1000),
        "blocks": blocks,
        "version": "2.28.2"
    }


def convert_document_to_blocks(file) -> Dict[str, Any]:
    """
    Convert a Word document or PDF file to Editor.js blocks format.
    
    Args:
        file: Django uploaded file object
        
    Returns:
        dict: Editor.js blocks format with extracted content
        
    Raises:
        ValueError: If file type is not supported
        ImportError: If required libraries are not installed
    """
    filename = file.name.lower()
    
    # Extract text based on file type
    if filename.endswith('.docx'):
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx is not installed. Please install it: pip install python-docx")
        text = extract_text_from_docx(file)
    elif filename.endswith('.pdf'):
        if not PDF_AVAILABLE:
            raise ImportError("PyMuPDF is not installed. Please install it: pip install PyMuPDF")
        text = extract_text_from_pdf(file)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Supported types: .docx, .pdf")
    
    # Convert text to Editor.js blocks
    return text_to_editorjs_blocks(text)




