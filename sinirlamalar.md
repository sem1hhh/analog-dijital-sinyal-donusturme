# Bilinen Sınırlamalar

Bu dosya, projenin **şu anki sürümünde** bilinen sınırları kullanıcılara bildirmek amacıyla hazırlanmıştır. Çoğu madde bilinçli bir tasarım tercihidir; hata olarak değerlendirilmemelidir. Projenin nasıl çalıştırıldığı ve özellikleri için `README.md`'ye bakınız.

Güncelleme: 22 Ekim 2026

---

## Sinyal işleme ve nicemleme

- **Örnekleme penceresi (WAV):** WAV kaynağında grafikler yalnızca ilk **20 ms**'yi gösterir (orijinal, örneklenmiş ve nicemlenmiş için aynı pencere). Uzun vadeli davranış grafikte görünmez; ses dinleme her zaman tam dosyayı kullanır.
- **Nyquist kontrolünün kapsamı:**
  - WAV'da "Yeniden Ornekle" kapalıyken kontrol yapılmaz; yalnızca *Orijinal örnekleme hızı: X Hz* bilgisi gösterilir.
  - Kare ve testere dalgalarında kontrol yalnızca **taban frekansa (f)** göre yapılır: fs > 2f koşulu sağlansa bile üst harmonikler (3f, 5f, …) aliasing yapabilir.
- **Teorik SNR:** `6.02*bit + 1.76` formülü **yalnızca tam genlikli sinüs + yuvarlat modu + ≥4 bit** için geçerlidir. Kare, testere, çok tonlu ve WAV sinyallerinde; ≤3 bitte; yukarı/aşağı nicemleme modlarında ölçülen SNR teorikten belirgin şekilde sapar (arayüzde uyarı gösterilir).
- **Sabit tam ölçek nicemleme:** `nicemle()` sinyali kendi genliğine göre normalize etmez. Tam ölçek: sentetikte genlik `A`, çok tonluda `sum(genlikler)`, WAV'da `max(|x|)`. Bu yüzden küçük genlikli bir sinyalde ölçülen SNR beklentinin altında çıkar.
- **Kuantizasyon adımı:** Adım `2*FS/(2^b - 1)` olarak hesaplanır; teorik formülün varsaydığı `2*FS/2^b` yerine kullanıldığı için ölçülen SNR teorik değere göre ~0,1–0,3 dB sapabilir.
- **Örnekleme indeksleri yuvarlanır:** `round(n * fs_kaynak / fs)` → 100 kHz kaynakta en fazla ~5 µs zaman hatası. Ayrıca `floor(süre / Ts)` nedeniyle son eksik periyot atılır (örn. 0,02 s / 2000 Hz → 41 yerine 40 örnek).

## WAV ve ses

- **Mono'ya indirgeme:** Stereo WAV dosyaları kanallar ortalanarak mono'ya çevrilir; ters fazlı bileşenler birbirini götürebilir.
- **Anti-aliasing filtresi isteğe bağlıdır:** Varsayılan **filtresiz** örneklemedir (aliasing duyulur — amaç budur). Onaylanırsa `resample_poly` kullanılır; `up/down` değerleri fs hedef ve fs kaynak gcd ile sadeleştirilerek verilir.
- **44100 Hz'e genişletme (st.audio öncesi):** Her örnek `round(44100/fs)` kez tekrarlanır (zero-order hold / interpolasyonsuz):
  - `fs ≥ 44100` olduğunda genişletme **yapılmaz**,
  - sonuç her zaman tam 44100 olmayabilir (ör. 8000 Hz → 48000 Hz),
  - örnek hızı doğru verildiği için sesin periyodu bozulmaz; ancak interpolasyon olmadığı için üst bantlarda görüntüleme (imaging) artefaktları oluşabilir.
- **`fmax` tahmini:** İçerik bant genişliği FFT ile ve **−60 dB eşiğiyle** bulunur. Bu eşik sezgiseldir; çok zayıf bileşenli veya gürültülü sinyallerde yanıltıcı olabilir.

## Performans

- **Önbellek (cache) kullanılmıyor:** `st.cache_data` bilinçli olarak kaldırıldı (matplotlib figür nesneleri hash'lenemiyor). Her parametre değişikliğinde tüm işlem yeniden çalışır:
  - uzun WAV'larda `fmax` FFT'si ve üç ses oynatıcısının yeniden kodlanması dahil,
  - birkaç dakikalık dosyalarda algılanabilir gecikme olabilir.

