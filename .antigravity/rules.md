# Antigravity Rules: School Report Card Generator

1. Word 템플릿(template.docx) 서식을 손상시키지 말 것.
2. 표의 동적 행 확장은 docxtpl의 {%tr for ... %} 구문 규칙을 준수할 것.
3. 엑셀 파일들을 디스크에 병합하지 말고, Pandas 메모리 상에서 student_id 기준으로 가상 취합할 것.
4. SLO 평가는 E, VG, G, S, N 값 유효성 검사를 수행할 것.
5. UI는 Streamlit을 사용하고 비즈니스 로직과 화면 코드를 분리할 것.