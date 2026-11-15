# ============================================================
# AI USAGE AND DEVELOPMENT DISCLOSURE
# ============================================================
# ChatGPT (OpenAI) was used as a development support tool
# during the development of this emergency guidance module.
#
# AI assistance included code explanations, debugging support,
# and implementation guidance.
#
# The emergency guidance content is predefined and
# retrieved through rule-based Python logic.
#
# No generative AI API is called by this module at runtime.
# The guidance is not a substitute for approved,
# mission-specific emergency procedures or medical care.
#
# The developer reviewed and integrated the implementation.
# ============================================================
def get_emergency_notice(topic, lang="English"):

    tr = lang == "Türkçe"

    guides = {
        "Unusual heart rate": {
            "title": "Olağandışı Kalp Atışı",
            "description": "Kalp atışındaki belirgin değişiklikler çarpıntı, ritim bozukluğu veya başka bir sağlık sorunuyla ilişkili olabilir.",
            "signs": "Dikkat edilmesi gerekenler: Göğüs ağrısı, baş dönmesi, bayılma hissi, nefes darlığı veya belirgin çarpıntı.",
            "actions": "Genel güvenlik adımları:\n1. Fiziksel aktiviteyi durdurun ve güvenli bir pozisyonda dinlenin.\n2. Durumu bir ekip arkadaşınıza bildirin.\n3. Belirtileri ve ne zaman başladığını kaydedin.\n4. Görev sağlık ekibiyle iletişime geçin ve görev prosedürlerini izleyin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA Medical Operations."
        },

        "Low oxygen reading": {
            "title": "Düşük Oksijen Okuması",
            "description": "Düşük oksijen doygunluğu, dokulara yeterli oksijen taşınamamasıyla ilişkili olabilir. Ölçüm cihazı ve sensör hataları da sonucu etkileyebilir.",
            "signs": "Dikkat edilmesi gerekenler: Nefes darlığı, dudaklarda veya tırnaklarda mavimsi renk, bilinç bulanıklığı, baş dönmesi ve olağandışı yorgunluk.",
            "actions": "Genel güvenlik adımları:\n1. Nefes alma güçlüğü veya bilinç değişikliği varsa durumu acil olarak bildirin.\n2. Güvenliyse sensörün doğru yerleştiğini kontrol edin.\n3. Ölçüm cihazının onaylanmış kullanım talimatlarını izleyin.\n4. Görev sağlık ekibiyle iletişime geçin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA In-Flight Medical Care."
        },

        "High temperature": {
            "title": "Yüksek Vücut Sıcaklığı",
            "description": "Yüksek vücut sıcaklığı enfeksiyon, aşırı ısınma veya başka bir sağlık sorunuyla ilişkili olabilir.",
            "signs": "Dikkat edilmesi gerekenler: Ateş hissi, titreme, yoğun terleme, baş ağrısı, halsizlik ve bilinç değişikliği.",
            "actions": "Genel güvenlik adımları:\n1. Fiziksel aktiviteyi durdurun.\n2. Belirtileri ve başlangıç zamanını kaydedin.\n3. Görev sağlık ekibine haber verin.\n4. Sağlık ekibinin yönlendirmelerini ve görev prosedürlerini izleyin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA Medical Operations."
        },

        "Feeling unwell / uncertain": {
            "title": "Kendini Kötü Hissetme veya Belirsizlik",
            "description": "Yeni başlayan veya açıklanamayan fiziksel ya da psikolojik belirtiler görev sırasında dikkate alınmalıdır.",
            "signs": "Dikkat edilmesi gerekenler: Olağandışı halsizlik, baş dönmesi, ağrı, mide bulantısı, bilinç değişikliği veya günlük görevleri yerine getirmekte zorlanma.",
            "actions": "Genel güvenlik adımları:\n1. Durumu bir ekip arkadaşınıza bildirin.\n2. Belirtilerin ne zaman başladığını ve nasıl değiştiğini kaydedin.\n3. Görev sağlık ekibiyle iletişime geçin.\n4. Onaylanmış görev prosedürlerini izleyin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health."
        },

        "Chest pain": {
            "title": "Göğüs Ağrısı",
            "description": "Göğüs ağrısı kalp, akciğer veya başka ciddi sağlık sorunlarının belirtisi olabilir.",
            "signs": "Dikkat edilmesi gerekenler: Göğüste baskı veya sıkışma, kola ya da çeneye yayılan ağrı, soğuk terleme, bulantı ve nefes darlığı.",
            "actions": "Genel güvenlik adımları:\n1. Aktiviteyi hemen durdurun.\n2. Durumu ekip arkadaşınıza ve görev sağlık ekibine acil olarak bildirin.\n3. Belirtilerin başlangıcını ve değişimini kaydedin.\n4. Yalnızca görev için onaylanmış tıbbi prosedürleri uygulayın.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA Medical Operations."
        },

        "Breathing difficulty": {
            "title": "Solunum Güçlüğü",
            "description": "Solunum güçlüğü oksijenlenme, solunum sistemi veya kabin ortamıyla ilişkili ciddi bir sorunun işareti olabilir.",
            "signs": "Dikkat edilmesi gerekenler: Nefes almakta zorlanma, hızlı veya düzensiz solunum, göğüste sıkışma, konuşmakta zorlanma ve bilinç değişikliği.",
            "actions": "Genel güvenlik adımları:\n1. Durumu acil olarak diğer ekip üyelerine bildirin.\n2. Görev sağlık ekibiyle hemen iletişime geçin.\n3. Kabin ortamına ilişkin bir tehlike şüphesi varsa ilgili çevresel acil durum prosedürünü izleyin.\n4. Görev için onaylanmış acil durum kontrol listesini takip edin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA-STD-3001, Volume 2."
        },

        "Loss of consciousness": {
            "title": "Bilinç Kaybı veya Bilinç Değişikliği",
            "description": "Bilinç kaybı veya ani bilinç değişikliği acil değerlendirme gerektiren ciddi bir durumdur.",
            "signs": "Dikkat edilmesi gerekenler: Bayılma, çevreye yanıt vermeme, ani kafa karışıklığı veya olağandışı davranış.",
            "actions": "Genel güvenlik adımları:\n1. Diğer ekip üyelerine ve görev sağlık ekibine derhal haber verin.\n2. Kişinin durumunu görev için öğretilmiş ilk yardım ve acil müdahale prosedürlerine göre değerlendirin.\n3. Eğitimli değilseniz onaylanmamış tıbbi müdahalelerde bulunmayın.\n4. Görev acil durum kontrol listesini izleyin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA Medical Operations."
        },

        "Bleeding / injury": {
            "title": "Kanama veya Yaralanma",
            "description": "Yaralanmalar uzay aracının sınırlı ortamında enfeksiyon, kan kaybı veya hareket kısıtlılığı gibi ek riskler oluşturabilir.",
            "signs": "Dikkat edilmesi gerekenler: Devam eden kanama, derin yara, şiddetli ağrı, şişlik, hareket kaybı veya bilinç değişikliği.",
            "actions": "Genel güvenlik adımları:\n1. Yaralanmayı ve çevredeki olası tehlikeleri bildirin.\n2. Güvenliyse görev eğitimi kapsamında öğretilen temel ilk yardım adımlarını uygulayın.\n3. Görev sağlık ekibiyle iletişime geçin.\n4. Kullanılan tıbbi malzemeleri ve yaralanmanın gelişimini kaydedin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA Medical Operations."
        },

        "Radiation exposure": {
            "title": "Radyasyon Maruziyeti",
            "description": "Uzay ortamında galaktik kozmik ışınlar ve Güneş kaynaklı parçacık olayları mürettebatın radyasyon maruziyetine katkıda bulunabilir.",
            "signs": "Radyasyon maruziyeti her zaman hemen fark edilebilir belirtiler oluşturmaz. Maruziyet kayıtları ve görev radyasyon izleme sistemi önemlidir.",
            "actions": "Genel güvenlik adımları:\n1. Görev radyasyon izleme ve uyarı sistemlerini takip edin.\n2. Görev tarafından belirlenmiş korunaklı alana geçiş prosedürlerini izleyin.\n3. Maruziyet bilgilerini görev ekibine bildirin.\n4. Radyasyon dozu ve olay kayıtlarının korunmasını sağlayın.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA-STD-3001, Volume 2."
        },

        "Cabin pressure / toxic exposure": {
            "title": "Kabin Basıncı veya Toksik Madde Maruziyeti",
            "description": "Basınç kaybı, karbondioksit artışı veya amonyak gibi toksik maddelere maruziyet uzay aracı ortamında ciddi tehlikeler oluşturabilir.",
            "signs": "Dikkat edilmesi gerekenler: Kabin uyarıları, olağandışı koku, göz veya solunum yolu tahrişi, baş ağrısı, baş dönmesi ve nefes darlığı.",
            "actions": "Genel güvenlik adımları:\n1. Kabin alarm ve çevresel izleme sistemlerini dikkate alın.\n2. İlgili çevresel acil durum prosedürünü derhal izleyin.\n3. Görev tarafından belirtilen koruyucu ekipmanı kullanın.\n4. Görev kontrolü ve sağlık ekibiyle iletişim kurun.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA-STD-3001, Volume 2."
        },

        "Psychological distress": {
            "title": "Psikolojik Zorlanma",
            "description": "Uzun süreli izolasyon, sınırlı yaşam alanı, yoğun iş yükü ve uyku düzenindeki değişiklikler psikolojik sağlığı etkileyebilir.",
            "signs": "Dikkat edilmesi gerekenler: Yoğun kaygı, sürekli uyku sorunu, belirgin duygu durum değişikliği, sosyal geri çekilme ve görevleri yerine getirmekte zorlanma.",
            "actions": "Genel destek adımları:\n1. Durumu güvendiğiniz bir ekip arkadaşınızla paylaşın.\n2. Görev sağlık veya psikolojik destek ekibiyle iletişime geçin.\n3. Görevde belirlenmiş uyku, dinlenme ve destek planlarını izleyin.\n4. Belirtilerin devam etmesi veya kötüleşmesi durumunda destek istemeyi ertelemeyin.",
            "source": "NASA-STD-3001, Volume 1 — Crew Health; NASA Medical Operations."
        }
    }

    guide = guides.get(topic)

    if guide is None:
        return (
            "Acil durum başlığı bulunamadı."
            if tr else
            "Emergency topic not found."
        )

    if tr:
        return (
            f"## {guide['title']}\n\n"
            f"**Genel Bilgi**\n{guide['description']}\n\n"
            f"**Belirtiler ve Riskler**\n{guide['signs']}\n\n"
            f"**Genel Güvenlik Adımları**\n{guide['actions']}\n\n"
            f"**Kaynak:** {guide['source']}\n\n"
            "Not: Bu içerik genel bilgilendirme amaçlıdır. "
            "Gerçek görevlerde ilgili aracın ve görevin onaylanmış "
            "acil durum prosedürleri esas alınmalıdır."
        )

    return (
        f"## {guide['title']}\n\n"
        f"**General Information**\n{guide['description']}\n\n"
        f"**Signs and Risks**\n{guide['signs']}\n\n"
        f"**General Safety Steps**\n{guide['actions']}\n\n"
        f"**Source:** {guide['source']}\n\n"
        "Note: This content is for general educational purposes. "
        "Actual missions must follow their approved vehicle- and "
        "mission-specific emergency procedures."
    )
