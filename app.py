import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st
import io
import os
import sinyal_core as sc
import rapor_grafikleri

st.set_page_config(page_title="Analog - Dijital Dönüştürme", layout="wide")
st.title("Sürekli Zamanlı Sinyalin Ayrık Zamanlı Sinyale Dönüştürülmesi")


def grafik_bytes(_fig):
    buf = io.BytesIO()
    _fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()


MAKS_NOKTA = 5000


def seyrelt(t, x, maks=MAKS_NOKTA):
    n = len(t)
    if n <= maks:
        return t, x
    adim = int(np.ceil(n / maks))
    return t[::adim], x[::adim]


def pencerele(t, x, pencere):
    if pencere is None:
        return t, x
    m = t < pencere
    return t[m], x[m]


def ciz(stip, t, x, t_n, x_n, x_q, bit, fs, fmax, pencere=None):
    t, x = pencerele(t, x, pencere)
    if pencere is not None:
        m_n = t_n < pencere
        t_n, x_n, x_q = t_n[m_n], x_n[m_n], x_q[m_n]
    tp, xp = seyrelt(t, x)
    fig, eksen = plt.subplots(2, 2, figsize=(12, 7))
    eksen[0, 0].plot(tp, xp, "r-")
    eksen[0, 0].set_title("Orijinal Surekli Sinyal x(t)")
    eksen[0, 0].set_xlabel("Zaman (s)")
    eksen[0, 0].set_ylabel("Genlik")
    eksen[0, 0].grid(True)

    eksen[0, 1].plot(tp, xp, "r-", alpha=0.3)
    eksen[0, 1].stem(t_n, x_n, linefmt="b-", markerfmt="bo", basefmt="k-")
    eksen[0, 1].set_title("Orneklendi Sinyal x[n]  (Ts = %.6f s)" % (1 / fs))
    eksen[0, 1].set_xlabel("Zaman (s)")
    eksen[0, 1].set_ylabel("Genlik")
    eksen[0, 1].grid(True)

    eksen[1, 0].plot(tp, xp, "r-", alpha=0.3)
    eksen[1, 0].step(t_n, x_q, where="post", color="g")
    eksen[1, 0].set_title("Nicemlenmis Sinyal (%d bit)" % bit)
    eksen[1, 0].set_xlabel("Zaman (s)")
    eksen[1, 0].set_ylabel("Genlik")
    eksen[1, 0].grid(True)

    hata = x_n - x_q
    eksen[1, 1].plot(tp, xp, "r-", alpha=0.3, label="Orijinal")
    eksen[1, 1].step(t_n, x_q, where="post", color="g", label="Nicemlenmis")
    eksen[1, 1].set_title("Karsilastirma ve Hata Sinyali")
    eksen[1, 1].set_xlabel("Zaman (s)")
    eksen[1, 1].legend(loc="upper right")
    eksen[1, 1].grid(True)
    eksen2 = eksen[1, 1].twinx()
    eksen2.plot(t_n, hata, "m-", alpha=0.6, label="Hata")
    eksen2.set_ylabel("Hata", color="m")

    fig.tight_layout()
    return fig


def bit_paneli(x, t, fs, nicem_mod, fs_kaynak, tam_olcek, pencere=None, bitler=(1, 2, 4, 8)):
    t_n, x_n = sc.ornekle(x, fs, fs_kaynak)
    t, x = pencerele(t, x, pencere)
    t_n, x_n = pencerele(t_n, x_n, pencere)
    tp, xp = seyrelt(t, x)
    fig, eksen = plt.subplots(1, len(bitler), figsize=(14, 3.5))
    for i, b in enumerate(bitler):
        x_q = sc.nicemle(x_n, b, nicem_mod, tam_olcek)
        eksen[i].plot(tp, xp, "r-", alpha=0.3)
        eksen[i].step(t_n, x_q, where="post", color="g")
        eksen[i].set_title("%d bit" % b)
        eksen[i].grid(True)
    fig.tight_layout()
    return fig


st.sidebar.header("Parametreler")
kaynak = st.sidebar.radio(
    "Sinyal Kaynagi",
    ["Sentetik", "Cok Tonlu", "WAV Dosyasi"],
)

bit = st.sidebar.slider("Nicemleme Bit Sayisi", 1, 16, 8)
nicem_mod = st.sidebar.selectbox("Nicemleme Tipi", ["yuvarlat", "yukari", "asagi"])

