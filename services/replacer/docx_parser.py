from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import _Cell, Table
from docx.document import Document as DocumentType

def iter_runs_in_container(container):
    """
    Recursively yield runs inside a container that directly holds paragraphs/tables.
    Used for cells, headers, footers.
    """
    for child in container._element.iterchildren():
        tag = child.tag
        if tag.endswith('p'):
            para = Paragraph(child, container.part)
            for run in para.runs:
                yield run
        elif tag.endswith('tbl'):
            table = Table(child, container.part)
            for row in table.rows:
                for cell in row.cells:
                    yield from iter_runs_in_container(cell)

def iter_all_runs(doc):
    """Yield all runs from the main document body, headers, and footers."""
    # Main document body
    body = doc._element.body
    for child in body.iterchildren():
        tag = child.tag
        if tag.endswith('p'):
            para = Paragraph(child, doc)
            for run in para.runs:
                yield run
        elif tag.endswith('tbl'):
            table = Table(child, doc)
            for row in table.rows:
                for cell in row.cells:
                    yield from iter_runs_in_container(cell)

    # Headers and footers of each section
    for section in doc.sections:
        yield from iter_runs_in_container(section.header)
        yield from iter_runs_in_container(section.footer)

def extract_run_texts(doc):
    """Return a list of all run texts in document order."""
    return [run.text for run in iter_all_runs(doc)]

def replace_run_texts(doc, new_texts):
    """
    Replace the text of each run with the corresponding string from new_texts.
    new_texts must have the same length as the number of runs.
    """
    text_iter = iter(new_texts)
    for run in iter_all_runs(doc):
        run.text = next(text_iter)