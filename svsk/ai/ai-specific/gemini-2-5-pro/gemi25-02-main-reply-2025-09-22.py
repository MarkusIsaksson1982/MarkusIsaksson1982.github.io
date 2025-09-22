import fitz  # PyMuPDF
import json
import csv
import re
import os

def load_config(config_path='config.json'):
    """Loads the subject bridge mapping configuration."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {config_path}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extracts all text from a given PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except fitz.fitz.FzError as e:
        print(f"Error opening or reading PDF {pdf_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred with {pdf_path}: {e}")
        return None


def parse_kunskapskrav(text):
    """
    Parses the 'Kunskapskrav' section of the curriculum text.
    Identifies requirements for grades E, C, and A.
    Handles both Swedish and English headers.
    """
    kunskapskrav = {"E": [], "C": [], "A": []}
    
    # Regex to find the main knowledge requirements section
    # Handles variations in titles and line breaks.
    section_pattern = re.compile(r'(Kunskapskrav|Knowledge requirements)[\s\S]*', re.IGNORECASE)
    section_match = section_pattern.search(text)

    if not section_match:
        print("Warning: 'Kunskapskrav' or 'Knowledge requirements' section not found.")
        return {}

    section_text = section_match.group(0)

    # Regex patterns for each grade level
    # These patterns look for the grade header and capture the text until the next grade header or end of section.
    patterns = {
        'E': r'(Betyget E|Grade E)\s*\n([\s\S]*?)(?=(Betyget C|Grade C|Betyget A|Grade A)|$)',
        'C': r'(Betyget C|Grade C)\s*\n([\s\S]*?)(?=(Betyget A|Grade A)|$)',
        'A': r'(Betyget A|Grade A)\s*\n([\s\S]*?)($|\Z|Kunskapskrav för)',
    }

    for grade, pattern in patterns.items():
        matches = re.finditer(pattern, section_text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            content = match.group(2).strip()
            # Clean up the extracted text: remove excessive newlines and split into distinct points
            descriptors = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('Betyget')]
            kunskapskrav[grade].extend(descriptors)

    # Check if any data was actually parsed
    if not any(kunskapskrav.values()):
        print("Warning: Could not parse any specific grade requirements from the section.")
        
    return kunskapskrav

def find_bridge_connections(kunskapskrav, config):
    """Finds connections to other subjects based on keywords from the config file."""
    if not config:
        return {}
        
    bridges = {}
    for subject, keywords in config.get('subject_bridges', {}).items():
        bridges[subject] = []
        # Create a case-insensitive regex pattern for the keywords
        keyword_pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\b', re.IGNORECASE)
        
        for grade, descriptors in kunskapskrav.items():
            for descriptor in descriptors:
                matches = keyword_pattern.findall(descriptor)
                if matches:
                    unique_matches = sorted(list(set([m.lower() for m in matches])))
                    bridges[subject].append({
                        'grade': grade,
                        'descriptor': descriptor,
                        'matched_keywords': unique_matches
                    })
    return bridges

def save_as_csv(data, bridges, output_prefix):
    """Saves the parsed kunskapskrav and bridges to CSV files."""
    # Save kunskapskrav
    krav_path = f"{output_prefix}_kunskapskrav.csv"
    with open(krav_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Grade', 'Descriptor'])
        for grade, descriptors in data.items():
            for descriptor in descriptors:
                writer.writerow([grade, descriptor])
    print(f"Successfully saved kunskapskrav to {krav_path}")

    # Save bridges
    bridge_path = f"{output_prefix}_bridges.csv"
    with open(bridge_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Subject', 'Grade', 'Matched Keywords', 'Descriptor'])
        for subject, connections in bridges.items():
            for conn in connections:
                writer.writerow([subject, conn['grade'], ', '.join(conn['matched_keywords']), conn['descriptor']])
    print(f"Successfully saved bridge connections to {bridge_path}")


def save_as_json(data, bridges, output_prefix):
    """Saves the combined data to a JSON file."""
    output_data = {
        'kunskapskrav': data,
        'bridge_connections': bridges
    }
    json_path = f"{output_prefix}_output.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    print(f"Successfully saved combined data to {json_path}")


def save_as_markdown(data, bridges, output_prefix, pdf_filename):
    """Saves the data to a Markdown file."""
    md_path = f"{output_prefix}_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Curriculum Analysis Report for {pdf_filename}\n\n")
        
        f.write("## Kunskapskrav (Knowledge Requirements)\n\n")
        for grade in ['E', 'C', 'A']:
            if data.get(grade):
                f.write(f"### Grade {grade}\n")
                for descriptor in data[grade]:
                    f.write(f"- {descriptor}\n")
                f.write("\n")

        f.write("## Bridge Connections to Other Subjects\n\n")
        for subject, connections in bridges.items():
            if connections:
                f.write(f"### Connections to {subject.capitalize()}\n")
                for conn in connections:
                    f.write(f"- **Grade {conn['grade']}**: Found keywords `{', '.join(conn['matched_keywords'])}` in descriptor:\n")
                    f.write(f"  > \"{conn['descriptor']}\"\n\n")
    print(f"Successfully saved Markdown report to {md_path}")


def main():
    """Main function to drive the curriculum parsing process."""
    pdf_path = input("Enter the path to the curriculum PDF file: ")
    
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' was not found.")
        return

    # Create output directory
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_prefix = os.path.join(output_dir, base_filename)

    config = load_config()
    if config is None:
        print("Halting execution due to missing or invalid configuration.")
        return

    text = extract_text_from_pdf(pdf_path)
    if text is None:
        print("Halting execution due to PDF extraction error.")
        return

    kunskapskrav = parse_kunskapskrav(text)
    if not kunskapskrav or not any(kunskapskrav.values()):
        print("Could not find or parse kunskapskrav. No output files will be generated.")
        return
        
    bridges = find_bridge_connections(kunskapskrav, config)

    # Save outputs
    save_as_csv(kunskapskrav, bridges, output_prefix)
    save_as_json(kunskapskrav, bridges, output_prefix)
    save_as_markdown(kunskapskrav, bridges, output_prefix, os.path.basename(pdf_path))
    
    print("\nProcessing complete.")

if __name__ == "__main__":
    main()
