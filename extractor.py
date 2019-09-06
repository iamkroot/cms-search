import json
from pathlib import Path
from pptx import Presentation
import docx2txt


def process_pptx(file_path: Path):
    prs = Presentation(file_path)
    text_runs = []
    for i, slide in enumerate(prs.slides):
        if i < 1:
            continue
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                para_text = ''.join(run.text for run in paragraph.runs)
                if para_text:
                    text_runs.append(para_text)
    return text_runs


def process_word(file_path: Path):
    pass


def process(file_path: Path):
    if file_path.suffix == '.pptx':
        sentences = process_pptx(file_path)
        data = {
            'name': str(file_path),
            'sentences': sentences
        }

    json_file = file_path.with_suffix('.json')
    with open(json_file, 'w') as f:
        json.dump(f, data)
    return sentences
