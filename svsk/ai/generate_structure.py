# generate_structure.py
import os
from datetime import datetime

def generate_directory_structure(start_path, output_file):
    """Generate directory structure and write to file"""
    with open(output_file, 'w') as f:
        f.write(f"Directory structure generated on: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        
        for root, dirs, files in os.walk(start_path):
            # Skip .git directory and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            level = root.replace(start_path, '').count(os.sep)
            indent = ' ' * 2 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if not file.startswith('.'):  # Skip hidden files
                    f.write(f"{subindent}{file}\n")

if __name__ == "__main__":
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"structure_{timestamp}.log"
    
    generate_directory_structure(current_dir, output_filename)
    print(f"Directory structure saved to: {output_filename}")
