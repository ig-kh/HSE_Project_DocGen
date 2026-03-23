import re
from schemas.extraction import ExtractedContract


class DocxRenderer:
    """
    Replace template placeholders with extracted contract values.
    """

    def render(self, parser, extracted: ExtractedContract):

        paragraphs = parser.get_paragraphs()

        values = self.build_value_map(extracted)

        for paragraph in paragraphs:

            self.replace_placeholders(parser, paragraph, values)

    def build_value_map(self, extracted: ExtractedContract):

        values = {
            "counterparty": extracted.counterparty,
            "date": extracted.date,
            "city": extracted.city,
            "work": extracted.work,
            "work_time_days": extracted.work_time_days,
        }

        if extracted.cost:

            values["cost"] = f"{extracted.cost.amount} {extracted.cost.currency}"

        return values

    def replace_placeholders(self, parser, paragraph, values):

        texts = paragraph.xpath(".//w:t", namespaces=parser.ns)

        for t in texts:

            if not t.text:
                continue

            for key, value in values.items():

                if value is None:
                    continue

                placeholder = "{{" + key + "}}"

                t.text = t.text.replace(placeholder, str(value))