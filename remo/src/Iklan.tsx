import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';

export type Kata = {w: string; mulai: number; durasi: number}; // detik
export type Props = {
  kode: string; judul: string; harga: string; durasi: number;
  artis: string; fotos: string[]; audio: string; musik: string;
  artisDetik: number; fotoDetik: number; kata: Kata[];
  terjual?: string; // mis. "378RB+"
  artisPotong?: string; // PNG artis tanpa latar (kecil, goyang di atas foto produk)
  produkKecil?: string; // foto produk kecil yang goyang di atas subtitle selama gambar artis tampil
  isiSisa?: boolean; // true = sisa durasi diisi foto produk (foto terakhir menyambung sampai akhir), bukan artis lagi
};
const src = (s: string) => (s.startsWith('http') ? s : staticFile(s));
const FONT = 'sans-serif';
const THUMB_DETIK = 1.5; // detik awal yang berupa thumbnail (hanya baris tanpa gambar AI sendiri)

// Foto bergerak (Ken Burns) + masuk dengan "pop". pelan = gambar artis: zoom-in pelan & sedikit saja.
const Foto: React.FC<{u: string; dur: number; i: number; pelan?: boolean}> = ({u, dur, i, pelan}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const p = f / dur;
  const arah = i % 4;
  const zoom = pelan ? interpolate(p, [0, 1], [1.0, 1.07])
    : arah === 1 ? interpolate(p, [0, 1], [1.22, 1.02]) : interpolate(p, [0, 1], [1.02, 1.2]);
  const geser = pelan ? 0 : arah === 2 ? interpolate(p, [0, 1], [-40, 40]) : arah === 3 ? interpolate(p, [0, 1], [40, -40]) : 0;
  const masuk = spring({frame: f, fps, config: {damping: 14, stiffness: 140}, durationInFrames: 14});
  const kelip = interpolate(f, [0, 3], [0.6, 0], {extrapolateRight: 'clamp'}); // kilatan tipis tiap pindah foto
  return (
    <AbsoluteFill style={{backgroundColor: '#111'}}>
      <AbsoluteFill style={{transform: `scale(${pelan ? 1 : 0.96 + 0.04 * masuk})`, overflow: 'hidden'}}>
        <Img src={src(u)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom}) translateX(${geser}px)`}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: '#fff', opacity: pelan ? 0 : kelip}} />
    </AbsoluteFill>
  );
};

const Judul: React.FC<{judul: string; harga: string}> = ({judul, harga}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const a = spring({frame: f - 4, fps, config: {damping: 10, stiffness: 160}});
  const b = spring({frame: f - 14, fps, config: {damping: 8, stiffness: 150}});
  const denyut = 1 + 0.04 * Math.sin(f / 5);
  return (
    <>
      <div style={{position: 'absolute', top: 170, left: 0, right: 0, textAlign: 'center', transform: `translateY(${(1 - a) * -120}px) scale(${a})`}}>
        <span style={{background: 'rgba(0,0,0,.6)', color: '#fff', fontSize: 50, fontWeight: 800, padding: '16px 30px', borderRadius: 18, fontFamily: FONT}}>{judul}</span>
      </div>
      {harga && (
        <div style={{position: 'absolute', top: 300, left: 0, right: 0, textAlign: 'center', transform: `scale(${b * denyut}) rotate(${(1 - b) * -8}deg)`}}>
          <span style={{background: '#FFD400', color: '#C8102E', fontSize: 84, fontWeight: 900, padding: '10px 36px', borderRadius: 24, fontFamily: FONT, boxShadow: '0 8px 0 #b38f00'}}>{harga}</span>
        </div>
      )}
    </>
  );
};

// Subtitle karaoke: 4 kata per layar, kata yang sedang diucapkan menyala kuning & membesar
const Subtitle: React.FC<{kata: Kata[]}> = ({kata}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const t = f / fps;
  if (!kata.length) return null;
  let idx = kata.findIndex((k) => t >= k.mulai && t < k.mulai + k.durasi);
  if (idx < 0) idx = Math.max(0, kata.findIndex((k) => k.mulai > t) - 1);
  const gStart = Math.floor(idx / 4) * 4;
  const grup = kata.slice(gStart, gStart + 4);
  if (t < kata[gStart].mulai - 0.2 || t > kata[Math.min(gStart + 3, kata.length - 1)].mulai + kata[Math.min(gStart + 3, kata.length - 1)].durasi + 0.3) return null;
  return (
    <div style={{position: 'absolute', bottom: 330, left: 50, right: 50, textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 60, lineHeight: 1.18}}>
      {grup.map((k, j) => {
        const aktif = gStart + j === idx;
        return (
          <span key={j} style={{display: 'inline-block', margin: '0 12px', color: aktif ? '#FFE600' : '#fff',
            transform: `scale(${aktif ? 1.12 : 1})`, textShadow: '0 0 8px #000, 0 6px 0 #000, 4px 4px 0 #000, -4px 4px 0 #000'}}>{k.w}</span>
        );
      })}
    </div>
  );
};

const Ajakan: React.FC<{kode: string}> = ({kode}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const m = spring({frame: f, fps, config: {damping: 9, stiffness: 120}});
  const goyang = Math.sin(f / 4) * 3;
  return (
    <div style={{position: 'absolute', bottom: 170, left: 0, right: 0, textAlign: 'center', transform: `scale(${m}) rotate(${goyang}deg)`}}>
      <div style={{display: 'inline-block', background: '#EE4D2D', color: '#fff', fontFamily: FONT, fontWeight: 900, fontSize: 54, padding: '20px 40px', borderRadius: 26, boxShadow: '0 10px 0 #9c2d16'}}>
        KODE {kode} • CEK LINK DI BIO 👆
      </div>
    </div>
  );
};

// Badge jumlah terjual
const Terjual: React.FC<{t: string}> = ({t}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const m = spring({frame: f - 22, fps, config: {damping: 9, stiffness: 140}});
  return (
    <div style={{position: 'absolute', top: 430, left: 0, right: 0, textAlign: 'center', transform: `scale(${m * (1 + 0.025 * Math.sin(f / 6))})`}}>
      <span style={{background: '#EE4D2D', color: '#fff', fontSize: 52, fontWeight: 900, padding: '10px 32px', borderRadius: 40, fontFamily: FONT, boxShadow: '0 6px 0 #9c2d16'}}>🔥 {t} TERJUAL</span>
    </div>
  );
};

// Artis kecil di sudut kanan bawah: SATU komponen untuk ketiga foto produk,
// jadi goyangannya mulus dan tidak putus saat foto berganti.
const ArtisKecil: React.FC<{u: string}> = ({u}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const masuk = spring({frame: f, fps, config: {damping: 12, stiffness: 90}});
  const goyang = Math.sin(f / 9) * 3.5;
  const naik = Math.sin(f / 9 + 1.2) * -12;
  return (
    <div style={{position: 'absolute', right: 8, bottom: 0, width: 470, height: 720, transformOrigin: '50% 100%',
      transform: `translateY(${(1 - masuk) * 300 + naik}px) rotate(${goyang}deg) scale(${0.85 + 0.15 * masuk})`}}>
      <Img src={src(u)} style={{width: '100%', height: '100%', objectFit: 'contain', objectPosition: 'bottom right',
        filter: 'drop-shadow(0 10px 14px rgba(0,0,0,.45))'}} />
    </div>
  );
};

// Foto produk kecil (300 px) goyang pelan di tengah, TEPAT DI ATAS subtitle (subtitle mulai ±y=1448,
// foto menempati ±y=1094..1406 + goyangan) dan jauh di atas kotak KODE (±y=1645) serta di bawah badge terjual (±y=540).
const UKURAN_KECIL = 300;
const ProdukKecil: React.FC<{u: string}> = ({u}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const masuk = spring({frame: f, fps, config: {damping: 10, stiffness: 120}});
  const miring = Math.sin(f / 7) * 4.5;
  const geserX = Math.sin(f / 11) * 12;
  const geserY = Math.sin(f / 9 + 1) * 6;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 1085, height: 330, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{transform: `translate(${geserX}px, ${geserY}px) rotate(${miring}deg) scale(${masuk})`, background: '#fff', padding: 6, borderRadius: 18, boxShadow: '0 10px 22px rgba(0,0,0,.5)'}}>
        <Img src={src(u)} style={{width: UKURAN_KECIL, height: UKURAN_KECIL, objectFit: 'cover', borderRadius: 13, display: 'block'}} />
      </div>
    </div>
  );
};

// THUMBNAIL: 1,5 detik pertama. Sudah tampil PENUH di frame 0 (tanpa animasi masuk) supaya jadi cover Reels/Shorts.
// Susunan: atas = pita hook + nama produk besar (di atas kepala artis), tengah = wajah artis dibiarkan terlihat,
// bawah = foto produk besar (kiri) + harga besar (kanan), semuanya di atas teks suara (±y=1448).
const Thumbnail: React.FC<{judul: string; harga: string; terjual?: string; foto: string; total: number}> = ({judul, harga, terjual, foto, total}) => {
  const f = useCurrentFrame();
  const hilang = interpolate(f, [total - 7, total], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const denyut = 1 + 0.025 * Math.sin(f / 3);
  const goyang = Math.sin(f / 4) * 1.5;
  const nama = judul.toUpperCase();
  const stroke = {WebkitTextStroke: '12px #000', paintOrder: 'stroke fill', textShadow: '0 8px 0 #000'} as React.CSSProperties;
  return (
    <AbsoluteFill style={{opacity: hilang}}>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.78) 0%, rgba(0,0,0,.35) 24%, rgba(0,0,0,0) 38%, rgba(0,0,0,0) 52%, rgba(0,0,0,.6) 100%)'}} />
      {/* pita hook */}
      <div style={{position: 'absolute', top: 120, left: 0, right: 0, textAlign: 'center', transform: `rotate(${-3 + goyang}deg) scale(${denyut})`}}>
        <span style={{display: 'inline-block', background: '#EE4D2D', color: '#fff', fontFamily: FONT, fontWeight: 900, fontSize: 70, padding: '12px 40px', borderRadius: 20, boxShadow: '0 10px 0 #9c2d16', border: '6px solid #fff'}}>
          {terjual ? `🔥 ${terjual} TERJUAL!` : '🔥 WAJIB PUNYA!'}
        </span>
      </div>
      {/* nama produk besar */}
      <div style={{position: 'absolute', top: 290, left: 40, right: 40, textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 112, lineHeight: 1.02, color: '#fff', ...stroke}}>
        {nama}
      </div>
      {/* foto produk besar (kiri bawah) */}
      <div style={{position: 'absolute', left: 50, top: 1000, transform: `rotate(${-5 + goyang}deg)`, background: '#fff', padding: 10, borderRadius: 24, boxShadow: '0 14px 30px rgba(0,0,0,.6)'}}>
        <Img src={src(foto)} style={{width: 440, height: 440, objectFit: 'cover', borderRadius: 16, display: 'block'}} />
      </div>
      {/* harga besar (kanan bawah) */}
      {harga ? (
        <div style={{position: 'absolute', left: 540, right: 30, top: 1060, textAlign: 'center', transform: `rotate(${4 - goyang}deg) scale(${denyut})`}}>
          <div style={{background: '#FFD400', border: '8px solid #fff', borderRadius: 36, padding: '16px 10px', boxShadow: '0 14px 0 #b38f00'}}>
            <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 40, color: '#C8102E'}}>CUMA</div>
            <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 92, lineHeight: 1.05, color: '#C8102E'}}>{harga}</div>
          </div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const Iklan: React.FC<Props> = (p) => {
  const {fps} = useVideoConfig();
  const akhir = Math.round(p.durasi * fps);
  // Susunan: foto artis (artisDetik) -> maks 3 foto asli (fotoDetik tiap foto, artis kecil goyang di atasnya)
  // -> sisa waktu foto artis lagi. Kalau isiSisa: sisa waktu diisi foto produk (foto terakhir menyambung
  // sampai akhir) dan tidak ada artis lagi -> tidak ada layar hitam.
  const bagian: {u: string; dur: number; i: number; kecil: boolean; pelan: boolean}[] = [];
  let kecilMulai = -1, kecilDur = 0;
  let sisa = akhir, i = 0;
  const tambah = (u: string, detik: number, kecil: boolean, pelan = false) => {
    const d = Math.min(sisa, Math.round(detik * fps));
    if (d > 0 && u) {
      if (kecil) { if (kecilMulai < 0) kecilMulai = akhir - sisa; kecilDur += d; }
      bagian.push({u, dur: d, i: i++, kecil, pelan}); sisa -= d;
    }
  };
  tambah(p.artis, p.artisDetik, false, true);
  const ff = p.fotos.slice(0, 3);
  ff.forEach((u, n) => tambah(u, p.isiSisa && n === ff.length - 1 ? sisa / fps : p.fotoDetik, !!p.artisPotong));
  if (sisa > 0 && !p.isiSisa) tambah(p.artis, sisa / fps, false, true);
  const produkDur = p.artis ? Math.min(akhir, Math.round(p.artisDetik * fps)) : 0;
  // thumbnail aktif hanya di mode "tanpa gambar AI sendiri" (ada foto produk kecil + gambar artis)
  const thumb = p.produkKecil && produkDur > 0 ? Math.min(produkDur, Math.round(THUMB_DETIK * fps)) : 0;
  let mulai = 0;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {bagian.map((s, n) => { const fr = mulai; mulai += s.dur; return (
        <Sequence key={n} from={fr} durationInFrames={s.dur}>
          <Foto u={s.u} dur={s.dur} i={s.i} pelan={s.pelan} />
        </Sequence>); })}
      {p.artisPotong && kecilDur > 0 ? <Sequence from={kecilMulai} durationInFrames={kecilDur}><ArtisKecil u={p.artisPotong} /></Sequence> : null}
      {thumb > 0 && p.produkKecil ? (
        <Sequence from={0} durationInFrames={thumb}>
          <Thumbnail judul={p.judul} harga={p.harga} terjual={p.terjual} foto={p.produkKecil} total={thumb} />
        </Sequence>
      ) : null}
      {p.produkKecil && produkDur - thumb > 0 ? <Sequence from={thumb} durationInFrames={produkDur - thumb}><ProdukKecil u={p.produkKecil} /></Sequence> : null}
      <Sequence from={thumb}><Judul judul={p.judul} harga={p.harga} /></Sequence>
      {p.terjual ? <Sequence from={thumb}><Terjual t={p.terjual} /></Sequence> : null}
      <Subtitle kata={p.kata} />
      <Sequence from={Math.max(0, akhir - 3 * fps)}><Ajakan kode={p.kode} /></Sequence>
      {p.audio ? <Audio src={src(p.audio)} /> : null}
      {p.musik ? <Audio src={src(p.musik)} volume={(f) => 0.13 * interpolate(f, [0, 30, akhir - 36, akhir], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} loop /> : null}
    </AbsoluteFill>
  );
};
