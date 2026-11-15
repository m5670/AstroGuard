import streamlit as st
import plotly.express as px

from database import (
    init_db,
    add_measurement,
    get_measurements,
    get_baseline,
    save_baseline,
    delete_measurements,

    # AI Chat
    add_chat_message,
    get_chat_history,
    clear_chat_history,
    create_chat_conversation,
    get_chat_conversations,
    delete_chat_conversation,

    # Astronauts
    add_astronaut,
    get_astronauts,
    astronaut_exists,
    delete_astronaut
)

from analysis import analyze_measurement
from assistant import answer_question
from emergency import get_emergency_notice

st.set_page_config(page_title="AstroGuard", page_icon="🚀", layout="wide")

# ==============================
# ASTROGUARD DESIGN SYSTEM
# ==============================

# CSS Tasarımı
st.markdown("""
<style>

/* Ana arka plan */
.stApp {
    background: radial-gradient(
        circle at top right,
        #142b45 0%,
        #081321 45%,
        #050b14 100%
    );
    color: #e6f4ff;
}

/* Ana içerik */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Başlıklar */
h1, h2, h3 {
    color: #eaf7ff !important;
    font-family: Arial, sans-serif;
    letter-spacing: 0.5px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0b1b2d,
        #07111e
    );
    border-right: 1px solid #173c59;
}

/* Kartlar */
div[data-testid="stMetric"] {
    background: rgba(14, 37, 59, 0.85);
    border: 1px solid #1d5273;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 0 12px rgba(0, 183, 255, 0.08);
}

/* Butonlar */
.stButton > button {
    background: linear-gradient(90deg, #087eaa, #00b4d8);
    color: white;
    border: 1px solid #35d5ff;
    border-radius: 8px;
    font-weight: bold;
}

.stButton > button:hover {
    background: #00a6cc;
    border: 1px solid #8beaff;
    box-shadow: 0 0 12px rgba(0, 200, 255, 0.4);
}

/* Giriş alanları */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #10263a;
    color: white;
    border: 1px solid #286080;
    border-radius: 7px;
}

/* Ayırıcılar */
hr {
    border-color: #21445e;
}
/* Üst siyah alan */
header[data-testid="stHeader"] {
    background: linear-gradient(
        90deg,
        #081321,
        #10243a
    ) !important;
}

/* Alt siyah alan */
div[data-testid="stBottom"] {
    background: linear-gradient(
        90deg,
        #081321,
        #10243a
    ) !important;
}

/* Alt alanın arka plan geçişini kaldır */
div[data-testid="stBottom"] > div {
    background: transparent !important;
}

/* Sohbet giriş alanı */
div[data-testid="stChatInput"] {
    background-color: #142b45 !important;
    border-radius: 16px !important;
}
/* Streamlit üst çubuğu */
header[data-testid="stHeader"] {
    background: linear-gradient(
        90deg,
        #081321,
        #142b45
    ) !important;
}

/* Üst çubuğa ASTROGUARD yazısı */
header[data-testid="stHeader"]::before {
    content: "🚀 ASTROGUARD";
    color: white;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 2px;
    position: absolute;
    left: 25px;
    top: 12px;
    z-index: 999999;
}
</style>
""", unsafe_allow_html=True)

init_db()

# LANGUAGE SELECTION
lang = st.sidebar.selectbox(
    "🌍 Language / Dil",
    ["Türkçe", "English"]
)

TR = lang == "Türkçe"


# Kayıtlı astronotları getir

astronauts = get_astronauts()

st.sidebar.markdown(
    f"### 🧑‍🚀 {'Astronot Kimliği' if lang == 'Türkçe' else 'Astronaut Identification'}"
)

astronaut_options = {
    f"{a['name']} ({a['astronaut_id']})": a['astronaut_id']
    for a in astronauts
}

if astronauts:

    selected_label = st.sidebar.selectbox(
        "Astronot Seç" if TR else "Select Astronaut",
        list(astronaut_options.keys())
    )

    selected_astronaut_id = astronaut_options[selected_label]

    astronaut_name = next(
        a["name"] for a in astronauts
        if a["astronaut_id"] == selected_astronaut_id
    )

else:
    selected_astronaut_id = None
    astronaut_name = None

    st.sidebar.warning(
        "Henüz kayıtlı astronot yok. Yeni astronot ekleyin."
        if TR else
        "No astronauts registered. Add a new astronaut."
    )


# Yeni astronot ekleme
with st.sidebar.expander(
    "➕ Yeni Astronot Ekle" if TR else "➕ Add New Astronaut"
):

    with st.form("add_astronaut_form"):

        new_name = st.text_input(
            "Astronot Adı" if TR else "Astronaut Name"
        )

        new_id = st.text_input(
            "Astronot ID" if TR else "Astronaut ID",
            placeholder="AST-002"
        ).strip().upper()

        add_submitted = st.form_submit_button(
            "Astronot Ekle" if TR else "Add Astronaut"
        )

    if add_submitted:

        if not new_name.strip() or not new_id:
            st.sidebar.error(
                "Tüm alanları doldurun!" if TR else "Fill in all fields!"
            )

        elif not new_id.startswith("AST-"):
            st.sidebar.error(
                "ID AST- ile başlamalı!" if TR else "ID must start with AST-!"
            )

        elif astronaut_exists(new_id):
            st.sidebar.error(
                "Bu ID zaten kayıtlı!" if TR else "This ID already exists!"
            )

        else:
            add_astronaut(new_id, new_name.strip())

            st.sidebar.success(
                "Astronot eklendi!" if TR else "Astronaut added!"
            )

            st.rerun()


