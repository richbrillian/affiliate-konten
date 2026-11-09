import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const FONT = "Montserrat, 'DejaVu Sans', Arial, sans-serif";
const cl = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const useSp = (d = 0, damping = 12) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - d, fps, config: {damping, stiffness: 160}});
};
const outline = '0 4px 0 #000, 0 -3px 0 #000, 3px 0 0 #000, -3px 0 0 #000, 0 8px 18px rgba(0,0,0,.5)';

const BlokAI: React.FC<{foto: string; label?: string; judul: string; isi?: string; warna: string; thumb?: any}> = ({foto, label, judul, isi, warna, thumb}) => {
  const f = useCurrentFrame();
  const zoom = interpolate(f, [0, 150], [1.04, 1.1]);
  const x = Math.sin(f / 40) * 6;
  const pop = thumb ? 1 : useSp(4);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <AbsoluteFill style={{transform: `translateX(${x}px) scale(${zoom})`}}>
        <Img src={staticFile(foto)} style={{width: 1080, height: 1920, objectFit: 'cover'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(to bottom, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 50%, rgba(0,0,0,.65) 100%)'}} />
      {thumb && (
        <div style={{position: 'absolute', top: 170, left: 50, right: 50, textAlign: 'center', fontFamily: FONT, fontWeight: 900}}>
          <div style={{fontSize: 122, whiteSpace: 'nowrap', lineHeight: 1, color: '#FFD60A', textShadow: outline, transform: `rotate(-3deg) scale(${1 + Math.sin(f / 8) * 0.015})`}}>{thumb.besar}</div>
          <div style={{display: 'inline-block', marginTop: 24, background: '#E63946', color: '#fff', fontSize: 64, padding: '10px 30px', borderRadius: 16, transform: 'rotate(2deg)'}}>{thumb.label}</div>
          <div style={{marginTop: 20, fontSize: 52, color: '#fff', textShadow: outline}}>{thumb.kecil}</div>
        </div>
      )}
      {!thumb && (
        <div style={{position: 'absolute', left: 60, right: 60, bottom: 170, opacity: pop, transform: `translateY(${(1 - pop) * 60}px)`}}>
          {label && <div style={{display: 'inline-block', background: warna, color: '#fff', fontFamily: FONT, fontWeight: 900, fontSize: 46, padding: '8px 26px', borderRadius: 14, marginBottom: 16}}>{label}</div>}
          <div style={{background: 'rgba(255,255,255,.96)', borderRadius: 32, padding: '32px 40px', borderLeft: `16px solid ${warna}`}}>
            <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 66, lineHeight: 1.15, color: '#111'}}>{judul}</div>
            {isi && <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 44, color: '#444', marginTop: 14}}>{isi}</div>}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

const Panggung: React.FC<{bg: string; no?: string; judul: string; sub: string; children: React.ReactNode}> = ({bg, no, judul, sub, children}) => {
  const f = useCurrentFrame();
  const a = useSp(0, 10);
  const b = useSp(8);
  const c = interpolate(f, [70, 85], [0, 1], cl);
  return (
    <AbsoluteFill style={{background: bg, fontFamily: FONT}}>
      {[0, 1, 2].map((k) => (
        <div key={k} style={{position: 'absolute', width: 500, height: 500, borderRadius: 999, background: 'rgba(255,255,255,.07)', left: [-150, 700, 300][k] + Math.sin(f / 50 + k) * 30, top: [200, 900, 1500][k] + Math.cos(f / 45 + k) * 30}} />
      ))}
      {no && (
        <div style={{position: 'absolute', top: 150, left: 70, fontSize: 200, fontWeight: 900, color: '#FFD60A', textShadow: outline, transform: `scale(${0.4 + a * 0.6}) rotate(${(1 - a) * -25}deg)`, transformOrigin: 'left center'}}>{no}</div>
      )}
      <div style={{position: 'absolute', top: no ? 400 : 200, left: 70, right: 70, color: '#fff', opacity: b, transform: `translateX(${(1 - b) * -80}px)`}}>
        <div style={{fontSize: 80, fontWeight: 900, lineHeight: 1.1, textShadow: '0 6px 20px rgba(0,0,0,.3)'}}>{judul}</div>
      </div>
      <div style={{position: 'absolute', top: 760, left: 0, right: 0, height: 760, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{children}</div>
      <div style={{position: 'absolute', bottom: 190, left: 70, right: 70, background: '#fff', borderRadius: 28, padding: '26px 36px', fontSize: 50, fontWeight: 800, color: '#111', opacity: c, transform: `translateY(${(1 - c) * 40}px)`}}>{sub}</div>
    </AbsoluteFill>
  );
};

const Kartu: React.FC<{x: number; y: number; w: number; h: number; warna: string; children?: React.ReactNode; style?: React.CSSProperties}> = ({x, y, w, h, warna, children, style}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: warna, borderRadius: 24, boxShadow: '0 14px 30px rgba(0,0,0,.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', ...style}}>{children}</div>
);

const S1: React.FC<{no: string; t: any}> = ({no, t}) => {
  const f = useCurrentFrame();
  const cap = useSp(40, 9);
  const asli = useSp(75);
  return (
    <Panggung bg="linear-gradient(160deg,#F77F00,#D62828)" no={no} judul={t[0]} sub={t[1]}>
      <div style={{position: 'relative', width: 900, height: 700}}>
        <Kartu x={60} y={80} w={380} h={540} warna="#2B2D42" style={{transform: `rotate(-6deg) translateY(${Math.sin(f / 15) * 6}px)`}}>
          <div style={{color: '#fff', fontSize: 40, fontWeight: 800, textAlign: 'center'}}>▶<br />cara<br />lama</div>
          <div style={{position: 'absolute', fontSize: 340, color: '#FF4D4D', fontWeight: 900, opacity: cap, transform: `scale(${2 - cap})`}}>✕</div>
        </Kartu>
        <Kartu x={470} y={80} w={380} h={540} warna="#fff" style={{opacity: asli, transform: `rotate(5deg) scale(${0.6 + asli * 0.4})`}}>
          <div style={{color: '#111', fontSize: 40, fontWeight: 800, textAlign: 'center'}}>
            <span style={{fontSize: 140, color: '#2A9D8F'}}>✓</span>
            <br />cara
            <br />benar
          </div>
        </Kartu>
      </div>
    </Panggung>
  );
};

const S2: React.FC<{no: string; t: any}> = ({no, t}) => {
  const f = useCurrentFrame();
  const rapi = interpolate(f, [45, 80], [0, 1], cl);
  const hari = ['S', 'S', 'R', 'K', 'J', 'S', 'M'];
  return (
    <Panggung bg="linear-gradient(160deg,#4361EE,#3A0CA3)" no={no} judul={t[0]} sub={t[1]}>
      <div style={{background: '#fff', borderRadius: 30, padding: 30, width: 900}}>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(7,1fr)', gap: 14}}>
          {hari.map((h, i) => (
            <div key={'h' + i} style={{textAlign: 'center', fontSize: 34, fontWeight: 800, color: '#555'}}>{h}</div>
          ))}
          {Array.from({length: 21}).map((_, i) => {
            const acak = [0, 1, 2, 9, 17].includes(i) ? 1 : 0;
            const teratur = i % 2 === 0 ? 1 : 0;
            const on = acak * (1 - rapi) + teratur * rapi;
            const muncul = interpolate(f, [5 + i * 1.5, 12 + i * 1.5], [0, 1], cl);
            return (
              <div key={i} style={{height: 90, borderRadius: 14, background: on > 0.5 ? '#4CC9F0' : '#EDF2F4', transform: `scale(${muncul * (0.9 + on * 0.1)})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 44, color: '#fff', fontWeight: 900}}>
                {on > 0.5 ? '▶' : ''}
              </div>
            );
          })}
        </div>
      </div>
    </Panggung>
  );
};

const S4: React.FC<{no: string; t: any}> = ({no, t}) => {
  const f = useCurrentFrame();
  const baris = ['Cek', 'Perbaiki', 'Ulangi'];
  return (
    <Panggung bg="linear-gradient(160deg,#2A9D8F,#1B4332)" no={no} judul={t[0]} sub={t[1]}>
      <div style={{background: '#fff', borderRadius: 34, padding: '40px 46px', width: 880}}>
        <div style={{fontSize: 44, fontWeight: 900, color: '#1B4332', marginBottom: 26}}>Langkah praktis</div>
        {baris.map((b, i) => {
          const v = interpolate(f, [20 + i * 18, 34 + i * 18], [0, 1], cl);
          return (
            <div key={b} style={{display: 'flex', alignItems: 'center', gap: 24, marginBottom: 22}}>
              <div style={{width: 76, height: 76, borderRadius: 999, background: v > 0.5 ? '#2A9D8F' : '#E9ECEF', color: '#fff', fontSize: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${1 + Math.sin(v * Math.PI) * 0.3})`}}>{v > 0.5 ? '✓' : ''}</div>
              <div style={{flex: 1}}>
                <div style={{fontSize: 40, fontWeight: 700, color: '#222'}}>{b}</div>
                <div style={{height: 16, borderRadius: 8, background: '#E9ECEF', marginTop: 8}}>
                  <div style={{height: 16, borderRadius: 8, width: `${v * 100}%`, background: '#52B788'}} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Panggung>
  );
};

const S5: React.FC<{no: string; t: any}> = ({no, t}) => {
  const f = useCurrentFrame();
  const nilai = [25, 40, 35, 60, 85];
  return (
    <Panggung bg="linear-gradient(160deg,#7209B7,#B5179E)" no={no} judul={t[0]} sub={t[1]}>
      <div style={{display: 'flex', alignItems: 'flex-end', gap: 34, height: 600, background: 'rgba(255,255,255,.12)', borderRadius: 30, padding: '30px 40px'}}>
        {nilai.map((n, i) => {
          const v = interpolate(f, [15 + i * 10, 35 + i * 10], [0, 1], cl);
          return (
            <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
              <div style={{width: 120, height: n * 5 * v, borderRadius: '18px 18px 6px 6px', background: i === 4 ? '#FFD60A' : '#fff'}} />
              <div style={{color: '#fff', fontSize: 32, fontWeight: 800}}>M{i + 1}</div>
            </div>
          );
        })}
      </div>
    </Panggung>
  );
};

const Bola: React.FC<{n: number; i: number}> = ({n, i}) => {
  const f = useCurrentFrame();
  const s = useSp(10 + i * 5, 8);
  return <div style={{width: 140, height: 140, borderRadius: 999, background: ['#E63946', '#F77F00', '#FFD60A', '#2A9D8F', '#4361EE'][i], color: '#fff', fontSize: 80, fontWeight: 900, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${s}) translateY(${Math.sin(f / 6 + i) * 8}px)`, textShadow: '0 3px 0 rgba(0,0,0,.3)'}}>{n}</div>;
};
const SCTA: React.FC<{t: any}> = ({t}) => {
  const f = useCurrentFrame();
  const g = useSp(5);
  return (
    <Panggung bg="linear-gradient(160deg,#1D3557,#0B132B)" judul={t} sub="Tulis di komentar & ikuti untuk tips berikutnya!">
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 50}}>
        <div style={{display: 'flex', gap: 26}}>
          {[1, 2, 3, 4, 5].map((n, i) => <Bola key={n} n={n} i={i} />)}
        </div>
        <div style={{background: '#fff', borderRadius: 40, padding: '30px 44px', fontSize: 48, fontWeight: 800, color: '#111', opacity: g, transform: `scale(${g})`}}>
          Aku nomor... {'●'.repeat(1 + (Math.floor(f / 8) % 3))}
        </div>
      </div>
    </Panggung>
  );
};

const ACAK = [S1, S2, S4, S5];
const NO = ['#1', '#2', '#3', '#4', '#5'];
const Transisi: React.FC<{first: boolean; children: React.ReactNode}> = ({first, children}) => {
  const f = useCurrentFrame();
  const t = first ? 1 : interpolate(f, [0, 8], [0, 1], cl);
  return <AbsoluteFill style={{opacity: t, transform: `scale(${1.06 - t * 0.06})`}}>{children}</AbsoluteFill>;
};

export const Film: React.FC<any> = (p) => {
  const f = useCurrentFrame();
  const urut: number[] = p.urut || [0, 1, 2, 3];
  const tip = (k: number, i: number) => {const C = ACAK[urut[k]]; return <C no={NO[i]} t={p.tips[i]} />;};
  const BLOK = [
    {d: 150, el: <BlokAI foto={p.foto[0]} judul="" warna="#E63946" thumb={p.thumb} />},
    {d: 150, el: tip(0, 0)},
    {d: 150, el: tip(1, 1)},
    {d: 150, el: <BlokAI foto={p.foto[1]} label="#3" judul={p.tips[2][0]} isi={p.tips[2][1]} warna="#F77F00" />},
    {d: 150, el: tip(2, 3)},
    {d: 150, el: tip(3, 4)},
    {d: 150, el: <BlokAI foto={p.foto[2]} label="BONUS" judul={p.bonus[0]} isi={p.bonus[1]} warna="#2A9D8F" />},
    {d: 150, el: <SCTA t={p.cta} />},
  ];
  let mulai = 0;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {BLOK.map((b, i) => {
        const s = mulai;
        mulai += b.d;
        return (
          <Sequence key={i} from={s} durationInFrames={b.d}>
            <Transisi first={i === 0}>{b.el}</Transisi>
          </Sequence>
        );
      })}
      <div style={{position: 'absolute', top: 60, right: 60, display: 'flex', gap: 12}}>
        <div style={{background: '#111', color: '#fff', fontFamily: FONT, fontWeight: 800, fontSize: 30, padding: '8px 20px', borderRadius: 40}}>Bu Rina</div>
        <div style={{background: 'rgba(255,255,255,.9)', color: '#111', fontFamily: FONT, fontWeight: 700, fontSize: 24, padding: '9px 16px', borderRadius: 40}}>karakter AI</div>
      </div>
      <div style={{position: 'absolute', bottom: 0, left: 0, height: 12, width: `${(f / 1200) * 100}%`, background: '#FFD60A'}} />
    </AbsoluteFill>
  );
};
