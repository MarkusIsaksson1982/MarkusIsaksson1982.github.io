import pdfplumber
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

class SkolverketPDFParser:
    """Specialized parser for Swedish curriculum PDFs with robust extraction."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Common Swedish curriculum patterns
        self.subject_patterns = [
            r'ÄMNE[:\s]+([A-ZÅÄÖ][a-zåäöA-ZÅÄÖ\s]+)',
            r'Subject[:\s]+([A-Z][a-zA-Z\s]+)',
            r'^([A-ZÅÄÖ][a-zåäöA-ZÅÄÖ\s]{3,})\s*$'  # Standalone subject titles
        ]
        
        self.competency_patterns = [
            r'Förmåga[:\s]*(.+?)(?=Förmåga|Innehåll|Kunskapskrav|$)',
            r'Centralt innehåll[:\s]*(.+?)(?=Kunskapskrav|Betygskriterier|$)',
            r'(?:Eleven|Students?)\s+(?:ska|should)\s+(.+?)(?=\n\n|\.|$)',
            r'Mål[:\s]*(.+?)(?=Innehåll|Bedömning|$)'
        ]
        
        self.grade_patterns = [
            r'(Kunskapskrav|Betygskriterier)[:\s]*(.+?)(?=Kommentarer|$)',
            r'(E|C|A)[:\s]*(.+?)(?=\n[ECA][:\s]|$)'
        ]
    
    def extract_structured_content(self, pdf_path: str) -> Dict:
        """Extract structured curriculum content from Skolverket PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return self._process_pdf_pages(pdf)
        except Exception as e:
            self.logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise
    
    def _process_pdf_pages(self, pdf: pdfplumber.PDF) -> Dict:
        """Process all pages and extract structured content."""
        result = {
            'subjects': [],
            'metadata': {
                'total_pages': len(pdf.pages),
                'extraction_method': 'hybrid_text_table'
            }
        }
        
        current_subject = None
        accumulated_text = ""
        
        for page_num, page in enumerate(pdf.pages):
            # Try table extraction first
            tables = page.extract_tables()
            if tables:
                table_content = self._process_tables(tables)
                if table_content:
                    result['subjects'].extend(table_content)
            
            # Extract text content
            text = page.extract_text()
            if text:
                accumulated_text += f"\n--- PAGE {page_num + 1} ---\n{text}"
        
        # Process accumulated text for subjects and competencies
        text_subjects = self._extract_from_text(accumulated_text)
        result['subjects'].extend(text_subjects)
        
        return result
    
    def _process_tables(self, tables: List[List[List[str]]]) -> List[Dict]:
        """Extract curriculum data from PDF tables."""
        subjects = []
        
        for table in tables:
            if not table or len(table) < 2:
                continue
                
            headers = [cell.strip().lower() if cell else '' for cell in table[0]]
            
            # Look for curriculum table patterns
            subject_col = self._find_column(headers, ['ämne', 'subject', 'område'])
            competency_col = self._find_column(headers, ['förmåga', 'mål', 'competency', 'goals'])
            content_col = self._find_column(headers, ['innehåll', 'content', 'centralt'])
            
            if subject_col >= 0:
                for row in table[1:]:
                    if len(row) > subject_col and row[subject_col]:
                        subject_name = row[subject_col].strip()
                        
                        competencies = []
                        if competency_col >= 0 and len(row) > competency_col and row[competency_col]:
                            competencies.append({
                                'type': 'competency',
                                'text': row[competency_col].strip()
                            })
                        
                        if content_col >= 0 and len(row) > content_col and row[content_col]:
                            competencies.append({
                                'type': 'content',
                                'text': row[content_col].strip()
                            })
                        
                        subjects.append({
                            'subject_name': subject_name,
                            'extraction_source': 'table',
                            'competencies': competencies
                        })
        
        return subjects
    
    def _find_column(self, headers: List[str], keywords: List[str]) -> int:
        """Find column index containing any of the keywords."""
        for i, header in enumerate(headers):
            for keyword in keywords:
                if keyword in header:
                    return i
        return -1
    
    def _extract_from_text(self, text: str) -> List[Dict]:
        """Extract subjects and competencies from raw text."""
        subjects = []
        
        # Split text into potential sections
        sections = re.split(r'\n\s*(?=ÄMNE|Subject:|[A-ZÅÄÖ]{3,}\s*\n)', text, flags=re.MULTILINE)
        
        for section in sections:
            if len(section.strip()) < 50:  # Skip short sections
                continue
                
            subject_name = self._extract_subject_name(section)
            if subject_name:
                competencies = self._extract_competencies(section)
                grade_criteria = self._extract_grade_criteria(section)
                
                subjects.append({
                    'subject_name': subject_name,
                    'extraction_source': 'text',
                    'competencies': competencies,
                    'grade_criteria': grade_criteria
                })
        
        return subjects
    
    def _extract_subject_name(self, text: str) -> Optional[str]:
        """Extract subject name using multiple patterns."""
        for pattern in self.subject_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Validate it looks like a subject name
                if 3 <= len(name) <= 50 and not re.match(r'^\d+', name):
                    return name
        return None
    
    def _extract_competencies(self, text: str) -> List[Dict]:
        """Extract competency descriptions."""
        competencies = []
        
        for pattern in self.competency_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            for match in matches:
                comp_text = match.group(1).strip()
                if len(comp_text) > 20:  # Filter out short fragments
                    # Clean up the text
                    comp_text = re.sub(r'\s+', ' ', comp_text)
                    comp_text = comp_text[:500]  # Limit length
                    
                    competencies.append({
                        'type': 'competency',
                        'text': comp_text,
                        'pattern_used': pattern
                    })
        
        return competencies
    
    def _extract_grade_criteria(self, text: str) -> List[Dict]:
        """Extract grade criteria (A, C, E levels)."""
        criteria = []
        
        for pattern in self.grade_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            for match in matches:
                grade_level = match.group(1).strip()
                criteria_text = match.group(2).strip()
                
                if len(criteria_text) > 20:
                    criteria.append({
                        'grade_level': grade_level,
                        'text': criteria_text[:300],
                        'pattern_used': pattern
                    })
        
        return criteria
    
    def validate_extraction(self, extracted_data: Dict) -> bool:
        """Validate that extraction produced reasonable results."""
        subjects = extracted_data.get('subjects', [])
        
        if not subjects:
            return False
        
        # Check that we have meaningful content
        valid_subjects = 0
        for subject in subjects:
            if (subject.get('subject_name') and 
                len(subject.get('subject_name', '')) >= 3 and
                subject.get('competencies')):
                valid_subjects += 1
        
        return valid_subjects >= 1

