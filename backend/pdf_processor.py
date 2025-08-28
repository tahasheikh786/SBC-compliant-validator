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

def extract_plan_type(text: str) -> str:
    """Extract plan type from SBC text"""
    text_lower = text.lower()
    if 'indemnity' in text_lower:
        return 'Indemnity Plan'
    elif 'hmo' in text_lower:
        return 'HMO Plan'
    elif 'ppo' in text_lower:
        return 'PPO Plan'
    elif 'pos' in text_lower:
        return 'POS Plan'
    elif 'hdhp' in text_lower or 'high deductible' in text_lower:
        return 'High Deductible Health Plan'
    return 'Health Plan'

def extract_deductible_info(text: str) -> dict:
    """Extract comprehensive deductible information"""
    deductible_info = {
        'individual': 'Not specified',
        'family': 'Not specified',
        'formatted': 'structured deductible'
    }
    
    # Pattern for individual deductible
    individual_patterns = [
        r'\$([0-9,]+)\s+individual.*?deductible',
        r'deductible.*?\$([0-9,]+)\s+individual',
        r'\$([0-9,]+)\s+individual'
    ]
    
    # Pattern for family deductible  
    family_patterns = [
        r'\$([0-9,]+)\s+family.*?deductible',
        r'deductible.*?\$([0-9,]+)\s+family',
        r'\$([0-9,]+)\s+family'
    ]
    
    for pattern in individual_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            deductible_info['individual'] = f"${match.group(1)}"
            break
    
    for pattern in family_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            deductible_info['family'] = f"${match.group(1)}"
            break
    
    # Create formatted string
    if deductible_info['individual'] != 'Not specified' or deductible_info['family'] != 'Not specified':
        if deductible_info['individual'] != 'Not specified' and deductible_info['family'] != 'Not specified':
            deductible_info['formatted'] = f"{deductible_info['individual']} individual / {deductible_info['family']} family deductible"
        elif deductible_info['individual'] != 'Not specified':
            deductible_info['formatted'] = f"{deductible_info['individual']} individual deductible"
        elif deductible_info['family'] != 'Not specified':
            deductible_info['formatted'] = f"{deductible_info['family']} family deductible"
    
    return deductible_info

def extract_coverage_period(text: str) -> str:
    """Extract coverage period from SBC"""
    period_patterns = [
        r'Coverage Period:\s*([0-9/\-\s]+)',
        r'Plan Year:\s*([0-9/\-\s]+)',
        r'Coverage for:\s*([0-9/\-\s]+)'
    ]
    
    for pattern in period_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            period = match.group(1).strip()
            if len(period) > 5:
                return period
    
    return 'annual coverage period'

def extract_out_of_pocket_limit(text: str) -> str:
    """Extract out-of-pocket limit information"""
    oop_patterns = [
        r'out-of-pocket.?$([0-9,]+)\s+individual.?$([0-9,]+)\s+family',
        r'$([0-9,]+)\s+individual.?$([0-9,]+)\s+family.?out-of-pocket',
        r'out-of-pocket.*?$([0-9,]+)'
    ]
    
    for pattern in oop_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) >= 2:
                return f"${match.group(1)} individual / ${match.group(2)} family"
            else:
                return f"${match.group(1)}"
    
    return "specified limits"

