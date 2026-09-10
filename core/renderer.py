from typing import Any, Dict, List, BinaryIO, Union
import io
import zipfile
from docxtpl import DocxTemplate


class BatchRenderer:
    """
    BatchRenderer processes compiled student records and renders individual
    Word report cards from template.docx, packaging them into an in-memory zip file.
    """

    def __init__(self, template_source: Union[str, BinaryIO, bytes]):
        """
        Args:
            template_source: File path, file-like object, or raw bytes representing template.docx.
        """
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
        """
        Renders report cards for all students in the dictionary and returns a zip archive in memory.

        Args:
            students: Dictionary mapping student_id to compiled student context.

        Returns:
            io.BytesIO: In-memory zip archive buffer containing rendered .docx files.
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            for student_id, context in students.items():
                doc = DocxTemplate(io.BytesIO(self._template_bytes))
                doc.render(context)

                doc_buffer = io.BytesIO()
                doc.save(doc_buffer)
                doc_buffer.seek(0)

                student_name = context.get("student_name", "").strip()
                # Clean filename to remove invalid characters
                safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '_', '-')).strip()
                safe_id = "".join(c for c in student_id if c.isalnum() or c in (' ', '_', '-')).strip()

                if safe_name:
                    filename = f"ReportCard_{safe_id}_{safe_name}.docx"
                else:
                    filename = f"ReportCard_{safe_id}.docx"

                zip_file.writestr(filename, doc_buffer.getvalue())

        zip_buffer.seek(0)
        return zip_buffer
