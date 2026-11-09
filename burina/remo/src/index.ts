import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Film} from './Film';
const contoh = {foto: ['foto/a.jpg', 'foto/b.jpg', 'foto/c.jpg'], thumb: {besar: '5 KESALAHAN', label: 'FB PRO', kecil: 'yang bikin belum menghasilkan'}, tips: [['a', 'b'], ['a', 'b'], ['a', 'b'], ['a', 'b'], ['a', 'b']], bonus: ['a', 'b'], cta: 'Kamu nomor berapa?', urut: [0, 1, 2, 3]};
const Root = () => React.createElement(Composition, {id: 'Film', component: Film, durationInFrames: 1200, fps: 30, width: 1080, height: 1920, defaultProps: contoh});
registerRoot(Root);
