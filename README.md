# 📅 Deadline Tracker — AI Vision & Schedule Digest

**Deadline Tracker** is an AI-powered assistant built with **Streamlit**, **Google Gemini (Vision + Chat)**, and **Gmail SMTP**.

Snap a photo of your course syllabus, lecture timetable, exam schedule, or assignment brief. Gemini automatically parses and extracts all dates, deliverables, and milestones into a clear, structured list. When you're ready, click one button to email a full deadline digest directly to your inbox.

---

## 🚀 Features

- 📸 **Multimodal Vision:** Photograph or upload a syllabus, timetable, assignment sheet, or whiteboard.
- 🎯 **Reliable Date & Deadline Extraction:** Parses messy real-world photos into structured tasks, dates, subjects, and notes.
- 🛡️ **Graceful Fallbacks:** If an uploaded photo doesn't contain a syllabus or deadlines (e.g. food, landscapes, memes), Gemini gracefully explains what it saw and guides you on what to provide.
- 💬 **Conversational Follow-ups:** Ask questions about your schedule (*"Which assignment has the highest weightage?"*, *"Create a study plan for Week 4"*).
- 📧 **Direct Email Digest (Gmail SMTP):** Uses Python's built-in `smtplib` to send a clean summary of your deadlines straight to your email. No paid APIs or third-party webhooks required!

---

## 📁 Project Structure

```text
AI Vision Chatbot/
├── app.py                      # Main Streamlit application & chat UI
├── prompts.py                  # Persona, system prompt, and email templates
├── requirements.txt            # Project dependencies
├── .gitignore                  # Keeps secrets.toml safe from git
├── README.md                   # Setup guide and instructions
└── .streamlit/
    └── secrets.toml.example    # Configuration template
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.9+ (Python 3.14 verified)
- Free [Google AI Studio](https://aistudio.google.com/) account for a Gemini API key.
- A Gmail account with 2-Step Verification enabled.

### 2. Configure Secrets
1. In the `.streamlit/` folder, copy `secrets.toml.example` to `secrets.toml`:
   - Windows PowerShell:
     ```powershell
     Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
     ```
2. Open `.streamlit/secrets.toml` and fill in your credentials:
   ```toml
   # Gemini API Key from https://aistudio.google.com/
   GEMINI_API_KEY = "your-actual-gemini-api-key"

   # Gmail Configuration
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
   ```

> 💡 **How to generate a Gmail App Password:**
> 1. Go to your [Google Account Security Settings](https://myaccount.google.com/security) and ensure **2-Step Verification** is turned ON.
> 2. Visit [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
> 3. Enter an app name (e.g. `Deadline Tracker`) and click **Create**.
> 4. Copy the 16-character code and paste it into `GMAIL_APP_PASSWORD` in `secrets.toml`.

---

## ▶️ Running the App

Run the Streamlit application:

```bash
py -m streamlit run app.py
```
Or if `streamlit` is in your PATH:
```bash
streamlit run app.py
```

The app will launch in your browser at `http://localhost:8501`.

---

## 🧪 How to Test

1. **Onboarding:** Enter your name and email address.
2. **Upload a Syllabus / Timetable:**
   - Attach a photo or screenshot of a syllabus or timetable.
   - Watch Gemini extract the dates, deadlines, and courses.
3. **Try Graceful Fallback:**
   - Upload an unrelated picture (e.g. a cup of coffee or a cat).
   - Observe how Gemini politely declines and asks for a schedule or syllabus.
4. **Email Digest:**
   - Click the **"📧 Email Digest"** button in the header.
   - Check your Gmail inbox for your organized deadline schedule!
