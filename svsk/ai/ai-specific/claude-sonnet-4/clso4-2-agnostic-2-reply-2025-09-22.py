#!/usr/bin/env python3
"""
Swedish Curriculum Document Parser
==================================

A comprehensive tool for parsing Swedish curriculum documents (Skolverket ARTI syllabi)
using PyMuPDF and pdfplumber. Extracts kunskapskrav sections, categorizes by grade levels,
and generates bridge connections to other subjects.

Requirements:
- PyMuPDF (fitz)
- pdfplumber
- pandas
- pyyaml

Install with: pip install PyMuPDF pdfplumber pandas pyyaml
"""

import re
import json
import csv
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

try:
    import fitz  # PyMuPDF
    import pdfplumber
    import pandas as pd
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install PyMuPDF pdfplumber pandas pyyaml")
    sys.exit(1)


@dataclass
class KunskapskravSection:
    """Data structure for storing kunskapskrav information."""
    grade_level: str  # E, C, A
    subject: str
    content: str
    competency_descriptors: List[str]
    page_number: int
    bridge_connections: Dict[str, List[str]]


@dataclass
class CurriculumDocument:
    """Data structure for storing parsed curriculum document."""
    filename: str
    subject: str
    kunskapskrav_sections: List[KunskapskravSection]
    metadata: Dict[str, str]
    parsing_errors: List[str]


