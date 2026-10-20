import numpy as np
import math
from scipy.io import wavfile
from scipy.signal import resample_poly

FS_YUKSEK = 100_000


def sinus_uret(f, A, faz=0.0, sure=0.02, fs_yuksek=FS_YUKSEK):
    t = np.arange(0, sure, 1 / fs_yuksek)
    x = A * np.sin(2 * np.pi * f * t + np.deg2rad(faz))
    return t, x


def kare_uret(f, A, sure=0.02, fs_yuksek=FS_YUKSEK):
    t = np.arange(0, sure, 1 / fs_yuksek)
    x = A * np.where(np.sin(2 * np.pi * f * t) < 0, -1.0, 1.0)
    return t, x


def testere_uret(f, A, sure=0.02, fs_yuksek=FS_YUKSEK):
    t = np.arange(0, sure, 1 / fs_yuksek)
    periyot = 1 / f
    x = A * (2 * ((t / periyot) % 1.0) - 1)
    return t, x


def carpanli_sinyal(freklanslar, genlikler, sure=0.02, fs_yuksek=FS_YUKSEK):
    t = np.arange(0, sure, 1 / fs_yuksek)
    x = np.zeros_like(t)
    for f, A in zip(freklanslar, genlikler):
        x += A * np.sin(2 * np.pi * f * t)
    return t, x


def fmax_hesapla(tip, frekans, freklanslar=None):
    if tip == "Cok Tonlu" and freklanslar:
        return float(np.max(freklanslar))
    return float(frekans)


def fmax_icerik(x, fs, esik_db=-60.0, maks=200_000):
    y = x[:maks] if len(x) > maks else x
    n = len(y)
    if n < 4:
        return fs / 2.0
    X = np.fft.rfft(y)
    f = np.fft.rfftfreq(n, 1.0 / fs)
    mag = 20.0 * np.log10(np.abs(X) + 1e-12)
    mag -= np.max(mag)
    gecen = np.where(mag > esik_db)[0]
    if len(gecen) == 0:
        return fs / 2.0
    return float(f[gecen[-1]])


def wav_yukle(dosya, mono=True):
    fs, x = wavfile.read(dosya)
    if x.dtype.kind in "iu":
        bilgi = np.iinfo(x.dtype)
        x = x.astype(np.float64)
        if bilgi.min == 0:
            x = (x - 128.0) / 128.0
        else:
            x = x / float(bilgi.max)
    elif x.dtype.kind == "f":
        x = x.astype(np.float64)
    if mono and x.ndim > 1:
        x = x.mean(axis=1)
    return fs, x


def ornekle(x, fs, fs_kaynak=FS_YUKSEK):
    ts = 1.0 / fs
    sure = len(x) / fs_kaynak
    n = int(np.floor(sure / ts))
    idx = np.round(np.arange(n) * fs_kaynak / fs).astype(int)
    idx = idx[idx < len(x)]
    x_n = x[idx]
    t_n = idx / fs_kaynak
    return t_n, x_n


def ornekle_wav(x, fs_orj, fs_hedef, anti_alias=False):
    if anti_alias:
        b = math.gcd(int(round(fs_hedef)), int(round(fs_orj)))
        up = int(round(fs_hedef)) // b
        down = int(round(fs_orj)) // b
        x_n = resample_poly(x, up, down)
        t_n = np.arange(len(x_n)) / fs_hedef
        return t_n, x_n
    return ornekle(x, fs_hedef, fs_kaynak=fs_orj)


def genislet(x_n, fs, hedef=44100):
    oran = hedef / fs
    faktor = max(1, int(round(oran)))
    x_g = np.repeat(x_n, faktor)
    return x_g, fs * faktor


def nicemle(x, bit, mod="yuvarlat", tam_olcek=1.0):
    seviye = 2 ** bit
    adim = 2.0 * tam_olcek / (seviye - 1) if seviye > 1 else 2.0 * tam_olcek
    if mod == "yukari":
        q = np.ceil((x + tam_olcek) / adim) * adim - tam_olcek
    elif mod == "asagi":
        q = np.floor((x + tam_olcek) / adim) * adim - tam_olcek
    else:
        q = np.round((x + tam_olcek) / adim) * adim - tam_olcek
    return np.clip(q, -tam_olcek, tam_olcek)


def snr_hesapla(x_orj, x_nicem):
    n = min(len(x_orj), len(x_nicem))
    hata = x_orj[:n] - x_nicem[:n]
    p_sinyal = np.mean(x_orj[:n] ** 2)
    p_hata = np.mean(hata ** 2)
    if p_hata <= 0:
        return float("inf")
    return 10 * np.log10(p_sinyal / p_hata)


def teorik_snr(bit):
    return 6.02 * bit + 1.76


def nyquist_kontrol(fs, fmax):
    return fs > 2 * fmax


def ses_dizisi(x, bit=16):
    x = np.asarray(x, dtype=np.float64)
    x = np.clip(x, -1.0, 1.0)
    n = (2 ** (bit - 1)) - 1
    return (x * n).astype(np.int16)
