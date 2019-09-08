import json
from pathlib import Path
from pptx import Presentation


def process_pptx(file_path: Path):
    """ Extracts text from .pptx files
    Args:
        file_path(Path) : Path object that contains the file_path of the .pptx file
    Returns:
        list : The sentences extracted from the file
    """
    prs = Presentation(file_path)
    text_runs = []
    for i, slide in enumerate(prs.slides):
        if i < 1:
            continue
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                para_text = "".join(run.text for run in paragraph.runs)
                if para_text:
                    text_runs.append(para_text)
    return text_runs


def process_word(file_path: Path):
    pass


def extract_sentences(file_path: Path):
    """ Extract sentences from file and store in JSON
    Args:
        file_path(Path) : Path object that contains the path of the file
    Returns:
        list : List of all sentences extracted from the file
    """
    data = {}
    sentences = []
    if file_path.suffix == ".pptx":
        sentences = process_pptx(file_path)
        data = {"name": str(file_path), "sentences": sentences}

    json_file = file_path.with_suffix(".json")
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)  # Create/Dump json file with file's text
    return sentences
