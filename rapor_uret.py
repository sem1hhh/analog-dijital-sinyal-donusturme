import os
import json
from datetime import date
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

BOSLUK = os.path.dirname(os.path.abspath(__file__))
KAYNAK = os.path.join(BOSLUK, "rapor_kaynak")
CIKTI = os.path.join(KAYNAK, "rapor.docx")

YER_TUTUCU = {
    "ad_soyad": "Ad Soyad",
    "ogrenci_no": "Öğrenci No",
    "universite": "",
    "hoca_adi": "",
    "ders_adi": "Sistemler ve Sinyaller Dersi",
    "tarih": "",
}


def kisisel_bilgileri_oku():
    bilgiler = dict(YER_TUTUCU)
    yol = os.path.join(BOSLUK, "kisisel_bilgiler.json")
    if os.path.exists(yol):
        try:
            with open(yol, "r", encoding="utf-8") as f:
                veri = json.load(f)
        except (OSError, ValueError):
            veri = None
        if isinstance(veri, dict):
            for anahtar, deger in veri.items():
                if anahtar in bilgiler and deger:
                    bilgiler[anahtar] = str(deger).strip()
    if not bilgiler["tarih"]:
        bilgiler["tarih"] = date.today().strftime("%d.%m.%Y")
    return bilgiler


def baslik(doc, metin, seviye=1):
    doc.add_heading(metin, level=seviye)


def paragraf(doc, metin):
    p = doc.add_paragraph(metin)
    p.paragraph_format.space_after = Pt(8)
    return p


def gorsel(doc, dosya, baslik_metni, genislik=6.0):
    yol = os.path.join(KAYNAK, dosya)
    if os.path.exists(yol):
        doc.add_picture(yol, width=Inches(genislik))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph(baslik_metni)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].italic = True
        cap.runs[0].font.size = Pt(9)


def tablo(doc, basliklar, satirlar):
    t = doc.add_table(rows=1, cols=len(basliklar))
    t.style = "Light Grid Accent 1"
    for i, b in enumerate(basliklar):
        t.rows[0].cells[i].text = b
    for s in satirlar:
        hucreler = t.add_row().cells
        for i, v in enumerate(s):
            hucreler[i].text = str(v)


