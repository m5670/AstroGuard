# ============================================================
# AI USAGE AND DEVELOPMENT DISCLOSURE
# ============================================================
# ChatGPT (OpenAI) was used as a development support tool
# during the development of this analysis module.
#
# AI assistance included code explanations, debugging support,
# and implementation guidance.
#
# IMPORTANT:
# This module uses predefined, rule-based evaluation logic.
# NEWS2 scoring and the configured NASA-related reference
# criteria are evaluated through programmed conditions.
# Generative AI is NOT used to calculate the scores or
# independently determine the health status in this module.
#
# The developer reviewed and integrated the implementation.
# ============================================================
def analyze_measurement(measurement, baseline, lang="English"):

    tr = lang == "Türkçe"
    baseline = baseline or {}

    warnings = []
    criticals = []
    observations = []
    news_score = 0

    def msg(tr_text, en_text):
        return tr_text if tr else en_text

    def number(data, key):
        value = data.get(key)
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def add_news(name, value, score):
        nonlocal news_score
        news_score += score
        observations.append(
            f"{name}: {value} | NEWS2 score: {score}"
        )

    # =================================
    # 1. BASIC MEASUREMENTS
    # =================================

    hr = number(measurement, "heart_rate")
    temp = number(measurement, "temperature")
    oxygen = number(measurement, "oxygen")
    respiratory = number(measurement, "respiratory_rate")

    systolic = number(measurement, "systolic_bp")
    diastolic = number(measurement, "diastolic_bp")

    activity = measurement.get("activity_state", "rest")
    hr_duration = number(
        measurement, "heart_rate_duration_minutes"
    )

    if hr is None or temp is None or oxygen is None:
        return {
            "status": "Review",
            "summary": msg(
                "Temel ölçümler eksik.",
                "Required measurements are missing."
            ),
            "details": msg(
                "Nabız, sıcaklık ve oksijen değerlerini kontrol edin.",
                "Check heart rate, temperature and oxygen values."
            )
        }

    if hr <= 0 or temp <= 0 or not 0 < oxygen <= 100:
        return {
            "status": "Review",
            "summary": msg(
                "Geçersiz ölçüm değeri.",
                "Invalid measurement value."
            ),
            "details": msg(
                "Ölçüm değerlerini kontrol edin.",
                "Check measurement values."
            )
        }

    # =================================
    # 2. HEART RATE - NEWS2
    # =================================

    if hr <= 40:
        score = 3
    elif hr <= 50:
        score = 1
    elif hr <= 90:
        score = 0
    elif hr <= 110:
        score = 1
    elif hr <= 130:
        score = 2
    else:
        score = 3

    add_news("Heart rate", f"{hr:g} bpm", score)

    if score == 3:
        warnings.append(
            msg(
                f"ACİL UYARI: Nabız {hr:g} bpm. NEWS2 tek parametre için 3 puanlık eşik.",
                f"URGENT ALERT: Heart rate {hr:g} bpm. NEWS2 single-parameter score of 3."
            )
        )

    # NASA astronaut medical evaluation criteria

    if hr < 30 and activity != "sleep":
        warnings.append(
            msg(
                "NASA kriteri: Uyku dışında 30 bpm altı nabız.",
                "NASA criterion: Heart rate below 30 bpm outside sleep."
            )
        )

    if activity == "rest" and hr > 130:
        if hr_duration is not None and hr_duration >= 60:
            warnings.append(
                msg(
                    "NASA kriteri: Dinlenmede 130 bpm üzeri nabız en az 1 saat sürdü.",
                    "NASA criterion: Resting heart rate above 130 bpm sustained for at least one hour."
                )
            )
        else:
            warnings.append(
                msg(
                    "Dinlenmede 130 bpm üzeri nabız. Süreyi doğrulayın.",
                    "Resting heart rate above 130 bpm. Verify duration."
                )
            )

    # =================================
    # 3. OXYGEN - NEWS2 SCALE 1
    # =================================

    if oxygen <= 91:
        score = 3
    elif oxygen <= 93:
        score = 2
    elif oxygen <= 95:
        score = 1
    else:
        score = 0

    add_news("Oxygen saturation", f"{oxygen:g}%", score)

    if score == 3:
        warnings.append(
            msg(
                f"ACİL UYARI: Oksijen doygunluğu %{oxygen:g}.",
                f"URGENT ALERT: Oxygen saturation is {oxygen:g}%."
            )
        )

    # =================================
    # 4. TEMPERATURE - NEWS2
    # =================================

    if temp <= 35:
        score = 3
    elif temp <= 36:
        score = 1
    elif temp <= 38:
        score = 0
    elif temp <= 39:
        score = 1
    else:
        score = 2

    add_news("Temperature", f"{temp:g} °C", score)

    if score >= 2:
        warnings.append(
            msg(
                f"Sıcaklık uyarısı: {temp:g} °C.",
                f"Temperature alert: {temp:g} °C."
            )
        )

    # =================================
    # 5. RESPIRATORY RATE - NEWS2
    # =================================

    if respiratory is not None:

        if respiratory <= 8 or respiratory >= 25:
            score = 3
        elif respiratory <= 11:
            score = 1
        elif respiratory <= 20:
            score = 0
        else:
            score = 2

        add_news(
            "Respiratory rate",
            f"{respiratory:g}/min",
            score
        )

        if score == 3:
            warnings.append(
                msg(
                    f"ACİL UYARI: Solunum hızı {respiratory:g}/dk.",
                    f"URGENT ALERT: Respiratory rate {respiratory:g}/min."
                )
            )

    # =================================
    # 6. BLOOD PRESSURE - NEWS2
    # =================================

    if systolic is not None:

        if systolic <= 90 or systolic >= 220:
            score = 3
        elif systolic <= 100:
            score = 2
        elif systolic <= 110:
            score = 1
        else:
            score = 0

        add_news(
            "Systolic blood pressure",
            f"{systolic:g} mmHg",
            score
        )

        if score == 3:
            warnings.append(
                msg(
                    f"ACİL UYARI: Sistolik tansiyon {systolic:g} mmHg.",
                    f"URGENT ALERT: Systolic blood pressure {systolic:g} mmHg."
                )
            )

    # NASA hypertension evaluation criterion

    if systolic is not None and diastolic is not None:

        if systolic >= 140 or diastolic >= 90:
            warnings.append(
                msg(
                    "NASA değerlendirme kriteri: Tansiyon 140/90 mmHg veya üzerinde. Ölçümü tekrarlayın.",
                    "NASA evaluation criterion: Blood pressure at or above 140/90 mmHg. Repeat measurement."
                )
            )

    # =================================
    # 7. NEWS2 TOTAL
    # =================================

    observations.append(
        f"NEWS2 total score: {news_score}"
    )

    if news_score >= 7:
        criticals.append(
            msg(
                f"NEWS2 YÜKSEK RİSK: Toplam puan {news_score}.",
                f"NEWS2 HIGH RISK: Total score {news_score}."
            )
        )

    elif news_score >= 5:
        warnings.append(
            msg(
                f"NEWS2 ORTA RİSK: Toplam puan {news_score}.",
                f"NEWS2 MEDIUM RISK: Total score {news_score}."
            )
        )

    # =================================
    # 8. RADIATION - NASA
    # =================================

    radiation_rate = number(measurement, "radiation_rate")
    mission_dose = number(measurement, "radiation_dose")
    career_dose = number(measurement, "career_radiation_dose")
    spe_dose = number(measurement, "spe_dose")
    nuclear_dose = number(measurement, "nuclear_radiation_dose")
    mission_days = number(measurement, "mission_duration_days")

    if radiation_rate is not None:
        observations.append(
            f"Radiation rate: {radiation_rate:g} µSv/hour"
        )

        if radiation_rate < 0:
            warnings.append(
                msg("Geçersiz radyasyon değeri.", "Invalid radiation value.")
            )

    if mission_dose is not None:
        observations.append(
            f"Mission radiation dose: {mission_dose:g} mSv"
        )

    if career_dose is not None:

        observations.append(
            f"Career radiation dose: {career_dose:g} mSv"
        )

        if career_dose >= 600:
            criticals.append(
                msg(
                    "NASA kariyer toplam etkin doz sınırı 600 mSv'ye ulaşıldı veya aşıldı.",
                    "NASA career cumulative effective dose limit of 600 mSv reached or exceeded."
                )
            )

    if spe_dose is not None:

        observations.append(
            f"SPE dose: {spe_dose:g} mSv"
        )

        if spe_dose >= 250:
            criticals.append(
                msg(
                    "NASA güneş parçacık olayı tasarım referans dozu 250 mSv'ye ulaşıldı veya aşıldı.",
                    "NASA solar particle event design reference dose of 250 mSv reached or exceeded."
                )
            )

    if nuclear_dose is not None and mission_days is not None:

        if mission_days > 0:

            limit = 20 * mission_days / 365.25

            observations.append(
                f"Nuclear technology dose: {nuclear_dose:g} mSv / limit: {limit:.3f} mSv"
            )

            if nuclear_dose >= limit:
                criticals.append(
                    msg(
                        "NASA nükleer teknoloji radyasyon sınırı karşılandı veya aşıldı.",
                        "NASA nuclear technology radiation limit reached or exceeded."
                    )
                )

    observations.append(
        msg(
            "NASA ALARA ilkesi: Radyasyon maruziyeti mümkün olan en düşük seviyede tutulmalıdır.",
            "NASA ALARA principle: Radiation exposure should be kept as low as reasonably achievable."
        )
    )

    # =================================
    # 9. BASELINE COMPARISON
    # =================================

    fields = {
        "heart_rate": ("Nabız", "Heart rate", "bpm"),
        "temperature": ("Sıcaklık", "Temperature", "°C"),
        "oxygen": ("Oksijen", "Oxygen", "%"),
        "respiratory_rate": ("Solunum", "Respiratory rate", "/min"),
        "systolic_bp": ("Sistolik tansiyon", "Systolic BP", "mmHg"),
        "diastolic_bp": ("Diyastolik tansiyon", "Diastolic BP", "mmHg")
    }

    for key, names in fields.items():

        current = number(measurement, key)
        reference = number(baseline, key)

        if current is not None and reference is not None:

            tr_name, en_name, unit = names

            observations.append(
                f"{tr_name if tr else en_name}: "
                f"{current - reference:+g} {unit} vs baseline"
            )

    # =================================
    # 10. SLEEP, FATIGUE, STRESS
    # =================================

    for key, label in [
        ("sleep_hours", "Sleep hours"),
        ("sleep_quality", "Sleep quality"),
        ("fatigue_level", "Fatigue"),
        ("stress_level", "Stress")
    ]:

        value = number(measurement, key)

        if value is not None:
            observations.append(f"{label}: {value:g}")

    # =================================
    # 11. EXERCISE AND SYMPTOMS
    # =================================

    exercise = number(measurement, "exercise_minutes")
    symptoms = measurement.get("symptoms", "")

    if exercise is not None:
        observations.append(
            f"Exercise: {exercise:g} minutes"
        )

    if symptoms and str(symptoms).strip():
        warnings.append(
            msg(
                "Astronot ek belirtiler bildirdi: ",
                "Astronaut reported additional symptoms: "
            ) + str(symptoms)
        )

    # =================================
    # RECOMMENDED ACTIONS
    # =================================

    actions = []

    def add_action(tr_text, en_text):
        actions.append(msg(tr_text, en_text))

    # HEART RATE
    if hr > 130:
        add_action(
            "Fiziksel aktiviteyi durdurun ve güvenli bir pozisyonda dinlenin. "
            "Sensör bağlantısını kontrol ederek nabzı tekrar ölçün. "
            "Değer yüksek kalıyorsa görev kontrol merkezine derhal bildirin.",
            "Stop physical activity and rest in a safe position. "
            "Check the sensor connection and repeat the measurement. "
            "If the value remains high, notify Mission Control immediately."
        )

    elif hr < 30 and activity != "sleep":
        add_action(
            "Ölçümü ve sensör bağlantısını kontrol edin. "
            "Nabız düşüklüğü devam ediyorsa görev kontrol merkezine derhal bildirin.",
            "Check the measurement and sensor connection. "
            "If the low heart rate persists, notify Mission Control immediately."
        )

    elif hr <= 40:
        add_action(
            "Dinlenin, ölçümü tekrar edin ve sonucu sağlık ekibine bildirin.",
            "Rest, repeat the measurement, and report the result to the medical team."
        )

    # OXYGEN
    if oxygen <= 91:
        add_action(
            "Sensörün doğru takıldığını kontrol edin. Oksijen değeri düşük kalıyorsa "
            "görev kontrol merkezine derhal bildirin.",
            "Check that the sensor is correctly positioned. If oxygen saturation "
            "remains low, notify Mission Control immediately."
        )

    elif oxygen <= 95:
        add_action(
            "Oksijen ölçümünü tekrar edin ve değişimi takip edin. "
            "Düşüş devam ederse sağlık ekibine bildirin.",
            "Repeat the oxygen measurement and monitor the trend. "
            "Notify the medical team if the decrease persists."
        )

    # TEMPERATURE
    if temp <= 35:
        add_action(
            "Sıcaklık ölçümünü doğrulayın. Uygun termal koşulları sağlayın "
            "ve sağlık ekibine derhal bildirin.",
            "Verify the temperature reading. Maintain appropriate thermal conditions "
            "and notify the medical team immediately."
        )

    elif temp > 39:
        add_action(
            "Sıcaklığı tekrar ölçün, fiziksel aktiviteyi durdurun "
            "ve sağlık ekibine bildirin.",
            "Repeat the temperature measurement, stop physical activity, "
            "and notify the medical team."
        )

    elif temp > 38:
        add_action(
            "Sıcaklığı tekrar ölçün ve belirtileri takip edin. "
            "Yüksek değer devam ederse sağlık ekibine bildirin.",
            "Repeat the temperature measurement and monitor symptoms. "
            "Notify the medical team if the elevated reading persists."
        )

    # RESPIRATORY RATE
    if respiratory is not None and (respiratory <= 8 or respiratory >= 25):
        add_action(
            "Solunum hızını tekrar kontrol edin. Değer anormalse "
            "görev kontrol merkezine derhal bildirin.",
            "Recheck the respiratory rate. If it remains abnormal, "
            "notify Mission Control immediately."
        )

    # BLOOD PRESSURE
    if systolic is not None and (systolic <= 90 or systolic >= 220):
        add_action(
            "Tansiyonu tekrar ölçün ve ölçüm pozisyonunu kontrol edin. "
            "Anormal değer devam ederse sağlık ekibine derhal bildirin.",
            "Repeat the blood pressure measurement and check the measurement position. "
            "If the abnormal value persists, notify the medical team immediately."
        )

    elif (
        systolic is not None and diastolic is not None
        and (systolic >= 140 or diastolic >= 90)
    ):
        add_action(
            "Uygun dinlenme sonrasında tansiyonu tekrar ölçün "
            "ve sonucu sağlık ekibine bildirin.",
            "Repeat the blood pressure measurement after appropriate rest "
            "and report the result to the medical team."
        )

    # NEWS2 RISK
    if news_score >= 7:
        add_action(
            "NEWS2 yüksek risk seviyesinde. Derhal acil tıbbi değerlendirme "
            "isteyin ve görev kontrol merkezinin talimatlarını uygulayın.",
            "NEWS2 indicates high risk. Request immediate urgent medical assessment "
            "and follow Mission Control instructions."
        )

    elif news_score >= 5:
        add_action(
            "NEWS2 orta risk seviyesinde. Sağlık ekibinden acil değerlendirme isteyin.",
            "NEWS2 indicates medium risk. Request urgent assessment from the medical team."
        )

    # SYMPTOMS
    if symptoms and str(symptoms).strip():
        add_action(
            "Bildirilen belirtileri kaydedin ve sağlık ekibine iletin. "
            "Belirtiler şiddetliyse derhal yardım isteyin.",
            "Record the reported symptoms and communicate them to the medical team. "
            "Seek immediate assistance if symptoms are severe."
        )

    if not actions and warnings:
        add_action(
            "Ölçümleri tekrar kontrol edin ve uyarıları sağlık ekibine bildirin.",
            "Recheck the measurements and report the alerts to the medical team."
        )

    # =================================
    # 12. FINAL RESULT
    # =================================

    details_text = "\n".join(
        criticals + warnings + observations
    )

    if actions:
        details_text += "\n\n" + msg(
            "📋 ÖNERİLEN EYLEMLER:\n",
            "📋 RECOMMENDED ACTIONS:\n"
        )

        details_text += "\n".join(
            f"{i + 1}. {action}"
            for i, action in enumerate(actions)
        )

    if criticals:
        return {
            "status": "Critical",
            "summary": msg(
                "KRİTİK UYARI: Yüksek riskli değerlendirme sonucu tespit edildi. Sağlık ekibine bildirin.",
                "CRITICAL ALERT: A high-risk evaluation result was detected. Notify the medical team."
            ),
            "details": details_text
        }

    if warnings:
        return {
            "status": "Warning",
            "summary": msg(
                "UYARI: Bir veya daha fazla değerlendirme eşiği aşıldı. Ölçümleri doğrulayın ve sağlık ekibine bildirin.",
                "WARNING: One or more evaluation thresholds were reached. Verify measurements and notify the medical team."
            ),
            "details": details_text
        }

    return {
        "status": "Normal",
        "summary": msg(
            "Mevcut değerlendirme eşiklerine göre uyarı tespit edilmedi. İzlemeye devam edin.",
            "No alert was detected by the available evaluation thresholds. Continue monitoring."
        ),
        "details": details_text
    }