def generate_penalty_explanation(company_name: str, essential_coverage: str, value_standards: str, full_text: str) -> dict:
    """Generate intelligent, contextual explanations for penalty compliance"""
    
    # Extract contextual information from the SBC
    plan_type = extract_plan_type(full_text)
    deductible_info = extract_deductible_info(full_text)
    coverage_period = extract_coverage_period(full_text)
    oop_limit = extract_out_of_pocket_limit(full_text)
    
    # Current year penalty amounts (2024-2025)
    current_employer_penalty = "$4,320"  # 2024 4980H penalty amount
    
    explanations = {
        'penalty_a_explanation': '',
        'penalty_b_explanation': ''
    }
    
    # Generate Minimum Essential Coverage explanation
    if essential_coverage and essential_coverage.lower() == 'yes':
        explanations['penalty_a_explanation'] = f"""✅ MINIMUM ESSENTIAL COVERAGE QUALIFIED

{company_name}'s {plan_type} meets all ACA requirements for Minimum Essential Coverage.

KEY QUALIFICATIONS:
• Comprehensive health benefits including preventive care at no cost
• Covers all 10 Essential Health Benefits required by ACA
• Active during {coverage_period}
• Includes prescription drug coverage and emergency services
• Meets federal standards for health insurance coverage

COMPLIANCE IMPACT:
• Employees enrolled in this plan are exempt from individual mandate penalties
• Plan satisfies ACA coverage requirements for tax purposes
• Qualifies for premium tax credit eligibility determinations

TECHNICAL DETAILS:
• Plan Structure: {plan_type} with {deductible_info['formatted']}
• Out-of-Pocket Protection: {oop_limit} maximum annual limits
• Coverage Level: Meets actuarial value and benefit design standards"""
    else:
        explanations['penalty_a_explanation'] = f"""❌ MINIMUM ESSENTIAL COVERAGE NOT QUALIFIED

{company_name}'s plan does NOT meet ACA Minimum Essential Coverage standards.

COMPLIANCE RISKS:
• Employees may face individual mandate penalties (varies by state)
• Plan may not qualify for premium tax credit interactions
• Potential tax reporting complications for employees

RECOMMENDED ACTIONS:
• Review plan benefits against ACA essential health benefit categories
• Consider supplemental coverage options
• Consult with benefits advisor for compliance strategies
• Evaluate plan upgrade options for next enrollment period

CURRENT GAPS:
• May lack required essential health benefit categories
• Could have insufficient preventive care coverage
• Possible limitations in prescription drug benefits"""
    
    # Generate Minimum Value Standards explanation
    if value_standards and value_standards.lower() == 'yes':
        explanations['penalty_b_explanation'] = f"""✅ MINIMUM VALUE STANDARDS ACHIEVED

{company_name}'s {plan_type} meets the 60% actuarial value requirement under ACA Section 4980H.

ACTUARIAL VALUE COMPLIANCE:
• Plan covers ≥60% of expected total healthcare costs
• Substantial coverage for inpatient hospital and physician services
• Meets affordability thresholds for employee premium contributions
• Qualified plan design under federal guidelines

EMPLOYER MANDATE PROTECTION:
• {company_name} AVOIDS Section 4980H penalties
• No {current_employer_penalty} per full-time employee penalty exposure
• Satisfies "offer of coverage" requirements for large employers
• Maintains safe harbor status for ACA compliance

PLAN PERFORMANCE METRICS:
• Structure: {plan_type} with {deductible_info['formatted']}
• Cost Sharing: {oop_limit} out-of-pocket protection
• Coverage Period: {coverage_period}
• Value Ratio: ≥60% actuarial value certified"""
    else:
        explanations['penalty_b_explanation'] = f"""❌ MINIMUM VALUE STANDARDS NOT MET

{company_name}'s plan FAILS the 60% actuarial value requirement.

IMMEDIATE PENALTY EXPOSURE:
• Potential {current_employer_penalty} penalty per full-time employee annually
• Applies to ALL full-time employees if triggered
• Section 4980H(b) "sledgehammer" penalty risk
• Retroactive penalty assessment possible

COMPLIANCE FAILURES:
• Plan covers <60% of expected total healthcare costs
• Insufficient coverage for inpatient hospital or physician services
• May fail affordability tests for employee contributions
• Does not qualify as "minimum value" coverage

URGENT ACTIONS REQUIRED:
• Immediate plan enhancement or replacement needed
• Calculate total potential penalty exposure (employees × {current_employer_penalty})
• Consider stop-loss or supplemental coverage options
• Engage benefits consultant for emergency compliance strategy
• Review all full-time employee classifications

FINANCIAL IMPACT EXAMPLE:
• 50 full-time employees = {current_employer_penalty} × 50 = $216,000 annual penalty risk"""
    
    return explanations

def extract_coverage_answers(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract answers to the two key questions"""
    
    # Question 1: Minimum Essential Coverage
    essential_coverage_patterns = [
        r'Does\s+this\s+plan\s+provide\s+Minimum\s+Essential\s+Coverage\?\s*(Yes|No)',
        r'Minimum\s+Essential\s+Coverage\?\s*(Yes|No)',
        r'Essential\s+Coverage[:\s]*(Yes|No)',
        r'Minimum\s+Essential[:\s]*(Yes|No)',
        r'Essential\s+Coverage\?\s*(Yes|No)',
        r'Minimum\s+Essential\s+Coverage[:\s]*(Yes|No)',
        r'Essential\s+Coverage[^.]*?\b(Yes|No)\b',  # More flexible pattern with word boundaries
        r'Minimum\s+Essential[^.]*?\b(Yes|No)\b',   # More flexible pattern with word boundaries
    ]
    
    # Question 2: Minimum Value Standards
    value_standards_patterns = [
        r'Does\s+this\s+plan\s+meet\s+the\s+Minimum\s+Value\s+Standards\?\s*(Yes|No)',
        r'Minimum\s+Value\s+Standards\?\s*(Yes|No)',
        r'Value\s+Standards[:\s]*(Yes|No)',
        r'Minimum\s+Value[:\s]*(Yes|No)',
        r'Value\s+Standards\?\s*(Yes|No)',
        r'Minimum\s+Value\s+Standards[:\s]*(Yes|No)',
        r'Value\s+Standards[^.]*?\b(Yes|No)\b',     # More flexible pattern with word boundaries
        r'Minimum\s+Value[^.]*?\b(Yes|No)\b',       # More flexible pattern with word boundaries
    ]
    
    essential_coverage_answer = None
    value_standards_answer = None
    
    # Search for answers
    for pattern in essential_coverage_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            essential_coverage_answer = match.group(1).strip()
            # Validate the answer
            if essential_coverage_answer.lower() not in ['yes', 'no']:
                print(f"Warning: Invalid essential coverage answer extracted: '{essential_coverage_answer}'")
                essential_coverage_answer = None
            else:
                break
    
    for pattern in value_standards_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value_standards_answer = match.group(1).strip()
            # Validate the answer
            if value_standards_answer.lower() not in ['yes', 'no']:
                print(f"Warning: Invalid value standards answer extracted: '{value_standards_answer}'")
                value_standards_answer = None
            else:
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
    """Process SBC PDF and extract required information with intelligent explanations"""
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
        
        # NEW: Generate intelligent explanations based on extracted content
        explanations = generate_penalty_explanation(
            company_name, essential_coverage, value_standards, full_text
        )
        
        # Calculate penalties (keep existing logic)
        penalty_a = essential_coverage if essential_coverage else "Unknown"
        penalty_b = value_standards if value_standards else "Unknown"
        
        return {
            'success': True,
            'company_name': company_name,
            'essential_coverage': essential_coverage,
            'value_standards': value_standards,
            'penalty_a': penalty_a,
            'penalty_b': penalty_b,
            'penalty_a_explanation': explanations['penalty_a_explanation'],  # NEW
            'penalty_b_explanation': explanations['penalty_b_explanation']   # NEW
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
