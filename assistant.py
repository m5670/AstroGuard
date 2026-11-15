# ============================================================
# AI USAGE AND INTEGRATION DISCLOSURE
# ============================================================
# DEVELOPMENT:
# ChatGPT (OpenAI) was used as a development support tool
# for code explanations, debugging, and implementation guidance.
#
# RUNTIME AI INTEGRATION:
# Google Gemini API is integrated into AstroGuard to provide
# AI-generated responses to astronauts' questions.
#
# The Gemini assistant can use the user's question, recent
# health measurements, Earth baseline data, and conversation
# history as contextual information.
#
# The AI-generated responses are informational and must not
# be considered a substitute for professional medical advice
# or approved mission medical protocols.
#
# AI MODEL:
# Gemini 3.5 Flash Lite
#
# The developer reviewed and integrated the implementation.
# ============================================================
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# API anahtarını yükle
load_dotenv(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
)

api_key = os.getenv("GEMINI_API_KEY")

# Streamlit Cloud Secrets kontrolü
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = None

client = genai.Client(api_key=api_key) if api_key else None


def answer_question(
    question,
    measurements,
    baseline,
    lang,
    chat_history=None
):

    if lang == "Türkçe":
        language_instruction = "Türkçe cevap ver."
    else:
        language_instruction = "Answer in English."

    if client is None:
        return (
            "Gemini API anahtarı bulunamadı."
            if lang == "Türkçe"
            else "Gemini API key not found."
        )

    # Son ölçümleri hazırla
    if measurements is not None and not measurements.empty:
        recent = measurements.tail(10)
        measurement_data = recent.to_string(index=False)
    else:
        measurement_data = "No measurements recorded."

    # Başlangıç değerlerini hazırla
    if baseline:
        baseline_data = str(baseline)
    else:
        baseline_data = "No Earth baseline recorded."

    # Sohbet geçmişini hazırla
    history_text = ""

    if chat_history:
        for message in chat_history[-30:]:

            role = (
                "Astronaut"
                if message["role"] == "user"
                else "Assistant"
            )

            history_text += (
                f"\n{role}: {message['content']}\n"
            )

    prompt = f"""
You are AstroGuard AI, an intelligent assistant for astronauts.

YOUR RESPONSIBILITIES:
- Answer general knowledge questions.
- Explain scientific and technical concepts.
- Help astronauts with space-related questions.
- Explain astronaut health measurements when asked.
- Compare measurements with Earth baseline when requested.
- Explain detected anomalies when requested.
- Remember and use conversation history.

CONVERSATION MEMORY RULES:
- Previous messages are provided below.
- Use them to understand follow-up questions.
- Remember information shared earlier in this conversation.
- Do not ask users to repeat information already in history.
- Do not claim to remember information that is not in history.
- History is ordered from oldest to newest.

HEALTH DATA RULES:
- Health data is background context.
- Do not automatically display health measurements.
- Do not mention health data in unrelated answers.
- Only show measurements when relevant or requested.
- Never invent health measurements.
- If requested data is unavailable, say so.
- Prototype thresholds are not validated medical advice.
- For urgent symptoms or critical readings, advise following mission medical protocols and contacting the medical team.

LANGUAGE:
{language_instruction}

ASTRONAUT EARTH BASELINE:
{baseline_data}

RECENT HEALTH MEASUREMENTS:
{measurement_data}

PREVIOUS CONVERSATION:
{history_text}

NEW ASTRONAUT MESSAGE:
{question}

RESPONSE RULES:
- Answer the latest message.
- Use previous conversation when relevant.
- Keep answers clear and helpful.
- Do not repeat the entire conversation.
- Do not include unrelated health statistics.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text or (
            "AI boş yanıt döndürdü."
            if lang == "Türkçe"
            else "AI returned an empty response."
        )

    except Exception as e:

        error = str(e)

        if "503" in error:
            return (
                "Gemini sunucusu şu anda yoğun. "
                "Lütfen biraz sonra tekrar deneyin."
                if lang == "Türkçe"
                else "Gemini is currently experiencing high demand. "
                     "Please try again later."
            )

        if "429" in error:
            return (
                "API kullanım limitine ulaşıldı."
                if lang == "Türkçe"
                else "API usage limit reached."
            )

        return (
            f"AI bağlantı hatası: {error}"
            if lang == "Türkçe"
            else f"AI connection error: {error}"
        )
