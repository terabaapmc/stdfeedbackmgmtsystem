
import logging

import streamlit as st

from database import (
    calculate_average_rating,
    get_all_feedback,
    get_course_wise_summary,
    get_highest_rated_course,
    initialize_database,
    insert_feedback,
)


logger = logging.getLogger(__name__)

PAGE_OPTIONS = ("Overview", "Submit feedback", "All feedback", "Analytics")
PAGE_LABELS = {
    "Overview": "🏠  Overview",
    "Submit feedback": "✍️  Submit feedback",
    "All feedback": "📋  All feedback",
    "Analytics": "📊  Analytics",
}


def _show_feedback_form() -> None:
    st.header("✍️ Submit feedback")
    st.write("Share your experience to help improve our courses.")

    with st.container(border=True):
        with st.form("feedback_form", clear_on_submit=True):
            student_name = st.text_input("Student Name")
            course_name = st.text_input("Course Name")
            rating = st.selectbox(
                "Rating",
                options=(1, 2, 3, 4, 5),
                index=None,
                placeholder="Select a rating",
            )
            comments = st.text_area("Comments", placeholder="Optional")
            submitted = st.form_submit_button(
                "Submit feedback",
                type="primary",
                use_container_width=True,
            )

    if not submitted:
        return

    if not student_name.strip() or not course_name.strip() or rating is None:
        st.error("Please enter a student name, course name, and rating.")
        return

    try:
        insert_feedback(
            student_name=student_name,
            course_name=course_name,
            rating=rating,
            comments=comments.strip() or None,
        )
    except ValueError as exc:
        st.error(str(exc))
    except RuntimeError as exc:
        logger.exception("Feedback submission failed")
        st.error(f"Could not save feedback: {exc}")
    else:
        st.success("Feedback submitted successfully.")


def _show_feedback_table() -> None:
    st.header("📋 All feedback")
    st.write("Browse the feedback shared by students.")

    try:
        records = get_all_feedback()
    except RuntimeError as exc:
        logger.exception("Could not load feedback records")
        st.error(f"Could not load feedback records: {exc}")
        return

    if not records:
        st.info("No feedback has been submitted yet.")
        return

    display_records = [
        {
            "Feedback ID": record["feedback_id"],
            "Student Name": record["student_name"],
            "Course Name": record["course_name"],
            "Rating": record["rating"],
            "Comments": record["comments"] or "",
        }
        for record in records
    ]
    st.dataframe(display_records, hide_index=True, width="stretch")


def _show_analytics() -> None:
    st.header("📊 Feedback analytics")
    st.write("Explore overall satisfaction and course-by-course performance.")

    try:
        average_rating = calculate_average_rating()
    except RuntimeError as exc:
        logger.exception("Could not calculate the overall average rating")
        st.error(f"Could not calculate the overall average rating: {exc}")
    else:
        average_value = (
            f"{average_rating:.2f} / 5" if average_rating is not None else "N/A"
        )
        st.metric("⭐ Overall average rating", average_value)
        if average_rating is None:
            st.caption("An average will appear after feedback is submitted.")

    st.divider()
    st.subheader("🏆 Highest rated course")
    try:
        highest_rated_courses = get_highest_rated_course()
    except RuntimeError as exc:
        logger.exception("Could not load the highest-rated course")
        st.error(f"Could not load the highest-rated course: {exc}")
    else:
        if not highest_rated_courses:
            st.info("No course ratings are available yet.")
        elif len(highest_rated_courses) == 1:
            course = highest_rated_courses[0]
            st.metric(
                course["course_name"],
                f'{course["average_rating"]:.2f} / 5',
            )
        else:
            st.caption("Courses are tied for the highest average rating.")
            tied_courses = [
                {
                    "Course Name": course["course_name"],
                    "Average Rating": round(course["average_rating"], 2),
                }
                for course in highest_rated_courses
            ]
            st.dataframe(tied_courses, hide_index=True, width="stretch")

    st.divider()
    st.subheader("📚 Course-wise summary")
    try:
        summary = get_course_wise_summary()
    except RuntimeError as exc:
        logger.exception("Could not load the course-wise summary")
        st.error(f"Could not load the course-wise summary: {exc}")
    else:
        if not summary:
            st.info("No course summaries are available yet.")
        else:
            display_summary = [
                {
                    "Course Name": course["course_name"],
                    "Total Feedback": course["feedback_count"],
                    "Average Rating": round(course["average_rating"], 2),
                }
                for course in summary
            ]
            st.dataframe(display_summary, hide_index=True, width="stretch")


