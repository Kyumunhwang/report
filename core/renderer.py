import os
import io
import re
import zipfile
from typing import Any, Dict, Union, BinaryIO
import docxtpl
from docxtpl import DocxTemplate


def patch_docxtpl_for_tables():
    def custom_patch_xml(self, src_xml: str) -> str:
        src_xml = re.sub(
            r'(?<={)(<[^>]*>)+(?=[\{%\#])|(?<=[%\}\#])(<[^>]*>)+(?=\})',
            '',
            src_xml,
            flags=re.DOTALL,
        )

        def striptags(m):
            return re.sub(r'</w:t>.*?(<w:t>|<w:t [^>]*>)', '', m.group(0), flags=re.DOTALL)

        src_xml = re.sub(
            r'{%(?:(?!%}).)*|{#(?:(?!#}).)*|{{(?:(?!}}).)*',
            striptags,
            src_xml,
            flags=re.DOTALL,
        )

        def replace_tr(m):
            row_content = m.group(0)
            m_for = re.search(r'\{%\s*tr\s+for\s+([^%]+)%\}(.*)', row_content, flags=re.DOTALL)
            if not m_for:
                return row_content
            for_expr = m_for.group(1).strip()
            cleaned_row = re.sub(r'\{%\s*tr\s+for\s+[^%]+%\}', '', row_content)
            cleaned_row = re.sub(r'\{%\s*tr\s*endfor\s*%\}|\{%\s*trendfor\s*%\}', '', cleaned_row)
            return '{% for ' + for_expr + ' %}' + cleaned_row + '{% endfor %}'

        pat = r'<w:tr[ >].*?\{%\s*tr\s+for\s+.*?trendfor\s*%\}.*?</w:tr>'
        patched = re.sub(pat, replace_tr, src_xml, flags=re.DOTALL)

        def clean_tags(m):
            return (
                m.group(0)
                .replace(r'&#8216;', "'")
                .replace('&lt;', '<')
                .replace('&gt;', '>')
            )

        patched = re.sub(r'(?<=\{[\{%])(.*?)(?=[\}%]})', clean_tags, patched)
        return patched

    docxtpl.DocxTemplate.patch_xml = custom_patch_xml


patch_docxtpl_for_tables()


class BatchRenderer:
    def __init__(self, template_source: Union[str, BinaryIO, bytes]):
        if isinstance(template_source, (bytes, bytearray)):
            self._template_bytes = bytes(template_source)
        elif hasattr(template_source, 'read'):
            current_pos = template_source.tell() if hasattr(template_source, 'tell') else None
            self._template_bytes = template_source.read()
            if current_pos is not None and hasattr(template_source, 'seek'):
                template_source.seek(current_pos)
        elif isinstance(template_source, str):
            with open(template_source, 'rb') as f:
                self._template_bytes = f.read()
        else:
            raise ValueError("Unsupported template source type.")

    def render_all(self, students: Dict[str, Dict[str, Any]]) -> io.BytesIO:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            for student_id, context in students.items():
                doc = DocxTemplate(io.BytesIO(self._template_bytes))
                doc.render(context)

                doc_buffer = io.BytesIO()
                doc.save(doc_buffer)
                doc_buffer.seek(0)

                grade = str(context.get("grade", "")).strip()
                student_name = str(context.get("student_name", "")).strip()

                safe_grade = "".join(c for c in grade if c.isalnum() or c in (' ', '_', '-')).strip()
                safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '_', '-')).strip()
                safe_id = "".join(c for c in student_id if c.isalnum() or c in (' ', '_', '-')).strip()

                # Filename format: Grade_Name.docx (or Name.docx if no grade)
                if safe_grade and safe_name:
                    filename = f"{safe_grade}_{safe_name}.docx"
                elif safe_name:
                    filename = f"{safe_name}.docx"
                elif safe_grade and safe_id:
                    filename = f"{safe_grade}_{safe_id}.docx"
                else:
                    filename = f"ReportCard_{safe_id}.docx"

                zip_file.writestr(filename, doc_buffer.getvalue())

        zip_buffer.seek(0)
        return zip_buffer