def olustur():
    doc = Document()
    bilgiler = kisisel_bilgileri_oku()

    for i in range(4):
        doc.add_paragraph("")
    doc.add_heading("SUREKLI ZAMANLI SINYALIN AYRIK ZAMANLI SINYALE DONUSUMU", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")
    paragraf(doc, bilgiler["ders_adi"] + " - Proje Raporu").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")
    paragraf(doc, "Hazırlayan: " + bilgiler["ad_soyad"]).alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraf(doc, "Öğrenci No: " + bilgiler["ogrenci_no"]).alignment = WD_ALIGN_PARAGRAPH.CENTER
    if bilgiler["universite"]:
        paragraf(doc, bilgiler["universite"]).alignment = WD_ALIGN_PARAGRAPH.CENTER
    if bilgiler["hoca_adi"]:
        paragraf(doc, "Ders Sorumlusu: " + bilgiler["hoca_adi"]).alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraf(doc, "Tarih: " + bilgiler["tarih"]).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    baslik(doc, "ICINDEKILER", 1)
    icindekiler = [
        "1. Giris ve Amac",
        "2. Teorik Temeller",
        "3. Yontem ve Algoritma",
        "4. Arayuz Tanimi",
        "5. Sonuclar ve Yorumlar",
        "6. Sonuc ve Oneriler",
        "7. Kaynakca",
    ]
    for m in icindekiler:
        doc.add_paragraph(m, style="List Number")
    doc.add_page_break()

    baslik(doc, "1. GIRIS VE AMAC", 1)
    paragraf(
        doc,
        "Bu projede, giris olarak alinan surekli zamanli (analog) sinyalin, gerekli parametrelere gore "
        "ayrik zamanli (dijital) sinyale donusturulmesi amaclanmistir. Donusumun iki temel adimi olan "
        "ornekleme (sampling) ve nicemleme (quantization) islemleri gerceklestirilmis, olusan dijital "
        "sinyalin orijinal sinyalle karsilastirilmasi yapilmistir.",
    )
    paragraf(
        doc,
        "Calismanin ikinci amaci, donusum parametrelerini (ornekleme frekansi, nicemleme bit sayisi, "
        "dalga sekli) kullaniciye acan bir arayuz yazilimi gelistirmek ve elde edilen sonuclari bir "
        "Word raporunda toplamaktir.",
    )

    baslik(doc, "2. TEORIK TEMELLER", 1)
    baslik(doc, "2.1 Ornekleme Teoremi ve Nyquist-Shannon", 2)
    paragraf(
        doc,
        "Surekli zamanli bir sinyal, ornekleme ile ayrık zamanli sinyale cevrilir. Ornekleme islemi, "
        "sinyalin belirli araliklarla (Ts ornekleme periyodu) degerlerinin alinmasiyla gerceklesir. "
        "Ts = 1 / fs baglantisi bulunur.",
    )
    paragraf(
        doc,
        "Nyquist-Shannon ornekleme teoremine gore, bir sinyalin bozulmadan ayrık zamanli temsil "
        "edilebilmesi icin ornekleme frekansi, sinyalin en yuksek frekans bileseninin en az iki kati "
        "olmalidir: fs >= 2 * fmax. Bu kosul saglanmadiginda aliasing (frekans karisimi) olgusu "
        "gozlemlenir ve sinyalin frekans icerigi bozulur.",
    )
    baslik(doc, "2.2 Nicemleme (Quantization)", 2)
    paragraf(
        doc,
        "Nicemleme, orneklendi sinyalin sonlu sayida seviyeye yuvarlanarak sonlu genlik degerlerine "
        "sahip hale getirilmesidir. b bit kullanildiginda 2^b farkli seviye olusur. Nicemleme sonucunda "
        "nicemleme hatasi (kuantizasyon gurultusu) ortaya cikar.",
    )
    baslik(doc, "2.3 Nicemleme SNR (Teorik)", 2)
    p = doc.add_paragraph()
    p.add_run(
        "Nicemleme sonucu olusan sinyalin gurultu-oran (SNR) degeri, bit sayisiyla dogrusal artis "
        "gosterir. Teorik formul: SNR(dB) ~= 6.02 * b + 1.76"
    )
    isaret = p.add_run("1")
    isaret.font.superscript = True
    p.add_run(".")

    alt = doc.add_paragraph()
    a = alt.add_run("1 ")
    a.font.superscript = True
    a.bold = True
    r = alt.add_run(
        "Bu teoretsel SNR ifadesi YALNIZCA tam genlikli (full-scale) sinüs sinyali icin gecerlidir. "
        "Kare, testere, cok tonlu veya gercek WAV sinyallerinde olculen SNR degeri bu teorik degerden "
        "sapabilir; teorik deger yalnizca karsilastirma amaclidir."
    )
    r.italic = True
    r.font.size = Pt(9)
    alt.paragraph_format.space_after = Pt(12)
    doc.add_page_break()

    baslik(doc, "3. YONTEM VE ALGORITMA", 1)
    paragraf(
        doc,
        "Donusum su adimlar halinde gerceklestirilmistir: (1) surekli sinyal uretilir, (2) ornekleme "
        "yapilir, (3) nicemleme uygulanir, (4) sonuclar cizilir.",
    )
    gorsel(doc, "fig_akis.png", "Sekil 1: Donusum akis semasi")
    tablo(
        doc,
        ["Adim", "Islem", "Fonksiyon"],
        [
            ["1", "Surekli sinyal uretimi (sinus/kare/testere/cok tonlu)", "sinus_uret, kare_uret, testere_uret"],
            ["2", "Ornekleme (x[n] = x(n*Ts))", "ornekle"],
            ["3", "Nicemleme (2^b seviyeye yuvarlama)", "nicemle"],
            ["4", "SNR ve Nyquist kontrolu", "snr_hesapla, nyquist_kontrol"],
        ],
    )
    paragraf(
        doc,
        "Ayrica WAV dosyasi yuklendiginde orijinal, orneklenmis ve nicemlenmis sesler arayuz uzerinden "
        "dinlenebilmektedir.",
    )

    baslik(doc, "4. ARAYUZ TANIMI", 1)
    paragraf(
        doc,
        "Arayuz Streamlit ile gelistirilmistir. Kullanici soldaki panelden sinyal kaynagi, dalga sekli, "
        "frekans, genlik, faz, sure, ornekleme frekansi (fs) ve nicemleme bit sayisini ayarlayabilir. "
        "Ts degeri otomatik olarak hesaplanmaktadir.",
    )
    tablo(
        doc,
        ["Parametre", "Arayuz Elemani", "Aralik / Varsayilan"],
        [
            ["Sinyal kaynagi", "Radio", "Sentetik / Cok Tonlu / WAV"],
            ["Dalga sekli", "Secim kutusu", "Sinus / Kare / Testere"],
            ["Frekans (sentetik)", "Slider", "10 - 2000 Hz (vars. 100)"],
            ["Genlik", "Slider", "0.1 - 1.0 (vars. 1.0)"],
            ["Faz", "Slider", "0 - 360 derece"],
            ["Sure", "Slider", "0.01 - 0.1 s"],
            ["Ornekleme fs", "Slider", "100 - 20000 Hz (Ts otomatik)"],
            ["Nicemleme bit sayisi", "Slider", "1 - 16 bit (vars. 8)"],
            ["Nicemleme tipi", "Secim kutusu", "yuvarlat / yukari / asagi"],
        ],
    )
    gorsel(doc, "fig6_arayuz_ekran.png", "Sekil 2: Arayuz ekran goruntusu")
    paragraf(
        doc,
        "Arayuzde ayrica Nyquist uyari kutusu, olculen ve teorik SNR degerleri, ornek sayisi, seviye "
        "sayisi gibi bilgiler goruntulenmektedir. WAV modunda uc ses oynatici (orijinal, orneklenmis, "
        "nicemlenmis) sunulmaktadir.",
    )
    paragraf(
        doc,
        "Kare ve testere dalgalar icin Nyquist kontrolunde fmax olarak sinyalin taban frekansi (f) "
        "alinmistir. Bu pratik bir sinirdir: ideal kare ve testere dalgalarin harmonikleri f, 3f, 5f... "
        "sekilde sonsuza kadar uzar. Bu nedenle fs >= 2f kosulu saglansa bile, ust harmonikler ornekleme "
        "frekansinin yarisini astiginda kismi bozulma (aliasing) olusur.",
    )

    baslik(doc, "5. SONUCLAR VE YORUMLAR", 1)
    baslik(doc, "5.1 Ornekleme", 2)
    gorsel(doc, "fig1_orijinal_vs_orneklendi.png", "Sekil 3: Orijinal surekli ve orneklenmis sinyal")
    paragraf(
        doc,
        "Nyquist kosulu saglandiginda orneklenmis sinyalin zarf uzerinde orijinal sinyali birebir "
        "izledigi gorulmektedir.",
    )
    baslik(doc, "5.2 Nicemleme ve Bit Derinligi", 2)
    gorsel(doc, "fig2_nicemleme_farkli_bitler.png", "Sekil 4: Farkli bit derinliklerinde nicemleme")
    tablo(
        doc,
        ["Bit", "Seviye (2^b)", "Teorik SNR (dB)"],
        [
            ["1", "2", "7.78"],
            ["2", "4", "13.80"],
            ["4", "16", "25.84"],
            ["8", "256", "49.92"],
        ],
    )
    paragraf(
        doc,
        "Bit sayisi arttikca nicemleme hatasi azalmakta ve olculen SNR degeri teoretsel olarak "
        "artan degerle uyumlu sekilde yukselmektedir.",
    )
    baslik(doc, "5.3 Aliasing (Nyquist Ihlali)", 2)
    gorsel(doc, "fig3_aliasing.png", "Sekil 5: Aliasing durumu (stem cizim ve alias sinusu)")
    paragraf(
        doc,
        "fs = 800 Hz < 2*f = 1000 Hz kosulunda 500 Hz'lik orijinal sinus 800 Hz ile orneklenmistir. "
        "Ornekler (stem cizim) uzerine cizilen kesikli alias sinusu, gorunen frekansin "
        "|fs - f| = 300 Hz oldugunu gostermektedir. Gorunen frekans orijinal frekanstan sapmistir; "
        "bu durum Nyquist teoreminin gerekliligini dogrulamaktadir.",
    )
    baslik(doc, "5.4 Kare ve Testere Dalga", 2)
    gorsel(doc, "fig4_kare_testere.png", "Sekil 6: Kare ve testere dalga nicemlemesi")
    paragraf(
        doc,
        "Kare ve testere dalgalar harmonik icerigi zengin sinyallerdir; bit sayisi dusukken kenar "
        "gecisleri ve egimler belirgin sekilde bozulmaktadir. Kare dalga yalnizca -A ve +A degerlerini "
        "aldigi icin 2 bit (4 seviye) yeterlidir ve nicemlemeden hemen hemen etkilenmez; buna karsilik "
        "testere dalgasi egimli oldugu icin 2 bitte ciddi sekilde bozulur.",
    )
    baslik(doc, "5.5 Sentetik Ton ile Aliasing (WAV Yerine)", 2)
    gorsel(
        doc,
        "fig5_wav_ornekleme.png",
        "Sekil 7: Sentetik ton (WAV yerine): fs = 600 Hz < 2*f = 880 Hz",
    )
    paragraf(
        doc,
        "Tekrarlanabilir bir sabit ornek olarak 440 Hz'lik sentetik ton, 2*f = 880 Hz altindaki "
        "fs = 600 Hz ile orneklenmistir. Nyquist kosulu saglanmadigi icin gorunen frekans "
        "|600 - 440| = 160 Hz olmus ve nicemlenmis dizide aliasing gozlemlenmistir.",
    )
    doc.add_page_break()

    baslik(doc, "6. SONUC VE ONERILER", 1)
    paragraf(
        doc,
        "Bu projede surekli zamanli sinyalin ayrık zamanli sinyale donusumunun iki temel adimi olan "
        "ornekleme ve nicemleme basariyla gerceklestirilmistir. Nyquist kosulunun saglanmasinin "
        "aliasing onlenmesi icin sart, nicemleme bit sayisinin artmasinin ses/sinyal kalitesini "
        "yukselttigi dogrulanmistir.",
    )
    paragraf(
        doc,
        "Oneriler: gercek bir ses dosyasi uzerinden sistemin denenmesi, interpolasyon (reconstrüksiyon) "
        "filtrelerinin eklenmesi ve farkli nicemleme yontemlerinin (non-uniform) karsilastirilmasi "
        "calismanin gelistirilmesine katki saglayabilir.",
    )

    baslik(doc, "7. KAYNAKCA", 1)
    for k in [
        "Oppenheim, A. V., Schafer, R. W. Discrete-Time Signal Processing.",
        "Proakis, J. G., Manolakis, D. G. Digital Signal Processing.",
        "Haykin, S. Communication Systems.",
    ]:
        doc.add_paragraph(k, style="List Number")

    os.makedirs(KAYNAK, exist_ok=True)
    doc.save(CIKTI)
    print("Rapor olusturuldu ->", CIKTI)


if __name__ == "__main__":
    olustur()
