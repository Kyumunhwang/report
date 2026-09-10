import os
import streamlit as st
from core.pipeline import ExcelDataPipeline
from core.renderer import BatchRenderer
from core.samples import SampleDataGenerator

st.set_page_config(
    page_title="Student Report Card Generator",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Student Report Card Generator")
st.markdown("Download sample templates, fill them in, upload your files, and generate student report card Word documents in batch as a ZIP package.")

with st.sidebar:
    st.header("Configuration")
    school_year = st.text_input("School Year", value="2025-2026")
    semester = st.selectbox("Semester", options=["Semester 1", "Semester 2", "Summer Session"])

st.subheader("1. Download Sample Excel Templates")
st.caption("Download the pre-formatted Excel template files below, fill in your student data, and upload them in the next section.")

s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)

with s_col1:
    st.download_button(
        label="📥 Sample Curricular",
        data=SampleDataGenerator.get_sample_curricular(),
        file_name="sample_curricular.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with s_col2:
    st.download_button(
        label="📥 Sample Awards",
        data=SampleDataGenerator.get_sample_awards(),
        file_name="sample_awards.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with s_col3:
    st.download_button(
        label="📥 Sample Volunteer",
        data=SampleDataGenerator.get_sample_volunteer(),
        file_name="sample_volunteer.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with s_col4:
    st.download_button(
        label="📥 Sample Activities",
        data=SampleDataGenerator.get_sample_activities(),
        file_name="sample_activities.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with s_col5:
    st.download_button(
        label="📥 Sample SLO",
        data=SampleDataGenerator.get_sample_slo(),
        file_name="sample_slo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.markdown("---")
st.subheader("2. Upload Input Files")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Word Template")
    file_template = st.file_uploader(
        "Upload Word Template (.docx)",
        type=["docx"],
        key="template_docx",
        help="Leave empty to use the default 'template.docx' in the project directory if available."
    )
    if not file_template and os.path.exists("template.docx"):
        st.info("Using default template: template.docx")

    st.markdown("##### Basic Student List & Curricular Activities")
    file_curricular = st.file_uploader(
        "Upload Curricular File (student_id, student_name, club_hours, etc.)",
        type=["xlsx", "xls"],
        key="curricular_file"
    )

    st.markdown("##### Student Awards")
    file_awards = st.file_uploader(
        "Upload Awards File (student_id, date, content)",
        type=["xlsx", "xls"],
        key="awards_file"
    )

with col2:
    st.markdown("##### Volunteer Work")
    file_volunteer = st.file_uploader(
        "Upload Volunteer File (student_id, date, content)",
        type=["xlsx", "xls"],
        key="volunteer_file"
    )

    st.markdown("##### Student Activities")
    file_activities = st.file_uploader(
        "Upload Activities File (student_id, club_name, hours, content)",
        type=["xlsx", "xls"],
        key="activities_file"
    )

    st.markdown("##### SLO Evaluation")
    file_slo = st.file_uploader(
        "Upload SLO File (student_id, slo_1_integrity ~ slo_5_enthusiasm)",
        type=["xlsx", "xls"],
        key="slo_file"
    )

st.markdown("---")

if st.button("Generate Report Cards", type="primary", use_container_width=True):
    # Determine template source
    template_src = None
    if file_template is not None:
        template_src = file_template
    elif os.path.exists("template.docx"):
        template_src = "template.docx"

    if template_src is None:
        st.error("Please upload a Word template file (.docx) or ensure 'template.docx' exists in the project root.")
    elif not all([file_curricular, file_awards, file_volunteer, file_activities, file_slo]):
        st.error("Please upload all 5 required Excel files before generating report cards.")
    else:
        with st.spinner("Processing Excel data and compiling student records..."):
            pipeline = ExcelDataPipeline(school_year=school_year, semester=semester)
            students, warnings = pipeline.process(
                file_curricular=file_curricular,
                file_awards=file_awards,
                file_volunteer=file_volunteer,
                file_activities=file_activities,
                file_slo=file_slo,
            )

        if warnings:
            st.warning(f"Validation completed with {len(warnings)} warning(s):")
            with st.expander("View Warning Details", expanded=True):
                for w in warnings:
                    st.write(f"- {w}")
        else:
            st.success("Data validation passed with 0 warnings!")

        if not students:
            st.error("No student records found in the uploaded Curricular file.")
        else:
            with st.spinner(f"Rendering Word report cards for {len(students)} student(s) into ZIP..."):
                renderer = BatchRenderer(template_src)
                zip_buffer = renderer.render_all(students)

            st.success(f"Successfully generated report cards for {len(students)} student(s)!")

            zip_filename = f"ReportCards_{school_year}_{semester}.zip".replace(" ", "_")
            st.download_button(
                label="📥 Download Report Cards (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=zip_filename,
                mime="application/zip",
                use_container_width=True
            )
