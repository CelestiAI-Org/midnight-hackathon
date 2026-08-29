
import base64
import hashlib
import time
import streamlit as st

st.set_page_config(
    page_title="HR Candidate Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Palette from the Figma design
# -----------------------------
BLUE = "#2E6796"
ORANGE = "#F89344"
ORANGE_2 = "#FF642F"
LIGHT_BLUE = "#B7D8EA"
GRAY = "#D9D9D9"
WHITE = "#FFFFFF"
TEXT = "#111111"
PAGE_BG = "#FFFFFF"

# -----------------------------
# Mock candidate data
# -----------------------------
def svg_avatar(bg, skin, hair, shirt, long_hair=False):
    extra = ""
    if long_hair:
        extra = f"""
        <path d='M30 46c-6 22 1 40 12 49' stroke='{hair}' stroke-width='10' fill='none' stroke-linecap='round'/>
        <path d='M90 46c6 22-1 40-12 49' stroke='{hair}' stroke-width='10' fill='none' stroke-linecap='round'/>
        """
    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 130'>
      <rect width='120' height='130' fill='{bg}'/>
      {extra}
      <circle cx='60' cy='48' r='28' fill='{skin}'/>
      <path d='M28 47c4-33 62-36 65 4-16-15-47-14-65-4z' fill='{hair}'/>
      <rect x='26' y='78' width='68' height='52' rx='30' fill='{shirt}'/>
      <circle cx='50' cy='48' r='2.5' fill='#222'/>
      <circle cx='70' cy='48' r='2.5' fill='#222'/>
      <path d='M51 62c6 5 12 5 18 0' stroke='#9d6251' stroke-width='2.2' fill='none' stroke-linecap='round'/>
    </svg>
    """
    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"

CANDIDATES = [
    {
        "id": 1,
        "name": "Ava Martinez",
        "phone": "0995 920 122",
        "position": "Software Engineer",
        "status": "Awaiting Verification",
        "email": "ava.martinez@example.com",
        "experience": "4 years",
        "skills": ["Python", "JavaScript", "REST APIs"],
        "location": "Manila, Philippines",
        "summary": "Software engineer with strong backend and web application experience.",
        "salary_expectation": 88000,
        "budget_min": 78000,
        "budget_max": 95000,
        "photo": svg_avatar(ORANGE, "#F2C5A2", "#3B2A20", BLUE, False),
    },
    {
        "id": 2,
        "name": "Noah Bennett",
        "phone": "0917 381 440",
        "position": "UI/UX Designer",
        "status": "Verified",
        "email": "noah.bennett@example.com",
        "experience": "5 years",
        "skills": ["Figma", "Prototyping", "UX Research"],
        "location": "Cebu, Philippines",
        "summary": "Product designer focused on clean interfaces, usability, and rapid prototyping.",
        "salary_expectation": 72000,
        "budget_min": 65000,
        "budget_max": 80000,
        "photo": svg_avatar(ORANGE, "#D9A278", "#1F1F1F", BLUE, False),
    },
    {
        "id": 3,
        "name": "Mia Santos",
        "phone": "0998 613 725",
        "position": "Data Analyst",
        "status": "Awaiting Verification",
        "email": "mia.santos@example.com",
        "experience": "3 years",
        "skills": ["SQL", "Python", "Tableau"],
        "location": "Davao, Philippines",
        "summary": "Data analyst experienced in dashboards, reporting, and business insights.",
        "salary_expectation": 67000,
        "budget_min": 60000,
        "budget_max": 72000,
        "photo": svg_avatar(ORANGE, "#E6B58D", "#4A2B1D", BLUE, True),
    },
    {
        "id": 4,
        "name": "Liam Cruz",
        "phone": "0927 455 810",
        "position": "Frontend Developer",
        "status": "Verified",
        "email": "liam.cruz@example.com",
        "experience": "4 years",
        "skills": ["React", "TypeScript", "CSS"],
        "location": "Quezon City, Philippines",
        "summary": "Frontend developer experienced in responsive web applications and reusable UI systems.",
        "salary_expectation": 91000,
        "budget_min": 70000,
        "budget_max": 88000,
        "photo": svg_avatar(ORANGE, "#DDA57E", "#2A201C", BLUE, False),
    },
    {
        "id": 5,
        "name": "Sophia Reyes",
        "phone": "0918 244 663",
        "position": "HR Specialist",
        "status": "Awaiting Verification",
        "email": "sophia.reyes@example.com",
        "experience": "6 years",
        "skills": ["Recruiting", "Onboarding", "HRIS"],
        "location": "Makati, Philippines",
        "summary": "HR specialist with experience in recruiting operations, onboarding, and employee support.",
        "salary_expectation": 62000,
        "budget_min": 55000,
        "budget_max": 68000,
        "photo": svg_avatar(ORANGE, "#E8B48E", "#512F24", BLUE, True),
    },
    {
        "id": 6,
        "name": "Ethan Lim",
        "phone": "0997 503 219",
        "position": "Backend Developer",
        "status": "Verified",
        "email": "ethan.lim@example.com",
        "experience": "5 years",
        "skills": ["Python", "Django", "PostgreSQL"],
        "location": "Pasig, Philippines",
        "summary": "Backend developer focused on APIs, data services, and reliable server-side systems.",
        "salary_expectation": 90000,
        "budget_min": 76000,
        "budget_max": 98000,
        "photo": svg_avatar(ORANGE, "#D8A17B", "#202020", BLUE, False),
    },
    {
        "id": 7,
        "name": "Isabella Flores",
        "phone": "0916 774 390",
        "position": "Product Manager",
        "status": "Verified",
        "email": "isabella.flores@example.com",
        "experience": "7 years",
        "skills": ["Product Strategy", "Agile", "Roadmaps"],
        "location": "Taguig, Philippines",
        "summary": "Product manager experienced in roadmap planning, stakeholder alignment, and product delivery.",
        "salary_expectation": 110000,
        "budget_min": 95000,
        "budget_max": 115000,
        "photo": svg_avatar(ORANGE, "#EAB790", "#493027", BLUE, True),
    },
    {
        "id": 8,
        "name": "Gabriel Tan",
        "phone": "0928 618 502",
        "position": "QA Engineer",
        "status": "Awaiting Verification",
        "email": "gabriel.tan@example.com",
        "experience": "4 years",
        "skills": ["Selenium", "Playwright", "API Testing"],
        "location": "Mandaluyong, Philippines",
        "summary": "QA engineer experienced in automated testing, regression coverage, and release validation.",
        "salary_expectation": 70000,
        "budget_min": 62000,
        "budget_max": 75000,
        "photo": svg_avatar(ORANGE, "#D7A37D", "#29231F", BLUE, False),
    },
    {
        "id": 9,
        "name": "Chloe Navarro",
        "phone": "0991 325 447",
        "position": "Marketing Specialist",
        "status": "Verified",
        "email": "chloe.navarro@example.com",
        "experience": "3 years",
        "skills": ["Content", "Analytics", "Campaigns"],
        "location": "Parañaque, Philippines",
        "summary": "Marketing specialist focused on digital campaigns, content strategy, and performance reporting.",
        "salary_expectation": 58000,
        "budget_min": 52000,
        "budget_max": 65000,
        "photo": svg_avatar(ORANGE, "#E7B48D", "#5A3428", BLUE, True),
    },
]

if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None

if "verification_results" not in st.session_state:
    st.session_state.verification_results = {}

if "status_overrides" not in st.session_state:
    st.session_state.status_overrides = {}

def candidate_status(candidate):
    return st.session_state.status_overrides.get(candidate["id"], candidate["status"])


def make_proof(candidate):
    eligible = (
        candidate["budget_min"]
        <= candidate["salary_expectation"]
        <= candidate["budget_max"]
    )
    raw = (
        f'{candidate["id"]}|{candidate["salary_expectation"]}|'
        f'{candidate["budget_min"]}|{candidate["budget_max"]}|{eligible}'
    )
    proof_id = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()
    return eligible, proof_id


# If a card's View Profile link was clicked, load that profile.
candidate_param = st.query_params.get("candidate")
if candidate_param:
    try:
        st.session_state.selected_candidate = int(candidate_param)
    except (TypeError, ValueError):
        st.session_state.selected_candidate = None

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    f"""
    <style>
      html, body, [data-testid="stAppViewContainer"] {{
        background: {PAGE_BG};
      }}

      [data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stSidebar"] {{
        display: none;
      }}

      .block-container {{
        max-width: 980px;
        padding-top: 28px;
        padding-bottom: 36px;
      }}

      .dashboard-shell {{
        background: {WHITE};
        border-radius: 0;
        overflow: hidden;
        box-shadow: none;
      }}

      .topbar {{
        height: 88px;
        background: {BLUE};
        position: relative;
      }}

      .user-box {{
        position: absolute;
        right: 92px;
        top: 20px;
        color: white;
        text-align: right;
        line-height: 1.22;
        font-size: 14px;
      }}

      .user-box strong {{
        display: block;
        font-weight: 500;
      }}

      .header-dot {{
        position: absolute;
        right: 18px;
        top: 9px;
        width: 68px;
        height: 68px;
        border-radius: 50%;
        background: {ORANGE};
      }}

      .content-wrap {{
        padding: 20px 22px 32px;
      }}

      .company-title {{
        text-align: center;
        margin: 2px 0 18px;
      }}

      .company-name {{
        color: {BLUE};
        font-size: 28px;
        font-weight: 900;
        letter-spacing: -0.5px;
      }}

      .company-subtitle {{
        color: #6B6B6B;
        font-size: 12px;
        margin-top: 4px;
        letter-spacing: 1.4px;
        text-transform: uppercase;
      }}

      /* SEARCH BAR — remove Streamlit/BaseWeb double border */
      div[data-testid="stTextInput"] div[data-baseweb="input"] {{
        background: #FFFFFF !important;
        border: none !important;
        outline: none !important;
        border-radius: 7px !important;
        box-shadow: inset 0 0 0 1px #C9D3DA !important;
        min-height: 42px !important;
        height: 42px !important;
        overflow: hidden !important;
      }}

      div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
        border: none !important;
        outline: none !important;
        box-shadow:
          inset 0 0 0 1.5px #2E6796,
          0 0 0 3px rgba(46, 103, 150, 0.10) !important;
      }}

      div[data-testid="stTextInput"] div[data-baseweb="base-input"] {{
        background: #FFFFFF !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        min-height: 42px !important;
        height: 42px !important;
      }}

      div[data-testid="stTextInput"] input {{
        background: #FFFFFF !important;
        color: #111111 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        height: 42px !important;
        line-height: 42px !important;
        text-align: left;
        font-size: 14px !important;
        padding: 0 14px !important;
      }}

      /* FILTER — fully white, matching the search field */
      div[data-testid="stSelectbox"],
      div[data-testid="stSelectbox"] > div,
      div[data-testid="stSelectbox"] div[data-baseweb="select"],
      div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: #FFFFFF !important;
      }}

      div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        color: #111111 !important;
        border: none !important;
        outline: none !important;
        border-radius: 7px !important;
        box-shadow: inset 0 0 0 1px #C9D3DA !important;
        min-height: 42px !important;
        height: 42px !important;
        padding-left: 10px !important;
        padding-right: 8px !important;
      }}

      div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {{
        background: #FFFFFF !important;
        box-shadow: inset 0 0 0 1px #2E6796 !important;
      }}

      div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {{
        background: #FFFFFF !important;
        border: none !important;
        box-shadow:
          inset 0 0 0 1.5px #2E6796,
          0 0 0 3px rgba(46, 103, 150, 0.10) !important;
      }}

      div[data-testid="stSelectbox"] {{
        font-size: 13px;
      }}

      div[data-testid="stSelectbox"] div[data-baseweb="select"] span {{
        color: #111111 !important;
        font-weight: 700 !important;
        background: transparent !important;
      }}

      div[data-testid="stSelectbox"] svg {{
        color: #2E6796 !important;
        fill: #2E6796 !important;
      }}

      /* Keep the opened filter menu white too */
      div[data-baseweb="popover"],
      div[data-baseweb="menu"],
      ul[role="listbox"] {{
        background: #FFFFFF !important;
      }}

      li[role="option"] {{
        background: #FFFFFF !important;
        color: #111111 !important;
      }}

      li[role="option"]:hover {{
        background: #F5F8FA !important;
      }}

      /* Compact top Search button, matching the white controls */
      .st-key-mobile_search button {{
        background: #FFFFFF !important;
        color: #111111 !important;
        border: 2px solid #000000 !important;
        min-height: 42px !important;
        height: 42px !important;
        padding: 0 16px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
        font-size: 13px !important;
      }}

      .st-key-mobile_search button:hover {{
        background: #FFFFFF !important;
        color: #111111 !important;
        border: 2px solid #000000 !important;
      }}

      .candidate-card {{
        background: #FFFFFF;
        min-height: 305px;
        padding: 16px 14px 16px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 14px;
        border: 1px solid #E2E8EE;
        border-radius: 10px;
        box-shadow: 0 7px 18px rgba(46, 103, 150, 0.07);
      }}

      .candidate-photo {{
        width: 98px;
        height: 104px;
        border-radius: 50%;
        object-fit: cover;
        display: block;
        margin: 0 auto 10px;
      }}

      .candidate-name {{
        color: {TEXT};
        font-size: 14px;
        font-weight: 700;
        margin-top: 1px;
      }}

      .candidate-position {{
        color: {TEXT};
        font-size: 13px;
        margin-top: 7px;
      }}

      /* View Profile is now INSIDE the same gray card */
      .view-profile {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-top: 10px;
        padding: 9px 15px;
        background: {ORANGE};
        color: #FFFFFF !important;
        border: 1px solid #E87525;
        border-radius: 7px;
        text-decoration: none !important;
        font-size: 11px;
        font-weight: 800;
        line-height: 1;
        box-shadow: 0 3px 8px rgba(248, 147, 68, 0.18);
      }}

      .view-profile:hover {{
        background: {ORANGE_2};
        color: #FFFFFF !important;
      }}

      .status-badge {{
        display: inline-block;
        margin-top: 9px;
        padding: 5px 9px;
        background: #E7F3FA;
        color: #244B66;
        border: 1px solid #C7E0EF;
        border-radius: 999px;
        font-size: 9px;
        font-weight: 700;
      }}

      /* Candidate review page — polished from the Figma sample */
      .review-shell {{
        background: #FFFFFF;
        padding: 0 0 24px;
        min-height: 500px;
        border: 1px solid #E2E8EE;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 10px 26px rgba(46, 103, 150, 0.08);
      }}

      .review-companybar {{
        height: 56px;
        background: #2E6796;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
      }}

      .review-company {{
        font-size: 16px;
        font-weight: 900;
        letter-spacing: -0.2px;
      }}

      .review-company-sub {{
        font-size: 11px;
        opacity: .82;
        margin-top: 2px;
      }}

      .review-user {{
        text-align: right;
        font-size: 11px;
        line-height: 1.25;
      }}

      .review-header {{
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 22px 26px 18px;
        border-bottom: 1px solid #EDF1F4;
      }}

      .review-avatar {{
        width: 92px;
        height: 92px;
        border-radius: 50%;
        object-fit: cover;
        flex: 0 0 auto;
        border: 4px solid #FFF1E7;
        box-shadow: 0 4px 10px rgba(0,0,0,.06);
      }}

      .review-name {{
        color: #111111;
        font-size: 22px;
        font-weight: 900;
        line-height: 1.05;
      }}

      .review-role {{
        color: #5F6B76;
        font-size: 13px;
        margin-top: 4px;
      }}

      .review-contact {{
        color: #6B7782;
        font-size: 11px;
        margin-top: 6px;
      }}

      .review-actions {{
        display: flex;
        gap: 7px;
        margin-top: 10px;
        flex-wrap: wrap;
      }}

      .review-pill {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 64px;
        min-height: 25px;
        padding: 0 11px;
        border-radius: 999px;
        background: #FFF1E7;
        color: #9A4E13;
        border: 1px solid #FFD3B1;
        font-size: 9px;
        font-weight: 800;
      }}

      .review-pill.action {{
        background: #F89344;
        color: #FFFFFF;
        border-color: #E87525;
      }}

      .midnight-toggle {{
        display: inline-flex;
        align-items: center;
        padding: 2px;
        background: #F2F5F7;
        border: 1px solid #DCE4E9;
        border-radius: 999px;
        margin-left: 2px;
      }}

      .midnight-option {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 23px;
        padding: 0 10px;
        border-radius: 999px;
        color: #66727C !important;
        text-decoration: none !important;
        font-size: 9px;
        font-weight: 900;
        white-space: nowrap;
      }}

      .midnight-option.active {{
        background: #F89344;
        color: #FFFFFF !important;
        box-shadow: 0 2px 5px rgba(248,147,68,.20);
      }}

      .midnight-option:hover {{
        color: #2E6796 !important;
      }}

      .midnight-option.active:hover {{
        color: #FFFFFF !important;
      }}

      .proof-good {{
        color: #287A4B;
        font-weight: 900;
      }}

      .proof-bad {{
        color: #B34A43;
        font-weight: 900;
      }}

      .review-tabs {{
        display: flex;
        align-items: flex-end;
        gap: 26px;
        padding: 0 26px;
        margin: 18px 0 0;
        border-bottom: 1px solid #E7EDF2;
        flex-wrap: wrap;
      }}

      .review-tab {{
        color: #3F4A54 !important;
        text-decoration: none !important;
        font-size: 14px;
        font-weight: 800;
        padding: 0 0 11px;
        border-bottom: 3px solid transparent;
      }}

      .review-tab:hover {{
        color: #2E6796 !important;
      }}

      .review-tab.active {{
        color: #111111 !important;
        border-bottom-color: #F89344;
      }}

      .review-layout {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) 220px;
        gap: 18px;
        padding: 20px 26px 0;
      }}

      .review-content {{
        min-height: 235px;
        background: #FFFFFF;
        border: 1px solid #E2E8EE;
        border-radius: 10px;
        padding: 20px 22px;
        color: #111111;
        font-size: 13px;
        line-height: 1.6;
        box-shadow: 0 4px 12px rgba(46,103,150,.045);
      }}

      .review-content h3 {{
        margin: 0 0 14px;
        color: #18344D;
        font-size: 17px;
      }}

      .review-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px 12px;
      }}

      .review-field {{
        background: #F7F9FB;
        padding: 10px 11px;
        border: 1px solid #EDF1F4;
        border-radius: 7px;
      }}

      .review-field b {{
        color: #2E6796;
      }}

      .review-resume-line {{
        padding: 10px 0;
        border-bottom: 1px solid #E7EDF2;
      }}

      .review-score {{
        display: inline-block;
        background: #EEF6FB;
        color: #244B66;
        border: 1px solid #D2E6F2;
        border-radius: 7px;
        padding: 6px 9px;
        margin: 3px 6px 3px 0;
        font-size: 11px;
        font-weight: 700;
      }}

      .decision-card {{
        background: #F7F9FB;
        border: 1px solid #E2E8EE;
        border-radius: 10px;
        padding: 16px;
        height: fit-content;
      }}

      .decision-title {{
        color: #18344D;
        font-size: 14px;
        font-weight: 900;
        margin-bottom: 10px;
      }}

      .decision-row {{
        font-size: 11px;
        color: #65727D;
        margin: 8px 0;
      }}

      .decision-row strong {{
        display: block;
        color: #111111;
        font-size: 12px;
        margin-top: 2px;
      }}

      .privacy-box {{
        margin-top: 14px;
        background: #F7F9FB;
        border: 1px solid #E2E8EE;
        border-radius: 9px;
        padding: 13px;
      }}

      .privacy-title {{
        color: #18344D;
        font-size: 13px;
        font-weight: 900;
        margin-bottom: 8px;
      }}

      .privacy-row {{
        display: flex;
        justify-content: space-between;
        gap: 10px;
        padding: 7px 0;
        border-bottom: 1px solid #E7EDF2;
        font-size: 11px;
      }}

      .privacy-row:last-child {{
        border-bottom: 0;
      }}

      .private-tag {{
        color: #2E6796;
        font-weight: 900;
      }}

      .profile-panel {{
        background: white;
        margin-top: 22px;
        border: 1px solid #e3e3e3;
      }}

      .profile-banner {{
        height: 78px;
        background: {BLUE};
        position: relative;
      }}

      .profile-banner-dot {{
        position: absolute;
        right: 18px;
        top: 8px;
        width: 62px;
        height: 62px;
        border-radius: 50%;
        background: {ORANGE};
      }}

      .profile-body {{
        padding: 22px;
      }}

      .profile-name {{
        font-size: 24px;
        font-weight: 800;
        color: {TEXT};
      }}

      .profile-role {{
        font-size: 14px;
        color: #666;
        margin-top: 4px;
      }}

      .profile-detail {{
        background: #F1F1F1;
        padding: 10px 12px;
        margin-top: 8px;
        font-size: 13px;
      }}

      .profile-detail b {{
        color: {BLUE};
      }}

      .section-label {{
        color: {BLUE};
        font-weight: 800;
        margin: 14px 0 7px;
      }}

      div.stButton > button {{
        width: 100%;
        border-radius: 0 !important;
        border: 2px solid #000000 !important;
        background: {ORANGE};
        color: white;
        font-weight: 700;
        min-height: 40px;
      }}

      div.stButton > button:hover {{
        background: {ORANGE_2};
        color: white;
        border: 2px solid #000000 !important;
      }}

      /* The top Search button: same white style as Search + Filter */
      div[data-testid="stButton"]:has(button[kind="secondary"]) button {{
        min-height: 40px;
      }}

      /* Candidate review actions — polished but still your blue/orange palette */
      .st-key-verify_salary_btn button {{
        background: {ORANGE} !important;
        color: #FFFFFF !important;
        border: 1px solid #E87525 !important;
        border-radius: 7px !important;
        min-height: 42px !important;
        box-shadow: 0 3px 8px rgba(248,147,68,.18) !important;
      }}

      .st-key-verify_salary_btn button:hover {{
        background: {ORANGE_2} !important;
        color: #FFFFFF !important;
      }}

      .st-key-close_profile button {{
        background: #FFFFFF !important;
        color: {BLUE} !important;
        border: 1px solid #BFD0DC !important;
        border-radius: 7px !important;
      }}

      .st-key-reject_candidate button {{
        background: #FFFFFF !important;
        color: #B34A43 !important;
        border: 1px solid #E6BEBB !important;
        border-radius: 7px !important;
      }}

      .st-key-move_forward button {{
        background: {ORANGE} !important;
        color: #FFFFFF !important;
        border: 1px solid #E87525 !important;
        border-radius: 7px !important;
      }}

      @media (max-width: 760px) {{
        .block-container {{
          padding-left: 10px;
          padding-right: 10px;
        }}

        .review-shell {{
          border-radius: 8px;
        }}

        .review-companybar {{
          padding: 0 14px;
        }}

        .review-header {{
          align-items: flex-start;
          padding: 18px 16px 14px;
        }}

        .review-avatar {{
          width: 78px;
          height: 78px;
        }}

        .review-name {{
          font-size: 18px;
        }}

        .review-tabs {{
          gap: 14px;
          padding: 0 16px;
        }}

        .review-tab {{
          font-size: 13px;
        }}

        .review-layout {{
          grid-template-columns: 1fr;
          padding: 16px;
        }}

        .review-grid {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Header
# -----------------------------
st.html(
    """
    <div class="topbar">
      <div class="user-box">
        <strong>James Al Ghul</strong>
        HR Leader
      </div>
      <div class="header-dot"></div>
    </div>
    """
)

# -----------------------------
# Company title + Search + Filter
# -----------------------------
# Only show the company title on the candidate-list/dashboard screen.
if st.session_state.selected_candidate is None:
    st.html(
        """
        <div class="company-title">
          <div class="company-name">Northstar People Co.</div>
          <div class="company-subtitle">Talent Review Dashboard</div>
        </div>
        """
    )

# When a candidate profile is open, hide the candidate list.
if st.session_state.selected_candidate is None:
    tool_a, tool_b, tool_c = st.columns([5.0, 1.55, 1.15], gap="small")

    # Long text field first
    with tool_a:
        search = st.text_input(
            "Search",
            placeholder="Search candidates",
            label_visibility="collapsed"
        )

    # Small search button in the middle
    with tool_b:
        st.button("🔍 Search", key="mobile_search", use_container_width=True)

    # Small filter control LAST
    with tool_c:
        filter_choice = st.selectbox(
            "Filter",
            [
                "Filter",
                "Software Engineer",
                "UI/UX Designer",
                "Data Analyst",
                "Frontend Developer",
                "HR Specialist",
                "Backend Developer",
                "Product Manager",
                "QA Engineer",
                "Marketing Specialist",
                "Verified",
                "Awaiting Verification",
            ],
            label_visibility="collapsed"
        )

    filtered = []
    for c in CANDIDATES:
        q = search.lower().strip()
        matches_search = (
            not q
            or q in c["name"].lower()
            or q in c["position"].lower()
            or q in c["email"].lower()
            or any(q in skill.lower() for skill in c["skills"])
        )

        matches_filter = (
            filter_choice == "Filter"
            or c["position"] == filter_choice
            or c["status"] == filter_choice
        )

        if matches_search and matches_filter:
            filtered.append(c)

    st.write("")

    # -----------------------------
    # Candidate cards
    # -----------------------------
    if filtered:
        cols = st.columns(3, gap="large")

        for i, c in enumerate(filtered):
            with cols[i % 3]:
                st.html(
                    f"""
                    <div class="candidate-card">
                      <img class="candidate-photo" src="{c['photo']}" alt="{c['name']}">
                      <div class="candidate-name">{c['name']}</div>
                      <div class="candidate-position">{c['position']}</div>
                      <div class="status-badge">{candidate_status(c)}</div>
                      <a class="view-profile" href="?candidate={c['id']}">View Profile</a>
                    </div>
                    """
                )
    else:
        st.info("No candidates found.")

# -----------------------------
# Candidate review / View Profile
# -----------------------------
if st.session_state.selected_candidate is not None:
    selected = next(
        (c for c in CANDIDATES if c["id"] == st.session_state.selected_candidate),
        None
    )

    if selected:
        active_tab = st.query_params.get("tab", "application")
        if active_tab not in {"application", "resume", "evaluation", "attachment", "verify"}:
            active_tab = "application"

        privacy_mode = st.query_params.get("privacy", "midnight")
        if privacy_mode not in {"before", "midnight"}:
            privacy_mode = "midnight"

        within_budget = selected["salary_expectation"] <= selected["budget_max"]

        privacy_toggle_html = f"""
          <div class="midnight-toggle">
            <a class="midnight-option {"active" if privacy_mode == "before" else ""}"
               href="?candidate={selected["id"]}&tab={active_tab}&privacy=before">Before</a>
            <a class="midnight-option {"active" if privacy_mode == "midnight" else ""}"
               href="?candidate={selected["id"]}&tab={active_tab}&privacy=midnight">With Midnight</a>
          </div>
        """

        tab_labels = [
            ("application", "Application"),
            ("resume", "Resume"),
            ("evaluation", "Evaluation"),
            ("attachment", "Attachments"),
            ("verify", "Verify"),
        ]

        tabs_html = "".join(
            f'<a class="review-tab {"active" if active_tab == tab_key else ""}" '
            f'href="?candidate={selected["id"]}&tab={tab_key}&privacy={privacy_mode}">{label}</a>'
            for tab_key, label in tab_labels
        )

        if active_tab == "application":
            if privacy_mode == "before":
                compensation_html = f"""
                  <div class="privacy-box">
                    <div class="privacy-title">Compensation Check — Before</div>
                    <div class="privacy-row">
                      <span>Candidate salary</span>
                      <span>${selected["salary_expectation"]:,}</span>
                    </div>
                    <div class="privacy-row">
                      <span>Company budget</span>
                      <span>${selected["budget_max"]:,}</span>
                    </div>
                    <div class="privacy-row">
                      <span>Result</span>
                      <span class="{"proof-good" if within_budget else "proof-bad"}">
                        {"Within budget" if within_budget else "Over budget"}
                      </span>
                    </div>
                  </div>
                """
            else:
                compensation_html = f"""
                  <div class="privacy-box">
                    <div class="privacy-title">Compensation Check — With Midnight</div>
                    <div class="privacy-row">
                      <span>Candidate salary</span>
                      <span class="private-tag">🔒 Private</span>
                    </div>
                    <div class="privacy-row">
                      <span>Company budget</span>
                      <span class="private-tag">🔒 Private</span>
                    </div>
                    <div class="privacy-row">
                      <span>Result</span>
                      <span class="{"proof-good" if within_budget else "proof-bad"}">
                        {"✓ Proven within budget" if within_budget else "✕ Proven outside budget"}
                      </span>
                    </div>
                  </div>
                """

            content_html = f"""
              <h3>Application Overview</h3>
              <div class="review-grid">
                <div class="review-field"><b>Position</b><br>{selected["position"]}</div>
                <div class="review-field"><b>Location</b><br>{selected["location"]}</div>
                <div class="review-field"><b>Experience</b><br>{selected["experience"]}</div>
                <div class="review-field"><b>Status</b><br>{candidate_status(selected)}</div>
                <div class="review-field"><b>Email</b><br>{selected["email"]}</div>
                <div class="review-field"><b>Phone</b><br>{selected["phone"]}</div>
              </div>
              <div style="margin-top:14px">
                <b style="color:#2E6796">Candidate summary</b><br>
                {selected["summary"]}
              </div>

              {compensation_html}
            """

        elif active_tab == "resume":
            content_html = f"""
              <h3>Resume</h3>
              <div class="review-resume-line"><b>Professional experience:</b> {selected["experience"]}</div>
              <div class="review-resume-line"><b>Core skills:</b> {", ".join(selected["skills"])}</div>
              <div class="review-resume-line"><b>Current location:</b> {selected["location"]}</div>
              <div class="review-resume-line"><b>Education:</b> Bachelor&apos;s Degree — Mock University</div>
              <div class="review-resume-line"><b>Last role:</b> {selected["position"]} — Sample Company</div>
            """

        elif active_tab == "evaluation":
            content_html = f"""
              <h3>Evaluation</h3>
              <span class="review-score">Skills 9/10</span>
              <span class="review-score">Experience 8/10</span>
              <span class="review-score">Communication 8/10</span>
              <span class="review-score">Culture fit 9/10</span>
              <div style="margin-top:16px">
                <b style="color:#2E6796">Overall recommendation</b><br>
                Strong mock candidate for the {selected["position"]} opening. Recommended for the next interview stage.
              </div>
            """

        elif active_tab == "attachment":
            content_html = """
              <h3>Attachments</h3>
              <div class="review-resume-line">📄 Resume_Candidate.pdf</div>
              <div class="review-resume-line">📄 Portfolio_Sample.pdf</div>
              <div class="review-resume-line">🖼️ Certificate_Verification.png</div>
            """
        else:
            result = st.session_state.verification_results.get(selected["id"])
            result_html = ""

            if result is not None:
                if result["eligible"]:
                    result_html = f"""
                      <div class="privacy-box" style="background:#F2FAF5;border-color:#CDE7D5;">
                        <div class="privacy-title">✓ Eligible</div>
                        <div style="font-size:12px;color:#5F6B76;line-height:1.55;">
                          The private salary expectation is within the approved company salary band.
                          The actual salary remains hidden.
                        </div>
                        <div style="margin-top:8px;font-size:10px;color:#2E6796;font-family:monospace;">
                          Proof ID: {result["proof_id"]}
                        </div>
                      </div>
                    """
                else:
                    result_html = f"""
                      <div class="privacy-box" style="background:#FFF5F2;border-color:#F0D0C6;">
                        <div class="privacy-title">✕ Not eligible under current band</div>
                        <div style="font-size:12px;color:#5F6B76;line-height:1.55;">
                          The private salary expectation is outside the approved role band.
                          The actual salary remains hidden.
                        </div>
                        <div style="margin-top:8px;font-size:10px;color:#2E6796;font-family:monospace;">
                          Proof ID: {result["proof_id"]}
                        </div>
                      </div>
                    """

            content_html = f"""
              <h3>Verify</h3>
              <div style="font-size:12px;color:#5F6B76;line-height:1.6;">
                Verify salary eligibility against company policy without revealing
                the candidate's private salary expectation.
              </div>
              {result_html}
            """

        st.html(
            f"""
            <div class="review-shell">
              <div class="review-companybar">
                <div>
                  <div class="review-company">Northstar People Co.</div>
                  <div class="review-company-sub">Candidate Review</div>
                </div>
                <div class="review-user"></div>
              </div>

              <div class="review-header">
                <img class="review-avatar" src="{selected['photo']}" alt="{selected['name']}">
                <div>
                  <div class="review-name">{selected['name']}</div>
                  <div class="review-role">{selected['position']} · {selected['location']}</div>
                  <div class="review-contact">{selected['email']} &nbsp; · &nbsp; {selected['phone']}</div>
                  <div class="review-actions">
                    <span class="review-pill">Application Received</span>
                    {privacy_toggle_html}
                  </div>
                </div>
              </div>

              <div class="review-tabs">
                {tabs_html}
              </div>

              <div class="review-layout">
                <div class="review-content">
                  {content_html}
                </div>

                <div class="decision-card">
                  <div class="decision-title">Hiring Decision</div>
                  <div class="decision-row">Current status<strong>{candidate_status(selected)}</strong></div>
                  <div class="decision-row">Reviewer<strong>James Al Ghul</strong></div>
                  <div class="decision-row">Suggested next step<strong>Interview</strong></div>
                  <div class="decision-row">Overall score<strong>8.5 / 10</strong></div>
                </div>
              </div>            </div>
            """
        )

        if active_tab == "verify":
            verify_col, _ = st.columns([1.45, 2.55])

            with verify_col:
                if st.button(
                    "Verify salary eligibility",
                    key="verify_salary_btn",
                    type="primary",
                    use_container_width=True,
                ):
                    with st.status("Generating proof...", expanded=True) as status:
                        st.write("Reading private salary commitment...")
                        time.sleep(0.45)
                        st.write("Comparing against company salary policy...")
                        time.sleep(0.45)
                        st.write("Finalizing proof...")
                        time.sleep(0.45)

                        eligible, proof_id = make_proof(selected)

                        st.session_state.verification_results[selected["id"]] = {
                            "eligible": eligible,
                            "proof_id": proof_id,
                        }
                        st.session_state.status_overrides[selected["id"]] = (
                            "Verified" if eligible else "Review Needed"
                        )

                        status.update(
                            label="Proof generated",
                            state="complete",
                            expanded=False,
                        )

                    st.rerun()

        back_col, reject_col, move_col = st.columns([1.2, 0.8, 1.0])

        with back_col:
            if st.button("← Back to Candidates", key="close_profile"):
                st.session_state.selected_candidate = None
                st.query_params.clear()
                st.rerun()

        with reject_col:
            if st.button("Reject", key="reject_candidate"):
                st.session_state.selected_candidate = None
                st.query_params.clear()
                st.toast(f"{selected['name']} marked as rejected. (Mock)", icon="🗂️")
                st.rerun()

        with move_col:
            if st.button("Move Forward", key="move_forward"):
                st.session_state.selected_candidate = None
                st.query_params.clear()
                st.toast(f"{selected['name']} reviewed and moved forward.", icon="✅")
                st.rerun()