class CurriculumParser:
    """Main parser class for Swedish curriculum documents."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize parser with configuration."""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.grade_patterns = self._compile_grade_patterns()
        self.competency_patterns = self._compile_competency_patterns()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file or use defaults."""
        default_config = {
            'bridge_keywords': {
                'Svenska': [
                    'språk', 'text', 'läsning', 'skrivning', 'kommunikation',
                    'berättelse', 'argumentation', 'reflektion', 'analys',
                    'språkbruk', 'ordförråd', 'grammatik', 'retorik'
                ],
                'Historia': [
                    'historia', 'historisk', 'utveckling', 'förändring',
                    'tid', 'epok', 'period', 'utvecklingsprocess', 'förr',
                    'samtid', 'framtid', 'kontinuitet', 'kronologi'
                ],
                'Samhällskunskap': [
                    'samhälle', 'demokrati', 'politik', 'ekonomi', 'miljö',
                    'rättigheter', 'ansvar', 'medborgar', 'hållbar',
                    'global', 'lokal', 'påverkan', 'delaktighet', 'värdering'
                ]
            },
            'grade_keywords': {
                'E': ['grundläggande', 'enkla', 'med stöd', 'delvis'],
                'C': ['utvecklade', 'förhållandevis', 'relativt', 'i huvudsak'],
                'A': ['välutvecklade', 'komplexa', 'självständigt', 'nyanserat']
            },
            'competency_indicators': [
                'kan', 'förmåga', 'kunskap', 'förståelse', 'färdighet',
                'beskriver', 'förklarar', 'analyserar', 'värderar', 'använder'
            ],
            'output_formats': ['csv', 'json', 'markdown'],
            'languages': ['sv', 'en']
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logging.warning(f"Could not load config from {config_path}: {e}")
                
        return default_config
    
    def _setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('curriculum_parser.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _compile_grade_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for identifying grade levels."""
        patterns = {}
        
        # Swedish grade level patterns
        patterns['E'] = re.compile(
            r'(?:betyg\s+)?E[:\.]?\s*(?=.*(?:grundläggande|enkla|med\s+stöd))',
            re.IGNORECASE | re.MULTILINE
        )
        patterns['C'] = re.compile(
            r'(?:betyg\s+)?C[:\.]?\s*(?=.*(?:utvecklade|förhållandevis))',
            re.IGNORECASE | re.MULTILINE
        )
        patterns['A'] = re.compile(
            r'(?:betyg\s+)?A[:\.]?\s*(?=.*(?:välutvecklade|komplexa|självständigt))',
            re.IGNORECASE | re.MULTILINE
        )
        
        return patterns
    
    def _compile_competency_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for identifying competency descriptors."""
        indicators = self.config['competency_indicators']
        patterns = []
        
        for indicator in indicators:
            # Match sentences containing competency indicators
            pattern = re.compile(
                rf'\b{re.escape(indicator)}\b.*?[.!?]',
                re.IGNORECASE | re.DOTALL
            )
            patterns.append(pattern)
            
        return patterns
    
    def parse_pdf(self, pdf_path: str) -> CurriculumDocument:
        """Parse a single PDF document."""
        pdf_path = Path(pdf_path)
        self.logger.info(f"Parsing PDF: {pdf_path}")
        
        document = CurriculumDocument(
            filename=pdf_path.name,
            subject=self._extract_subject_from_filename(pdf_path.name),
            kunskapskrav_sections=[],
            metadata={},
            parsing_errors=[]
        )
        
        try:
            # Try PyMuPDF first
            sections_pymupdf = self._parse_with_pymupdf(pdf_path)
            if sections_pymupdf:
                document.kunskapskrav_sections.extend(sections_pymupdf)
                self.logger.info(f"PyMuPDF extracted {len(sections_pymupdf)} sections")
            
            # Try pdfplumber as fallback/supplement
            sections_pdfplumber = self._parse_with_pdfplumber(pdf_path)
            if sections_pdfplumber and not sections_pymupdf:
                document.kunskapskrav_sections.extend(sections_pdfplumber)
                self.logger.info(f"pdfplumber extracted {len(sections_pdfplumber)} sections")
            
            # Extract metadata
            document.metadata = self._extract_metadata(pdf_path)
            
            # Generate bridge connections for all sections
            for section in document.kunskapskrav_sections:
                section.bridge_connections = self._generate_bridge_connections(section.content)
                
        except Exception as e:
            error_msg = f"Error parsing {pdf_path}: {str(e)}"
            document.parsing_errors.append(error_msg)
            self.logger.error(error_msg)
        
        return document
    
    def _parse_with_pymupdf(self, pdf_path: Path) -> List[KunskapskravSection]:
        """Parse PDF using PyMuPDF."""
        sections = []
        
        try:
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                page_sections = self._extract_kunskapskrav_from_text(
                    text, page_num + 1, pdf_path.stem
                )
                sections.extend(page_sections)
                
            doc.close()
            
        except Exception as e:
            self.logger.error(f"PyMuPDF parsing error: {e}")
            raise
        
        return sections
    
    def _parse_with_pdfplumber(self, pdf_path: Path) -> List[KunskapskravSection]:
        """Parse PDF using pdfplumber."""
        sections = []
        
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if not text or not text.strip():
                        continue
                    
                    page_sections = self._extract_kunskapskrav_from_text(
                        text, page_num + 1, pdf_path.stem
                    )
                    sections.extend(page_sections)
                    
        except Exception as e:
            self.logger.error(f"pdfplumber parsing error: {e}")
            raise
        
        return sections
    
    def _extract_kunskapskrav_from_text(self, text: str, page_num: int, subject: str) -> List[KunskapskravSection]:
        """Extract kunskapskrav sections from text."""
        sections = []
        
        # Look for grade level indicators
        for grade, pattern in self.grade_patterns.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 500)
                end = min(len(text), match.end() + 1500)
                context = text[start:end]
                
                # Clean up the context
                context = self._clean_text(context)
                
                if len(context.split()) < 10:  # Skip very short contexts
                    continue
                
                # Extract competency descriptors
                competencies = self._extract_competency_descriptors(context)
                
                section = KunskapskravSection(
                    grade_level=grade,
                    subject=subject,
                    content=context,
                    competency_descriptors=competencies,
                    page_number=page_num,
                    bridge_connections={}
                )
                
                sections.append(section)
        
        return sections
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^(?:Skolverket|ARTI).*$', '', text, flags=re.MULTILINE)
        
        # Fix common OCR errors for Swedish text
        text = text.replace('å', 'å').replace('ä', 'ä').replace('ö', 'ö')
        text = text.replace('Å', 'Å').replace('Ä', 'Ä').replace('Ö', 'Ö')
        
        return text.strip()
    
    def _extract_competency_descriptors(self, text: str) -> List[str]:
        """Extract competency descriptors from text."""
        descriptors = []
        
        for pattern in self.competency_patterns:
            matches = pattern.findall(text)
            for match in matches:
                cleaned = self._clean_text(match)
                if cleaned and len(cleaned.split()) > 3:
                    descriptors.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_descriptors = []
        for desc in descriptors:
            if desc not in seen:
                seen.add(desc)
                unique_descriptors.append(desc)
        
        return unique_descriptors[:5]  # Limit to top 5
    
    def _generate_bridge_connections(self, content: str) -> Dict[str, List[str]]:
        """Generate bridge connections to other subjects based on keyword matching."""
        bridges = {}
        content_lower = content.lower()
        
        for subject, keywords in self.config['bridge_keywords'].items():
            matches = []
            
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    # Find sentences containing the keyword
                    sentences = re.split(r'[.!?]+', content)
                    for sentence in sentences:
                        if keyword.lower() in sentence.lower():
                            cleaned = self._clean_text(sentence)
                            if cleaned and len(cleaned.split()) > 4:
                                matches.append(cleaned)
                                break  # One example per keyword
            
            if matches:
                bridges[subject] = matches[:3]  # Limit to 3 examples per subject
        
        return bridges
    
    def _extract_subject_from_filename(self, filename: str) -> str:
        """Extract subject name from filename."""
        # Remove file extension and common prefixes
        subject = Path(filename).stem
        subject = re.sub(r'^(?:arti|skolverket)[-_]?', '', subject, flags=re.IGNORECASE)
        subject = subject.replace('_', ' ').replace('-', ' ')
        return subject.title()
    
    def _extract_metadata(self, pdf_path: Path) -> Dict[str, str]:
        """Extract metadata from PDF."""
        metadata = {
            'filename': pdf_path.name,
            'file_size': str(pdf_path.stat().st_size),
            'parsed_at': datetime.now().isoformat()
        }
        
        try:
            doc = fitz.open(str(pdf_path))
            pdf_metadata = doc.metadata
            if pdf_metadata:
                metadata.update({
                    'title': pdf_metadata.get('title', ''),
                    'author': pdf_metadata.get('author', ''),
                    'subject': pdf_metadata.get('subject', ''),
                    'creator': pdf_metadata.get('creator', ''),
                    'creation_date': pdf_metadata.get('creationDate', ''),
                    'modification_date': pdf_metadata.get('modDate', '')
                })
            doc.close()
        except Exception as e:
            self.logger.warning(f"Could not extract metadata: {e}")
        
        return metadata
    
    def export_to_csv(self, documents: List[CurriculumDocument], output_path: str):
        """Export parsed data to CSV format."""
        rows = []
        
        for doc in documents:
            for section in doc.kunskapskrav_sections:
                row = {
                    'filename': doc.filename,
                    'subject': doc.subject,
                    'grade_level': section.grade_level,
                    'page_number': section.page_number,
                    'content': section.content[:500] + '...' if len(section.content) > 500 else section.content,
                    'competency_count': len(section.competency_descriptors),
                    'competencies': '; '.join(section.competency_descriptors),
                    'bridge_subjects': ', '.join(section.bridge_connections.keys()),
                    'parsing_errors': '; '.join(doc.parsing_errors)
                }
                
                # Add bridge connections as separate columns
                for subject, connections in section.bridge_connections.items():
                    row[f'bridge_{subject.lower()}'] = '; '.join(connections)
                
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, encoding='utf-8')
        self.logger.info(f"CSV exported to: {output_path}")
    
    def export_to_json(self, documents: List[CurriculumDocument], output_path: str):
        """Export parsed data to JSON format."""
        data = {
            'export_metadata': {
                'timestamp': datetime.now().isoformat(),
                'document_count': len(documents),
                'total_sections': sum(len(doc.kunskapskrav_sections) for doc in documents)
            },
            'documents': [asdict(doc) for doc in documents]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"JSON exported to: {output_path}")
    
    def export_to_markdown(self, documents: List[CurriculumDocument], output_path: str):
        """Export parsed data to Markdown format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Swedish Curriculum Analysis Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary statistics
            total_sections = sum(len(doc.kunskapskrav_sections) for doc in documents)
            f.write(f"## Summary\n\n")
            f.write(f"- **Documents processed**: {len(documents)}\n")
            f.write(f"- **Total sections**: {total_sections}\n")
            
            grade_counts = {'E': 0, 'C': 0, 'A': 0}
            for doc in documents:
                for section in doc.kunskapskrav_sections:
                    grade_counts[section.grade_level] += 1
            
            f.write(f"- **Grade E sections**: {grade_counts['E']}\n")
            f.write(f"- **Grade C sections**: {grade_counts['C']}\n")
            f.write(f"- **Grade A sections**: {grade_counts['A']}\n\n")
            
            # Document details
            for doc in documents:
                f.write(f"## {doc.subject} ({doc.filename})\n\n")
                
                if doc.parsing_errors:
                    f.write("### Parsing Errors\n\n")
                    for error in doc.parsing_errors:
                        f.write(f"- {error}\n")
                    f.write("\n")
                
                if doc.kunskapskrav_sections:
                    f.write("### Kunskapskrav Sections\n\n")
                    
                    for section in doc.kunskapskrav_sections:
                        f.write(f"#### Grade {section.grade_level} (Page {section.page_number})\n\n")
                        
                        # Content preview
                        preview = section.content[:300] + "..." if len(section.content) > 300 else section.content
                        f.write(f"**Content**: {preview}\n\n")
                        
                        # Competency descriptors
                        if section.competency_descriptors:
                            f.write("**Competency Descriptors**:\n")
                            for comp in section.competency_descriptors:
                                f.write(f"- {comp}\n")
                            f.write("\n")
                        
                        # Bridge connections
                        if section.bridge_connections:
                            f.write("**Bridge Connections**:\n")
                            for subject, connections in section.bridge_connections.items():
                                f.write(f"- **{subject}**: {', '.join(connections[:2])}\n")
                            f.write("\n")
                        
                        f.write("---\n\n")
        
        self.logger.info(f"Markdown exported to: {output_path}")


