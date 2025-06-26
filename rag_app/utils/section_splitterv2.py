import fitz  # PyMuPDF
from collections import OrderedDict
import re

def extract_sections_by_format(pdf_path):
    doc = fitz.open(pdf_path)
    all_font_sizes = []

    # compute the average font size across the document
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    all_font_sizes.append(span["size"])
    avg_font_size = sum(all_font_sizes) / len(all_font_sizes)

    # extract sections, titles based on formatting, and remove images
    sections = OrderedDict()
    current_section = "initial"
    sections[current_section] = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block or block["type"] != 0:
                continue  # ignore images or non-text blocks

            title_candidate = ""
            max_size = 0
            bold_count = 0
            total_spans = 0
            first_line = block["lines"][0]
            for span in first_line["spans"]:
                title_candidate += span["text"]
                max_size = max(max_size, span["size"])
                if span["flags"] & 2:  # flag "bold"
                    bold_count += 1
                total_spans += 1

            title_candidate = title_candidate.strip()
            if not title_candidate or len(title_candidate) < 4:
                continue

            is_bold = bold_count / total_spans > 0.5
            is_upper = title_candidate.isupper()
            is_title = (
                (
                    (max_size > avg_font_size * 1.15)
                    or is_bold
                    or is_upper
                )
                and len(title_candidate.split()) <= 12
                and "=" not in title_candidate  # to avoid equations
                and "<" not in title_candidate
                and ">" not in title_candidate
                and "∈" not in title_candidate
                and "+" not in title_candidate
                and "-" not in title_candidate
            )
           
            if "lines" not in block or block["type"] != 0:
                continue  # ignorer images ou blocs non textuels

            if is_title:
                # Use only the first line as the section title
                section_title = ""
                for span in first_line["spans"]:
                    section_title += span["text"]
                section_title = section_title.replace("\n", " ").strip()
                if section_title not in sections:
                    section_title = re.sub(r"^(\d\.?)*\s*", "", section_title).strip()
                    sections[section_title] = []
                current_section = section_title

            block_text = ""
            for line in block["lines"][(1 if is_title else 0):]:
                for span in line["spans"]:
                    block_text += span["text"]
            block_text = block_text.strip()
            sections[current_section].append(block_text)
            
        # Group all sections before "abstract" into "metadata" if "abstract" exists
        metadata_section = ""
        if "abstract" in sections:
            for key in list(sections.keys()):
                if key == "abstract":
                    break
                metadata_section += "\n" + key + " : " + sections[key]
                del sections[key]
    
    return metadata_section, sections
