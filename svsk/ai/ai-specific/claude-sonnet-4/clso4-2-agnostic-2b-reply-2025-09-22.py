#!/usr/bin/env python3
"""
Usage Examples and Test Script for Swedish Curriculum Parser
===========================================================

This script demonstrates how to use the CurriculumParser class
with various configuration options and processing scenarios.
"""

import os
import sys
from pathlib import Path
import tempfile
import json

# Import the main parser (assuming it's saved as curriculum_parser.py)
try:
    from curriculum_parser import CurriculumParser, create_default_config
except ImportError:
    print("Please ensure curriculum_parser.py is in the same directory or Python path")
    sys.exit(1)


def example_basic_usage():
    """Basic usage example - parse a single PDF."""
    print("=== Basic Usage Example ===")
    
    # Initialize parser with default configuration
    parser = CurriculumParser()
    
    # Example: Parse a single PDF file
    pdf_path = "sample_curriculum.pdf"  # Replace with actual path
    
    if Path(pdf_path).exists():
        try:
            document = parser.parse_pdf(pdf_path)
            
            print(f"Parsed: {document.filename}")
            print(f"Subject: {document.subject}")
            print(f"Sections found: {len(document.kunskapskrav_sections)}")
            
            # Show first section details
            if document.kunskapskrav_sections:
                section = document.kunskapskrav_sections[0]
                print(f"\nFirst section (Grade {section.grade_level}):")
                print(f"Content preview: {section.content[:200]}...")
                print(f"Competencies: {len(section.competency_descriptors)}")
                print(f"Bridge connections: {list(section.bridge_connections.keys())}")
            
            if document.parsing_errors:
                print(f"Parsing errors: {len(document.parsing_errors)}")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"PDF file not found: {pdf_path}")
        print("Please provide a valid PDF path for this example")


