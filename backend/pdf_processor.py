import pdfplumber
import re
from typing import Tuple, Optional

def extract_company_name(text: str) -> Optional[str]:
    """Extract company name from the first page of SBC document"""
    # Look for company name patterns in the beginning of the document
    lines = text.split('\n')[:30]  # Check first 30 lines
    
    # Common patterns for company names in SBC documents
    patterns = [
        r'([A-Za-z\s]+(?:Company|Corp|Corporation|Inc|LLC|Group))\s+Employee\s+Benefits',
        r'([A-Za-z\s]+)\s+Employee\s+Benefits\s+Plan',
        r'^([A-Za-z\s]+(?:Company|Corp|Corporation|Inc|LLC))',
        r'([A-Za-z\s]+(?:Delivery|Service|Solutions|Systems))\s+Company',
        r'([A-Za-z\s]+)\s+Benefits\s+Plan',
        r'([A-Za-z\s]+Delivery\s+Company)',  # Specific pattern for Fasttrack Delivery Company
        r'([A-Za-z\s]+)\s+Employee\s+Benefits\s+Plan:\s+Plan\s+\d+',  # Pattern with plan number
    ]
    
    for line in lines:
        line = line.strip()
        if len(line) > 5:  # Skip very short lines
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    company_name = match.group(1).strip()
                    # Clean up the company name
                    company_name = re.sub(r'\s+', ' ', company_name)
                    if len(company_name) > 3:  # Ensure it's not too short
                        return company_name
    
    # Fallback: look for "Company" in any line
    for line in lines:
        line = line.strip()
        if 'Company' in line and len(line) > 10:
            # Extract the part before "Company"
            company_match = re.search(r'([A-Za-z\s]+)\s+Company', line, re.IGNORECASE)
            if company_match:
                return company_match.group(1).strip() + ' Company'
    
    # Final fallback: return the first substantial line as company name
    for line in lines:
        line = line.strip()
        if len(line) > 10 and not line.startswith('Summary') and not line.startswith('Coverage'):
            return line
    
    return "Unknown Company"

def extract_coverage_answers(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract answers to the two key questions"""
    
    # Question 1: Minimum Essential Coverage
    essential_coverage_patterns = [
        r'Does\s+this\s+plan\s+provide\s+Minimum\s+Essential\s+Coverage\?\s*([Yes|No]+)',
        r'Minimum\s+Essential\s+Coverage\?\s*([Yes|No]+)',
        r'Essential\s+Coverage[:\s]*([Yes|No]+)',
        r'Minimum\s+Essential[:\s]*([Yes|No]+)',
        r'Essential\s+Coverage\?\s*([Yes|No]+)',
        r'Minimum\s+Essential\s+Coverage[:\s]*([Yes|No]+)',
        r'Essential\s+Coverage[^.]*?([Yes|No])',  # More flexible pattern
        r'Minimum\s+Essential[^.]*?([Yes|No])',   # More flexible pattern
    ]
    
    # Question 2: Minimum Value Standards
    value_standards_patterns = [
        r'Does\s+this\s+plan\s+meet\s+the\s+Minimum\s+Value\s+Standards\?\s*([Yes|No]+)',
        r'Minimum\s+Value\s+Standards\?\s*([Yes|No]+)',
        r'Value\s+Standards[:\s]*([Yes|No]+)',
        r'Minimum\s+Value[:\s]*([Yes|No]+)',
        r'Value\s+Standards\?\s*([Yes|No]+)',
        r'Minimum\s+Value\s+Standards[:\s]*([Yes|No]+)',
        r'Value\s+Standards[^.]*?([Yes|No])',     # More flexible pattern
        r'Minimum\s+Value[^.]*?([Yes|No])',       # More flexible pattern
    ]
    
    essential_coverage_answer = None
    value_standards_answer = None
    
    # Search for answers
    for pattern in essential_coverage_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            essential_coverage_answer = match.group(1).strip()
            break
    
    for pattern in value_standards_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value_standards_answer = match.group(1).strip()
            break
    
    # If not found with specific patterns, try broader search
    if not essential_coverage_answer:
        # Look for "Yes" or "No" near "Essential Coverage" text
        essential_matches = re.findall(r'Essential\s+Coverage.*?([Yes|No])', text, re.IGNORECASE | re.DOTALL)
        if essential_matches:
            essential_coverage_answer = essential_matches[0].strip()
        else:
            # Try to find "Yes" or "No" in the same paragraph as "Essential Coverage"
            essential_paragraphs = re.findall(r'Essential\s+Coverage[^.]*\.', text, re.IGNORECASE | re.DOTALL)
            for paragraph in essential_paragraphs:
                yes_no_match = re.search(r'\b([Yes|No])\b', paragraph, re.IGNORECASE)
                if yes_no_match:
                    essential_coverage_answer = yes_no_match.group(1).strip()
                    break
    
    if not value_standards_answer:
        # Look for "Yes" or "No" near "Value Standards" text
        value_matches = re.findall(r'Value\s+Standards.*?([Yes|No])', text, re.IGNORECASE | re.DOTALL)
        if value_matches:
            value_standards_answer = value_matches[0].strip()
        else:
            # Try to find "Yes" or "No" in the same paragraph as "Value Standards"
            value_paragraphs = re.findall(r'Value\s+Standards[^.]*\.', text, re.IGNORECASE | re.DOTALL)
            for paragraph in value_paragraphs:
                yes_no_match = re.search(r'\b([Yes|No])\b', paragraph, re.IGNORECASE)
                if yes_no_match:
                    value_standards_answer = yes_no_match.group(1).strip()
                    break
    
    return essential_coverage_answer, value_standards_answer

def process_sbc_pdf(file_path: str) -> dict:
    """Process SBC PDF and extract required information"""
    try:
        with pdfplumber.open(file_path) as pdf:
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
        # Extract company name (usually on first page)
        first_page_text = ""
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) > 0:
                first_page_text = pdf.pages[0].extract_text() or ""
        
        company_name = extract_company_name(first_page_text)
        
        # Extract answers to coverage questions
        essential_coverage, value_standards = extract_coverage_answers(full_text)
        
        # Simply use the extracted answers as penalties (no inference needed)
        penalty_a = essential_coverage if essential_coverage else "Unknown"
        penalty_b = value_standards if value_standards else "Unknown"
        

        
        return {
            'success': True,
            'company_name': company_name,
            'essential_coverage': essential_coverage,
            'value_standards': value_standards,
            'penalty_a': penalty_a,
            'penalty_b': penalty_b
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
