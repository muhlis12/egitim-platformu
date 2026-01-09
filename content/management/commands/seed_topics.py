from django.core.management.base import BaseCommand
from content.models import Grade, Subject, TopicTemplate


# Alt başlık şablonları (B modeli)
TR_CHILD = ["Konu Anlatımı", "Örnekler", "Test"]
MATH_CHILD = ["Kurallar", "İşlemler", "Problemler", "Test"]
SCI_CHILD = ["Kavramlar", "Örnekler", "Test"]
SOC_CHILD = ["Konu", "Özet", "Test"]
ENG_CHILD = ["Grammar", "Vocabulary", "Practice"]


# 1) Senin mevcut (detaylı) DATA’nı aynen koruyoruz
BASE_DATA = {
    1: {
        "Türkçe": [
            {"title": "Sesler ve harfler", "children": ["Harfler", "Hece-Kelime", "Alıştırmalar"]},
            {"title": "Okuduğunu anlama", "children": ["Metin okuma", "Sorular", "Kısa test"]},
            {"title": "Yazma çalışmaları", "children": ["Cümle kurma", "Kısa paragraf", "Alıştırmalar"]},
        ],
        "Matematik": [
            {"title": "Doğal sayılar", "children": ["Sayı okuma-yazma", "Karşılaştırma", "Alıştırmalar"]},
            {"title": "Toplama", "children": ["Kurallar", "İşlemler", "Problemler"]},
            {"title": "Çıkarma", "children": ["Kurallar", "İşlemler", "Problemler"]},
            {"title": "Geometrik şekiller", "children": ["Şekiller", "Örnekler", "Alıştırmalar"]},
        ],
        "Hayat Bilgisi": [
            {"title": "Okul kuralları", "children": ["Sınıf kuralları", "Okul düzeni", "Etkinlik"]},
            {"title": "Sağlık ve temizlik", "children": ["Temizlik", "Beslenme", "Günlük rutin"]},
            {"title": "Güvenlik", "children": ["Evde güvenlik", "Okulda güvenlik", "Trafik"]},
        ],
    },

    5: {
        "Türkçe": [
            {"title": "Sözcükte anlam", "children": ["Gerçek-Mecaz", "Eş-Zıt", "Konu test"]},
            {"title": "Cümlede anlam", "children": ["Neden-Sonuç", "Amaç-Sonuç", "Konu test"]},
            {"title": "Paragraf", "children": ["Ana fikir", "Yardımcı fikir", "Paragraf test"]},
            {"title": "Yazım kuralları", "children": ["Büyük harf", "Birleşik kelime", "Test"]},
            {"title": "Noktalama işaretleri", "children": ["Nokta-virgül", "İki nokta-tırnak", "Test"]},
        ],
        "Matematik": [
            {"title": "Doğal sayılar", "children": ["İşlemler", "Problemler", "Test"]},
            {"title": "Kesirler", "children": ["Karşılaştırma", "Toplama-Çıkarma", "Problemler"]},
            {"title": "Ondalık sayılar", "children": ["Dönüştürme", "İşlemler", "Problemler"]},
            {"title": "Yüzdeler", "children": ["Yüzde hesap", "Problemler", "Test"]},
            {"title": "Veri analizi", "children": ["Grafikler", "Tablolar", "Yorumlama"]},
        ],
        "Fen Bilimleri": [
            {"title": "Güneş-Dünya-Ay", "children": ["Dünya hareketleri", "Ayın evreleri", "Test"]},
            {"title": "Kuvvet ve sürtünme", "children": ["Sürtünme", "Günlük yaşam", "Test"]},
            {"title": "Madde ve değişim", "children": ["Hal değişimi", "Isı", "Test"]},
            {"title": "Işık", "children": ["Yansıma", "Kırılma", "Test"]},
        ],
    },

    8: {
        "Türkçe": [
            {"title": "Fiilimsiler", "children": ["İsim-fiil", "Sıfat-fiil", "Zarf-fiil", "Test"]},
            {"title": "Cümle türleri", "children": ["Yapı", "Anlam", "Test"]},
            {"title": "Anlatım bozuklukları", "children": ["Türler", "Örnekler", "Test"]},
            {"title": "Paragraf", "children": ["Anlam", "Soru çözüm", "Deneme"]},
            {"title": "Yazım ve noktalama", "children": ["Yazım", "Noktalama", "Test"]},
        ],
        "Matematik": [
            {"title": "Çarpanlar ve katlar", "children": ["Asal sayılar", "EBOB-EKOK", "Problemler"]},
            {"title": "Üslü ifadeler", "children": ["Kurallar", "İşlemler", "Problemler"]},
            {"title": "Köklü ifadeler", "children": ["Kurallar", "İşlemler", "Problemler"]},
            {"title": "Eşitsizlikler", "children": ["Kurallar", "Çözüm", "Problemler"]},
            {"title": "Olasılık", "children": ["Temel kavramlar", "Uygulama", "Problemler"]},
        ],
        "Fen Bilimleri": [
            {"title": "DNA ve genetik", "children": ["Kalıtım", "Mutasyon", "Test"]},
            {"title": "Basınç", "children": ["Katı basıncı", "Sıvı basıncı", "Test"]},
            {"title": "Madde ve endüstri", "children": ["Asit-baz", "Tepkimeler", "Test"]},
            {"title": "Basit makineler", "children": ["Kuvvet kazancı", "Örnekler", "Test"]},
            {"title": "Elektrik", "children": ["Devreler", "Enerji", "Test"]},
        ],
    },
}


