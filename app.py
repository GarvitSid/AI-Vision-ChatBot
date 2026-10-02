import re
import smtplib
from email.mime.text import MIMEText
import streamlit as st
from google import genai
from google.genai import types
from prompts import EMAIL_DIGEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# --- Page Configuration ---
st.set_page_config(
    page_title="Deadline Tracker",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom Styling for polished aesthetics
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-caption {
        color: #6c757d;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Configuration & Secrets ---
MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3.5-flash")

if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "⚠️ **Missing Configuration**: `GEMINI_API_KEY` was not found in `.streamlit/secrets.toml`.\n\n"
        "Please copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your API keys."
    )
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "").replace(" ", "")


# --- Cached Resource: Gemini Client ---
@st.cache_resource
def get_gemini_client(api_key: str):
    """
    Creates and caches the Google GenAI client instance.
    Cached so it survives Streamlit reruns without dropping active chat sessions.
    """
    return genai.Client(api_key=api_key)


gemini_client = get_gemini_client(GEMINI_API_KEY)


# --- Helper Functions ---
def is_valid_email(email_str: str) -> bool:
    """Basic validation for recipient email address."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email_str.strip()))


def send_email(to_address: str, subject: str, body: str):
    """
    Sends an email using Python's built-in smtplib and Gmail SMTP.
    Requires Gmail 2-Step Verification and a 16-character App Password.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        return (
            False,
            "Gmail SMTP credentials are not configured in .streamlit/secrets.toml.",
        )

    try:
        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = subject
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_address

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(message)
        return True, "Email sent successfully"
    except Exception as error:
        return False, str(error)


def render_message(message):
    """Renders a single chat message (text or photo)."""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], caption="Uploaded Schedule / Document")


def add_message(role, kind, content):
    """Adds a message to the session state and immediately renders it."""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    """Sends user content (text and/or image parts) to the active Gemini chat session."""
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"⚠️ Sorry, something went wrong while communicating with Gemini: {error}"


# --- Sidebar Setup ---
with st.sidebar:
    st.subheader("🗓️ Deadline Tracker")
    st.write(
        "Upload a photo of your **syllabus**, **timetable**, **assignment sheet**, or **exam schedule**."
    )
    st.markdown("---")
    st.markdown(
        """
        **💡 Tips for best results:**
        - Ensure good lighting when photographing printed syllabi.
        - Multiple pages? Upload each page or ask follow-up questions.
        - You can ask:
          - *"Which deadline is coming up first?"*
          - *"Create a 1-week study plan for Midterm 1."*
          - *"Summarize only assignments worth > 15%."*
        """
    )
    if "onboarded" in st.session_state and st.session_state.onboarded:
        st.markdown("---")
        st.write(f"👤 **Student:** {st.session_state.name}")
        st.write(f"📬 **Email:** {st.session_state.email}")
        if st.button("🔄 Start New Session / Switch Account", use_container_width=True):
            for key in ["onboarded", "name", "email", "chat", "messages"]:
                st.session_state.pop(key, None)
            st.rerun()


# --- Step 1: Onboarding Screen ---
if "onboarded" not in st.session_state:
    st.markdown('<div class="main-header">📅 Deadline Tracker</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-caption">Snap your syllabus or timetable. Extract deadlines instantly. Get an email digest straight to your inbox.</div>',
        unsafe_allow_html=True,
    )

    with st.form("onboarding_form"):
        st.subheader("Let's get you set up ✨")
        name = st.text_input("Your Name", placeholder="e.g. Maya")
        email = st.text_input(
            "Your Email Address",
            placeholder="you@university.edu or you@gmail.com",
            help="Deadline Tracker will email your complete deadline digests to this address.",
        )
        submitted = st.form_submit_button("Start Tracking 🚀", use_container_width=True)

    if submitted:
        if not name.strip():
            st.warning("Please provide your name.")
        elif not email.strip() or not is_valid_email(email):
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()
            # Initialize persistent Gemini chat session with custom system prompt
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# --- Step 2: Main Chat & Extraction Interface ---
header_col, action_col = st.columns([5, 2], vertical_alignment="center")
with header_col:
    st.title("📅 Deadline Tracker")
    st.caption(
        f"Active student: **{st.session_state.name}** • Notifications: **{st.session_state.email}**"
    )

with action_col:
    # Disable button until at least one user exchange has happened
    send_disabled = len(st.session_state.messages) <= 1
    if st.button("📧 Email Digest (Minimum 2 responses required!)", disabled=send_disabled, use_container_width=True):
        with st.spinner("Compiling your deadline digest..."):
            digest = ask_gemini([EMAIL_DIGEST_PROMPT])
            success, info = send_email(
                st.session_state.email,
                f"📅 Your Academic Deadline Digest — {st.session_state.name}",
                digest,
            )
        if success:
            st.success(f"Digest sent to {st.session_state.email}! 📬")
        else:
            st.error(f"Couldn't send email: {info}")

st.markdown("---")

# Render message history or initial welcome prompt
if not st.session_state.messages:
    welcome_text = WELCOME_MESSAGE_TEMPLATE.format(
        name=st.session_state.name, email=st.session_state.email
    )
    add_message("assistant", "text", welcome_text)
else:
    for msg in st.session_state.messages:
        render_message(msg)


# --- Step 3: Multimodal Input (Text and/or Photos) ---
user_input = st.chat_input(
    "Ask a question, or attach a photo of your syllabus / timetable...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    # Handle attached image
    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    # Handle text or provide default prompt for lone photo
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Please analyze this image carefully. Extract all dates, deadlines, assignment due dates, "
            "and exam schedules you find into a clear, structured list. If this photo does not appear to contain "
            "any syllabus, timetable, or deadlines, politely explain what you see instead."
        )

    # Send to Gemini chat session
    with st.spinner("Analyzing document and extracting deadlines..."):
        response_text = ask_gemini(parts)
        add_message("assistant", "text", response_text)