# Astronot silme
with st.sidebar.expander(
    "🗑️ Kayıtlı Astronotu Sil" if TR else "🗑️ Delete Astronaut"
):

    if not astronauts:
        st.info(
            "Silinecek kayıtlı astronot yok."
            if TR else
            "There are no astronauts to delete."
        )

    else:
        with st.form("delete_astronaut_form"):

            delete_confirm = st.checkbox(
                f"{astronaut_name} ({selected_astronaut_id}) "
                + (
                    "astronotunu silmek istiyorum."
                    if TR else
                    "I want to delete this astronaut."
                )
            )

            delete_submitted = st.form_submit_button(
                "Astronotu Sil" if TR else "Delete Astronaut"
            )

        if delete_submitted:

            if delete_confirm:
                deleted = delete_astronaut(selected_astronaut_id)

                if deleted:
                    st.session_state["astronaut_delete_message"] = (
                        "Astronot ve tüm kayıtları silindi!"
                        if TR else
                        "Astronaut and all records deleted!"
                    )
                    st.rerun()

                else:
                    st.sidebar.error(
                        "Astronot bulunamadı!"
                        if TR else
                        "Astronaut not found!"
                    )

            else:
                st.sidebar.warning(
                    "Lütfen silme işlemini onaylayın."
                    if TR else
                    "Please confirm deletion."
                )

if "astronaut_delete_message" in st.session_state:
    st.sidebar.success(
        st.session_state.pop("astronaut_delete_message")
    )




T = {
    "title": "Astronot Sağlık Takip Sistemi" if TR else "Astronaut Health Monitoring System",
    "dashboard": "Ana Sayfa" if TR else "Dashboard",
    "baseline": "Dünya Başlangıç Verileri" if TR else "Earth Baseline",
    "measurement": "Yeni Ölçüm" if TR else "New Measurement",
    "measurements": "Ölçümler" if TR else "Measurements",
    "assistant": "Yapay Zeka Asistanı" if TR else "AI Assistant",
    "emergency": "Acil Durum Rehberi" if TR else "Emergency Guidance",
    "guide": "Ölçüm Rehberi" if TR else "Measurement Guide",
    "navigation": "Menü" if TR else "Navigation",
    "heart": "Kalp Atış Hızı (bpm)" if TR else "Heart Rate (bpm)",
    "temperature": "Vücut Sıcaklığı (°C)" if TR else "Body Temperature (°C)",
    "oxygen": "Oksijen Doygunluğu (%)" if TR else "Oxygen Saturation (%)",
    "save": "Kaydet" if TR else "Save",
    "history": "Ölçüm Geçmişi" if TR else "Measurement History",
    "assessment": "Sağlık Değerlendirmesi" if TR else "Health Assessment",
    "question": "Sorunuzu yazın" if TR else "Ask your question",
    "ask": "Sor" if TR else "Ask",
    "notes": "Ek Notlar" if TR else "Additional Notes",
    "situation": "Bir durum seçin" if TR else "Select a situation",
    "no_data": "Henüz ölçüm kaydedilmedi." if TR else "No measurements recorded yet.",
    "saved": "Ölçüm kaydedildi!" if TR else "Measurement saved!",
    "baseline_saved": "Başlangıç verileri kaydedildi!" if TR else "Baseline saved!",
    "metric": "Ölçüm türünü seçin" if TR else "Select measurement",
    "baseline_info": "Astronotun Dünya'daki kişisel referans değerlerini kaydedin." if TR else "Save the astronaut's personal reference measurements on Earth.",
    "emergency_warning": "Gerçek bir acil durumda onaylanmış tıbbi prosedürleri izleyin ve görev kontrol merkeziyle iletişime geçin." if TR else "For a real emergency, follow approved medical procedures and contact mission control.",
    "mission_control": "Görev Kontrol Merkezi" if TR else "Mission Control",
    "alert": "Sağlık Uyarıları" if TR else "Health Alerts",
    "astronaut": "Astronot" if TR else "Astronaut",
    "alert_time": "Ölçüm Zamanı" if TR else "Measurement Time",
    "alert_reason": "Uyarı Nedeni" if TR else "Alert Reason",
    "no_alert": "Şu anda incelenmesi gereken bir uyarı yok." if TR else "No alerts requiring review."
}


def show_health_result(result, measurement, astronaut_name=None):
    """Display a clean and consistent astronaut health alert."""

    status = result.get("status", "Review")
    details = result.get("details", "")

    if status == "Critical":
        st.error("🚨 " + result["summary"])
    elif status == "Warning":
        st.warning("⚠️ " + result["summary"])
    elif status == "Normal":
        st.success("🟢 " + result["summary"])
    else:
        st.info("ℹ️ " + result["summary"])

    if astronaut_name:
        st.caption(f"👨‍🚀 {astronaut_name}")

    # Main measurements
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "❤️ " + ("Kalp Atış Hızı" if TR else "Heart Rate"),
        f"{measurement.get('heart_rate', '—')} bpm"
    )

    col2.metric(
        "🌡️ " + ("Sıcaklık" if TR else "Temperature"),
        f"{measurement.get('temperature', '—')} °C"
    )

    col3.metric(
        "🫁 " + ("Oksijen" if TR else "Oxygen"),
        f"{measurement.get('oxygen', '—')}%"
    )

    # Separate recommended actions from technical details
    marker_tr = "📋 ÖNERİLEN EYLEMLER:"
    marker_en = "📋 RECOMMENDED ACTIONS:"

    marker = marker_tr if TR else marker_en

    technical_details, separator, action_details = details.partition(marker)

    # Recommended actions
    if separator and action_details.strip():
        st.markdown(
            "### 📋 " + (
                "Önerilen Eylemler" if TR else "Recommended Actions"
            )
        )
        st.markdown(action_details.strip())

    # Technical report
    if technical_details.strip():
        with st.expander(
            "📊 " + (
                "Detaylı Sağlık Raporu" if TR else "Detailed Health Report"
            )
        ):
            st.text(technical_details.strip())

