
def analyze_measurement(measurement, baseline, lang="English"):

    tr = lang == "Türkçe"

    if not baseline:
        return {
            "status": "Needs baseline",
            "summary": "Önce Dünya başlangıç verilerini kaydedin." if tr else "Please save an Earth baseline first.",
            "details": "Kişisel referans verisi bulunamadı." if tr else "No personal reference data is available."
        }

    warnings = []
    criticals = []
    observations = []

    # Temel sağlık değerleri
    hr = measurement["heart_rate"]
    temp = measurement["temperature"]
    oxygen = measurement["oxygen"]

    # Yeni sağlık değerleri
    respiratory_rate = measurement.get("respiratory_rate", 0)
    systolic_bp = measurement.get("systolic_bp", 0)
    diastolic_bp = measurement.get("diastolic_bp", 0)

    # Radyasyon değerleri
    radiation_rate = measurement.get("radiation_rate", 0)
    radiation_dose = measurement.get("radiation_dose", 0)

    activity = measurement.get("activity_state", "rest")
    sleep_hours = measurement.get("sleep_hours", 0)
    sleep_quality = measurement.get("sleep_quality", 3)
    exercise_minutes = measurement.get("exercise_minutes", 0)
    exercise_intensity = measurement.get("exercise_intensity", "none")
    fatigue = measurement.get("fatigue_level", 1)
    stress = measurement.get("stress_level", 1)
    symptoms = measurement.get("symptoms", "")

    # Kişisel başlangıç değerlerinden farklar
    differences = {
        "heart_rate": abs(hr - baseline["heart_rate"]),
        "temperature": abs(temp - baseline["temperature"]),
        "oxygen": abs(oxygen - baseline["oxygen"])
    }

    # =================================
    # 1. VERİ GEÇERLİLİĞİ
    # =================================

    if (
        hr <= 0
        or temp <= 0
        or oxygen <= 0
        or respiratory_rate <= 0
        or systolic_bp <= 0
        or diastolic_bp <= 0
        or radiation_rate < 0
        or radiation_dose < 0
    ):
        return {
            "status": "Review",
            "summary": "Geçersiz veya eksik ölçüm verisi. Ölçümü kontrol edin."
            if tr else
            "Invalid or incomplete measurement. Check the readings.",
            "details": "Bir veya daha fazla ölçüm geçersiz."
            if tr else
            "One or more measurements are invalid."
        }

    # =================================
    # 2. AKTİVİTE BAĞLAMI
    # =================================

    if activity == "exercise":
        observations.append(
            "Ölçüm egzersiz sırasında alınmıştır."
            if tr else
            "Measurement was taken during exercise."
        )

        if hr > 120:
            observations.append(
                "Egzersiz sırasında yüksek nabız kaydedildi; aktivite yoğunluğu ve toparlanma süresi dikkate alınmalıdır."
                if tr else
                "Elevated heart rate recorded during exercise; activity intensity and recovery time should be considered."
            )

    elif activity == "sleep":
        observations.append(
            "Ölçüm uyku sırasında alınmıştır."
            if tr else
            "Measurement was taken during sleep."
        )

    elif activity == "rest":
        observations.append(
            "Ölçüm dinlenme sırasında alınmıştır."
            if tr else
            "Measurement was taken during rest."
        )

    elif activity == "light_activity":
        observations.append(
            "Ölçüm hafif aktivite sırasında alınmıştır."
            if tr else
            "Measurement was taken during light activity."
        )

    elif activity == "mission_work":
        observations.append(
            "Ölçüm görev çalışması sırasında alınmıştır."
            if tr else
            "Measurement was taken during mission work."
        )

    # =================================
    # 3. HEART RATE
    # =================================

    # Bunlar prototip eşikleridir.
    if hr < 30 or hr > 180:
        criticals.append(
            "Kalp atış hızı kritik prototip sınırının dışında."
            if tr else
            "Heart rate is outside the critical prototype threshold."
        )

    elif hr < 40 or hr > 120:
        warnings.append(
            "Kalp atış hızı prototip referans aralığının dışında."
            if tr else
            "Heart rate is outside the prototype reference range."
        )

    # Egzersiz sırasında kişisel farkı tek başına alarm yapma.
    if activity != "exercise":

        if differences["heart_rate"] > 40:
            criticals.append(
                "Kalp atış hızında çok büyük kişisel değişim."
                if tr else
                "Very large personal heart rate deviation."
            )

        elif differences["heart_rate"] > 20:
            warnings.append(
                "Kalp atış hızı başlangıçtan belirgin farklı."
                if tr else
                "Heart rate differs significantly from baseline."
            )

    # =================================
    # 4. BODY TEMPERATURE
    # =================================

    if temp < 35 or temp > 39:
        criticals.append(
            "Vücut sıcaklığı kritik prototip sınırının dışında."
            if tr else
            "Body temperature is outside the critical prototype threshold."
        )

    elif temp < 36 or temp > 38:
        warnings.append(
            "Vücut sıcaklığı prototip referans aralığının dışında."
            if tr else
            "Body temperature is outside the prototype reference range."
        )

    if differences["temperature"] > 2:
        criticals.append(
            "Vücut sıcaklığında çok büyük kişisel değişim."
            if tr else
            "Very large personal temperature deviation."
        )

    elif differences["temperature"] > 1:
        warnings.append(
            "Vücut sıcaklığı başlangıçtan belirgin farklı."
            if tr else
            "Temperature differs significantly from baseline."
        )

    # =================================
    # 5. OXYGEN SATURATION
    # =================================

    if oxygen < 90:
        criticals.append(
            "Oksijen doygunluğu kritik derecede düşük."
            if tr else
            "Oxygen saturation is critically low."
        )

    elif oxygen < 95:
        warnings.append(
            "Oksijen doygunluğu düşük."
            if tr else
            "Oxygen saturation is low."
        )

    if differences["oxygen"] > 6:
        criticals.append(
            "Oksijen doygunluğunda çok büyük kişisel değişim."
            if tr else
            "Very large personal oxygen saturation deviation."
        )

    elif differences["oxygen"] > 3:
        warnings.append(
            "Oksijen doygunluğu başlangıçtan belirgin farklı."
            if tr else
            "Oxygen saturation differs significantly from baseline."
        )

    # =================================
    # 6. SLEEP ANALYSIS
    # =================================

    if sleep_hours < 6:
        warnings.append(
            "Son 24 saatte uyku süresi düşük."
            if tr else
            "Sleep duration in the last 24 hours is low."
        )

    if sleep_quality <= 2:
        warnings.append(
            "Uyku kalitesi düşük olarak bildirildi."
            if tr else
            "Low sleep quality was reported."
        )

    # =================================
    # 7. FATIGUE AND STRESS
    # =================================

    if fatigue >= 4:
        warnings.append(
            "Yüksek yorgunluk seviyesi bildirildi."
            if tr else
            "High fatigue level was reported."
        )

    if stress >= 4:
        warnings.append(
            "Yüksek stres seviyesi bildirildi."
            if tr else
            "High stress level was reported."
        )

    # =================================
    # 8. EXERCISE ANALYSIS
    # =================================

    if exercise_minutes > 0:

        observations.append(
            f"Son egzersiz süresi: {exercise_minutes} dakika."
            if tr else
            f"Last exercise duration: {exercise_minutes} minutes."
        )

        if exercise_intensity == "high":
            observations.append(
                "Yüksek yoğunluklu egzersiz bildirildi."
                if tr else
                "High-intensity exercise was reported."
            )

    # =================================
    # 9. SYMPTOMS
    # =================================

    if symptoms.strip():

        warnings.append(
            "Astronot ek belirtiler bildirdi: " + symptoms
            if tr else
            "Astronaut reported additional symptoms: " + symptoms
        )

    # =================================
    # 10. FINAL STATUS
    # =================================

    if criticals:

        return {
            "status": "Critical",
            "summary": "Kritik sapma tespit edildi! Ölçümü doğrulayın ve görev sağlık protokolünü uygulayarak sağlık ekibine bildirin."
            if tr else
            "Critical deviation detected! Verify the reading, follow mission health protocols and notify the medical team.",

            "details": "\n".join(criticals + warnings + observations)
        }

    if warnings:

        return {
            "status": "Warning",
            "summary": "Olağandışı değişimler tespit edildi. Aktivite ve diğer koşulları dikkate alarak ölçümleri takip edin."
            if tr else
            "Unusual changes detected. Monitor readings while considering activity and other conditions.",

            "details": "\n".join(warnings + observations)
        }

    return {
        "status": "Normal",
        "summary": "Belirgin sağlık verisi sapması tespit edilmedi."
        if tr else
        "No significant health data deviation detected.",

        "details": "\n".join(observations) if observations else (
            "İzlemeye devam edin." if tr else "Continue monitoring."
        )
    }
