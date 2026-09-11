from typing import Any, Dict, List, Tuple
import pandas as pd


class ExcelDataPipeline:

  def __init__(self, school_year: str, semester: str):
    self.school_year = school_year
    self.semester = semester
    # Evaluation rating criteria: E=Excellent, VG=Very Good, G=Good, S=Satisfactory, N=Needs Improvement
    self.valid_slo = {"E", "VG", "G", "S", "N", ""}

    # SLO 10개 필드 목록 정의
    self.slo_keys = [
        "slo_1_integrity",
        "slo_1_enthusiasm",
        "slo_2_integrity",
        "slo_2_enthusiasm",
        "slo_3_integrity",
        "slo_3_enthusiasm",
        "slo_4_integrity",
        "slo_4_enthusiasm",
        "slo_5_integrity",
        "slo_5_enthusiasm",
    ]

  def process(
      self,
      file_curricular: Any,
      file_awards: Any,
      file_volunteer: Any,
      file_activities: Any,
      file_slo: Any,
  ) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    warnings = []
    students: Dict[str, Dict[str, Any]] = {}

    # 1. Curricular Activities (Club Activity & Music / PA) + 학생 기본 명부
    df_base = pd.read_excel(file_curricular).fillna("")
    for _, row in df_base.iterrows():
      sid = str(row.get("student_id", "")).strip()
      if not sid:
        continue

      # 기본 구조 생성
      student_entry = {
          "school_year": self.school_year,
          "semester": self.semester,
          "student_name": str(row.get("student_name", "")).strip(),
          "grade": str(row.get("grade", row.get("Grade", row.get("학년", "")))).strip(),
          # Curricular 4개 빈칸
          "club_hours": str(row.get("club_hours", "")).strip(),
          "club_content": str(row.get("club_content", "")).strip(),
          "music_hours": str(row.get("music_hours", "")).strip(),
          "music_content": str(row.get("music_content", "")).strip(),
          # 동적 테이블 리스트 초기화
          "awards": [],
          "volunteer": [],
          "activities": [],
      }

      # SLO 10개 항목 기본값(빈칸) 세팅
      for key in self.slo_keys:
        student_entry[key] = ""

      students[sid] = student_entry

    # 2. Awards 내역 취합 (동적 행)
    df_awards = pd.read_excel(file_awards).fillna("")
    for _, row in df_awards.iterrows():
      sid = str(row.get("student_id", "")).strip()
      if sid in students:
        date_val = str(row.get("date", "")).split("T")[0].strip()
        students[sid]["awards"].append(
            {"date": date_val, "content": str(row.get("content", "")).strip()}
        )
      elif sid:
        warnings.append(f"[Awards] 기본 명부에 없는 학번: {sid}")

    # 3. Volunteer Work 내역 취합 (동적 행)
    df_vol = pd.read_excel(file_volunteer).fillna("")
    for _, row in df_vol.iterrows():
      sid = str(row.get("student_id", "")).strip()
      if sid in students:
        date_val = str(row.get("date", "")).split("T")[0].strip()
        students[sid]["volunteer"].append(
            {"date": date_val, "content": str(row.get("content", "")).strip()}
        )
      elif sid:
        warnings.append(f"[Volunteer] 기본 명부에 없는 학번: {sid}")

    # 4. Student Activities 내역 취합 (다중 클럽 동적 행)
    df_act = pd.read_excel(file_activities).fillna("")
    for _, row in df_act.iterrows():
      sid = str(row.get("student_id", "")).strip()
      if sid in students:
        students[sid]["activities"].append({
            "club_name": str(row.get("club_name", "")).strip(),
            "hours": str(row.get("hours", "")).strip(),
            "content": str(row.get("content", "")).strip(),
        })
      elif sid:
        warnings.append(f"[Activities] 기본 명부에 없는 학번: {sid}")

    # 5. SLO Evaluation 취합 (5개 영역 x 2 = 총 10개 필드 검증)
    df_slo = pd.read_excel(file_slo).fillna("")
    for _, row in df_slo.iterrows():
      sid = str(row.get("student_id", "")).strip()
      if sid in students:
        for key in self.slo_keys:
          val = str(row.get(key, "")).strip().upper()
          if val not in self.valid_slo:
            warnings.append(
                f"[SLO Error] {students[sid]['student_name']}({sid}) - {key} value"
                f" '{val}' is invalid (Expected: E, VG, G, S, N)"
            )
          students[sid][key] = val
      elif sid:
        warnings.append(f"[SLO] 기본 명부에 없는 학번: {sid}")

    return students, warnings