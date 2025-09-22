Swedish Curriculum Document Parser
This Python script extracts and analyzes Swedish curriculum documents (e.g., Skolverket syllabi) from PDF files. It identifies and categorizes "kunskapskrav" (knowledge requirements) by grade level (E/C/A), extracts key competency descriptors, and suggests potential "bridge connections" to other subjects based on keyword matching.

The output is provided in CSV, JSON, and Markdown formats for easy use in spreadsheets, web applications, or documentation.

Features
Text Extraction: Uses PyMuPDF to efficiently extract text from PDF documents.

Kunskapskrav Parsing: Automatically identifies and parses the knowledge requirements section for grades E, C, and A.

Multi-language Support: Recognizes both Swedish ("Kunskapskrav", "Betyget E") and English ("Knowledge requirements", "Grade E") headers.

Bridge Connections: Identifies connections to other subjects (Svenska, Historia, Samhällskunskap) by matching keywords defined in a configuration file.

Multiple Output Formats:

CSV: Two files (_kunskapskrav.csv and _bridges.csv) for easy import into spreadsheets.

JSON: A single file containing all parsed data, suitable for web backends or data analysis.

Markdown: A human-readable report summarizing the findings.

Configurable: Subject keywords can be easily customized in the config.json file.

Error Handling: Includes checks for missing files, corrupted PDFs, and sections that cannot be parsed.

Setup
Prerequisites
Python 3.7 or newer

Installation
Clone the repository or download the files.

Create and activate a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install the required libraries:

pip install -r requirements.txt

How to Use
Place your PDF curriculum file in the same directory as the script, or have the path to it ready.

Customize your subject bridges (optional):
Open config.json and add or modify the subjects and keywords. The script will search for these words (case-insensitively) in the competency descriptors.

Run the script from your terminal:

python curriculum_parser.py

Enter the path to your PDF file when prompted:

Enter the path to the curriculum PDF file: path/to/your/document.pdf

Check the output/ directory. The script will generate files named after the original PDF. For example, if you processed fysik.pdf, you will get:

output/fysik_kunskapskrav.csv

output/fysik_bridges.csv

output/fysik_output.json

output/fysik_report.md

Project Structure
.
├── curriculum_parser.py    # The main Python script
├── config.json             # Configuration for subject keywords
├── requirements.txt        # Python library dependencies
├── README.md               # This documentation file
└── output/                 # Directory for generated files (created on first run)