def example_with_custom_config():
    """Example using custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Create a custom configuration
    config_path = "custom_config.yaml"
    create_default_config(config_path)
    
    # Initialize parser with custom config
    parser = CurriculumParser(config_path)
    
    print(f"Parser initialized with config: {config_path}")
    print(f"Bridge subjects configured: {list(parser.config['bridge_keywords'].keys())}")
    
    # Clean up
    if Path(config_path).exists():
        Path(config_path).unlink()


def example_batch_processing():
    """Example of processing multiple PDFs in a directory."""
    print("\n=== Batch Processing Example ===")
    
    # Create parser
    parser = CurriculumParser()
    
    # Example directory with PDFs
    pdf_directory = "curriculum_pdfs"  # Replace with actual directory
    
    if Path(pdf_directory).exists():
        pdf_files = list(Path(pdf_directory).glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files")
        
        documents = []
        for pdf_file in pdf_files[:3]:  # Process first 3 files as example
            try:
                doc = parser.parse_pdf(str(pdf_file))
                documents.append(doc)
                print(f"Processed: {pdf_file.name} - {len(doc.kunskapskrav_sections)} sections")
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
        
        # Export results
        if documents:
            output_dir = Path("batch_output")
            output_dir.mkdir(exist_ok=True)
            
            # Export to all formats
            parser.export_to_csv(documents, str(output_dir / "batch_results.csv"))
            parser.export_to_json(documents, str(output_dir / "batch_results.json"))
            parser.export_to_markdown(documents, str(output_dir / "batch_results.md"))
            
            print(f"Results exported to: {output_dir}")
            
    else:
        print(f"Directory not found: {pdf_directory}")
        print("Please create this directory and add some PDF files for batch processing")


def example_analyzing_results():
    """Example of analyzing parsing results."""
    print("\n=== Results Analysis Example ===")
    
    # Simulate some parsing results for demonstration
    mock_results = create_mock_results()
    
    # Analyze grade distribution
    grade_distribution = {'E': 0, 'C': 0, 'A': 0}
    subject_count = {}
    bridge_connections = {}
    
    for doc in mock_results:
        subject_count[doc.subject] = subject_count.get(doc.subject, 0) + 1
        
        for section in doc.kunskapskrav_sections:
            grade_distribution[section.grade_level] += 1
            
            for bridge_subject in section.bridge_connections.keys():
                if bridge_subject not in bridge_connections:
                    bridge_connections[bridge_subject] = 0
                bridge_connections[bridge_subject] += 1
    
    print("Analysis Results:")
    print(f"Total documents: {len(mock_results)}")
    print(f"Grade distribution: {grade_distribution}")
    print(f"Subjects: {list(subject_count.keys())}")
    print(f"Most common bridge connections: {sorted(bridge_connections.items(), key=lambda x: x[1], reverse=True)}")


def example_custom_bridge_mapping():
    """Example of creating custom bridge mappings."""
    print("\n=== Custom Bridge Mapping Example ===")
    
    # Create custom bridge keywords for a specific subject area
    custom_config = {
        'bridge_keywords': {
            'Svenska': ['språk', 'text', 'kommunikation', 'läsning', 'skrivning'],
            'Matematik': ['matematik', 'räkning', 'beräkning', 'geometri', 'statistik'],
            'Naturvetenskap': ['experiment', 'observation', 'hypotes', 'miljö', 'natur'],
            # Add a new subject area
            'Programmering': ['kod', 'algoritm', 'digitala verktyg', 'problemlösning', 'logik'],
            'Entreprenörskap': ['innovation', 'kreativitet', 'företagande', 'initiativ', 'ansvar']
        }
    }
    
    # Save custom config temporarily
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        import yaml
        yaml.dump(custom_config, f, allow_unicode=True)
        custom_config_path = f.name
    
    try:
        # Create parser with custom config
        parser = CurriculumParser(custom_config_path)
        
        print(f"Custom bridge subjects: {list(parser.config['bridge_keywords'].keys())}")
        
        # Test bridge connection generation
        sample_text = """
        Eleven kan använda digitala verktyg för problemlösning och visar kreativitet
        i sitt arbete. Genom kod och algoritmer demonstrerar eleven logiskt tänkande
        och kan ta initiativ för innovation i olika sammanhang.
        """
        
        # Create a mock section to test bridge connections
        from curriculum_parser import KunskapskravSection
        
        test_section = KunskapskravSection(
            grade_level='C',
            subject='Teknik',
            content=sample_text,
            competency_descriptors=[],
            page_number=1,
            bridge_connections={}
        )
        
        # Generate bridge connections
        bridges = parser._generate_bridge_connections(sample_text)
        
        print("Bridge connections found:")
        for subject, connections in bridges.items():
            print(f"  {subject}: {connections}")
            
    finally:
        # Clean up temporary file
        Path(custom_config_path).unlink()


def create_mock_results():
    """Create mock parsing results for demonstration."""
    from curriculum_parser import CurriculumDocument, KunskapskravSection
    
    # Create mock sections
    sections = [
        KunskapskravSection(
            grade_level='E',
            subject='Svenska',
            content='Eleven kan läsa och förstå enkla texter med stöd...',
            competency_descriptors=['kan läsa', 'förstå texter'],
            page_number=1,
            bridge_connections={'Historia': ['texter från olika tider']}
        ),
        KunskapskravSection(
            grade_level='C',
            subject='Matematik',
            content='Eleven kan lösa utvecklade problem och använda olika metoder...',
            competency_descriptors=['kan lösa problem', 'använda metoder'],
            page_number=2,
            bridge_connections={'Naturvetenskap': ['matematiska beräkningar']}
        ),
        KunskapskravSection(
            grade_level='A',
            subject='Historia',
            content='Eleven kan självständigt analysera komplexa historiska sammanhang...',
            competency_descriptors=['kan analysera', 'förstå sammanhang'],
            page_number=3,
            bridge_connections={'Samhällskunskap': ['samhällsutveckling'], 'Svenska': ['källkritik']}
        )
    ]
    
    # Create mock documents
    documents = [
        CurriculumDocument(
            filename='svenska_kursplan.pdf',
            subject='Svenska',
            kunskapskrav_sections=[sections[0]],
            metadata={'title': 'Svenska Kursplan', 'pages': 10},
            parsing_errors=[]
        ),
        CurriculumDocument(
            filename='matematik_kursplan.pdf',
            subject='Matematik',
            kunskapskrav_sections=[sections[1]],
            metadata={'title': 'Matematik Kursplan', 'pages': 12},
            parsing_errors=[]
        ),
        CurriculumDocument(
            filename='historia_kursplan.pdf',
            subject='Historia',
            kunskapskrav_sections=[sections[2]],
            metadata={'title': 'Historia Kursplan', 'pages': 8},
            parsing_errors=[]
        )
    ]
    
    return documents


def example_export_formats():
    """Demonstrate different export formats."""
    print("\n=== Export Formats Example ===")
    
    # Create parser and mock data
    parser = CurriculumParser()
    documents = create_mock_results()
    
    # Create output directory
    output_dir = Path("export_examples")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Export to CSV
        csv_path = output_dir / "example_export.csv"
        parser.export_to_csv(documents, str(csv_path))
        print(f"CSV exported: {csv_path}")
        
        # Show CSV preview
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:3]  # First few lines
                print("CSV preview:")
                for line in lines:
                    print(f"  {line.strip()}")
        
        # Export to JSON
        json_path = output_dir / "example_export.json"
        parser.export_to_json(documents, str(json_path))
        print(f"JSON exported: {json_path}")
        
        # Show JSON structure
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print("JSON structure preview:")
                print(f"  Documents: {len(data['documents'])}")
                print(f"  Total sections: {data['export_metadata']['total_sections']}")
        
        # Export to Markdown
        md_path = output_dir / "example_export.md"
        parser.export_to_markdown(documents, str(md_path))
        print(f"Markdown exported: {md_path}")
        
        # Show Markdown preview
        if md_path.exists():
            with open(md_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]  # First few lines
                print("Markdown preview:")
                for line in lines:
                    print(f"  {line.strip()}")
                    
        print(f"\nAll examples exported to: {output_dir}")
        
    except Exception as e:
        print(f"Export error: {e}")


def example_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n=== Error Handling Example ===")
    
    parser = CurriculumParser()
    
    # Test with non-existent file
    try:
        doc = parser.parse_pdf("non_existent_file.pdf")
        print("This shouldn't print - file doesn't exist")
    except Exception as e:
        print(f"Handled missing file error: {type(e).__name__}")
    
    # Test with invalid PDF (create empty file)
    invalid_pdf = Path("invalid.pdf")
    invalid_pdf.write_text("This is not a PDF file")
    
    try:
        doc = parser.parse_pdf(str(invalid_pdf))
        if doc.parsing_errors:
            print(f"Parsing errors captured: {len(doc.parsing_errors)}")
            for error in doc.parsing_errors:
                print(f"  - {error}")
        else:
            print("No errors found (unexpected)")
    except Exception as e:
        print(f"Exception during parsing: {type(e).__name__}: {e}")
    finally:
        # Clean up
        if invalid_pdf.exists():
            invalid_pdf.unlink()
    
    print("Error handling demonstration complete")


def main():
    """Run all examples."""
    print("Swedish Curriculum Parser - Usage Examples")
    print("=" * 50)
    
    # Run all examples
    try:
        example_basic_usage()
        example_with_custom_config()
        example_batch_processing()
        example_analyzing_results()
        example_custom_bridge_mapping()
        example_export_formats()
        example_error_handling()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nTo use the parser with your own PDFs:")
        print("1. Install required packages: pip install PyMuPDF pdfplumber pandas pyyaml")
        print("2. Save the curriculum_parser.py file")
        print("3. Run: python curriculum_parser.py path/to/your/pdfs/")
        print("4. Or use the CurriculumParser class in your own scripts")
        
    except Exception as e:
        print(f"Example execution error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