fs = 0.0
fmax = 0.0
fs_kaynak = sc.FS_YUKSEK
tam_olcek = 1.0
anti_alias = False
yeniden = False
x = None
t = None
wav_fs = None
wav_adi = None

if kaynak == "Sentetik":
    dalga = st.sidebar.selectbox("Dalga Sekli", ["Sinus", "Kare", "Testere"])
    f = st.sidebar.slider("Frekans (Hz)", 10, 2000, 100)
    A = st.sidebar.slider("Genlik", 0.1, 1.0, 1.0, 0.1)
    faz = st.sidebar.slider("Faz (derece)", 0, 360, 0)
    sure = st.sidebar.slider("Sure (s)", 0.01, 0.1, 0.02, 0.005)
    fs = st.sidebar.slider("Ornekleme Frekansi fs (Hz)", 100, 20000, 2000, 100)
    if dalga == "Sinus":
        t, x = sc.sinus_uret(f, A, faz, sure)
    elif dalga == "Kare":
        t, x = sc.kare_uret(f, A, sure)
    else:
        t, x = sc.testere_uret(f, A, sure)
    fmax = sc.fmax_hesapla("Sentetik", f)
    tam_olcek = A

elif kaynak == "Cok Tonlu":
    freklanslar = [50, 120, 300]
    genlikler = [1.0, 0.5, 0.25]
    st.sidebar.write("Frekanslar (Hz):", freklanslar)
    sure = st.sidebar.slider("Sure (s)", 0.01, 0.1, 0.02, 0.005)
    fs = st.sidebar.slider("Ornekleme Frekansi fs (Hz)", 100, 20000, 4000, 100)
    t, x = sc.carpanli_sinyal(freklanslar, genlikler, sure)
    fmax = sc.fmax_hesapla("Cok Tonlu", 0, freklanslar)
    tam_olcek = sum(genlikler)

else:
    dosya = st.sidebar.file_uploader("WAV Dosyasi Yukle", type=["wav"])
    if dosya is not None:
        wav_fs, x = sc.wav_yukle(dosya)
        wav_adi = dosya.name
        fs_kaynak = wav_fs
        fs_kullan = st.sidebar.checkbox("Yeniden Ornekle", value=False)
        yeniden = fs_kullan
        anti_alias = st.sidebar.checkbox(
            "Anti-aliasing filtresi uygula",
            value=False,
            disabled=not fs_kullan,
        )
        fs = st.sidebar.slider(
            "Ornekleme Frekansi fs (Hz)",
            100, max(20000, wav_fs), wav_fs, 100,
            disabled=not fs_kullan,
        )
        if not fs_kullan:
            fs = wav_fs
        fmax = sc.fmax_icerik(x, wav_fs)
        tam_olcek = float(np.max(np.abs(x))) if len(x) else 1.0
        t = np.arange(len(x)) / wav_fs


st.sidebar.divider()
if st.sidebar.button("Hazır Rapor Görsellerini Üret (sabit örnekler)"):
    with st.spinner("Rapor grafikleri uretiliyor..."):
        rapor_grafikleri.tumunu_uret()
    st.sidebar.success("Rapor grafikleri rapor_kaynak/ klasorune kaydedildi.")
kaydet_guncel = st.sidebar.button("Mevcut Grafiği Rapor Klasörüne Kaydet")

st.header("Dönüşüm")

