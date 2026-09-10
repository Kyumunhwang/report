from typing import Dict
import io
import pandas as pd


class SampleDataGenerator:
    """
    Generates in-memory sample Excel templates with valid column headers and dummy data.
    """

    @staticmethod
    def get_sample_curricular() -> bytes:
        data = [
            {
                "student_id": "2026001",
                "student_name": "Alice Kim",
                "club_hours": "30",
                "club_content": "Active participation in Coding Club and algorithm study.",
                "music_hours": "20",
                "music_content": "Played violin in the school orchestra.",
            },
            {
                "student_id": "2026002",
                "student_name": "Brian Park",
                "club_hours": "25",
                "club_content": "Led debate sessions in Model United Nations.",
                "music_hours": "20",
                "music_content": "Vocal choir member and solo performance.",
            },
        ]
        return SampleDataGenerator._to_excel_bytes(data)

    @staticmethod
    def get_sample_awards() -> bytes:
        data = [
            {
                "student_id": "2026001",
                "date": "2026-03-15",
                "content": "1st Place - School Science Fair",
            },
            {
                "student_id": "2026001",
                "date": "2026-05-20",
                "content": "Excellence Award - Math Olympiad",
            },
            {
                "student_id": "2026002",
                "date": "2026-04-10",
                "content": "Best Delegate - MUN Conference",
            },
        ]
        return SampleDataGenerator._to_excel_bytes(data)

    @staticmethod
    def get_sample_volunteer() -> bytes:
        data = [
            {
                "student_id": "2026001",
                "date": "2026-04-12",
                "content": "Community Library Book Organizing (8 hours)",
            },
            {
                "student_id": "2026002",
                "date": "2026-05-01",
                "content": "Peer Tutoring in English and Mathematics (10 hours)",
            },
        ]
        return SampleDataGenerator._to_excel_bytes(data)

    @staticmethod
    def get_sample_activities() -> bytes:
        data = [
            {
                "student_id": "2026001",
                "club_name": "Robotics Society",
                "hours": "15",
                "content": "Designed sensor modules for competition robot.",
            },
            {
                "student_id": "2026001",
                "club_name": "School Newspaper",
                "hours": "12",
                "content": "Authored monthly STEM review articles.",
            },
            {
                "student_id": "2026002",
                "club_name": "Student Council",
                "hours": "20",
                "content": "Managed campus events and student orientation.",
            },
        ]
        return SampleDataGenerator._to_excel_bytes(data)

    @staticmethod
    def get_sample_slo() -> bytes:
        data = [
            {
                "student_id": "2026001",
                "slo_1_integrity": "E",
                "slo_1_enthusiasm": "VG",
                "slo_2_integrity": "VG",
                "slo_2_enthusiasm": "E",
                "slo_3_integrity": "G",
                "slo_3_enthusiasm": "VG",
                "slo_4_integrity": "E",
                "slo_4_enthusiasm": "E",
                "slo_5_integrity": "VG",
                "slo_5_enthusiasm": "G",
            },
            {
                "student_id": "2026002",
                "slo_1_integrity": "VG",
                "slo_1_enthusiasm": "E",
                "slo_2_integrity": "E",
                "slo_2_enthusiasm": "VG",
                "slo_3_integrity": "VG",
                "slo_3_enthusiasm": "G",
                "slo_4_integrity": "VG",
                "slo_4_enthusiasm": "E",
                "slo_5_integrity": "E",
                "slo_5_enthusiasm": "VG",
            },
        ]
        return SampleDataGenerator._to_excel_bytes(data)

    @staticmethod
    def _to_excel_bytes(data: list) -> bytes:
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer.getvalue()