page = st.sidebar.radio(
    T["navigation"],
    [
        T["dashboard"],
        T["measurements"],
        T["assistant"],
        T["emergency"],
        T["guide"],
        T["mission_control"]
    ]
)
if not selected_astronaut_id:
    st.info(
        "Devam etmek için sol menüden yeni bir astronot ekleyin."
        if TR else
        "Please add a new astronaut from the sidebar to continue."
    )

elif page == T["dashboard"]:

    st.header(T["dashboard"])

    df = get_measurements(selected_astronaut_id)
    baseline = get_baseline(selected_astronaut_id)

    if df.empty:
        st.info(T["no_data"])

    else:
        latest = df.iloc[-1]



        result = analyze_measurement(
            latest.to_dict(),
            baseline,
            lang
        )

        st.subheader(T["assessment"])

        show_health_result(
            result,
            latest.to_dict(),
            astronaut_name
        )


        st.subheader(T["history"])
        
        metric_labels = {
            "heart_rate": "❤️ Kalp Atış Hızı (bpm)" if TR else "❤️ Heart Rate (bpm)",
            "temperature": "🌡️ Vücut Sıcaklığı (°C)" if TR else "🌡️ Body Temperature (°C)",
            "oxygen": "🫁 Oksijen Doygunluğu (%)" if TR else "🫁 Oxygen Saturation (%)",
            "respiratory_rate": "🌬️ Solunum Hızı (nefes/dk)" if TR else "🌬️ Respiratory Rate (breaths/min)",
            "systolic_bp": "🩸 Büyük Tansiyon (mmHg)" if TR else "🩸 Systolic BP (mmHg)",
            "diastolic_bp": "🩸 Küçük Tansiyon (mmHg)" if TR else "🩸 Diastolic BP (mmHg)",
            "radiation_rate": "☢️ Radyasyon Doz Hızı (µSv/saat)" if TR else "☢️ Radiation Rate (µSv/hour)",
            "radiation_dose": "☢️ Toplam Radyasyon Dozu (mSv)" if TR else "☢️ Total Radiation Dose (mSv)"
        }

        metric = st.selectbox(
            T["metric"],
            list(metric_labels.keys()),
            format_func=lambda x: metric_labels[x]
        )  

        fig = px.line(
            df,
            x="measured_at",
            y=metric,
            markers=True,
            title=metric_labels[metric],
            template="plotly_dark"
        )

        fig.update_traces(
            line=dict(color="#00c8ff", width=3),
            marker=dict(size=8, color="#39d9ff")
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(8,19,33,0.5)",
            font=dict(color="#e6f4ff"),
            xaxis=dict(showgrid=True, gridcolor="#19364d"),
            yaxis=dict(showgrid=True, gridcolor="#19364d")
        )

        st.plotly_chart(fig, use_container_width=True)


