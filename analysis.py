
def analyze_measurement(measurement, baseline, lang="English"):

    tr = lang == "Türkçe"

    if not baseline:
        return {
            "status": "Needs baseline",
            "summary": "Önce Dünya başlangıç verilerini kaydedin." if tr else
                       "Please save an Earth baseline first.",
            "details": "Kişisel referans verisi bulunamadı." if tr else
                       "No personal reference data is available."
        }

    warnings = []
    criticals = []
    observations = []

    def number(data, key):
        value = data.get(key)
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def compare_with_baseline(key, label, unit):
        current = number(measurement, key)
        reference = number(baseline, key)

        if current is None:
            return

        if reference is None:
            observations.append(
                f"{label}: {current:g} {unit}. " +
                ("Başlangıç karşılaştırması yapılamıyor."
                 if tr else "No baseline comparison is available.")
            )
            return

        difference = current - reference

        observations.append(
            f"{label}: {current:g} {unit} | " +
            (
                f"Başlangıç değerine göre {difference:+g} {unit}."
                if tr else
                f"{difference:+g} {unit} compared with baseline."
            )
        )

    # =================================
    # 1. TEMEL ÖLÇÜMLER
    # =================================

    hr = number(measurement, "heart_rate")
    temp = number(measurement, "temperature")
    oxygen = number(measurement, "oxygen")

    if (
        hr is None or hr <= 0
        or temp is None or temp <= 0
        or oxygen is None or not 0 < oxygen <= 100
    ):
        return {
            "status": "Review",
            "summary": "Temel ölçümler eksik veya geçersiz. Verileri kontrol edin."
            if tr else
            "Required measurements are missing or invalid. Check the data.",
            "details": "Heart rate, temperature ve oxygen değerleri kontrol edilmeli."
            if tr else
            "Heart rate, temperature and oxygen values need to be checked."
        }

    # =================================
    # 2. KİŞİSEL BAŞLANGIÇ KARŞILAŞTIRMASI
    # =================================

    compare_with_baseline("heart_rate", "Heart rate", "bpm")
    compare_with_baseline("temperature", "Body temperature", "°C")
    compare_with_baseline("oxygen", "Oxygen saturation", "%")

    # =================================
    # 3. SOLUNUM VE TANSİYON
    # =================================

    respiratory_rate = number(measurement, "respiratory_rate")
    systolic_bp = number(measurement, "systolic_bp")
    diastolic_bp = number(measurement, "diastolic_bp")

    if respiratory_rate is not None and respiratory_rate > 0:
        compare_with_baseline(
            "respiratory_rate", "Respiratory rate", "breaths/min"
        )
    else:
        observations.append(
            "Solunum hızı ölçümü kaydedilmemiş."
            if tr else "Respiratory rate was not recorded."
        )

    if systolic_bp is not None and systolic_bp > 0:
        compare_with_baseline("systolic_bp", "Systolic blood pressure", "mmHg")

    if diastolic_bp is not None and diastolic_bp > 0:
        compare_with_baseline("diastolic_bp", "Diastolic blood pressure", "mmHg")

    # =================================
    # 4. AKTİVİTE BAĞLAMI
    # =================================

    activity = measurement.get("activity_state", "rest")

    activity_names = {
        "rest": ("Dinlenme", "Rest"),
        "sleep": ("Uyku", "Sleep"),
        "exercise": ("Egzersiz", "Exercise"),
        "light_activity": ("Hafif aktivite", "Light activity"),
        "mission_work": ("Görev çalışması", "Mission work")
    }

    if activity in activity_names:
        observations.append(
            "Aktivite durumu: " +
            activity_names[activity][0 if tr else 1]
        )

    if activity == "exercise":
        observations.append(
            "Egzersiz sırasında alınan ölçümlerde aktivite yoğunluğu dikkate alınmalıdır."
            if tr else
            "Activity intensity should be considered when interpreting exercise measurements."
        )

    # =================================
    # 5. RADYASYON TAKİBİ
    # =================================

    radiation_rate = number(measurement, "radiation_rate")
    radiation_dose = number(measurement, "radiation_dose")

    if radiation_rate is not None and radiation_rate >= 0:

        compare_with_baseline(
            "radiation_rate", "Radiation dose rate", "µSv/hour"
        )

        observations.append(
            "Radyasyon doz hızı ALARA ilkesi doğrultusunda izlenmelidir."
            if tr else
            "Radiation dose rate should be monitored according to the ALARA principle."
        )

    if radiation_dose is not None and radiation_dose >= 0:

        observations.append(
            f"Görev boyunca biriken radyasyon dozu: {radiation_dose:g} mSv."
            if tr else
            f"Cumulative mission radiation dose: {radiation_dose:g} mSv."
        )

    # NASA'nın 600 mSv sınırı kariyer toplam dozuna aittir.
    # Bu alan mevcut projede yoksa görev dozuyla karşılaştırma yapılmaz.

    career_dose = number(measurement, "career_radiation_dose")

    if career_dose is not None and career_dose >= 0:

        observations.append(
            f"Kariyer boyunca biriken etkin radyasyon dozu: {career_dose:g} mSv."
            if tr else
            f"Cumulative career effective radiation dose: {career_dose:g} mSv."
        )

        if career_dose >= 600:
            criticals.append(
                "NASA-STD-3001 kariyer radyasyon doz sınırı (600 mSv) karşılanmıyor."
                if tr else
                "NASA-STD-3001 career radiation dose limit (600 mSv) has been reached or exceeded."
            )

    else:
        observations.append(
            "Kariyer toplam dozu verisi bulunmadığından NASA'nın 600 mSv sınırı değerlendirilemedi."
            if tr else
            "NASA's 600 mSv career limit cannot be evaluated because career dose data is unavailable."
        )

    # =================================
    # 6. UYKU VE DAVRANIŞSAL SAĞLIK
    # =================================

    sleep_hours = number(measurement, "sleep_hours")
    sleep_quality = number(measurement, "sleep_quality")
    fatigue = number(measurement, "fatigue_level")
    stress = number(measurement, "stress_level")

    if sleep_hours is not None:
        observations.append(
            f"Son 24 saatte uyku süresi: {sleep_hours:g} saat."
            if tr else
            f"Sleep duration in the last 24 hours: {sleep_hours:g} hours."
        )

    if sleep_quality is not None:
        observations.append(
            f"Uyku kalitesi bildirimi: {sleep_quality:g}/5."
            if tr else
            f"Reported sleep quality: {sleep_quality:g}/5."
        )

    if fatigue is not None:
        observations.append(
            f"Yorgunluk seviyesi bildirimi: {fatigue:g}/5."
            if tr else
            f"Reported fatigue level: {fatigue:g}/5."
        )

    if stress is not None:
        observations.append(
            f"Stres seviyesi bildirimi: {stress:g}/5."
            if tr else
            f"Reported stress level: {stress:g}/5."
        )

    # NASA Standard Measures uyku, aktivite ve davranışsal
    # sağlık verilerinin izlenmesini destekler.
    # Bu alanlarda NASA tarafından belirlenmemiş alarm eşikleri kullanılmaz.

    # =================================
    # 7. EGZERSİZ
    # =================================

    exercise_minutes = number(measurement, "exercise_minutes")
    exercise_intensity = measurement.get("exercise_intensity", "none")

    if exercise_minutes is not None:
        observations.append(
            f"Egzersiz süresi: {exercise_minutes:g} dakika."
            if tr else
            f"Exercise duration: {exercise_minutes:g} minutes."
        )

    if exercise_intensity != "none":
        observations.append(
            f"Egzersiz yoğunluğu: {exercise_intensity}."
            if tr else
            f"Exercise intensity: {exercise_intensity}."
        )

    # =================================
    # 8. BELİRTİLER
    # =================================

    symptoms = measurement.get("symptoms", "")

    if symptoms and str(symptoms).strip():
        warnings.append(
            "Astronot ek belirtiler bildirdi: " + str(symptoms)
            if tr else
            "Astronaut reported additional symptoms: " + str(symptoms)
        )

    # =================================
    # 9. SONUÇ
    # =================================

    if criticals:
        return {
            "status": "Critical",
            "summary": "Kritik radyasyon sınırı tespit edildi. Ölçümü doğrulayın ve görev sağlık protokolünü uygulayarak sağlık ekibine bildirin."
            if tr else
            "A critical radiation limit has been reached. Verify the data and notify the medical team according to mission health protocols.",
            "details": "\n".join(criticals + warnings + observations)
        }

    if warnings:
        return {
            "status": "Warning",
            "summary": "Astronot tarafından belirtiler bildirildi. Sağlık ekibinin değerlendirmesi önerilir."
            if tr else
            "Symptoms have been reported. Medical team evaluation is recommended.",
            "details": "\n".join(warnings + observations)
        }

    return {
        "status": "Normal",
        "summary": "Ölçümler kaydedildi. Kişisel başlangıç değerleri ve görev boyunca değişimler izlenmeye devam ediyor."
        if tr else
        "Measurements recorded. Personal baseline values and changes throughout the mission continue to be monitored.",
        "details": "\n".join(observations) if observations else (
            "İzlemeye devam edin." if tr else "Continue monitoring."
        )
    }
