
def analyze_measurement(measurement, baseline, lang="English"):

    tr = lang == "Türkçe"

    if baseline is None:
        baseline = {}

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

    def msg(tr_text, en_text):
        return tr_text if tr else en_text

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
            "summary": msg(
                "Temel ölçümler eksik veya geçersiz.",
                "Required measurements are missing or invalid."
            ),
            "details": msg(
                "Nabız, sıcaklık ve oksijen değerlerini kontrol edin.",
                "Check heart rate, temperature and oxygen readings."
            )
        }

    activity = measurement.get("activity_state", "rest")

    # =================================
    # 2. NASA KARDİYOVASKÜLER DEĞERLENDİRME
    # =================================

    # NASA OCHMO-STD-100.1A:
    # HR <30 bpm, uyku sırasında değilse tıbbi değerlendirme kriteridir.

    if hr < 30 and activity != "sleep":
        warnings.append(
            msg(
                "NASA tıbbi değerlendirme kriteri: Uyku dışında 30 bpm altı nabız kaydedildi. Ölçümü doğrulayın ve sağlık ekibine bildirin.",
                "NASA medical evaluation criterion: Heart rate below 30 bpm outside sleep. Verify the reading and notify the medical team."
            )
        )

    # NASA standardında dinlenme sırasında >130 bpm'nin
    # 1 saatten uzun sürmesi değerlendirme gerektirir.

    hr_duration = number(measurement, "heart_rate_duration_minutes")

    if (
        activity == "rest"
        and hr > 130
        and hr_duration is not None
        and hr_duration >= 60
    ):
        warnings.append(
            msg(
                "NASA tıbbi değerlendirme kriteri: Dinlenme sırasında 1 saatten uzun süren 130 bpm üzeri nabız.",
                "NASA medical evaluation criterion: Resting heart rate above 130 bpm sustained for more than one hour."
            )
        )

    elif activity == "rest" and hr > 130:
        observations.append(
            msg(
                "Dinlenme sırasında 130 bpm üzeri nabız kaydedildi. Süre bilgisi olmadığı için NASA'nın 1 saatlik kriteri doğrulanamadı.",
                "Resting heart rate above 130 bpm recorded. NASA's one-hour criterion cannot be confirmed without duration data."
            )
        )

    # =================================
    # 3. NASA TANSİYON DEĞERLENDİRMESİ
    # =================================

    systolic = number(measurement, "systolic_bp")
    diastolic = number(measurement, "diastolic_bp")

    if systolic is not None and diastolic is not None:

        if systolic >= 140 or diastolic >= 90:
            warnings.append(
                msg(
                    "NASA astronot tıbbi değerlendirme standardındaki hipertansiyon kriteri karşılandı (sistolik ≥140 veya diyastolik ≥90 mmHg). Tek ölçüm kalıcılığı kanıtlamaz; ölçümü tekrarlayın ve sağlık ekibine bildirin.",
                    "NASA astronaut medical evaluation hypertension criterion reached (systolic ≥140 or diastolic ≥90 mmHg). A single reading does not establish sustained hypertension; repeat and report to the medical team."
                )
            )

        else:
            observations.append(
                f"Tansiyon: {systolic:g}/{diastolic:g} mmHg"
            )

    else:
        observations.append(
            msg(
                "Tansiyon ölçümü eksik.",
                "Blood pressure measurement is missing."
            )
        )

    # =================================
    # 4. KİŞİSEL BAŞLANGIÇ VE EĞİLİM
    # =================================

    baseline_fields = {
        "heart_rate": ("Nabız", "Heart rate", "bpm"),
        "temperature": ("Vücut sıcaklığı", "Body temperature", "°C"),
        "oxygen": ("Oksijen doygunluğu", "Oxygen saturation", "%"),
        "respiratory_rate": ("Solunum hızı", "Respiratory rate", "breaths/min"),
        "systolic_bp": ("Sistolik tansiyon", "Systolic blood pressure", "mmHg"),
        "diastolic_bp": ("Diyastolik tansiyon", "Diastolic blood pressure", "mmHg")
    }

    for key, (tr_name, en_name, unit) in baseline_fields.items():

        current = number(measurement, key)
        reference = number(baseline, key)

        if current is not None and reference is not None:
            difference = current - reference

            observations.append(
                f"{tr_name if tr else en_name}: "
                f"{current:g} {unit} | "
                f"Başlangıca göre {difference:+g} {unit}"
                if tr else
                f"{en_name}: {current:g} {unit} | "
                f"{difference:+g} {unit} compared with baseline"
            )

    observations.append(
        msg(
            "NASA yaklaşımı: Sağlık ölçümleri zaman içinde izlenmeli ve eğilimleri değerlendirilmelidir. Tek ölçüm tek başına tanı koymaz.",
            "NASA approach: Health measurements should be monitored over time and evaluated for trends. A single reading does not establish a diagnosis."
        )
    )

    # =================================
    # 5. NASA UZAY RADYASYONU STANDARTLARI
    # =================================

    radiation_rate = number(measurement, "radiation_rate")
    mission_dose = number(measurement, "radiation_dose")

    # Kariyer toplam etkin doz
    career_dose = number(measurement, "career_radiation_dose")

    # Güneş parçacık olayı dozu
    spe_dose = number(measurement, "spe_dose")

    # Nükleer teknolojilerden kaynaklanan doz
    nuclear_dose = number(measurement, "nuclear_radiation_dose")

    mission_days = number(measurement, "mission_duration_days")

    if radiation_rate is not None:

        if radiation_rate < 0:
            return {
                "status": "Review",
                "summary": msg(
                    "Radyasyon doz hızı geçersiz.",
                    "Radiation dose rate is invalid."
                ),
                "details": msg(
                    "Radyasyon ölçüm cihazını kontrol edin.",
                    "Check the radiation measurement device."
                )
            }

        observations.append(
            f"Radyasyon doz hızı: {radiation_rate:g} µSv/hour"
            if tr else
            f"Radiation dose rate: {radiation_rate:g} µSv/hour"
        )

    if mission_dose is not None:

        if mission_dose < 0:
            return {
                "status": "Review",
                "summary": msg(
                    "Birikimli radyasyon dozu geçersiz.",
                    "Cumulative radiation dose is invalid."
                ),
                "details": msg(
                    "Radyasyon doz verisini kontrol edin.",
                    "Check the radiation dose data."
                )
            }

        observations.append(
            f"Görev boyunca biriken doz: {mission_dose:g} mSv"
            if tr else
            f"Cumulative mission dose: {mission_dose:g} mSv"
        )

    # NASA V1 4030: Kariyer toplam etkin doz <600 mSv

    if career_dose is not None:

        observations.append(
            f"Kariyer toplam etkin doz: {career_dose:g} mSv"
            if tr else
            f"Career cumulative effective dose: {career_dose:g} mSv"
        )

        if career_dose >= 600:
            criticals.append(
                msg(
                    "NASA sınırı: Kariyer toplam etkin radyasyon dozu 600 mSv sınırına ulaştı veya aştı.",
                    "NASA limit: Career cumulative effective radiation dose has reached or exceeded 600 mSv."
                )
            )

        elif career_dose >= 500:
            warnings.append(
                msg(
                    "Kariyer toplam radyasyon dozu 600 mSv NASA sınırına yaklaşıyor.",
                    "Career radiation dose is approaching NASA's 600 mSv limit."
                )
            )

    else:
        observations.append(
            msg(
                "Kariyer toplam dozu girilmediği için 600 mSv sınırı değerlendirilemedi.",
                "The 600 mSv limit cannot be evaluated because career dose data is unavailable."
            )
        )

    # NASA V1 4031: SPE tasarım referans dozu <250 mSv / olay

    if spe_dose is not None:

        if spe_dose >= 250:
            criticals.append(
                msg(
                    "NASA güneş parçacık olayı doz sınırı olan 250 mSv'ye ulaşıldı veya aşıldı.",
                    "NASA solar particle event dose limit of 250 mSv has been reached or exceeded."
                )
            )

        else:
            observations.append(
                f"Güneş parçacık olayı dozu: {spe_dose:g} mSv"
                if tr else
                f"Solar particle event dose: {spe_dose:g} mSv"
            )

    # NASA V1 4032: Nükleer teknoloji dozu <20 mSv / görev yılı

    if nuclear_dose is not None and mission_days is not None:

        if mission_days <= 0:
            warnings.append(
                msg(
                    "Görev süresi geçersiz; nükleer radyasyon sınırı hesaplanamadı.",
                    "Mission duration is invalid; nuclear radiation limit could not be calculated."
                )
            )

        else:
            allowed_nuclear_dose = 20 * mission_days / 365.25

            observations.append(
                f"Görev süresine göre nükleer radyasyon sınırı: {allowed_nuclear_dose:.3f} mSv"
                if tr else
                f"Mission-duration-adjusted nuclear radiation limit: {allowed_nuclear_dose:.3f} mSv"
            )

            if nuclear_dose >= allowed_nuclear_dose:
                criticals.append(
                    msg(
                        "NASA nükleer teknoloji radyasyon sınırı aşıldı veya karşılandı.",
                        "NASA nuclear technology radiation limit has been reached or exceeded."
                    )
                )

    # ALARA ilkesi
    observations.append(
        msg(
            "NASA ALARA ilkesi: Radyasyon maruziyeti makul ölçüde mümkün olan en düşük seviyede tutulmalıdır.",
            "NASA ALARA principle: Radiation exposure should be kept as low as reasonably achievable."
        )
    )

    # =================================
    # 6. NASA UYKU DEĞERLENDİRMESİ
    # =================================

    sleep_hours = number(measurement, "sleep_hours")
    sleep_quality = number(measurement, "sleep_quality")

    if sleep_hours is not None:
        observations.append(
            f"Son 24 saat uyku süresi: {sleep_hours:g} saat"
            if tr else
            f"Sleep duration in the last 24 hours: {sleep_hours:g} hours"
        )

    if sleep_quality is not None:
        observations.append(
            f"Uyku kalitesi bildirimi: {sleep_quality:g}"
            if tr else
            f"Reported sleep quality: {sleep_quality:g}"
        )

    observations.append(
        msg(
            "NASA standardı uyku miktarı ve kalitesinin düzenli değerlendirilmesini ister.",
            "NASA standards require regular assessment of sleep quantity and quality."
        )
    )

    # =================================
    # 7. YORGUNLUK VE STRES
    # =================================

    fatigue = number(measurement, "fatigue_level")
    stress = number(measurement, "stress_level")

    if fatigue is not None:
        observations.append(
            f"Yorgunluk seviyesi: {fatigue:g}/5"
            if tr else
            f"Fatigue level: {fatigue:g}/5"
        )

    if stress is not None:
        observations.append(
            f"Stres seviyesi: {stress:g}/5"
            if tr else
            f"Stress level: {stress:g}/5"
        )

    # =================================
    # 8. EGZERSİZ VE BELİRTİLER
    # =================================

    exercise_minutes = number(measurement, "exercise_minutes")
    symptoms = measurement.get("symptoms", "")

    if exercise_minutes is not None:
        observations.append(
            f"Egzersiz süresi: {exercise_minutes:g} dakika"
            if tr else
            f"Exercise duration: {exercise_minutes:g} minutes"
        )

    if symptoms and str(symptoms).strip():
        warnings.append(
            msg(
                "Astronot ek belirtiler bildirdi: ",
                "Astronaut reported additional symptoms: "
            ) + str(symptoms)
        )

    # =================================
    # 9. SONUÇ
    # =================================

    if criticals:
        return {
            "status": "Critical",
            "summary": msg(
                "NASA radyasyon sınırlarından biri karşılandı veya aşıldı. Ölçümleri doğrulayın ve görev sağlık protokolünü uygulayarak sağlık ekibine bildirin.",
                "A NASA radiation limit has been reached or exceeded. Verify readings and notify the medical team according to mission health protocols."
            ),
            "details": "\n".join(criticals + warnings + observations)
        }

    if warnings:
        return {
            "status": "Warning",
            "summary": msg(
                "NASA tıbbi değerlendirme kriterlerinden biri işaretlendi. Ölçümü doğrulayın ve sağlık ekibine bildirin.",
                "A NASA medical evaluation criterion has been flagged. Verify the reading and notify the medical team."
            ),
            "details": "\n".join(warnings + observations)
        }

    return {
        "status": "Normal",
        "summary": msg(
            "Kaydedilen verilerde mevcut NASA değerlendirme kriterlerine göre bir uyarı oluşmadı. İzlemeye devam edin.",
            "No alert was triggered by the available NASA evaluation criteria. Continue monitoring."
        ),
        "details": "\n".join(observations)
    }