elif page == T["measurements"]:

    st.header(T["measurements"])

    tab1, tab2 = st.tabs([
        "🌍 Dünya Başlangıç Verileri" if TR else "🌍 Earth Baseline",
        "🚀 Yeni Ölçüm" if TR else "🚀 New Measurement"
    ])

    # ==============================
    # TAB 1 - DÜNYA BAŞLANGIÇ VERİLERİ
    # ==============================

    with tab1:

        st.write(T["baseline_info"])

        with st.form("baseline_form"):

            st.markdown("### ❤️ Temel Sağlık Değerleri" if TR else "### ❤️ Basic Health Values")

            col1, col2, col3 = st.columns(3)

            with col1:
                hr = st.number_input(
                    T["heart"],
                    min_value=1,
                    max_value=300,
                    value=70
                )

            with col2:
                temp = st.number_input(
                    T["temperature"],
                    min_value=30.0,
                    max_value=45.0,
                    value=36.8,
                    step=0.1
                )

            with col3:
                oxygen = st.number_input(
                    T["oxygen"],
                    min_value=1,
                    max_value=100,
                    value=98
                )

            st.divider()

            st.markdown(
                "### 🫁 Solunum ve Tansiyon" if TR
                else "### 🫁 Respiratory and Blood Pressure"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                respiratory_rate = st.number_input(
                    "Solunum Hızı (nefes/dk)" if TR else "Respiratory Rate (breaths/min)",
                    min_value=1,
                    max_value=100,
                    value=16
                )

            with col2:
                systolic_bp = st.number_input(
                    "Büyük Tansiyon (mmHg)" if TR else "Systolic BP (mmHg)",
                    min_value=1,
                    max_value=300,
                    value=120
                )

            with col3:
                diastolic_bp = st.number_input(
                    "Küçük Tansiyon (mmHg)" if TR else "Diastolic BP (mmHg)",
                    min_value=1,
                    max_value=200,
                    value=80
                )

            st.divider()

            st.markdown(
                "### ☢️ Radyasyon Referansı" if TR
                else "### ☢️ Radiation Reference"
            )

            col1, col2 = st.columns(2)

            with col1:
                radiation_rate = st.number_input(
                    "Anlık Doz Hızı (µSv/saat)" if TR else "Radiation Rate (µSv/hour)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01
                )

            with col2:
                radiation_dose = st.number_input(
                    "Toplam Radyasyon Dozu (mSv)" if TR else "Total Radiation Dose (mSv)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01
                )

            submitted = st.form_submit_button(T["save"])
            if submitted:

                if not selected_astronaut_id:
                    st.warning("Önce bir astronot ekleyin!")

                elif not astronaut_exists(selected_astronaut_id):
                    st.error("Geçersiz Astronot ID!")

                else:
                    save_baseline(
                        hr,
                        temp,
                        oxygen,
                        respiratory_rate,
                        systolic_bp,
                        diastolic_bp,
                        radiation_rate,
                        radiation_dose,
                        astronaut_id=selected_astronaut_id
                    )

                    st.success(T["baseline_saved"])

    # ==============================
    # TAB 2 - YENİ ÖLÇÜM
    # ==============================

    with tab2:

        st.subheader(
            "🧬 Astronot Sağlık Ölçümü"
            if TR else
            "🧬 Astronaut Health Measurement"
        )

        with st.form("measurement_form"):

            st.markdown("### ❤️ Temel Sağlık Değerleri" if TR else "### ❤️ Basic Health Values")

            col1, col2, col3 = st.columns(3)

            with col1:
                hr = st.number_input(
                    T["heart"],
                    min_value=0,
                    max_value=300,
                    value=75
                )

            with col2:
                temp = st.number_input(
                    T["temperature"],
                    min_value=0.0,
                    max_value=60.0,
                    value=36.8,
                    step=0.1
                )

            with col3:
                oxygen = st.number_input(
                    T["oxygen"],
                    min_value=0,
                    max_value=100,
                    value=98
                )

            st.divider()

            st.markdown(
                "### 🫁 Solunum ve Tansiyon" if TR
                else "### 🫁 Respiratory and Blood Pressure"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                respiratory_rate = st.number_input(
                    "Solunum Hızı (nefes/dk)" if TR else "Respiratory Rate (breaths/min)",
                    min_value=0,
                    max_value=100,
                    value=16
                )

            with col2:
                systolic_bp = st.number_input(
                    "Büyük Tansiyon (mmHg)" if TR else "Systolic BP (mmHg)",
                    min_value=0,
                    max_value=300,
                    value=120
                )

            with col3:
                diastolic_bp = st.number_input(
                    "Küçük Tansiyon (mmHg)" if TR else "Diastolic BP (mmHg)",
                    min_value=0,
                    max_value=200,
                    value=80
                )

            st.divider()

            st.markdown(
                "### ☢️ Radyasyon Takibi" if TR
                else "### ☢️ Radiation Monitoring"
            )

            col1, col2 = st.columns(2)

            with col1:
                radiation_rate = st.number_input(
                    "Anlık Doz Hızı (µSv/saat)" if TR else "Radiation Rate (µSv/hour)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01
                )

            with col2:
                radiation_dose = st.number_input(
                    "Toplam Radyasyon Dozu (mSv)" if TR else "Total Radiation Dose (mSv)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01
                )

            st.divider()

            st.markdown("### 🏃 Aktivite Durumu" if TR else "### 🏃 Activity Status")

            activity_options = {
                "Uyku": "sleep",
                "Dinlenme": "rest",
                "Egzersiz": "exercise",
                "Hafif Aktivite": "light_activity",
                "Görev Çalışması": "mission_work"
            } if TR else {
                "Sleep": "sleep",
                "Rest": "rest",
                "Exercise": "exercise",
                "Light Activity": "light_activity",
                "Mission Work": "mission_work"
            }

            activity_label = st.selectbox(
                "Ölçüm sırasında astronot ne yapıyordu?"
                if TR else
                "What was the astronaut doing during measurement?",
                list(activity_options.keys())
            )

            activity_state = activity_options[activity_label]

            st.divider()

            st.markdown("### 😴 Uyku Bilgileri" if TR else "### 😴 Sleep Information")

            col1, col2 = st.columns(2)

            with col1:
                sleep_hours = st.number_input(
                    "Son 24 saatte uyku süresi (saat)"
                    if TR else
                    "Sleep duration in the last 24 hours (hours)",
                    min_value=0.0,
                    max_value=24.0,
                    value=8.0,
                    step=0.5
                )

            with col2:
                sleep_quality = st.slider(
                    "Uyku kalitesi (1: Çok kötü - 5: Çok iyi)"
                    if TR else
                    "Sleep quality (1: Very poor - 5: Excellent)",
                    min_value=1,
                    max_value=5,
                    value=3
                )

            st.divider()

            st.markdown("### 💪 Egzersiz Bilgileri" if TR else "### 💪 Exercise Information")

            col1, col2 = st.columns(2)

            with col1:
                exercise_minutes = st.number_input(
                    "Son egzersiz süresi (dakika)"
                    if TR else
                    "Last exercise duration (minutes)",
                    min_value=0,
                    max_value=600,
                    value=0
                )

            with col2:
                intensity_options = {
                    "Yok": "none",
                    "Hafif": "light",
                    "Orta": "moderate",
                    "Yüksek": "high"
                } if TR else {
                    "None": "none",
                    "Light": "light",
                    "Moderate": "moderate",
                    "High": "high"
                }

                intensity_label = st.selectbox(
                    "Egzersiz yoğunluğu" if TR else "Exercise intensity",
                    list(intensity_options.keys())
                )

                exercise_intensity = intensity_options[intensity_label]

            st.divider()

            st.markdown("### 🧠 Genel Durum" if TR else "### 🧠 General Condition")

            col1, col2 = st.columns(2)

            with col1:
                fatigue_level = st.slider(
                    "Yorgunluk seviyesi (1: Yok - 5: Çok yüksek)"
                    if TR else
                    "Fatigue level (1: None - 5: Very high)",
                    min_value=1,
                    max_value=5,
                    value=1
                )

            with col2:
                stress_level = st.slider(
                    "Stres seviyesi (1: Yok - 5: Çok yüksek)"
                    if TR else
                    "Stress level (1: None - 5: Very high)",
                    min_value=1,
                    max_value=5,
                    value=1
                )

            st.divider()

            st.markdown("### 🩺 Belirtiler ve Notlar" if TR else "### 🩺 Symptoms and Notes")

            symptoms = st.text_area(
                "Astronotun hissettiği belirtiler (baş ağrısı, baş dönmesi vb.)"
                if TR else
                "Symptoms experienced (headache, dizziness, etc.)"
            )

            note = st.text_input(T["notes"])

            submitted = st.form_submit_button(
                "💾 Ölçümü Kaydet" if TR else "💾 Save Measurement"
            )

        
            if submitted:
                if not selected_astronaut_id:
                    st.warning("Önce bir astronot ekleyin!")
                else:

                    if not selected_astronaut_id:
                        st.warning(
                            "Lütfen Astronot ID girin!"
                            if TR else
                            "Please enter your Astronaut ID!"
                        )

                    else:
                        measurement = {
                            "heart_rate": hr,
                            "temperature": temp,
                            "oxygen": oxygen,
                            "respiratory_rate": respiratory_rate,
                            "systolic_bp": systolic_bp,
                            "diastolic_bp": diastolic_bp,
                            "radiation_rate": radiation_rate,
                            "radiation_dose": radiation_dose,
                            "activity_state": activity_state,
                            "sleep_hours": sleep_hours,
                            "sleep_quality": sleep_quality,
                            "exercise_minutes": exercise_minutes,
                            "exercise_intensity": exercise_intensity,
                            "fatigue_level": fatigue_level,
                            "stress_level": stress_level,
                            "symptoms": symptoms
                        }

                        add_measurement(
                            heart_rate=hr,
                            temperature=temp,
                            oxygen=oxygen,
                            note=note,
                            activity_state=activity_state,
                            sleep_hours=sleep_hours,
                            sleep_quality=sleep_quality,
                            exercise_minutes=exercise_minutes,
                            exercise_intensity=exercise_intensity,
                            fatigue_level=fatigue_level,
                            stress_level=stress_level,
                            symptoms=symptoms,
                            astronaut_id=selected_astronaut_id,
                            respiratory_rate=respiratory_rate,
                            systolic_bp=systolic_bp,
                            diastolic_bp=diastolic_bp,
                            radiation_rate=radiation_rate,
                            radiation_dose=radiation_dose
                        )

                        result = analyze_measurement(
                            measurement,
                            get_baseline(selected_astronaut_id),
                            lang
                        )

                        st.success(T["saved"])

                        st.subheader(
                            "📋 Ölçüm Özeti" if TR else "📋 Measurement Summary"
                        )

                        st.write(f"**Aktivite:** {activity_label}")
                        st.write(f"**Uyku:** {sleep_hours} saat | Kalite: {sleep_quality}/5")
                        st.write(f"**Egzersiz:** {exercise_minutes} dakika | {intensity_label}")
                        st.write(f"**Yorgunluk:** {fatigue_level}/5 | **Stres:** {stress_level}/5")

                        if symptoms.strip():
                            st.write(f"**Belirtiler:** {symptoms}")

                        st.divider()

                        show_health_result(
                            result,
                            measurement,
                            astronaut_name
                        )


elif page == T["assistant"]:

    st.header("🤖 " + T["assistant"])

    st.caption(
        "AstroGuard AI Assistant"
        if not TR else
        "AstroGuard Yapay Zeka Asistanı"
    )

    # Astronot değiştiğinde aktif sohbeti sıfırla
    if st.session_state.get("chat_astronaut") != selected_astronaut_id:
        st.session_state.chat_astronaut = selected_astronaut_id
        st.session_state.active_conversation = None

    # Astronotun sohbetlerini getir
    conversations = get_chat_conversations(selected_astronaut_id)

    # Aktif sohbet yoksa son sohbeti aç veya yeni sohbet oluştur
    active_id = st.session_state.get("active_conversation")

    conversation_ids = [c["id"] for c in conversations]

    if active_id not in conversation_ids:
        if conversations:
            active_id = conversations[0]["id"]
        else:
            active_id = create_chat_conversation(selected_astronaut_id)

        st.session_state.active_conversation = active_id

    # Sekmeler
    tab_chat, tab_history = st.tabs([
        "💬 Sohbet" if TR else "💬 Chat",
        "🕘 Geçmiş Sohbetler" if TR else "🕘 Chat History"
    ])

    # -------------------------
    # SOHBET SEKME
    # -------------------------
    with tab_chat:

        if st.button(
            "🆕 Yeni Sohbet" if TR else "🆕 New Chat",
            key="new_chat"
        ):
            new_id = create_chat_conversation(selected_astronaut_id)

            st.session_state.active_conversation = new_id
            st.rerun()

        st.divider()

        # Aktif sohbetin mesajlarını getir
        history = get_chat_history(
            astronaut_id=selected_astronaut_id,
            conversation_id=active_id
        )

        # Mesajları göster
        for message in history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Yeni soru alanı
        question = st.chat_input(
            "AstroGuard'a bir soru sor..."
            if TR else
            "Ask AstroGuard a question..."
        )

        if question:

            # AI cevabını oluştur
            response = answer_question(
                question,
                get_measurements(selected_astronaut_id),
                get_baseline(selected_astronaut_id),
                lang,
                history
            )

            # Mesajları aktif sohbete kaydet
            add_chat_message(
                "user",
                question,
                selected_astronaut_id,
                active_id
            )

            add_chat_message(
                "assistant",
                response,
                selected_astronaut_id,
                active_id
            )

            st.rerun()

    # -------------------------
    # GEÇMİŞ SOHBETLER SEKME
    # -------------------------
    with tab_history:

        st.subheader(
            "🕘 Geçmiş Sohbetler"
            if TR else
            "🕘 Previous Conversations"
        )

        conversations = get_chat_conversations(selected_astronaut_id)

        if conversations:

            for conversation in conversations:

                col1, col2 = st.columns([4, 1])

                with col1:

                    if st.button(
                        f"💬 {conversation['title']}  |  {conversation['created_at']}",
                        key=f"conversation_{conversation['id']}",
                        use_container_width=True
                    ):
                        st.session_state.active_conversation = conversation["id"]
                        st.rerun()

                with col2:

                    if st.button(
                        "🗑️",
                        key=f"delete_conversation_{conversation['id']}"
                    ):
                        delete_chat_conversation(
                            conversation["id"],
                            selected_astronaut_id
                        )

                        if st.session_state.active_conversation == conversation["id"]:
                            st.session_state.active_conversation = None

                        st.rerun()

        else:
            st.info(
                "Henüz geçmiş sohbet bulunmuyor."
                if TR else
                "No previous conversations yet."
            )

        

elif page == T["emergency"]:

    st.header("🚨 " + T["emergency"])

    st.warning(
        "Bu rehber genel bilgilendirme amaçlıdır. "
        if TR else
        "This guide is for general educational purposes."
    )

    topics_tr = {
        "Unusual heart rate": "Olağandışı kalp atışı",
        "Low oxygen reading": "Düşük oksijen ölçümü",
        "High temperature": "Yüksek vücut sıcaklığı",
        "Feeling unwell / uncertain": "Kendini kötü hissetme veya emin olamama",
        "Chest pain": "Göğüs ağrısı",
        "Breathing difficulty": "Solunum güçlüğü",
        "Loss of consciousness": "Bilinç kaybı veya bilinç değişikliği",
        "Bleeding / injury": "Kanama veya yaralanma",
        "Radiation exposure": "Radyasyon maruziyeti",
        "Cabin pressure / toxic exposure": "Kabin basıncı veya toksik madde maruziyeti",
        "Psychological distress": "Psikolojik zorlanma"
    }

    st.subheader(
        "Acil Durum Konuları" if TR else "Emergency Topics"
    )

    if TR:
        selected = st.selectbox(
            "İncelemek istediğiniz durumu seçin:",
            list(topics_tr.values())
        )
        topic = {v: k for k, v in topics_tr.items()}[selected]
    else:
        topic = st.selectbox(
            "Select an emergency topic:",
            list(topics_tr.keys())
        )

    st.divider()

    notice = get_emergency_notice(topic, lang)

    st.markdown(notice)



elif page == T["guide"]:

    st.header("📘 " + T["guide"])

    if TR:
        st.info(
            "Bu bölüm genel ölçüm eğitimi sunar. "
            "Herhangi bir astronotun kişisel ölçüm verilerini analiz etmez."
        )
    else:
        st.info(
            "This section provides general measurement education. "
            "It does not analyze any astronaut's personal measurements."
        )

    guides = {
        "Heart Rate": {
            "name": "Kalp Atış Hızı",
            "unit": "BPM — Dakikadaki kalp atışı",
            "meaning": "Kalbin bir dakikada kaç kez attığını ifade eder.",
            "how": "Onaylanmış kalp atış hızı monitörünü veya uygun ölçüm cihazını kullanın. Ölçüm sırasında mümkün olduğunca hareketsiz kalın. Dinlenme ve aktivite durumunu ölçümle birlikte değerlendirin.",
            "avoid": "Hareket, egzersiz sonrası ölçüm, cihazın yanlış takılması ve sinyal kaybı sonuçları etkileyebilir.",
            "source": "NASA-STD-3001 Volume 1 — Crew Health; cihazın üretici kullanım talimatları."
        },

        "Blood Pressure": {
            "name": "Kan Basıncı",
            "unit": "mmHg — Milimetre cıva",
            "meaning": "Sistolik değer kalp kasılırken, diyastolik değer kalp gevşerken arterlerdeki basıncı ifade eder.",
            "how": "Uygun manşon boyutuna sahip doğrulanmış bir cihaz kullanın. Manşonu çıplak üst kola yerleştirin. Sırtınızı destekleyerek oturun, ayaklarınızı yere basın ve kolunuzu kalp hizasında destekleyin. Ölçüm öncesinde en az 5 dakika dinlenin.",
            "avoid": "Konuşmak, hareket etmek, bacakları çaprazlamak, yanlış manşon boyutu ve kolu kalp seviyesinden aşağıda tutmak ölçümü etkileyebilir. Standart ev ölçümünde iki ölçüm arasında yaklaşık 1 dakika beklenebilir.",
            "source": "American Heart Association — Home Blood Pressure Monitoring; CDC — Measuring Your Blood Pressure."
        },

        "Oxygen Saturation": {
            "name": "Oksijen Doygunluğu (SpO₂)",
            "unit": "% — Oksijen doygunluğu",
            "meaning": "Kandaki hemoglobinin oksijen taşıyan kısmının tahmini yüzdesini gösterir.",
            "how": "Parmak tipi oksimetreyi cihaz talimatlarına göre yerleştirin. Elinizi rahat ve sıcak tutun. Hareketsiz kalın ve değer sabitlenene kadar bekleyin.",
            "avoid": "Soğuk el, zayıf dolaşım, hareket, oje, cilt özellikleri ve cihaz kalitesi ölçüm doğruluğunu etkileyebilir. Oksimetre sonucu tek başına sağlık durumunu belirlemez.",
            "source": "FDA — Pulse Oximeters; FDA — Pulse Oximeter Basics."
        },

        "Body Temperature": {
            "name": "Vücut Sıcaklığı",
            "unit": "°C — Santigrat derece",
            "meaning": "Vücudun sıcaklık durumunu gösterir. Sonuç ölçüm bölgesine ve kullanılan yönteme göre değişebilir.",
            "how": "Uygun ve onaylanmış termometre kullanın. Cihazın üretici talimatlarını izleyin. Ölçüm bölgesini ve kullanılan yöntemi kayıt sırasında belirtin.",
            "avoid": "Farklı ölçüm bölgelerinden alınan sonuçları doğrudan karşılaştırmayın. Fiziksel aktivite ve çevresel koşullar ölçümü etkileyebilir.",
            "source": "MedlinePlus — Body Temperature; NASA-STD-3001 Volume 1."
        },

        "Respiratory Rate": {
            "name": "Solunum Sayısı",
            "unit": "Nefes/dakika",
            "meaning": "Bir dakikada gerçekleşen nefes alma ve verme döngülerinin sayısını ifade eder.",
            "how": "Kişi dinlenirken göğüs veya karın hareketlerini gözlemleyin. Bir yükselme ve alçalma bir nefes döngüsü olarak sayılır. Mümkünse tam 60 saniye boyunca sayım yapın.",
            "avoid": "Ölçüm sırasında kişinin konuşması, hareket etmesi veya nefesini bilerek değiştirmesi sonucu etkileyebilir.",
            "source": "MedlinePlus — Vital Signs; NASA-STD-3001 Volume 1."
        },

        "Heart Rate Variability": {
            "name": "Kalp Atım Hızı Değişkenliği (HRV)",
            "unit": "ms — Milisaniye",
            "meaning": "Ardışık kalp atımları arasındaki zaman aralıklarının değişkenliğini ifade eder. Kalp atış hızından farklı bir ölçümdür.",
            "how": "HRV ölçümü yapabilen uygun bir sensör veya ECG tabanlı cihaz kullanın. Karşılaştırma yapılacaksa aynı cihazı ve benzer ölçüm koşullarını kullanın.",
            "avoid": "Farklı cihazların algoritmaları ve ölçüm yöntemleri farklı sonuçlar verebilir. Tek bir HRV değeri tek başına sağlık durumu veya stres düzeyi teşhisi koymaz.",
            "source": "NASA-STD-3001 Volume 1 — Crew Health; cihazın teknik dokümantasyonu."
        },

        "Radiation Dose": {
            "name": "Radyasyon Dozu",
            "unit": "mSv — Milisievert; doz hızı için µSv/h gibi birimler kullanılabilir.",
            "meaning": "Radyasyon dozu, alınan radyasyonun biyolojik etkisini değerlendirmede kullanılan bir büyüklüktür. Toplam birikmiş doz ile anlık doz hızı aynı şey değildir.",
            "how": "Görev için onaylanmış dozimetre ve radyasyon izleme sistemlerini kullanın. Cihazın ölçüm aralığını, zamanını ve doz birimini kayıt altına alın.",
            "avoid": "Doz hızı ile toplam dozu birbirine karıştırmayın. Farklı radyasyon türleri ve ölçüm cihazları farklı değerlendirmeler gerektirebilir.",
            "source": "NASA-STD-3001 Volume 1 — Crew Health; NASA-STD-3001 Volume 2 — Environmental Health."
        },

        "Sleep": {
            "name": "Uyku",
            "unit": "Saat — Uyku süresi",
            "meaning": "Uyku süresi ve uyku düzeni, dinlenme ve görev performansının izlenmesinde kullanılan göstergelerdir.",
            "how": "Uyku başlangıç ve bitiş zamanlarını, toplam uyku süresini ve uyanma dönemlerini düzenli şekilde kaydedin. Kullanılan cihazın ölçüm yöntemini belirtin.",
            "avoid": "Akıllı saatlerin uyku evresi tahminleri doğrudan klinik uyku ölçümüyle aynı değildir.",
            "source": "NASA-STD-3001 Volume 1 — Crew Health; NASA Human Research Program."
        },

        "Fatigue": {
            "name": "Yorgunluk",
            "unit": "Öz değerlendirme ölçeği veya görev için tanımlanmış puanlama sistemi",
            "meaning": "Fiziksel veya zihinsel yorgunluk, dikkat ve görev performansını etkileyebilir.",
            "how": "Görev için belirlenmiş standart yorgunluk değerlendirme formunu kullanın. Değerlendirme zamanını ve kullanılan ölçeği kaydedin.",
            "avoid": "Farklı puanlama ölçeklerini birbirleriyle doğrudan karşılaştırmayın. Öz değerlendirme tek başına tıbbi teşhis değildir.",
            "source": "NASA-STD-3001 Volume 1 — Crew Health; NASA Human Research Program."
        }
    }

    for key, guide in guides.items():

        title = guide["name"] if TR else key

        with st.expander(title):

            if TR:
                st.markdown("**Ne ifade eder?**")
                st.write(guide["meaning"])

                st.markdown("**Ölçüm birimi**")
                st.write(guide["unit"])

                st.markdown("**Nasıl ölçülür?**")
                st.write(guide["how"])

                st.markdown("**Dikkat edilmesi gerekenler**")
                st.write(guide["avoid"])

                st.caption("Kaynak: " + guide["source"])

            else:
                translations = {
                    "meaning": "What does it measure?",
                    "unit": "Measurement unit",
                    "how": "How to measure",
                    "avoid": "Important considerations",
                    "source": "Source"
                }

                st.markdown("**" + translations["meaning"] + "**")
                st.write({
                    "Heart Rate": "The number of heartbeats per minute.",
                    "Blood Pressure": "The pressure in the arteries during and between heartbeats.",
                    "Oxygen Saturation": "The estimated percentage of hemoglobin carrying oxygen.",
                    "Body Temperature": "An indicator of the body's thermal state. Results vary by measurement site and method.",
                    "Respiratory Rate": "The number of breathing cycles per minute.",
                    "Heart Rate Variability": "The variation in time intervals between consecutive heartbeats.",
                    "Radiation Dose": "A measure used to evaluate radiation exposure and its potential biological effects.",
                    "Sleep": "Sleep duration and patterns are indicators used to monitor rest and performance.",
                    "Fatigue": "Physical or mental tiredness that may affect attention and task performance."
                }[key])

                st.markdown("**" + translations["unit"] + "**")
                st.write(guide["unit"])

                st.markdown("**" + translations["how"] + "**")
                st.write({
                    "Heart Rate": "Use an approved heart rate monitor. Remain still when possible and consider whether the measurement is taken at rest or after activity.",
                    "Blood Pressure": "Use a validated device and correctly sized cuff. Sit with your back supported, feet flat and arm supported at heart level. Rest quietly for at least 5 minutes before measuring.",
                    "Oxygen Saturation": "Place the pulse oximeter according to its instructions. Keep your hand warm and still, and wait for the reading to stabilize.",
                    "Body Temperature": "Use an appropriate thermometer and follow its instructions. Record the measurement site and method.",
                    "Respiratory Rate": "Observe chest or abdominal movements while the person is resting. Count one complete breathing cycle for 60 seconds.",
                    "Heart Rate Variability": "Use a suitable sensor or ECG-based device. Use the same device and similar measurement conditions when comparing readings.",
                    "Radiation Dose": "Use mission-approved dosimeters and radiation monitoring systems. Record the time, measurement unit and device.",
                    "Sleep": "Record sleep start and end times, total duration and periods of waking. Identify the device or method used.",
                    "Fatigue": "Use the standardized fatigue assessment form defined for the mission. Record the time and scoring method."
                }[key])

                st.markdown("**" + translations["avoid"] + "**")
                st.write({
                    "Heart Rate": "Movement, recent exercise, incorrect device placement and signal loss may affect readings.",
                    "Blood Pressure": "Talking, movement, crossed legs, incorrect cuff size and unsupported arm position can affect results.",
                    "Oxygen Saturation": "Cold hands, poor circulation, movement, nail polish, skin characteristics and device quality can affect accuracy. Do not rely on the reading alone.",
                    "Body Temperature": "Do not directly compare measurements taken at different body sites or using different methods.",
                    "Respiratory Rate": "Talking, movement or intentionally changing breathing can affect the result.",
                    "Heart Rate Variability": "Different devices and algorithms may produce different results. One HRV value cannot diagnose a health condition.",
                    "Radiation Dose": "Do not confuse dose rate with cumulative dose. Radiation type and device characteristics matter.",
                    "Sleep": "Smartwatch estimates of sleep stages are not equivalent to clinical sleep studies.",
                    "Fatigue": "Different scoring scales should not be directly compared. Self-assessment alone is not a medical diagnosis."
                }[key])

                st.caption("Source: " + guide["source"])

    st.divider()

    if TR:
        st.info(
            "Not: Bu rehber genel eğitim amaçlıdır. "
            "Gerçek uzay görevlerinde ölçümler, görev için onaylanmış "
            "cihazlar ve prosedürler doğrultusunda yapılmalıdır. "
            "Buradaki bilgiler NASA tarafından belirlenmiş klinik alarm eşikleri değildir."
        )
    else:
        st.info(
            "Note: This guide is for general education. "
            "Measurements during actual space missions must follow "
            "mission-approved devices and procedures. "
            "The information here does not represent NASA clinical alert thresholds."
        )

elif page == T["mission_control"]:
    if "delete_success" in st.session_state:
        st.success(st.session_state.pop("delete_success"))
    st.header("🛰️ " + T["mission_control"])

    st.caption(
        "AstroGuard Mission Control Dashboard"
        if not TR else
        "AstroGuard Görev Kontrol Paneli"
    )

    df = get_measurements(selected_astronaut_id)
    baseline = get_baseline(selected_astronaut_id)

    if df.empty:
        st.warning(T["no_data"])

    else:
        latest = df.iloc[-1]

        st.subheader(
            "Astronaut Health Status"
            if not TR else
            "Astronot Sağlık Durumu"
        )

        result = analyze_measurement(
            latest.to_dict(), baseline, lang
        )

        st.divider()
        st.subheader("🚨 " + T["alert"])

        show_health_result(
            result,
            latest.to_dict(),
            astronaut_name
        )

        st.divider()
        st.subheader("📊 " + T["history"])

        st.dataframe(
            df.tail(20),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("📥 Ölçümleri Dışa Aktar")

        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                label="📥 CSV olarak indir",
                data=csv,
                file_name="astroguard_measurements.csv",
                mime="text/csv"
            )
        else:
            st.info("İndirilecek ölçüm bulunamadı.")
        st.divider()

        st.subheader(
            "🗑️ Ölçüm Yönetimi"
            if TR else
            "🗑️ Measurement Management"
        )

        measurement_labels = {
            int(row["id"]): (
                f"ID {int(row['id'])} | {row['measured_at']} | "
                f"HR: {row['heart_rate']} | "
                f"Temp: {row['temperature']} | "
                f"O2: {row['oxygen']}"
            )
            for _, row in df.iterrows()
        }

        selected_ids = st.multiselect(
            "Silmek istediğin ölçümleri seç:"
            if TR else
            "Select measurements to delete:",
            options=list(measurement_labels.keys()),
            format_func=lambda x: measurement_labels[x]
        )

        confirm_delete = st.checkbox(
            "Seçtiğim ölçümleri kalıcı olarak silmeyi onaylıyorum."
            if TR else
            "I confirm that I want to permanently delete the selected measurements."
        )

        if st.button(
            "🗑️ Seçilen Ölçümleri Sil"
            if TR else
            "🗑️ Delete Selected Measurements",
            disabled=not selected_ids or not confirm_delete
        ):

            deleted_count = delete_measurements(selected_ids)

            st.session_state["delete_success"] = (
                f"{deleted_count} ölçüm silindi."
                if TR else
                f"{deleted_count} measurements deleted."
            )

            st.rerun()

        if st.button("🔄 " + ("Verileri Yenile" if TR else "Refresh Data")):
            st.rerun()
