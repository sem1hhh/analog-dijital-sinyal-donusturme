import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import sinyal_core as sc

KAYNAK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rapor_kaynak")
os.makedirs(KAYNAK, exist_ok=True)


def kaydet(fig, ad):
    fig.savefig(os.path.join(KAYNAK, ad), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("kaydedildi:", ad)


def fig1():
    t, x = sc.sinus_uret(100, 1.0, sure=0.03)
    t_n, x_n = sc.ornekle(x, 2000)
    fig, eksen = plt.subplots(figsize=(10, 4))
    eksen.plot(t, x, "r-", label="Orijinal surekli sinyal x(t)")
    eksen.stem(t_n, x_n, linefmt="b-", markerfmt="bo", basefmt="k-", label="Orneklendi x[n]")
    eksen.set_title("Orijinal ve Orneklendi Sinyal (fs = 2000 Hz, f = 100 Hz)")
    eksen.set_xlabel("Zaman (s)")
    eksen.set_ylabel("Genlik")
    eksen.legend()
    eksen.grid(True)
    kaydet(fig, "fig1_orijinal_vs_orneklendi.png")


def fig2():
    t, x = sc.sinus_uret(100, 1.0, sure=0.03)
    t_n, x_n = sc.ornekle(x, 2000)
    fig, eksen = plt.subplots(2, 2, figsize=(12, 6))
    for i, b in enumerate([1, 2, 4, 8]):
        x_q = sc.nicemle(x_n, b, tam_olcek=1.0)
        ax = eksen[i // 2, i % 2]
        ax.plot(t, x, "r-", alpha=0.3, label="Orijinal")
        ax.step(t_n, x_q, where="post", color="g", label="Nicemlenmis")
        ax.set_title("%d bit (%d seviye)" % (b, 2 ** b))
        ax.grid(True)
        ax.legend(loc="upper right")
    fig.tight_layout()
    kaydet(fig, "fig2_nicemleme_farkli_bitler.png")


def fig3():
    f = 500
    fs = 800
    alias = abs(fs - f)
    t, x = sc.sinus_uret(f, 1.0, sure=0.02)
    t_n, x_n = sc.ornekle(x, fs)
    fig, eksen = plt.subplots(figsize=(10, 4))
    eksen.plot(t, x, "r-", label="Orijinal %d Hz" % f)
    eksen.stem(t_n, x_n, linefmt="b-", markerfmt="bo", basefmt="k-",
               label="Orneklendi x[n] (fs = %d Hz)" % fs)
    eksen.plot(t, np.sin(2 * np.pi * alias * t + np.pi), "k--",
               label="Görünen (alias) frekans: %d Hz" % alias)
    eksen.set_title("ALIASING: fs = %d Hz < 2*fmax = %d Hz" % (fs, 2 * f))
    eksen.set_xlabel("Zaman (s)")
    eksen.set_ylabel("Genlik")
    eksen.legend()
    eksen.grid(True)
    kaydet(fig, "fig3_aliasing.png")


def fig4():
    fig, eksen = plt.subplots(2, 2, figsize=(12, 6))
    t_k, x_k = sc.kare_uret(100, 1.0, sure=0.03)
    t_n, x_kn = sc.ornekle(x_k, 2000)
    x_kq = sc.nicemle(x_kn, 6, tam_olcek=1.0)
    eksen[0, 0].plot(t_k, x_k, "r-", alpha=0.4)
    eksen[0, 0].step(t_n, x_kq, where="post", color="g")
    eksen[0, 0].set_title("Kare Dalga - 6 bit Nicemleme")
    eksen[0, 0].grid(True)

    t_t, x_t = sc.testere_uret(100, 1.0, sure=0.03)
    t_n2, x_tn = sc.ornekle(x_t, 2000)
    x_tq = sc.nicemle(x_tn, 6, tam_olcek=1.0)
    eksen[0, 1].plot(t_t, x_t, "r-", alpha=0.4)
    eksen[0, 1].step(t_n2, x_tq, where="post", color="g")
    eksen[0, 1].set_title("Testere Dalga - 6 bit Nicemleme")
    eksen[0, 1].grid(True)

    eksen[1, 0].step(t_n, sc.nicemle(x_kn, 2, tam_olcek=1.0), where="post", color="g")
    eksen[1, 0].plot(t_k, x_k, "r-", alpha=0.3)
    eksen[1, 0].set_title("Kare dalga nicemlemeden etkilenmez (yalnızca 2 seviye)")
    eksen[1, 0].grid(True)

    eksen[1, 1].step(t_n2, sc.nicemle(x_tn, 2, tam_olcek=1.0), where="post", color="g")
    eksen[1, 1].plot(t_t, x_t, "r-", alpha=0.3)
    eksen[1, 1].set_title("Testere - 2 bit (ciddi bozulma)")
    eksen[1, 1].grid(True)
    fig.tight_layout()
    kaydet(fig, "fig4_kare_testere.png")


def fig5():
    f = 440
    fs = 600
    sure = 0.1
    t, x = sc.sinus_uret(f, 0.7, sure=sure)
    t_n, x_n = sc.ornekle(x, fs)
    x_q = sc.nicemle(x_n, 4, tam_olcek=0.7)
    fig, eksen = plt.subplots(figsize=(10, 4))
    eksen.plot(t, x, "r-", alpha=0.4, label="Orijinal %d Hz ton" % f)
    eksen.step(t_n, x_q, where="post", color="g",
               label="Orneklendi (fs = %d Hz < 2*%d = %d Hz) + 4 bit" % (fs, f, 2 * f))
    eksen.set_title("Sentetik ton (WAV yerine): fs = %d Hz < 2*f = %d Hz -> aliasing" % (fs, 2 * f))
    eksen.set_xlabel("Zaman (s)")
    eksen.set_ylabel("Genlik")
    eksen.legend()
    eksen.grid(True)
    kaydet(fig, "fig5_wav_ornekleme.png")


def fig_akis():
    adimlar = [
        "(1) Surekli sinyal\nx(t) uret",
        "(2) Ornekleme\nx[n] = x(n*Ts)",
        "(3) Nicemleme\n2^b seviye",
        "(4) Cizdir + SNR/Nyquist\nrapor gorselleri",
    ]
    fig, eksen = plt.subplots(figsize=(13, 2.2))
    eksen.set_xlim(0, 13)
    eksen.set_ylim(0, 2.2)
    eksen.axis("off")
    en = 2.7
    yuk = 1.1
    for i, m in enumerate(adimlar):
        x0 = 0.4 + i * 3.1
        kutu = plt.Rectangle((x0, 0.55), en, yuk, fill=False, lw=1.6, ec="navy")
        eksen.add_patch(kutu)
        eksen.text(x0 + en / 2, 0.55 + yuk / 2, m, ha="center", va="center", fontsize=10)
        if i < len(adimlar) - 1:
            eksen.annotate(
                "", xy=(x0 + en + 0.4, 1.1), xytext=(x0 + en, 1.1),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="navy"),
            )
    kaydet(fig, "fig_akis.png")


def tumunu_uret():
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig_akis()
    print("Tum rapor grafikleri uretildi ->", KAYNAK)


if __name__ == "__main__":
    tumunu_uret()
