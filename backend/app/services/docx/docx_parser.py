import zipfile
from pathlib import Path
from lxml import etree


class DocxParser:
    DOCUMENT_PATH = "word/document.xml"
    def __init__(self, docx_path: str):
        self.docx_path = Path(docx_path)
        with zipfile.ZipFile(self.docx_path) as z:
            xml_content = z.read(self.DOCUMENT_PATH)
        self.tree = etree.fromstring(xml_content)
        self.ns = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

    def get_paragraphs(self):
        paragraphs = self.tree.xpath("//w:p", namespaces=self.ns)
        return paragraphs
    
    def get_paragraph_text(self, paragraph):
        texts = paragraph.xpath(".//w:t", namespaces=self.ns)
        return "".join(t.text for t in texts if t.text)
    
    def extract_text(self):
        paragraphs = self.get_paragraphs()
        text_blocks = []
        for p in paragraphs:
            text = self.get_paragraph_text(p)
            if text.strip():
                text_blocks.append(text)
        return text_blocks
    
    def save(self, output_path):
        xml_bytes = etree.tostring(
            self.tree,
            xml_declaration=True,
            encoding="UTF-8",
            standalone="yes"
        )
        with zipfile.ZipFile(self.docx_path) as zin:
            with zipfile.ZipFile(output_path, "w") as zout:
                for item in zin.infolist():
                    if item.filename != self.DOCUMENT_PATH:
                        zout.writestr(
                            item,
                            zin.read(item.filename)
                        )
                zout.writestr(self.DOCUMENT_PATH, xml_bytes)


"""
parser = DocxParser("contract.docx")
paragraphs = parser.extract_text()
print(paragraphs)
"""