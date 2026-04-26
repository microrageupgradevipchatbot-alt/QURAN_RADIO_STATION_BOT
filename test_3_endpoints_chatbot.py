# ─────────────────────────────────────────────
# 📦 IMPORTS
# ─────────────────────────────────────────────
import requests
import json
import os
from datetime import datetime, timedelta
# from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

import streamlit as st

# ─────────────────────────────────────────────
# 🔑 ENV
# ─────────────────────────────────────────────
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]  # for streamlit deployment

# ─────────────────────────────────────────────
# 🌐 CONSTANTS
# ─────────────────────────────────────────────
API_URL = "https://dev.quranradioksa.com/api/api.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://quranradioksa.com/",
    "Origin": "https://quranradioksa.com",
}


# ─────────────────────────────────────────────
# 📡 TOOL 1 → SINGLE DATE
# ─────────────────────────────────────────────
@tool
def get_single_date(date: str) -> str:
    """Get all recordings for ONE specific date (YYYY-MM-DD)"""

    print(f"📅 TOOL1 called → {date}")

    try:
        dt = datetime.strptime(date, "%m-%d-%Y")
        date = dt.strftime("%Y-%m-%d")
    except:
        pass

    params = {
        "j": "readers_by_date",
        "start_date": date,
        "end_date": date
    }

    res = requests.get(API_URL, headers=HEADERS, params=params)

    try:
        data = res.json()
    except:
        print("❌ API error:", res.text[:200])
        return "ERROR"

    result = json.dumps(data, ensure_ascii=False)
    print("🟢 TOOL1 RETURN:\n", json.dumps(data, ensure_ascii=False, indent=4))
    return result


# ─────────────────────────────────────────────
# 📡 TOOL 2 → LAST N DAYS
# ─────────────────────────────────────────────
@tool
def get_last_n_days(end_date: str, days: int) -> str:
    """Get recordings across a range of N days ending on end_date (YYYY-MM-DD format)"""

    print(f"📅 TOOL2 called → last {days} days from {end_date}")

    end = datetime.strptime(end_date, "%Y-%m-%d")
    start = end - timedelta(days=days)

    params = {
        "j": "readers_by_date",
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d")
    }

    res = requests.get(API_URL, headers=HEADERS, params=params)

    try:
        data = res.json()
    except:
        print("❌ API error:", res.text[:200])
        return "ERROR"

    result = json.dumps(data, ensure_ascii=False)
    print("🟢 TOOL2 RETURN:\n", json.dumps(data, ensure_ascii=False, indent=4))
    return result


# ─────────────────────────────────────────────
# 🧠 LLM
# ─────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)

memory = InMemorySaver()


# ─────────────────────────────────────────────
# 🧠 SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an AI assistant for Quran Radio.

Every message you receive includes:

CONTEXT:
- current_date: YYYY-MM-DD              ← the date currently loaded on screen
- loaded_schedule: [...]                ← the full list of recordings for current_date, already fetched

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOOL SELECTION — READ CAREFULLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You have 2 tools. Choose based on these strict rules:

── RULE 1: Question is about current_date (today's loaded schedule) ──
→ DO NOT call any tool.
→ Answer directly from loaded_schedule in the context.
Examples:
  "did surah Yusuf play today?"          → search loaded_schedule, answer directly
  "what surahs were broadcast today?"    → list from loaded_schedule
  "who read today?"                      → answer from loaded_schedule

── RULE 2: Question mentions a SPECIFIC past date (not current_date) ──
→ Call get_single_date(date) with that exact date.
Examples:
  "did surah Yusuf play on April 2nd?"   → get_single_date("2026-04-02")
  "what was the schedule on 2026-03-30?" → get_single_date("2026-03-30")

── RULE 3: Question is about a RANGE / repetition / history ──
→ Call get_last_n_days(end_date=current_date, days=N)
→ Extract N from the question. If not mentioned, use N=3.
Examples:
  "did any surah repeat in the last 4 days?" → get_last_n_days(end_date, 4)
  "was this reader used before?"             → get_last_n_days(end_date, 3)
  "check last 7 days"                        → get_last_n_days(end_date, 7)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DECISION FLOWCHART
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Question mentions current_date OR "today"?
  YES → Answer from loaded_schedule. No tool call.

Question mentions a specific different date?
  YES → get_single_date(that date)

Question mentions "last N days" / "repeat" / "before" / "history"?
  YES → get_last_n_days(current_date, N)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Never return raw JSON
- Answer in English if the question is mostly English, even if it contains Arabic words; answer in Arabic only if the whole question is in Arabic.
- Structure: 1) Direct answer (yes/no or summary), 2) Brief detail, 3) Ask a follow-up.
- Only answer Quran Radio schedule questions. If off-topic i.e salary of elon musk etc., reply: "Sorry, I can only help with Quran Radio schedules."
- Never return raw JSON.
- Never ask for the date.
- Max Answer length (5-8 sentences).
- Never ask the user for the date
"""


# ─────────────────────────────────────────────
# 🤖 AGENT
# ─────────────────────────────────────────────
agent = create_react_agent(
    llm,
    tools=[get_single_date, get_last_n_days],
    checkpointer=memory,
    prompt=SYSTEM_PROMPT,
)


# ─────────────────────────────────────────────
# 🧩 INPUT BUILDER (IMPORTANT)
# ─────────────────────────────────────────────
def build_input(question: str, current_date: str):
    return f"""
CONTEXT:
- current_date: {current_date}

USER QUESTION:
{question}
"""


# ─────────────────────────────────────────────
# 💬 CLI LOOP
# ─────────────────────────────────────────────
# CURRENT_DATE = "2026-04-02"

# print("🚀 Agent Ready\n")

# while True:
#     q = input("❓ Ask: ")

#     if q.lower() in ["exit", "quit"]:
#         break

#     final_input = build_input(q, CURRENT_DATE)
#     print("\n📝 PROMPT SENT TO AGENT:\n", final_input)

#     result = agent.invoke(
#         {"messages": [("user", final_input)]},
#         config={
#             "configurable": {"thread_id": "cli-session"},
#             "max_iterations": 5
#         }
#     )

#     print("\n🤖 Answer:")

#     reply = result["messages"][-1].content

#     if isinstance(reply, list) and reply and isinstance(reply[0], dict):
#         print(reply[0].get("text", reply))
#     else:
#         print(reply)

#     print("\n" + "=" * 50 + "\n")