def build_full_data():
    # 2) Full 1–12 skeleton (genel)
    data = {}

    # 1–4 İlkokul
    for g in range(1, 5):
        data[g] = {
            "Türkçe": [
                {"title": "Okuma-Anlama", "children": TR_CHILD},
                {"title": "Yazma", "children": ["Cümle", "Paragraf", "Etkinlik"]},
                {"title": "Dil Bilgisi (Temel)", "children": TR_CHILD},
            ],
            "Matematik": [
                {"title": "Sayılar", "children": MATH_CHILD},
                {"title": "İşlemler", "children": MATH_CHILD},
                {"title": "Problemler", "children": ["Kolay", "Orta", "Zor"]},
                {"title": "Geometri", "children": ["Şekiller", "Örnekler", "Etkinlik"]},
            ],
            "Hayat Bilgisi": [
                {"title": "Ben ve Okulum", "children": ["Konu", "Etkinlik"]},
                {"title": "Sağlık", "children": ["Konu", "Etkinlik"]},
                {"title": "Güvenlik", "children": ["Ev", "Okul", "Trafik"]},
            ],
        }

    # 5–8 Ortaokul
    for g in range(5, 9):
        data[g] = {
            "Türkçe": [
                {"title": "Paragraf", "children": TR_CHILD},
                {"title": "Sözcükte Anlam", "children": TR_CHILD},
                {"title": "Cümlede Anlam", "children": TR_CHILD},
                {"title": "Dil Bilgisi", "children": ["Kurallar", "Örnekler", "Test"]},
                {"title": "Yazım ve Noktalama", "children": ["Kurallar", "Örnekler", "Test"]},
            ],
            "Matematik": [
                {"title": "Sayılar", "children": MATH_CHILD},
                {"title": "Cebir", "children": MATH_CHILD},
                {"title": "Geometri", "children": MATH_CHILD},
                {"title": "Veri & Olasılık", "children": ["Konu", "Örnek", "Test"]},
            ],
            "Fen Bilimleri": [
                {"title": "Canlılar", "children": SCI_CHILD},
                {"title": "Fiziksel Olaylar", "children": SCI_CHILD},
                {"title": "Madde ve Değişim", "children": SCI_CHILD},
                {"title": "Dünya ve Evren", "children": SCI_CHILD},
            ],
            "Sosyal Bilgiler": [
                {"title": "Tarih", "children": SOC_CHILD},
                {"title": "Coğrafya", "children": SOC_CHILD},
                {"title": "Vatandaşlık", "children": SOC_CHILD},
            ],
            "İngilizce": [
                {"title": "Grammar", "children": ENG_CHILD},
                {"title": "Vocabulary", "children": ENG_CHILD},
                {"title": "Reading", "children": ["Text", "Questions", "Practice"]},
            ],
        }

    # 9–12 Lise
    for g in range(9, 13):
        data[g] = {
            "Türk Dili ve Edebiyatı": [
                {"title": "Edebiyat", "children": ["Dönemler", "Eser-Yazar", "Test"]},
                {"title": "Dil Bilgisi", "children": ["Sözcük türleri", "Cümle", "Test"]},
                {"title": "Paragraf", "children": TR_CHILD},
            ],
            "Matematik": [
                {"title": "Temel Matematik", "children": MATH_CHILD},
                {"title": "Fonksiyonlar", "children": MATH_CHILD},
                {"title": "Geometri", "children": MATH_CHILD},
            ],
            "Fizik": [
                {"title": "Kuvvet-Hareket", "children": SCI_CHILD},
                {"title": "Elektrik", "children": SCI_CHILD},
                {"title": "Dalgalar/Optik", "children": SCI_CHILD},
            ],
            "Kimya": [
                {"title": "Madde", "children": SCI_CHILD},
                {"title": "Tepkimeler", "children": SCI_CHILD},
                {"title": "Karışımlar", "children": SCI_CHILD},
            ],
            "Biyoloji": [
                {"title": "Hücre", "children": SCI_CHILD},
                {"title": "Genetik", "children": SCI_CHILD},
                {"title": "Ekosistem", "children": SCI_CHILD},
            ],
            "Tarih": [
                {"title": "Tarih Konuları", "children": SOC_CHILD},
            ],
            "Coğrafya": [
                {"title": "Coğrafya Konuları", "children": SOC_CHILD},
            ],
            "İngilizce": [
                {"title": "Grammar", "children": ENG_CHILD},
                {"title": "Reading", "children": ["Text", "Questions", "Practice"]},
                {"title": "Writing", "children": ["Tasks", "Practice"]},
            ],
        }

    # 3) BASE_DATA ile override (1,5,8 detaylı kalsın)
    for g, subjects in BASE_DATA.items():
        data[g] = subjects

    return data


DATA = build_full_data()


class Command(BaseCommand):
    help = "B modeli: 1–12. sınıf ders konu bankasını (üst konu + alt konular) yükler"

    def handle(self, *args, **options):
        created_count = 0

        for grade_num, subjects in DATA.items():
            grade, _ = Grade.objects.get_or_create(number=grade_num)

            for subject_name, topics in subjects.items():
                subject, _ = Subject.objects.get_or_create(name=subject_name)

                for i, item in enumerate(topics, start=1):
                    parent_obj, parent_created = TopicTemplate.objects.get_or_create(
                        grade=grade,
                        subject=subject,
                        parent=None,
                        title=item["title"],
                        order=i,
                    )
                    if parent_created:
                        created_count += 1

                    children = item.get("children", []) or []
                    for j, child_title in enumerate(children, start=1):
                        _, child_created = TopicTemplate.objects.get_or_create(
                            grade=grade,
                            subject=subject,
                            parent=parent_obj,
                            title=child_title,
                            order=j,
                        )
                        if child_created:
                            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Konu bankası yüklendi. Toplam {created_count} kayıt eklendi."))
