#!/usr/bin/env node
'use strict';
// Deterministic physical-layout and printable-crop vector art.
// Requires Node.js only for manual regeneration, NOT for Mac installation.
// Measured 210 mm clear gap between INNER edges of 60 mm corner pads in X/Y.
// Thus the pads are 15 mm in from the real 360 mm plate edges.
// The 300x305 printable SVG is a mathematically exact crop of that plate.
const fs=require('node:fs');
const path=require('node:path');
function generateSvgs(){
  const A=[],P=[];
  const head=(out,w,h,title)=>{
    out.push('<?xml version="1.0" encoding="UTF-8"?>');
    out.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`);
    out.push(`<title>${title}</title>`);
    out.push('<defs><linearGradient id="metal" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="#e6eef5"/><stop offset=".52" stop-color="#d4e0eb"/><stop offset="1" stop-color="#bacbd9"/></linearGradient>');
    out.push('<linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="#dfcba0"/><stop offset=".5" stop-color="#c9b280"/><stop offset="1" stop-color="#b69c6c"/></linearGradient>');
    out.push('<radialGradient id="bolt"><stop stop-color="#f7fbfc"/><stop offset=".55" stop-color="#a2b7c7"/><stop offset="1" stop-color="#758a99"/></radialGradient></defs>');
  };
  const bolt=(out,x,y)=>{
    let h='';for(let i=0;i<6;i++){let a=Math.PI*(-.5+i/3);h+=(i?' L':'M')+(x+6*Math.cos(a)).toFixed(2)+' '+(y+6*Math.sin(a)).toFixed(2);}
    out.push(`<g class="allen-bolt"><circle cx="${x}" cy="${y}" r="13" fill="#859aab" stroke="#edf4fa" stroke-width="2"/><circle cx="${x}" cy="${y}" r="10" fill="url(#bolt)" stroke="#698092" stroke-width="1.5"/><path d="${h} Z" fill="#435968" stroke="#e3eef4" stroke-width="1.3"/></g>`);
  };
  const collar=(out,x,y)=>{
    out.push(`<g class="centre-hole-free-collar"><circle cx="${x}" cy="${y}" r="27" fill="#d6e2eb" stroke="#8a9caa" stroke-width="2"/><circle cx="${x}" cy="${y}" r="21" fill="none" stroke="#eff5f9" stroke-width="2"/></g>`);
    bolt(out,x,y);
  };
  // Image displayed on actual printable polygon, 300 mm x 305 mm.
  // Top of image is printer Y=305, bottom Y=0 (front).
  head(A,1200,1220,'Zortrax M300 Classic - measured plate, 300 x 305 printable crop');
  A.push('<desc>SVG is the true X=30..330, Y=30..335 mm crop of the 360 mm plate. Corner pads measure 60x60 mm; inner pad gap 210 mm in both axes. No silver strip appears between rear printable boundary and gold pads. Central gold pad is 50x50 mm.</desc>');
  A.push('<rect id="full-bleed-opaque-base" x="0" y="0" width="1200" height="1220" fill="url(#metal)"/>');
  A.push('<g id="five-flush-gold-pads" fill="url(#gold)" stroke="#99845d" stroke-width="1.0">');
  // Full plate corner pads: X/Y = [15,75] and [285,345] mm.
  // Printable crop is physically X=[30,330], Y=[30,335] mm,
  // so the four visible corner areas are exactly:
  // rear left (0,0,180,200), rear right (1020,0,180,200),
  // front left (0,1040,180,180), front right (1020,1040,180,180).
  // Crucially both rear pads TOUCH y=0: no false silver stripe behind them.
  const croppedGoldPads=[[0,0,180,200],[1020,0,180,200],
                         [0,1040,180,180],[1020,1040,180,180],
                         [500,520,200,200]];
  croppedGoldPads.forEach(([x,y,w,h])=>A.push(`<rect class="gold-perforated-area" x="${x}" y="${y}" width="${w}" height="${h}"/>`));
  A.push('</g>');
  A.push('<g id="all-perforations-including-gold" fill="#314a59" stroke="#f5f9fc" stroke-width=".65">');
  for(let iy=0;iy<102;iy++)for(let ix=0;ix<100;ix++)A.push(`<circle cx="${6+12*ix}" cy="${6+12*iy}" r="2.9"/>`);
  A.push('</g>');
  [450,750].forEach(x=>collar(A,x,620));
  A.push('<rect x="1.25" y="1.25" width="1197.5" height="1217.5" fill="none" stroke="#94aab8" stroke-width="1.5" opacity=".7"/>');
  A.push('</svg>');
  // Full-size REFERENCE plan; NOT an Orca 360 mm texture. The clipped SVG
  // for the real 300x305 printable region is unchanged.
  // Full-size plan for verifying exact measured sizes and safe printable inset.
  head(P,1440,1440,'Zortrax M300 Classic - physical 360 mm platform, printable 300 x 305 mm');
  P.push('<rect x="0" y="0" width="1440" height="1440" fill="#c5d5e1"/>');
  P.push('<rect x="3" y="3" width="1434" height="1434" rx="19" fill="url(#metal)" stroke="#71899b" stroke-width="4"/>');
  P.push('<rect id="perforation-rectangle" x="56" y="64" width="1328" height="1316" fill="none" stroke="#94a8b5" stroke-width="2"/>');
  P.push('<g id="five-flush-gold-pads" fill="url(#gold)" stroke="#99845d" stroke-width="1.3">');
  // The full 360 mm reference matches the 210 mm clear gap exactly:
  // 15 mm outer margin + 60 mm pad + 210 mm gap + 60 mm pad + 15 mm = 360.
  const physicalGoldPads=[[60,60,240,240],[1140,60,240,240],
                          [60,1140,240,240],[1140,1140,240,240],
                          [620,620,200,200]];
  physicalGoldPads.forEach(([x,y,w,h])=>P.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}"/>`));
  P.push('</g><g id="all-perforations-including-gold" fill="#314a59" stroke="#f5f9fc" stroke-width=".65">');
  for(let fy=16.5;fy<=340.5;fy+=3)for(let fx=16.5;fx<=343.5;fx+=3)P.push(`<circle cx="${fx*4}" cy="${(360-fy)*4}" r="2.9"/>`);
  P.push('</g>');
  [142.5,217.5].forEach(x=>collar(P,x*4,720));
  // OEM photo: sixteen unique perimeter hex screws. Four corners + three
  // intermediates per edge, ~6 mm from metal boundaries, not 17 mm inward.
  // Distances are approximate, derived from the rectified reference photograph.
  const edge=[6,93,180,267,354],frame=[];
  for(const x of edge)frame.push([x,6],[x,354]);
  for(const y of edge.slice(1,-1))frame.push([6,y],[354,y]);
  if(frame.length!==16)throw Error('Incorrect perimeter screw count');
  frame.forEach(([x,y])=>bolt(P,x*4,(360-y)*4));

  // Design reference ONLY: stock OrcaSlicer 2.5 forces a dark material
  // on external custom STL geometry. This 15% shade is an SVG proposal
  // demonstrating the requested future renderer behavior, not what Orca
  // can currently display outside its true 300 x 305 printable polygon.
  P.push('<path id="excluded-margin-reference-only" d="M0 0H1440V1440H0Z M120 100H1320V1320H120Z" fill="#000000" fill-opacity=".15" fill-rule="evenodd"/>');
  P.push('<rect id="actual-printable-area-300x305" x="120" y="100" width="1200" height="1220" fill="none" stroke="#ff5a31" stroke-width="5"/>');
  P.push('</svg>');
  return {texture:A.join('\n')+'\n',layout:P.join('\n')+'\n'};
}
if(require.main===module){
 const root=path.resolve(__dirname,'..'),a=generateSvgs();
 for(const [name,data] of [
 ['profiles/Zortrax/model/Zortrax_M300_Classic_bed.svg',a.texture],
 ['docs/Zortrax_M300_360mm_plate_layout.svg',a.layout]]){
 const dest=path.join(root,name);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,data);console.log(name);}
}
module.exports={generateSvgs};
