import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".env"
    )
)

api_key = os.getenv("GEMINI_API_KEY")
import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API anahtarı bulunamadı!")
    st.stop()

client = genai.Client(api_key=api_key)

st.title("🚀 AstroGuard AI Assistant")
st.write("Astronot sağlık asistanına hoş geldin!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Astronot olarak sorunuzu yazın...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AstroGuard düşünüyor..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[
                        "Sen AstroGuard adlı bir astronot "
                        "sağlık destek asistanısın. "
                        "Soruları bilimsel ve anlaşılır şekilde "
                        "yanıtla. Teşhis koyma. Acil durumlarda "
                        "astronotun görev sağlık ekibine "
                        "başvurmasını öner.\n\n"
                        + prompt
                    ]
                )

                answer = response.text
                st.write(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"AI bağlantı hatası: {e}")
