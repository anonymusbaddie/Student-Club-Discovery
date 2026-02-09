import streamlit as st
from data.clubs import clubs
import os

FILE_PATH = "data/applications.txt"

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Club Platform", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>
.main { background-color: #0f172a; }

.card {
    padding: 18px;
    border-radius: 14px;
    background: rgba(30, 41, 59, 0.9);
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    margin-bottom: 12px;
    color: #e5e7eb;
}
.card h3 { color: #f8fafc; }

.submitted { color:#38bdf8; font-weight:bold; }
.interview { color:#facc15; font-weight:bold; }
.approved { color:#22c55e; font-weight:bold; }
.rejected { color:#ef4444; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Club Discovery & Enrollment Platform")

# ---------------- HELPERS ----------------
def read_apps():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        return [line.strip().split(",", 5) for line in f if line.strip()]

def write_apps(apps):
    with open(FILE_PATH, "w") as f:
        for a in apps:
            f.write(",".join(a) + "\n")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["🏫 Clubs", "📄 Application Status", "🔐 Admin"])

# ================= TAB 1: APPLY =================
with tab1:
    st.subheader("Explore Clubs")

    c1, c2 = st.columns(2)
    search = c1.text_input("Search club")
    category = c2.selectbox("Category", ["All", "Tech", "Arts", "Sports"])

    for club in clubs:
        if (search.lower() in club["name"].lower()) and (
            category == "All" or club["category"] == category
        ):
            st.markdown(f"""
            <div class="card">
                <h3>{club['name']}</h3>
                <p><b>Category:</b> {club['category']}</p>
                <p>{club['description']}</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Apply to {club['name']}"):
                with st.form(f"form_{club['name']}"):
                    sid = st.text_input("Student ID")
                    name = st.text_input("Name")
                    email = st.text_input("Email")
                    interest = st.text_area("Why do you want to join?")

                    submit = st.form_submit_button("Submit")

                    if submit:
                        if not sid or not name or "@" not in email or len(interest) < 10:
                            st.error("❌ Invalid input")
                        else:
                            with open(FILE_PATH, "a") as f:
                                f.write(f"{sid},{name},{email},{club['name']},{interest},Submitted\n")
                            st.success("✅ Application Submitted")

# ================= TAB 2: STUDENT STATUS =================
with tab2:
    st.subheader("Check Application Status")

    sid = st.text_input("Enter Student ID")

    if st.button("Check Status"):
        apps = read_apps()
        found = False

        for a in apps:
            if a[0] == sid:
                found = True
                status = a[5]

                css = status.lower()
                st.markdown(f"""
                <div class="card">
                    <b>Club:</b> {a[3]}<br>
                    <b>Status:</b> <span class="{css}">{status}</span>
                </div>
                """, unsafe_allow_html=True)

        if not found:
            st.warning("No applications found")

# ================= TAB 3: ADMIN =================
with tab3:
    st.subheader("Admin Dashboard")

    password = st.text_input("Admin Password", type="password")

    if password == "admin123":
        st.success("Admin Access Granted")

        apps = read_apps()
        st.metric("Total Applications", len(apps))

        for i, a in enumerate(apps):
            status = a[5].strip()   # IMPORTANT

            st.markdown(f"""
            <div class="card">
                <b>{a[1]}</b> ({a[0]})<br>
                {a[2]}<br>
                <b>Club:</b> {a[3]}<br>
                <b>Status:</b> {status}
            </div>
            """, unsafe_allow_html=True)

            # ---------- SUBMITTED ----------
            if status == "Submitted":
                c1, c2 = st.columns(2)

                if c1.button("Move to Interview", key=f"interview_{i}"):
                    apps[i][5] = "Interview"
                    write_apps(apps)
                    st.rerun()

                if c2.button("Reject", key=f"reject_sub_{i}"):
                    apps[i][5] = "Rejected"
                    write_apps(apps)
                    st.rerun()

            # ---------- INTERVIEW ----------
            elif status == "Interview":
                c1, c2 = st.columns(2)

                if c1.button("Approve", key=f"approve_{i}"):
                    apps[i][5] = "Approved"
                    write_apps(apps)
                    st.rerun()

                if c2.button("Reject", key=f"reject_int_{i}"):
                    apps[i][5] = "Rejected"
                    write_apps(apps)
                    st.rerun()

            # ---------- FINAL ----------
            else:
                st.info("Final decision made")
