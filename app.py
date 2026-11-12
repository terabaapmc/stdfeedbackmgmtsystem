
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
    st.caption("DASHBOARD OVERVIEW")
    st.title("Feedback, at a glance")
    st.write(
        "A welcoming space to share feedback and understand course performance."
    )

    try:
        average_rating = calculate_average_rating()
        feedback_records = get_all_feedback()
        highest_rated_courses = get_highest_rated_course()
    except RuntimeError as exc:
        logger.exception("Could not load dashboard overview")
        st.error(f"Could not load dashboard overview: {exc}")
        return

    if not highest_rated_courses:
        highest_course_name = "No ratings yet"
        highest_course_average = "—"
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

    st.markdown("#### Key indicators")
    feedback_column, average_column, course_column = st.columns(3)
    with feedback_column:
        st.metric("📝 Total feedback", len(feedback_records))
    with average_column:
        st.metric(
            "⭐ Overall average rating",
            f"{average_rating:.2f} / 5" if average_rating is not None else "—",
        )
    with course_column:
        st.metric(
            "🏆 Highest rated course",
            highest_course_average,
            delta=highest_course_name,
            delta_color="off",
        )

    st.divider()
    st.subheader("🕒 Recent feedback")
    if not feedback_records:
        st.info(
            "No feedback has been submitted yet. Add the first response to get started."
        )
        st.markdown(
            """
            <div class="welcome-card">
                <div class="welcome-icon">✍️</div>
                <div>
                    <strong>Your feedback helps courses grow.</strong>
                    <p>Share a rating and a few thoughts to get the dashboard started.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
        [data-testid="stMain"] > div { background: transparent; }
        [data-testid="stSidebar"] {
            background: var(--feedback-surface);
            border-right: 1px solid var(--feedback-border);
        }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px; }
        h1, h2, h3 { color: var(--feedback-ink); letter-spacing: -0.02em; }
        [data-testid="stCaptionContainer"] p { color: var(--feedback-muted); }
        [data-testid="stMarkdownContainer"] p { line-height: 1.65; }
        [data-testid="stRadio"] > label { display: none; }
        [data-testid="stRadio"] label[data-testid="stWidgetLabel"] { display: none; }
        [data-testid="stRadio"] div[role="radiogroup"] {
            gap: 0.35rem;
        }
        [data-testid="stRadio"] div[role="radiogroup"] label {
            padding: 0.55rem 0.75rem;
            border-radius: 0.65rem;
            transition: background-color 140ms ease, color 140ms ease;
        }
        [data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background: #eef3ff;
        }
        [data-testid="stRadioOption"] input[type="radio"] {
            accent-color: var(--feedback-accent);
        }
        [data-testid="stMetric"] {
            background: var(--feedback-surface);
            border: 1px solid var(--feedback-border);
            border-left: 4px solid var(--feedback-accent);
            border-radius: 0.85rem;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 4px 14px rgba(23, 43, 77, 0.04);
            min-height: 108px;
            transition: transform 140ms ease, box-shadow 140ms ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(23, 43, 77, 0.08);
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
            border-color: var(--feedback-border);
            box-shadow: 0 4px 14px rgba(23, 43, 77, 0.035);
        }
        [data-testid="stForm"] {
            padding: 1.35rem;
            border: 1px solid var(--feedback-border);
            border-radius: 0.85rem;
            background: var(--feedback-surface);
            box-shadow: 0 4px 14px rgba(23, 43, 77, 0.035);
        }
        .welcome-card {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-top: 1rem;
            padding: 1.2rem 1.4rem;
            border: 1px solid var(--feedback-border);
            border-radius: 0.85rem;
            background: linear-gradient(110deg, #ffffff 0%, #edf3ff 100%);
            color: var(--feedback-ink);
        }
        .welcome-icon {
            display: grid;
            width: 2.8rem;
            height: 2.8rem;
            flex: 0 0 2.8rem;
            place-items: center;
            border-radius: 0.75rem;
            background: #e3ecff;
            font-size: 1.35rem;
        }
        .welcome-card p {
            margin: 0.2rem 0 0;
            color: var(--feedback-muted);
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 0.2rem 0 0.35rem;
            color: var(--feedback-ink);
            font-size: 1.15rem;
            font-weight: 750;
            letter-spacing: -0.02em;
        }
        .sidebar-brand-icon {
            display: grid;
            width: 2rem;
            height: 2rem;
            place-items: center;
            border-radius: 0.6rem;
            background: #e8efff;
        }
        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] {
            background: var(--feedback-accent);
            border-color: var(--feedback-accent);
            color: #ffffff;
            border-radius: 0.6rem;
            font-weight: 600;
        }
        .stButton > button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]:hover {
            background: #2456c4;
            border-color: #2456c4;
            color: #ffffff;
        }
        [data-testid="stDataFrame"] {
            border: 1px solid var(--feedback-border);
            border-radius: 0.75rem;
            overflow: hidden;
        }
        @media (max-width: 700px) {
            .block-container { padding: 1.25rem 1rem 2rem; }
            [data-testid="stMetric"] { min-height: 96px; padding: 0.9rem; }
            [data-testid="stMetricValue"] { font-size: 1.45rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <span class="sidebar-brand-icon">🎓</span>
                <span>Feedback Portal</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
