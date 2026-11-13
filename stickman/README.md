# Video Affiliate Gaya Stickman

Tulis file `cerita/*.json` lalu GitHub otomatis merender `video/<nama>.mp4`
(animasi stickman, foto produk, suara ElevenLabs/edge-tts, subtitle, musik pelan).

Pola affiliate: adegan 1 `tata: penuh`, adegan 2 `tata: atas_produk`, sisanya `tata: goyang`.
Foto produk: `produk_foto` (path atau URL foto Shopee).
Suara ElevenLabs aktif jika secret `ELEVENLABS_API_KEY` dipasang (default voice Raya Fie).