# Integration with existing CurriculumParser
def enhanced_parse_pdf(self, pdf: pdfplumber.PDF, source: str) -> CurriculumData:
    """Enhanced PDF parsing using SkolverketPDFParser."""
    skolverket_parser = SkolverketPDFParser()
    
    # Use specialized extraction
    extracted = skolverket_parser.extract_structured_content(source)
    
    if not skolverket_parser.validate_extraction(extracted):
        self.logger.warning(f"Extraction validation failed for {source}, falling back to simple method")
        return self._parse_pdf_simple(pdf, source)  # Your original method as fallback
    
    subjects = []
    metadata = {
        'source': source,
        **self.teacher_metadata,
        'gdpr': self.gdpr_compliance,
        'extraction_metadata': extracted['metadata']
    }
    
    for extracted_subject in extracted['subjects']:
        subject_name = extracted_subject['subject_name']
        section_id = hashlib.md5(subject_name.encode()).hexdigest()[:8]
        competencies = {}
        
        for idx, comp_data in enumerate(extracted_subject.get('competencies', [])):
            descriptor = comp_data['text']
            keywords = [w for w in re.findall(r'\w+', descriptor.lower()) 
                       if w not in STOPWORDS['sv']]
            bridges = self.generate_bridges_embedding(descriptor) if self.use_transformers else {}
            
            competencies[f"comp_{idx}"] = CompetencyLevel(
                descriptor=descriptor,
                keywords=keywords,
                bridges=bridges
            )
        
        subjects.append(SubjectSection(subject_name, section_id, competencies))
    
    data = CurriculumData(metadata=metadata, subjects=subjects)
    
    try:
        jsonschema.validate(asdict(data), self.schema)
    except jsonschema.ValidationError as e:
        self.logger.error(f"Schema validation failed: {e}")
        # Continue anyway but log the issue
    
    return data
