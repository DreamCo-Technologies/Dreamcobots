(function () {
  'use strict';

  const PALETTES = [
    ['#111827', '#f4f7fb', '#18b7c9', '#d6a84f'],
    ['#151515', '#e8edf2', '#c64045', '#66c7d4'],
    ['#12211b', '#f2f5ed', '#4fb286', '#f0b44d'],
    ['#1c1a24', '#f4f0e8', '#7c9cff', '#d96f52'],
    ['#18212a', '#eff3f6', '#ef8354', '#54c6be'],
  ];
  const MOTIFS = ['compass', 'shield', 'signal', 'spark', 'lens', 'ledger', 'bridge', 'gear', 'book', 'globe'];

  function hash(value) {
    let result = 2166136261;
    for (let index = 0; index < String(value).length; index += 1) {
      result ^= String(value).charCodeAt(index);
      result = Math.imul(result, 16777619);
    }
    return result >>> 0;
  }

  function describe(seed, division, category) {
    const value = hash(`${seed}:${division}:${category}`);
    return {
      seed: String(seed),
      division: String(division),
      category: String(category),
      palette: PALETTES[value % PALETTES.length],
      motif: MOTIFS[Math.floor(value / 7) % MOTIFS.length],
      antenna: value % 3,
      eyeStyle: Math.floor(value / 11) % 3,
      faceWidth: 78 + (value % 15),
      badgeSides: 4 + (value % 4),
      identityCode: value.toString(16).padStart(8, '0'),
    };
  }

  function polygon(context, x, y, radius, sides, rotation) {
    context.beginPath();
    for (let index = 0; index < sides; index += 1) {
      const angle = rotation + (Math.PI * 2 * index) / sides;
      const px = x + Math.cos(angle) * radius;
      const py = y + Math.sin(angle) * radius;
      if (index === 0) context.moveTo(px, py); else context.lineTo(px, py);
    }
    context.closePath();
  }

  function render(canvas, input) {
    const descriptor = input.palette ? input : describe(input.seed, input.division, input.category);
    const [background, shell, accent, detail] = descriptor.palette;
    const size = 180;
    canvas.width = size;
    canvas.height = size;
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', `${descriptor.division} robot identity for ${descriptor.category}`);
    const context = canvas.getContext('2d');
    if (!context) return descriptor;
    context.clearRect(0, 0, size, size);
    context.fillStyle = background;
    context.beginPath();
    context.arc(90, 90, 86, 0, Math.PI * 2);
    context.fill();
    context.strokeStyle = detail;
    context.lineWidth = 3;
    context.stroke();
    context.fillStyle = shell;
    context.strokeStyle = '#58616d';
    context.lineWidth = 3;
    context.beginPath();
    context.roundRect((180 - descriptor.faceWidth) / 2, 43, descriptor.faceWidth, 83, 24);
    context.fill();
    context.stroke();

    context.fillStyle = '#0e1319';
    context.beginPath();
    context.roundRect(52, 65, 76, 43, 18);
    context.fill();
    const eyeY = descriptor.eyeStyle === 2 ? 89 : 84;
    context.fillStyle = accent;
    if (descriptor.eyeStyle === 1) {
      context.fillRect(68, eyeY, 14, 4);
      context.fillRect(98, eyeY, 14, 4);
    } else {
      context.beginPath(); context.arc(75, eyeY, descriptor.eyeStyle === 2 ? 7 : 5, 0, Math.PI * 2); context.fill();
      context.beginPath(); context.arc(105, eyeY, descriptor.eyeStyle === 2 ? 7 : 5, 0, Math.PI * 2); context.fill();
    }
    context.strokeStyle = accent;
    context.lineWidth = 3;
    context.beginPath();
    context.arc(90, 94, 20, .25, Math.PI - .25);
    context.stroke();

    context.fillStyle = shell;
    context.beginPath();
    context.roundRect(58, 124, 64, 38, 10);
    context.fill();
    context.strokeStyle = '#58616d';
    context.stroke();
    context.fillStyle = accent;
    polygon(context, 90, 143, 12, descriptor.badgeSides, -Math.PI / 2);
    context.fill();
    context.strokeStyle = detail;
    context.lineWidth = 2;
    context.stroke();

    context.strokeStyle = detail;
    context.fillStyle = detail;
    context.lineWidth = 3;
    if (descriptor.antenna === 0) {
      context.beginPath(); context.moveTo(90, 43); context.lineTo(90, 25); context.stroke();
      context.beginPath(); context.arc(90, 21, 5, 0, Math.PI * 2); context.fill();
    } else if (descriptor.antenna === 1) {
      context.beginPath(); context.moveTo(72, 46); context.lineTo(63, 29); context.moveTo(108, 46); context.lineTo(117, 29); context.stroke();
      context.beginPath(); context.arc(62, 27, 4, 0, Math.PI * 2); context.fill();
      context.beginPath(); context.arc(118, 27, 4, 0, Math.PI * 2); context.fill();
    } else {
      polygon(context, 90, 34, 10, 4, Math.PI / 4); context.fill();
    }
    descriptor.identityCode.split('').forEach((digit, index) => {
      const level = Number.parseInt(digit, 16) / 15;
      context.fillStyle = level > .5 ? accent : detail;
      context.fillRect(54 + index * 9, 166, 5, 3 + Math.round(level * 5));
    });
    canvas.dataset.robotMotif = descriptor.motif;
    return descriptor;
  }

  function renderInto(container, input) {
    const canvas = document.createElement('canvas');
    render(canvas, input);
    container.replaceChildren(canvas);
    return canvas;
  }

  window.DREAMCO_ROBOT_AVATAR = { describe, render, renderInto };
})();
