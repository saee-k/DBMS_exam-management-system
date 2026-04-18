import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------- DATABASE ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="saee2804",
    database="examination_system"
)

cursor = conn.cursor()

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None

if not st.session_state.logged_in:

    st.title("🎓 Examination Management System Login")

    full_name = st.text_input("Full Name")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        cursor.execute("""
            SELECT full_name, password, role 
            FROM USERS 
            WHERE full_name=%s
        """, (full_name,))

        user = cursor.fetchone()

        if user:
            db_name, db_pass, db_role = user

            if password == db_pass:
                st.session_state.logged_in = True
                st.session_state.user = db_name
                st.session_state.role = db_role
                st.success(f"Welcome {db_name} ({db_role}) ✅")
            else:
                st.error("Wrong Password ❌")
        else:
            st.error("User not found ❌")

    st.stop()

st.sidebar.success(f"Logged in as: {st.session_state.user} ({st.session_state.role})")

# ---------------- MENU ----------------
menu = st.sidebar.selectbox(
    "Select Option",
    ["Dashboard", "Course", "Room", "Section", "Exam", "Attendance", "Report"]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    st.subheader("📊 Project Dashboard")

    course_count = pd.read_sql("SELECT COUNT(*) as total FROM COURSE", conn)["total"][0]
    room_count = pd.read_sql("SELECT COUNT(*) as total FROM ROOM", conn)["total"][0]
    section_count = pd.read_sql("SELECT COUNT(*) as total FROM SECTION", conn)["total"][0]
    exam_count = pd.read_sql("SELECT COUNT(*) as total FROM EXAM", conn)["total"][0]
    attendance_count = pd.read_sql("SELECT COUNT(*) as total FROM ATTENDANCE", conn)["total"][0]

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Courses", course_count)
    col2.metric("Rooms", room_count)
    col3.metric("Sections", section_count)
    col4.metric("Exams", exam_count)
    col5.metric("Attendance", attendance_count)

    st.markdown("---")

    labels = ["Courses", "Rooms", "Sections", "Exams", "Attendance"]
    values = [course_count, room_count, section_count, exam_count, attendance_count]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    st.pyplot(fig)

# ---------------- COURSE ----------------
elif menu == "Course":

    st.subheader("Course Management")

    course_no = st.number_input("Course No", min_value=1, step=1)
    name = st.text_input("Course Name")
    dept = st.text_input("Department")

    if st.button("Add Course"):
        cursor.execute("INSERT INTO COURSE VALUES (%s,%s,%s)",
                       (course_no, name, dept))
        conn.commit()
        st.success("Course Added ✅")

    st.dataframe(pd.read_sql("SELECT * FROM COURSE", conn))

# ---------------- ROOM ----------------
elif menu == "Room":

    st.subheader("Room Management")

    r_no = st.number_input("Room No", min_value=1, step=1)
    cap = st.number_input("Capacity", min_value=1, step=1)
    building = st.text_input("Building")

    if st.button("Add Room"):
        cursor.execute("INSERT INTO ROOM VALUES (%s,%s,%s)",
                       (r_no, cap, building))
        conn.commit()
        st.success("Room Added ✅")

    st.dataframe(pd.read_sql("SELECT * FROM ROOM", conn))

# ---------------- SECTION ----------------
elif menu == "Section":

    st.subheader("Section Management")

    s_no = st.number_input("Section No", min_value=1, step=1)
    enroll = st.number_input("Enrollment", min_value=1, step=1)

    course_df = pd.read_sql("SELECT course_no FROM COURSE", conn)
    course_no = st.selectbox("Select Course", course_df["course_no"].tolist())

    if st.button("Add Section"):
        cursor.execute("INSERT INTO SECTION VALUES (%s,%s,%s)",
                       (s_no, enroll, course_no))
        conn.commit()
        st.success("Section Added ✅")

    st.dataframe(pd.read_sql("SELECT * FROM SECTION", conn))

# ---------------- EXAM ----------------
elif menu == "Exam":

    st.subheader("Exam Scheduling")

    exam_id = st.number_input("Exam ID", min_value=1, step=1)

    course_df = pd.read_sql("SELECT course_no FROM COURSE", conn)
    section_df = pd.read_sql("SELECT s_no FROM SECTION", conn)
    room_df = pd.read_sql("SELECT r_no FROM ROOM", conn)

    course_no = st.selectbox("Course", course_df["course_no"].tolist())
    s_no = st.selectbox("Section", section_df["s_no"].tolist())
    r_no = st.selectbox("Room", room_df["r_no"].tolist())

    date = st.date_input("Date")
    time = st.time_input("Time")

    if st.button("Schedule Exam"):

        dt = datetime.combine(date, time)

        cursor.execute("""
            SELECT * FROM EXAM 
            WHERE r_no=%s AND exam_time=%s
        """, (r_no, dt))

        if cursor.fetchall():
            st.error("❌ Exam Clash")
        else:
            cursor.execute(
                "INSERT INTO EXAM VALUES (%s,%s,%s,%s,%s)",
                (exam_id, course_no, s_no, r_no, dt)
            )
            conn.commit()
            st.success("Exam Scheduled ✅")

# ---------------- ATTENDANCE ----------------
elif menu == "Attendance":

    st.subheader("Attendance System")

    att_id = st.number_input("Attendance ID", min_value=1, step=1)

    exam_df = pd.read_sql("SELECT exam_id FROM EXAM", conn)
    exam_id = st.selectbox("Exam", exam_df["exam_id"].tolist())

    student = st.text_input("Student Name")
    status = st.selectbox("Status", ["Present", "Absent"])

    if st.button("Mark Attendance"):
        cursor.execute(
            "INSERT INTO ATTENDANCE VALUES (%s,%s,%s,%s)",
            (att_id, exam_id, student, status)
        )
        conn.commit()
        st.success("Attendance Marked ✅")

    st.dataframe(pd.read_sql("SELECT * FROM ATTENDANCE", conn))

# ---------------- REPORT ----------------
elif menu == "Report":

    st.subheader("Exam Report")

    query = """
    SELECT EXAM.exam_id, COURSE.name, SECTION.s_no, ROOM.r_no, ROOM.building, EXAM.exam_time
    FROM EXAM
    JOIN COURSE ON EXAM.course_no = COURSE.course_no
    JOIN SECTION ON EXAM.s_no = SECTION.s_no
    JOIN ROOM ON EXAM.r_no = ROOM.r_no
    """

    df = pd.read_sql(query, conn)
    st.dataframe(df)
