
def get_emergency_notice(topic, lang="English"):

    messages_en = {
        "Unusual heart rate": "Verify the reading using the approved device procedure. Record symptoms and contact mission medical support according to the approved checklist.",
        "Low oxygen reading": "Check sensor placement and repeat the measurement if safe. Follow the approved emergency checklist and contact mission medical support.",
        "High temperature": "Verify the measurement using the approved method. Record symptoms and contact medical support.",
        "Feeling unwell / uncertain": "Inform another crew member, contact mission medical support and follow the approved onboard medical checklist."
    }

    messages_tr = {
        "Unusual heart rate": "Ölçümü onaylanmış cihaz prosedürüne göre doğrulayın. Belirtileri kaydedin ve onaylanmış kontrol listesine göre sağlık desteğine başvurun.",
        "Low oxygen reading": "Sensörün yerleşimini kontrol edin. Güvenliyse ölçümü tekrarlayın. Onaylanmış acil durum prosedürünü izleyin ve sağlık desteğine başvurun.",
        "High temperature": "Ölçümü onaylanmış yöntemle doğrulayın. Belirtileri kaydedin ve sağlık desteğine başvurun.",
        "Feeling unwell / uncertain": "Bir ekip arkadaşınıza haber verin, görev sağlık desteğiyle iletişime geçin ve onaylanmış tıbbi kontrol listesini izleyin."
    }

    if lang == "Türkçe":
        return messages_tr[topic]

    return messages_en[topic]
