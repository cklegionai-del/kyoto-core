python
import os
from fpdf import FPDF
import subprocess

def list_files_by_extension(directory):
    files = {}
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            name, ext = os.path.splitext(filename)
            ext = ext[1:]  # Remove the dot
            if ext not in files:
                files[ext] = []
            files[ext].append(filename)
    return files

def create_summary_pdf(files_by_extension, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for ext, files in files_by_extension.items():
        pdf.cell(200, 10, txt=f'Extension: .{ext}', ln=True, align='L')
        for file in files:
            pdf.cell(200, 10, txt=f'- {file}', ln=True, align='L')
        pdf.ln(5)
    
    pdf.output(output_path)

def github_push(repo, file, content):
    with open(file, 'w') as f:
        f.write(content)
    subprocess.run(['git', '-C', repo, 'add', file])
    subprocess.run(['git', '-C', repo, 'commit', '-m', f'Add {file}'])
    subprocess.run(['git', '-C', repo, 'push'])

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
files_by_extension = list_files_by_extension(desktop_path)
output_pdf = os.path.join(desktop_path, "Desktop_Inventory.pdf")
create_summary_pdf(files_by_extension, output_pdf)

repo_path = '/path/to/kyoto-core'
github_push(repo=repo_path, file=output_pdf, content=open(output_pdf, 'rb').read())
