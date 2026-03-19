import os
import re
import shutil

def slugify(name):
    return name.lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '').strip('_')

def organize():
    base_dir = '/Users/fahimmorshed/Documents/Thesis/thesis-experiments-v1'
    dataset_dir = os.path.join(base_dir, 'dataset')
    csv_src = os.path.join(dataset_dir, 'CSV')
    cv_src = os.path.join(dataset_dir, 'CV')
    
    clean_matches_dir = os.path.join(dataset_dir, 'clean_matches')
    ambiguous_dir = os.path.join(dataset_dir, 'ambiguous', 'others', 'confusions')
    
    mapping_file = os.path.join(base_dir, 'docs', 'applicant_mapping.md')
    
    if not os.path.exists(mapping_file):
        print(f"Error: Mapping file not found: {mapping_file}")
        return

    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content by H2 headers
    sections = re.split(r'\n## ', '\n' + content)
    
    section_map = {}
    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue
        header = lines[0].strip()
        body = '\n'.join(lines[1:])
        section_map[header] = body

    # 1. Clean Matches
    if 'Clean Matches' in section_map:
        rows = section_map['Clean Matches'].strip().split('\n')
        for row in rows:
            if '|' not in row or '---' in row or 'Applicant Name' in row:
                continue
            cols = [c.strip() for c in row.split('|') if c.strip()]
            if len(cols) >= 3:
                name = cols[1]
                csv_files = [f.strip() for f in cols[2].split(',') if f.strip()]
                cv_file = cols[3]
                
                slug = slugify(name)
                target_dir = os.path.join(clean_matches_dir, slug)
                os.makedirs(target_dir, exist_ok=True)
                
                if csv_files:
                    src_csv = os.path.join(csv_src, csv_files[0])
                    if os.path.exists(src_csv):
                        shutil.copy2(src_csv, os.path.join(target_dir, 'qna.csv'))
                
                if cv_file and cv_file != 'TODO: Manual Match Required':
                    src_cv = os.path.join(cv_src, cv_file)
                    if os.path.exists(src_cv):
                        shutil.copy2(src_cv, os.path.join(target_dir, 'cv.pdf'))

    # 2. Ambiguous / TODO Matches
    target_todo = os.path.join(ambiguous_dir, 'todo_manual_match')
    if 'Ambiguous / TODO Matches' in section_map:
        os.makedirs(target_todo, exist_ok=True)
        rows = section_map['Ambiguous / TODO Matches'].strip().split('\n')
        for row in rows:
            if '|' not in row or '---' in row or 'Applicant Name' in row:
                continue
            cols = [c.strip() for c in row.split('|') if c.strip()]
            if len(cols) >= 3:
                name = cols[1]
                csv_files = [f.strip() for f in cols[2].split(',') if f.strip()]
                slug = slugify(name)
                sub_todo = os.path.join(target_todo, slug)
                os.makedirs(sub_todo, exist_ok=True)
                if csv_files:
                    src_csv = os.path.join(csv_src, csv_files[0])
                    if os.path.exists(src_csv):
                        shutil.copy2(src_csv, os.path.join(sub_todo, 'qna.csv'))

    # 3. Names found in PDFs with no obvious matching CSV
    target_pdf_no_csv = os.path.join(ambiguous_dir, 'pdf_no_csv')
    header_3 = 'Names found in PDFs with no obvious matching CSV'
    if header_3 in section_map:
        os.makedirs(target_pdf_no_csv, exist_ok=True)
        lines = section_map[header_3].strip().split('\n')
        for line in lines:
            match = re.search(r'- (.*?) \((.*?)\)', line)
            if match:
                pdf_file = match.group(2)
                src_cv = os.path.join(cv_src, pdf_file)
                if os.path.exists(src_cv):
                    shutil.copy2(src_cv, os.path.join(target_pdf_no_csv, pdf_file))

    # 4. Other Unmatched PDF Files
    target_unmatched = os.path.join(ambiguous_dir, 'unmatched_pdfs')
    header_4 = 'Other Unmatched PDF Files'
    if header_4 in section_map:
        os.makedirs(target_unmatched, exist_ok=True)
        lines = section_map[header_4].strip().split('\n')
        for line in lines:
            pdf_file = line.strip('- ').strip()
            if pdf_file.endswith('.pdf'):
                src_cv = os.path.join(cv_src, pdf_file)
                if os.path.exists(src_cv):
                    shutil.copy2(src_cv, os.path.join(target_unmatched, pdf_file))

    print("Organization complete.")

if __name__ == '__main__':
    organize()
