import json
import uuid
import logging
import traceback
import streamlit as st
from datetime import date
from test_3_endpoints_chatbot import agent, get_single_date

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quran Radio · Schedule Checker",
    page_icon="📻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&family=Space+Mono:wght@400;700&display=swap');

html, body, .stApp, [class*="css"] {
    font-family: 'Tajawal', sans-serif !important;
    background: #0d0f14 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.qr-topbar {
    background: #111318;
    border-bottom: 1px solid #1e2130;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 28px;
    height: 54px;
    margin-bottom: 0;
}
.qr-logo {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #c8a84b;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.qr-topbar-right {
    margin-left: auto;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #8a90a8;
    letter-spacing: 1px;
}

.sec-lbl {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #8a90a8;
    margin-bottom: 12px;
}



.tbl-wrap { border: 1px solid #1e2130; border-radius: 10px; overflow: hidden; }
.tbl-head {
    display: grid;
    grid-template-columns: 36px 1.8fr 1.8fr 1fr 1.4fr 70px;
    background: #111318; border-bottom: 1px solid #1e2130;
    padding: 10px 16px; gap: 8px;
}
.tbl-head-cell {
    font-family: 'Space Mono', monospace; font-size: 9px;
    font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #8a90a8 !important;
}
.tbl-row {
    display: grid;
    grid-template-columns: 36px 1.8fr 1.8fr 1fr 1.4fr 70px;
    padding: 11px 16px; border-bottom: 1px solid #1a1c26;
    gap: 8px; align-items: center; animation: rowIn 0.25s ease both;
}
.tbl-row:last-child { border-bottom: none; }
.tbl-row:hover { background: #14161f !important; }

@keyframes rowIn {
    from { opacity: 0; transform: translateY(5px); }
    to   { opacity: 1; transform: translateY(0); }
}

.row-neutral { background: #0d0f14; }
.row-pass    { background: #0a1410; }
.row-fail    { background: #160e0e; }

.tbl-cell       { font-size: 13px; color: #c8cad8 !important; }
.tbl-cell-mono  { font-size: 11px; color: #c8cad8 !important; font-family: 'Space Mono', monospace; }
.tbl-cell-muted { font-size: 12px; color: #c8cad8 !important; }

.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin: auto; }
.dot-neutral { background: #2a2d3e; border: 1px solid #3a3d50; }
.dot-pass    { background: #1a7a44; box-shadow: 0 0 6px #1a7a4488; }
.dot-fail    { background: #b03030; box-shadow: 0 0 6px #b0303088; }

.popup-wrap { padding: 8px 16px 14px 52px; border-bottom: 1px solid #1a1c26; animation: rowIn 0.2s ease; }
.popup-box  { border-radius: 8px; padding: 12px 16px; font-size: 13px; line-height: 1.7; }
.popup-pass { background: #0a1a12; border: 1px solid #1a5c30; color: #6dbf8a !important; direction: rtl; text-align: right; }
.popup-fail { background: #1a0d0d; border: 1px solid #5c1a1a; color: #d47a7a !important; direction: rtl; text-align: right; }

.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon  { font-size: 40px; margin-bottom: 16px; }
.empty-title { font-size: 15px; color: #3a3d50 !important; font-weight: 500; }
.empty-sub   { font-size: 12px; color: #2a2d3e !important; margin-top: 6px; }

.chat-header {
    padding: 16px 20px 12px; background: #111318;
    border-bottom: 1px solid #1e2130;
    font-family: 'Space Mono', monospace; font-size: 10px;
    font-weight: 700; letter-spacing: 2px; color: #8a90a8 !important; text-transform: uppercase;
}
.reply-bubble {
    background: #14161f; border: 1px solid #1e2130; border-radius: 10px;
    padding: 14px 16px; font-size: 13px; line-height: 1.7;
    color: #c8cad8 !important; animation: rowIn 0.25s ease; margin-bottom: 10px;
}
.reply-pass { background: #0a1a12; border-color: #1a5c30; }
.reply-fail { background: #1a0d0d; border-color: #5c1a1a; }



[data-testid="stDateInput"] label,
[data-testid="stTextInput"] label {
    color: #8a90a8 !important; font-size: 10px !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
}
[data-baseweb="base-input"], [data-baseweb="input"] {
    background: #111318 !important; border: 1px solid #1e2130 !important; border-radius: 8px !important;
}
[data-baseweb="input"] input, [data-testid="stDateInput"] input {
    color: #c8cad8 !important; font-family: 'Space Mono', monospace !important; font-size: 12px !important;
}
[data-baseweb="input"] input::placeholder {
    color: #8a90a8 !important; opacity: 1 !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background: #c8a84b !important; color: #0d0f14 !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-family: 'Tajawal', sans-serif !important;
    font-size: 13px !important; height: 38px !important;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover { background: #d9b95a !important; }
.stSpinner > div { border-top-color: #c8a84b !important; }
.stForm small, [data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, v in {
    "table_data":   [],
    "thread_id":    str(uuid.uuid4()),
    "current_date": date.today().isoformat(),
    "expanded_row": None,
    "last_reply":   "",
    "reply_class":  "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def fetch_schedule(d: str):
    """
    Directly call Tool 1 to load one day's schedule.
    No agent needed — fast and deterministic.
    """
    try:
        raw  = get_single_date.invoke({"date": d})
        data = json.loads(raw)

        # handle both {"schedules": [...]} and flat list
        if isinstance(data, dict):
            recordings = []
            for schedule in data.get("schedules", []):
                for rec in schedule.get("recordings", []):
                    recordings.append({
                        "date":              schedule.get("date", d),
                        "surah_name":        rec.get("surah_name", ""),
                        "reader":            rec.get("reader", ""),
                        "category":          rec.get("category", ""),
                        "recording_number":  rec.get("recording_number", ""),
                        "duration":          rec.get("duration", ""),
                        "recitation_timing": rec.get("recitation_timing", ""),
                    })
        else:
            recordings = data  # already flat list

        st.session_state.table_data   = [{**r, "status": "neutral", "reason": ""} for r in recordings]
        st.session_state.current_date = d
        st.session_state.expanded_row = None
        st.session_state.last_reply   = ""
        st.session_state.thread_id    = str(uuid.uuid4())  # fresh memory per date load
        return True, len(recordings)
    except Exception as e:
        return False, str(e)


def build_agent_prompt(question: str) -> str:
    """
    Always inject current_date AND the already-loaded records into the prompt.
    This way the LLM knows exactly what's on screen without re-fetching.
    For repetition questions it will still call get_last_n_days itself.
    """
    records_json = json.dumps(
        [
            {
                "recording_number":  r["recording_number"],
                "surah_name":        r["surah_name"],
                "reader":            r["reader"],
                "category":          r.get("category", ""),
                "recitation_timing": r.get("recitation_timing", ""),
                "duration":          r.get("duration", ""),
            }
            for r in st.session_state.table_data
        ],
        ensure_ascii=False,
    )

    return f"""
CONTEXT:
- current_date: {st.session_state.current_date}
- loaded_schedule (records currently on screen for {st.session_state.current_date}):
{records_json}

USER QUESTION:
{question}
"""

# ─────────────────────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qr-topbar">
    <span class="qr-logo">📻 &nbsp;Quran Radio</span>
    <span class="qr-topbar-right">Schedule Checker &nbsp;·&nbsp; {date.today().strftime("%d %b %Y")}</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────
col_main, col_chat = st.columns([3.2, 1], gap="small")

# ═════════════════════════════════════════════════════════════
# LEFT — SCHEDULE TABLE
# ═════════════════════════════════════════════════════════════
with col_main:
    st.markdown("<div style='padding:24px 32px 32px'>", unsafe_allow_html=True)

    # date controls
    c1, c2, _ = st.columns([1.6, 0.5, 2.3])
    with c1:
        selected_date = st.date_input("DATE", value=date(2026, 4, 1))
    with c2:
        st.markdown("<div style='margin-top:22px'>", unsafe_allow_html=True)
        load_btn = st.button("Load", key="load_btn", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── LOAD ──
    if load_btn:
        with st.spinner("Fetching schedule…"):
            ok, info = fetch_schedule(selected_date.isoformat())
        if not ok:
            st.error(f"API error: {info}")
        elif info == 0:
            st.warning("No recordings found for this date.")



    # ── TABLE ──
    st.markdown('<div class="sec-lbl" style="margin-top:8px">Recitation Schedule</div>', unsafe_allow_html=True)

    if st.session_state.table_data:
        st.markdown("""
        <div class="tbl-wrap">
          <div class="tbl-head">
            <div class="tbl-head-cell">●</div>
            <div class="tbl-head-cell">Surah</div>
            <div class="tbl-head-cell">Reader</div>
            <div class="tbl-head-cell">Category</div>
            <div class="tbl-head-cell">Timing</div>
            <div class="tbl-head-cell">Dur.</div>
          </div>
        """, unsafe_allow_html=True)

        for idx, row in enumerate(st.session_state.table_data):
            rec     = row.get("recording_number", str(idx))
            status  = row.get("status", "neutral")
            reason  = row.get("reason", "")
            is_open = st.session_state.expanded_row == rec
            delay   = min(idx * 0.025, 0.5)

            st.markdown(f"""
            <div class="tbl-row row-{status}" style="animation-delay:{delay}s">
              <div style="display:flex;justify-content:center">
                <span class="dot dot-{status}"></span>
              </div>
              <div class="tbl-cell">{row.get('surah_name','—')}</div>
              <div class="tbl-cell">{row.get('reader','—')}</div>
              <div class="tbl-cell-muted">{row.get('category','—')}</div>
              <div class="tbl-cell-mono">{row.get('recitation_timing','—')}</div>
              <div class="tbl-cell-mono">{row.get('duration','—')}m</div>
            </div>
            """, unsafe_allow_html=True)

            if status in ("pass", "fail"):
                label = f"{'▲' if is_open else '▼'} {row.get('surah_name','')}"
                if st.button(label, key=f"tog_{rec}_{idx}"):
                    st.session_state.expanded_row = None if is_open else rec
                    st.rerun()
                if is_open:
                    cls  = "popup-pass" if status == "pass" else "popup-fail"
                    icon = "✅" if status == "pass" else "⚠️"
                    text = reason if reason else "لم تتكرر هذه السورة أو القارئ في النطاق الزمني المحدد."
                    st.markdown(f"""
                    <div class="popup-wrap">
                      <div class="popup-box {cls}">{icon} {text}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="tbl-wrap">
          <div class="empty-state">
            <div class="empty-icon">📅</div>
            <div class="empty-title">No schedule loaded</div>
            <div class="empty-sub">Pick a date and press Load to view the recitation schedule</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# RIGHT — CHAT PANEL
# ═════════════════════════════════════════════════════════════
with col_chat:
    st.markdown('<div class="chat-header">🤖 &nbsp;AI Checker</div>', unsafe_allow_html=True)

    # show last reply if exists
    if st.session_state.last_reply:
        rc = st.session_state.get("reply_class", "")
        st.markdown(f"""
        <div style="padding:14px 16px 0">
          <div class="reply-bubble {rc}">{st.session_state.last_reply}</div>
        </div>
        """, unsafe_allow_html=True)

    # input
    st.markdown("<div style='padding:12px 16px 16px'>", unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_input(
            "q", value="",
            placeholder="اسأل سؤالك هنا",
            label_visibility="collapsed",
            autocomplete="off",
        )
        send_btn = st.form_submit_button("Check ✓", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── HANDLE SEND ──
    if send_btn and user_query.strip():
        if not st.session_state.table_data:
            st.warning("⚠️ Load a schedule first!")
        else:
            with st.spinner("Analyzing…"):
                try:
                    prompt = build_agent_prompt(user_query)
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}

                    result = agent.invoke(
                        {"messages": [("user", prompt)]},
                        config=config,
                    )

                    ai_raw = result["messages"][-1].content
                    if isinstance(ai_raw, list):
                        ai_raw = " ".join(
                            p.get("text", "") if isinstance(p, dict) else str(p)
                            for p in ai_raw
                        ).strip()
                    ai_raw = ai_raw.replace("```json", "").replace("```", "").strip()

                    display_msg = ""
                    reply_class = ""

                    try:
                        parsed = json.loads(ai_raw)
                        if isinstance(parsed, list) and parsed and "status" in parsed[0]:
                            # structured result → update table dots
                            result_map = {r["recording_number"]: r for r in parsed}
                            st.session_state.table_data = [
                                {
                                    **row,
                                    "status": result_map.get(row["recording_number"], {}).get("status", row["status"]),
                                    "reason": result_map.get(row["recording_number"], {}).get("reason", row["reason"]),
                                }
                                for row in st.session_state.table_data
                            ]
                            fails  = [r for r in parsed if r["status"] == "fail"]
                            passes = [r for r in parsed if r["status"] == "pass"]
                            if fails:
                                display_msg = (
                                    f"🔴 <b>{len(fails)}</b> issue(s) &nbsp;|&nbsp; "
                                    f"🟢 <b>{len(passes)}</b> clean.<br>"
                                    f"<small style='color:#888'>Click a row to see details.</small>"
                                )
                                reply_class = "reply-fail"
                            else:
                                display_msg = f"✅ All <b>{len(passes)}</b> passed!"
                                reply_class = "reply-pass"
                        else:
                            display_msg = ai_raw
                    except (json.JSONDecodeError, TypeError):
                        display_msg = ai_raw  # plain text answer

                    st.session_state.last_reply  = display_msg
                    st.session_state.reply_class = reply_class

                except Exception as e:
                    logging.getLogger("QuranRadio").error(traceback.format_exc())
                    st.session_state.last_reply  = f"⚠️ Error: {e}"
                    st.session_state.reply_class = "reply-fail"

            st.rerun()
