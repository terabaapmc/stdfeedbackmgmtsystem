# Student Feedback Management System

A lightweight web application for collecting student feedback and reviewing
course ratings. Built with Python, Streamlit, and SQLite, it provides a simple
dashboard for submitting feedback, browsing responses, and comparing course
ratings.

## Project Objectives

- Provide a straightforward way to record student feedback.
- Store feedback persistently in a local SQLite database.
- Summarize overall and course-level ratings.
- Demonstrate a simple database-backed web application suitable for an
  academic software engineering project.

## Technologies Used

- **Python** — application and database logic.
- **Streamlit** — interactive web interface.
- **SQLite** — local relational database, accessed using Python's built-in
  `sqlite3` module.

## System Requirements

- Python **3.10 or later**.
- A web browser.
- Internet access when installing Streamlit.
- Windows, macOS, or Linux.

SQLite is included with Python; no separate database server is needed.

## Project Folder Structure

```text
student-feedback-management-system/
├── app.py          # Streamlit pages, feedback form, and dashboard
├── database.py     # SQLite setup and feedback database operations
├── feedback.db     # Created automatically when the app initializes
├── req.txt         # Present in this project; currently empty
└── README.md       # Project documentation
```

The `venv/` directory, if present, contains a local virtual environment. It is
created during setup and is not required to be committed with the project.
`feedback.db` is generated beside `database.py` the first time the app runs.

## Database Design

The database file is named `feedback.db` and contains one table, `feedback`.

| Column | SQLite type | Constraints | Description |
|---|---|---|---|
| `feedback_id` | INTEGER | Primary key, auto-increment | Unique feedback record ID |
| `student_name` | TEXT | Not null | Name of the student |
| `course_name` | TEXT | Not null | Name of the course |
| `rating` | INTEGER | Not null, between 1 and 5 | Student's course rating |
| `comments` | TEXT | Optional | Additional written feedback |

The table is initialized automatically by `database.initialize_database()`.
Database operations are implemented in `database.py`; the Streamlit interface
uses those functions rather than issuing SQL directly.

## Features and Functionality

- **Dashboard overview:** Displays total feedback, overall average rating,
  highest-rated course, and recent responses.
- **Submit feedback:** Collects student name, course name, a rating from 1 to 5,
  and optional comments. Required fields and ratings are validated.
- **View all feedback:** Shows submitted records in a table.
- **Overall average:** Calculates and displays the average of submitted ratings.
- **Highest-rated course:** Compares course average ratings and handles ties.
- **Course-wise summary:** Shows each course's feedback count and average rating.
- **Empty-state handling:** Displays suitable messages when no feedback is
  available.

## Installation

Open a terminal in the project directory:

```powershell
cd "C:\path\to\student-feedback-management-system"
```

Create and activate a virtual environment. In Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell does not recognize the `python` command, use the Python launcher
(`py`) to create the environment, or invoke the environment's interpreter
directly as shown below.

On macOS or Linux, use:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Package Installation

Install Streamlit in the activated environment:

```bash
python -m pip install streamlit
```

On Windows, if the environment is not activated, use:

```powershell
.\venv\Scripts\python.exe -m pip install streamlit
```

The `req.txt` file is currently empty, so install Streamlit with the command
above rather than relying on that file.

## Run the Application

From the project directory, with the virtual environment activated, run:

```bash
streamlit run app.py
```

Streamlit opens the application in your default browser. If it does not, open
the local URL printed in the terminal. The database and feedback table are
created automatically on startup.

## Testing Details

The current application was exercised with Streamlit's app test runner and an
isolated temporary SQLite database. The test scenarios covered:

- Valid feedback submission and persistence.
- Empty student name and empty course name validation.
- Ratings below 1 or above 5.
- Display of saved feedback records.
- Correct overall average and highest-rated course.
- Course-wise averages and aggregation of repeated course names.
- Empty-database behavior.

All ten scenarios passed in the final test run. The temporary test database was
used so the tests did not modify the project's regular database. No automated
test files are currently included in the project.

## Future Enhancements

- Add student or administrator authentication and role-based access.
- Add search, filtering, and sorting for feedback records.
- Allow feedback export to CSV or Excel.
- Add date/time tracking and trend charts.
- Add course management and stronger duplicate-course name normalization.
- Add automated unit and UI tests to the project.
- Document and pin dependencies in a populated requirements file.