if x is not None:
    pencere = 0.02 if kaynak == "WAV Dosyasi" else None
    if kaynak == "WAV Dosyasi" and fs != fs_kaynak:
        t_n, x_n = sc.ornekle_wav(x, fs_kaynak, fs, anti_alias)
    else:
        t_n, x_n = sc.ornekle(x, fs, fs_kaynak)
    x_q = sc.nicemle(x_n, bit, nicem_mod, tam_olcek)
    snr_olcu = sc.snr_hesapla(x_n, x_q)
    snr_teorik = sc.teorik_snr(bit)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ornek Sayisi", len(x_n))
    c2.metric("fs (Hz)", "%.0f" % fs)
    c3.metric("Ts (s)", "%.6f" % (1 / fs))
    c4.metric("Seviye Sayisi (2^bit)", 2 ** bit)

    if kaynak == "WAV Dosyasi" and not yeniden:
        st.info("Orijinal örnekleme hızı: %d Hz" % wav_fs)
    elif sc.nyquist_kontrol(fs, fmax):
        st.success("Nyquist uyumlu: fs (%.0f Hz) > 2*fmax (%.0f Hz)" % (fs, 2 * fmax))
    else:
        st.error("ALIASING: fs (%.0f Hz) <= 2*fmax (%.0f Hz) - sinyal bozuluyor" % (fs, 2 * fmax))

    s1, s2 = st.columns(2)
    s1.metric("Nicemleme SNR (olculen, dB)", "%.2f" % snr_olcu)
    s2.metric("Teorik SNR (6.02*bit + 1.76, dB)", "%.2f" % snr_teorik)
    st.info(
        "SNR teorisi 6.02*bit + 1.76 dB SADECE tam genlikli (full-scale) sinüs sinyali icin gecerlidir. "
        "Kare, testere, cok tonlu veya WAV sinyallerinde teorik deger yalnizca karsilastirma amaclidir."
    )

    if kaynak == "Sentetik" and dalga in ("Kare", "Testere"):
        st.warning(
            "Kare/testere dalgalarin harmonikleri (f, 3f, 5f...) oldugunden, fs > 2f kosulu "
            "saglansa bile ust harmonikler aliasing yapabilir. Nyquist uyari kutusu yalnizca "
            "taban frekansi (f) baz alinarak hesaplanir."
        )

    if bit <= 3 or nicem_mod != "yuvarlat":
        st.warning(
            "Teorik SNR (6.02*bit + 1.76) yalnizca yuvarlat (round) modu ve yeterli bit "
            "derinligi (>=4 bit) icin gecerlidir. Asagi/yukari nicemleme modlarinda ve dusuk "
            "bit sayilarinda (<4) olculen SNR teorik degerden belirgin sapis gosterecektir."
        )

    fig = ciz(kaynak, t, x, t_n, x_n, x_q, bit, fs, fmax, pencere)
    st.pyplot(fig)
    plt.close(fig)
    st.download_button(
        "Grafigi Indir",
        grafik_bytes(fig),
        file_name="donusum.png",
        mime="image/png",
    )

    fig_b = bit_paneli(x, t, fs, nicem_mod, fs_kaynak, tam_olcek, pencere)
    st.subheader("Bit Derinligi Karsilastirmasi")
    st.pyplot(fig_b)
    plt.close(fig_b)

    if kaydet_guncel:
        if kaynak == "Sentetik":
            taban = "%s_f%d" % (dalga.lower(), f)
        elif kaynak == "Cok Tonlu":
            taban = "coktonlu_f%d" % int(fmax)
        else:
            kok = os.path.splitext(wav_adi)[0]
            temiz = "".join(
                c if (c.isascii() and (c.isalnum() or c in "-_")) else "_" for c in kok
            )
            taban = "wav_" + (temiz.strip("_") or "dosya")
        ad = "%s_fs%d_%dbit" % (taban, int(fs), bit)
        yol_ana = os.path.join(rapor_grafikleri.KAYNAK, ad + ".png")
        yol_panel = os.path.join(rapor_grafikleri.KAYNAK, ad + "_panel.png")
        fig.savefig(yol_ana, dpi=150, bbox_inches="tight")
        fig_b.savefig(yol_panel, dpi=150, bbox_inches="tight")
        st.sidebar.success(
            "Kaydedildi: %s | %s" % (os.path.basename(yol_ana), os.path.basename(yol_panel))
        )

    if kaynak == "WAV Dosyasi" and x is not None:
        st.subheader("Ses Dinleme")
        a1, a2, a3 = st.columns(3)
        x_n_g, fs_n_g = sc.genislet(x_n, int(fs), 44100)
        x_q_g, fs_q_g = sc.genislet(x_q, int(fs), 44100)
        a1.audio(sc.ses_dizisi(x), format="audio/wav", sample_rate=int(wav_fs))
        a2.audio(sc.ses_dizisi(x_n_g), format="audio/wav", sample_rate=int(fs_n_g))
        a3.audio(sc.ses_dizisi(x_q_g), format="audio/wav", sample_rate=int(fs_q_g))
        st.caption("1) Orijinal  2) Orneklenmis (44100 Hz'e tekrarlanmis)  3) Nicemlenmis")

else:
    if kaydet_guncel:
        st.sidebar.warning("Kaydedilecek grafik yok - once bir sinyal kaynagi secin.")
    st.info("Bir sinyal kaynagi secin - sonuclar parametrelerle anlik olarak guncellenir.")