def _show_overview() -> None:
    st.subheader("DASHBOARD")
    st.title("🎓 Overview")
    st.write("A snapshot of student sentiment and course performance.")

    try:
        average_rating = calculate_average_rating()
        feedback_records = get_all_feedback()
        highest_rated_courses = get_highest_rated_course()
    except RuntimeError as exc:
        logger.exception("Could not load dashboard overview")
        st.error(f"Could not load dashboard overview: {exc}")
        return

    average_value = f"{average_rating:.2f} / 5" if average_rating is not None else "—"
    if not highest_rated_courses:
        highest_course_name = "No ratings yet"
        highest_course_average = "Submit the first review"
    elif len(highest_rated_courses) == 1:
        highest_course = highest_rated_courses[0]
        highest_course_name = highest_course["course_name"]
        highest_course_average = f'{highest_course["average_rating"]:.2f} / 5'
    else:
        highest_course_name = ", ".join(
            course["course_name"] for course in highest_rated_courses
        )
        highest_course_average = (
            f'{highest_rated_courses[0]["average_rating"]:.2f} / 5 · tied'
        )

    st.markdown("#### At a glance")
    feedback_column, average_column, course_column = st.columns(3)
    with feedback_column:
        st.metric("📝 Total feedback", len(feedback_records))
    with average_column:
        st.metric("⭐ Overall average rating", average_value)
    with course_column:
        st.metric(
            "🏆 Highest rated course",
            highest_course_name,
            delta=highest_course_average,
            delta_color="off",
        )

    st.divider()
    st.subheader("🕒 Recent feedback")
    if not feedback_records:
        st.info("No feedback has been submitted yet. Add the first response to get started.")
        return

    recent_records = [
        {
            "Student Name": record["student_name"],
            "Course Name": record["course_name"],
            "Rating": f'{record["rating"]} / 5',
            "Comments": record["comments"] or "—",
        }
        for record in reversed(feedback_records[-5:])
    ]
    with st.container(border=True):
        st.dataframe(recent_records, hide_index=True, width="stretch")


def main() -> None:
    st.set_page_config(
        page_title="Student Feedback Management",
        page_icon=":material/rate_review:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        :root {
            --feedback-ink: #172b4d;
            --feedback-muted: #63748b;
            --feedback-accent: #356ae6;
            --feedback-surface: #ffffff;
            --feedback-border: #e4eaf3;
        }
        .stApp { background: #f5f7fb; color: var(--feedback-ink); }
        [data-testid="stSidebar"] {
            background: var(--feedback-surface);
            border-right: 1px solid var(--feedback-border);
        }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px; }
        h1, h2, h3 { color: var(--feedback-ink); letter-spacing: -0.02em; }
        [data-testid="stCaptionContainer"] p { color: var(--feedback-muted); }
        [data-testid="stMetric"] {
            background: var(--feedback-surface);
            border: 1px solid var(--feedback-border);
            border-left: 4px solid var(--feedback-accent);
            border-radius: 0.85rem;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 4px 14px rgba(23, 43, 77, 0.04);
            min-height: 108px;
        }
        [data-testid="stMetricLabel"] p {
            color: var(--feedback-muted);
            font-weight: 600;
        }
        [data-testid="stMetricValue"] {
            color: var(--feedback-ink);
            font-size: 1.8rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--feedback-surface);
            border-radius: 0.85rem;
        }
        [data-testid="stRadio"] label { font-weight: 500; }
        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] button {
            border-radius: 0.6rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("🎓 Student Feedback Management")
    st.caption("A clear view of student feedback and course performance")

    with st.sidebar:
        st.markdown("## 🎓 Feedback Portal")
        st.caption("Student feedback dashboard")
        st.divider()
        page = st.radio(
            "Navigate",
            PAGE_OPTIONS,
            format_func=lambda option: PAGE_LABELS[option],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Understand feedback. Improve courses.")

    try:
        initialize_database()
    except RuntimeError as exc:
        logger.exception("Could not initialize the application database")
        st.error(f"Could not initialize the application database: {exc}")
        st.stop()

    if page == "Overview":
        _show_overview()
    elif page == "Submit feedback":
        _show_feedback_form()
    elif page == "All feedback":
        _show_feedback_table()
    else:
        _show_analytics()


if __name__ == "__main__":
    main()
