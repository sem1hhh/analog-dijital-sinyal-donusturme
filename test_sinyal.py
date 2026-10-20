import numpy as np
import pytest
import sinyal_core as sc


def test_900hz_sinyal_1000hz_orneklemede_100hz_gorunur():
    f = 900.0
    fs = 1000.0
    _, x = sc.sinus_uret(f, 1.0, sure=0.1)
    _, x_n = sc.ornekle(x, fs, sc.FS_YUKSEK)
    genlikler = np.abs(np.fft.rfft(x_n))
    frekanslar = np.fft.rfftfreq(len(x_n), 1.0 / fs)
    gorunen_frekans = frekanslar[np.argmax(genlikler)]
    assert abs(gorunen_frekans - 100.0) <= 2.0


def test_3_bit_8_seviye_uretir():
    x = np.linspace(-1.0, 1.0, 1000)
    x_q = sc.nicemle(x, 3, "yuvarlat", tam_olcek=1.0)
    assert len(np.unique(x_q)) == 8


@pytest.mark.parametrize("bit", [4, 6, 8, 10, 12])
def test_tam_genlikli_sinus_snr_teorik_formule_yakin(bit):
    _, x = sc.sinus_uret(440.0, 1.0, sure=1.0)
    _, x_n = sc.ornekle(x, 44100, sc.FS_YUKSEK)
    x_q = sc.nicemle(x_n, bit, "yuvarlat", tam_olcek=1.0)
    snr = sc.snr_hesapla(x_n, x_q)
    assert abs(snr - sc.teorik_snr(bit)) <= 1.0


@pytest.mark.parametrize("bit", [4, 5, 6, 8, 9, 10])
def test_her_ek_bit_snr_yaklasik_6db_artirir(bit):
    _, x = sc.sinus_uret(440.0, 1.0, sure=1.0)
    _, x_n = sc.ornekle(x, 44100, sc.FS_YUKSEK)
    snr_dusuk = sc.snr_hesapla(x_n, sc.nicemle(x_n, bit, "yuvarlat", tam_olcek=1.0))
    snr_yuksek = sc.snr_hesapla(x_n, sc.nicemle(x_n, bit + 1, "yuvarlat", tam_olcek=1.0))
    artis = snr_yuksek - snr_dusuk
    assert 5.0 <= artis <= 7.0


def test_fs_2f_den_kucukse_nyquist_uyarisi_true():
    f = 900.0
    fs = 1000.0
    uyari = not sc.nyquist_kontrol(fs, f)
    assert uyari is True


def test_nyquist_kosulu_saglaninca_uyari_false():
    f = 900.0
    fs = 2000.0
    uyari = not sc.nyquist_kontrol(fs, f)
    assert uyari is False
