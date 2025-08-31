import os
import threading
import pywhatkit
import speech_recognition as sr
import pyttsx3
from datetime import datetime, timedelta
import pytz

os.environ['DISPLAY'] = ':0'  # For Linux GUI automation (skip if on Windows)

PHONE_NUMBER = "+91XXXXXXXXXX"   # Change this to your WhatsApp number
INDIA_TZ = pytz.timezone("Asia/Kolkata")

# ------------------- Helper Functions -------------------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_once():
    """Listen for one sentence from microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("✅ You said:", text)
            return text.lower()
        except Exception:
            speak("Sorry, I could not understand. Please repeat.")
            return ""

# ------------------- WhatsApp Reminder -------------------
def send_reminder(message, hour, minute):
    """Send WhatsApp reminder in a new thread so it doesn’t block."""
    def worker():
        try:
            pywhatkit.sendwhatmsg(
                PHONE_NUMBER,
                message,
                hour,
                minute,
                wait_time=10,
                tab_close=True
            )
            print(f"📩 Reminder scheduled: {message} at {hour:02d}:{minute:02d} IST")
        except Exception as e:
            print(f"❌ Error sending reminder: {e}")

    threading.Thread(target=worker).start()

def parse_and_schedule(entry):
    """
    Parse entry like '10:30 Meeting with team'
    """
    try:
        time_part, task = entry.strip().split(' ', 1)
        hour, minute = map(int, time_part.strip().split(':'))

        now = datetime.now(INDIA_TZ)
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if scheduled_time < now:
            scheduled_time = scheduled_time + timedelta(days=1)  # schedule next day if time already passed

        print(f"📌 Scheduling: {task.strip()} at {hour:02d}:{minute:02d} IST")
        send_reminder(f"Reminder: {task.strip()}", hour, minute)

    except Exception as e:
        print(f"⚠️ Skipping invalid entry: {entry} ({e})")
import re
# ------------------- Main Routine -------------------
def ask_and_schedule():
    speak("Please start telling me your tasks one by one with time. Say STOP when you are done.")
    tasks = []

    while True:
        spoken_text = listen_once().lower()

        if "stop" in spoken_text:
            break

        # Look for pattern like "HH past MM"
        match = re.search(r"\b(\d{1,2})\s*past\s*(\d{1,2})\b", spoken_text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))

            # Remove the time part from spoken_text to keep only the task description
            task_desc = re.sub(r"\b\d{1,2}\s*o\s*\d{1,2}\b", "", spoken_text).strip()

            task_entry = f"{hour:02d}:{minute:02d} - {task_desc}"
            tasks.append(task_entry)
            speak("Got it. Task noted.")
        else:
            speak("Please say time in format like '10 o 30 task name'.")

    speak("Okay, scheduling your reminders now.")
    for task in tasks:
        parse_and_schedule(task)

    speak("All reminders have been scheduled. Bot is stopping now.")
    print("✅ All reminders scheduled. Exiting...")

# ------------------- Run Once -------------------
if __name__ == "__main__":
    ask_and_schedule()