def create_default_config(config_path: str):
    """Create a default configuration file."""
    default_config = {
        'bridge_keywords': {
            'Svenska': [
                'språk', 'text', 'läsning', 'skrivning', 'kommunikation',
                'berättelse', 'argumentation', 'reflektion', 'analys',
                'språkbruk', 'ordförråd', 'grammatik', 'retorik'
            ],
            'Historia': [
                'historia', 'historisk', 'utveckling', 'förändring',
                'tid', 'epok', 'period', 'utvecklingsprocess', 'förr',
                'samtid', 'framtid', 'kontinuitet', 'kronologi'
            ],
            'Samhällskunskap': [
                'samhälle', 'demokrati', 'politik', 'ekonomi', 'miljö',
                'rättigheter', 'ansvar', 'medborgar', 'hållbar',
                'global', 'lokal', 'påverkan', 'delaktighet', 'värdering'
            ],
            'Matematik': [
                'matematik', 'räkning', 'beräkning', 'statistik', 'diagram',
                'mätning', 'geometri', 'procent', 'proportion', 'logik'
            ],
            'Naturvetenskap': [
                'natur', 'miljö', 'ekosystem', 'hållbarhet', 'experiment',
                'observation', 'hypotes', 'undersökning', 'fenomen'
            ]
        },
        'competency_indicators': [
            'kan', 'förmåga', 'kunskap', 'förståelse', 'färdighet',
            'beskriver', 'förklarar', 'analyserar', 'värderar', 'använder',
            'tillämpar', 'resonerar', 'reflekterar', 'kommunicerar'
        ],
        'grade_keywords': {
            'E': ['grundläggande', 'enkla', 'med stöd', 'delvis', 'översiktligt'],
            'C': ['utvecklade', 'förhållandevis', 'relativt', 'i huvudsak', 'utförligt'],
            'A': ['välutvecklade', 'komplexa', 'självständigt', 'nyanserat', 'fördjupat']
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"Default configuration created at: {config_path}")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse Swedish curriculum documents')
    parser.add_argument('input_path', help='Path to PDF file or directory containing PDFs')
    parser.add_argument('-o', '--output', default='output', help='Output directory')
    parser.add_argument('-c', '--config', help='Path to configuration YAML file')
    parser.add_argument('--create-config', help='Create default configuration file')
    parser.add_argument('--formats', nargs='+', default=['csv', 'json', 'markdown'],
                       choices=['csv', 'json', 'markdown'], help='Output formats')
    
    args = parser.parse_args()
    
    # Create default config if requested
    if args.create_config:
        create_default_config(args.create_config)
        return
    
    # Initialize parser
    parser_instance = CurriculumParser(args.config)
    
    # Find PDF files
    input_path = Path(args.input_path)
    if input_path.is_file():
        pdf_files = [input_path]
    elif input_path.is_dir():
        pdf_files = list(input_path.glob('*.pdf'))
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        return
    
    if not pdf_files:
        print("No PDF files found")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Parse documents
    documents = []
    for pdf_file in pdf_files:
        try:
            doc = parser_instance.parse_pdf(str(pdf_file))
            documents.append(doc)
            print(f"Processed: {pdf_file.name} - {len(doc.kunskapskrav_sections)} sections")
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # Export to requested formats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if 'csv' in args.formats:
        csv_path = output_dir / f'curriculum_analysis_{timestamp}.csv'
        parser_instance.export_to_csv(documents, str(csv_path))
    
    if 'json' in args.formats:
        json_path = output_dir / f'curriculum_analysis_{timestamp}.json'
        parser_instance.export_to_json(documents, str(json_path))
    
    if 'markdown' in args.formats:
        md_path = output_dir / f'curriculum_analysis_{timestamp}.md'
        parser_instance.export_to_markdown(documents, str(md_path))
    
    print(f"\nProcessing complete! Results saved to: {output_dir}")
    print(f"Total documents processed: {len(documents)}")
    total_sections = sum(len(doc.kunskapskrav_sections) for doc in documents)
    print(f"Total sections extracted: {total_sections}")


if __name__ == '__main__':
    main()
