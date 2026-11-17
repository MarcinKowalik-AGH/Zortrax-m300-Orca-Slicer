#!/usr/bin/env node
// Deterministic source for the R7.6 M300 Classic vector bed texture.
// Top-view appearance only; never change the functional 300x300 printable area.
'use strict';
const fs=require('node:fs');
const path=require('node:path');
function generateSvg() {
  const out=[];
  const a=s=>out.push(s);
  a('<?xml version="1.0" encoding="UTF-8"?>');
  a('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200">');
  a('<title>Zortrax M300 Classic — flat perforated build plate with Allen bolts</title>');
  a('<desc>Opaque, full-bleed top view. Five flush gold perforated areas, 12100 circular holes on one orthogonal lattice, sixteen frame hex-socket bolts and two centre bolts with solid hole-free collars.</desc>');
  a('<defs>');
  a(' <linearGradient id="silver" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#e6eef5"/><stop offset="52%" stop-color="#d4e0eb"/><stop offset="100%" stop-color="#bacbd9"/></linearGradient>');
  a(' <linearGradient id="gold" x1="0%" y1="0%" x2="88%" y2="100%"><stop offset="0%" stop-color="#deca9a"/><stop offset="45%" stop-color="#c7b17f"/><stop offset="100%" stop-color="#b59c6a"/></linearGradient>');
  a(' <radialGradient id="bolt" cx="30%" cy="24%" r="86%"><stop offset="0%" stop-color="#f5f9fc"/><stop offset="55%" stop-color="#a4b8c7"/><stop offset="100%" stop-color="#738796"/></radialGradient>');
  a('</defs>');
  a('<rect id="full-bleed-opaque-base" x="0" y="0" width="1200" height="1200" fill="#c3d2de"/>');
  a('<rect id="continuous-flat-plate" x="1.8" y="1.8" width="1196.4" height="1196.4" rx="23" fill="url(#silver)" stroke="#7d909e" stroke-width="3.2"/>');
  a('<rect x="9" y="9" width="1182" height="1182" rx="20" fill="none" stroke="#edf4f9" stroke-width="2" opacity=".88"/>');
  a('<rect x="65" y="65" width="1070" height="1070" rx="2" fill="none" stroke="#94a9b8" stroke-width="1.2" opacity=".70"/>');
  a('<g id="five-flush-gold-pads" fill="url(#gold)" stroke="#99875f" stroke-width=".95">');
  for (const [x,y,w,h] of [[100,100,200,200],[900,100,200,200],[100,900,200,200],[900,900,200,200],[518,518,164,164]]) {
    a(` <rect class="gold-perforated-area" x="${x}" y="${y}" width="${w}" height="${h}"/>`);
  }
  a('</g>');
  a('<g id="all-perforations-including-gold" fill="#314958" stroke="#f5f9fc" stroke-width=".42">');
  for(let iy=0; iy<110; iy++) {
    const y=(76.8+iy*9.6).toFixed(1);
    for(let ix=0; ix<110; ix++) {
      const x=(76.8+ix*9.6).toFixed(1);
      a(` <circle cx="${x}" cy="${y}" r="2.15"/>`);
    }
  }
  a('</g>');
  function hexPath(cx,cy,r) {
    let d='';
    for(let i=0;i<6;i++) {
      const angle=Math.PI*(-90+i*60)/180;
      d+=(i?' L':'M')+(cx+r*Math.cos(angle)).toFixed(2)+' '+(cy+r*Math.sin(angle)).toFixed(2);
    }
    return d+' Z';
  }
  function allen(cx,cy,border) {
    a(`<g class="allen-bolt" data-x="${cx}" data-y="${cy}">`);
    a(` <circle cx="${cx}" cy="${cy}" r="${border?12.0:10.5}" fill="#8195a3" stroke="#edf5fa" stroke-width="1.5"/>`);
    a(` <circle cx="${cx}" cy="${cy}" r="${border?9.8:8.7}" fill="url(#bolt)" stroke="#677b89" stroke-width="1.15"/>`);
    a(` <path d="${hexPath(cx,cy,border?5.45:4.8)}" fill="#3c4d58" stroke="#e3edf2" stroke-width="1.05" stroke-linejoin="round"/>`);
    a('</g>');
  }
  for(const cx of [478,722]) {
    a(`<g class="centre-hole-free-collar"><circle cx="${cx}" cy="600" r="20" fill="#d5e1ea" stroke="#8da1b0" stroke-width="1.4"/><circle cx="${cx}" cy="600" r="15.5" fill="none" stroke="#eff5f8" stroke-width="1.7"/></g>`);
    allen(cx,600,false);
  }
  a('<g id="frame-allen-bolts">');
  for(const x of [56,335,600,865,1144]) {
    allen(x,54,true);
    allen(x,1146,true);
  }
  for(const y of [325,600,875]) {
    allen(54,y,true);
    allen(1146,y,true);
  }
  a('</g>');
  a('</svg>');
  return out.join('\n')+'\n';
}
if(require.main===module) {
  const dest=process.argv[2]||path.join(__dirname,'../profiles/Zortrax/model/Zortrax_M300_Classic_bed.svg');
  fs.mkdirSync(path.dirname(dest),{recursive:true});
  fs.writeFileSync(dest,generateSvg(),'utf8');
  process.stdout.write('Generated: '+dest+'\n');
}
module.exports={generateSvg};
