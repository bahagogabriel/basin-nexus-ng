/* Basin Nexus NG S22 — original, self-contained geographic resource pictograms.
   Each path is purpose-drawn and rendered consistently on maps and in the profile.
   The pictogram is a category/type identifier, never proof of an exact site. */
(function(){
'use strict';
const P={
 gold:'M5 9 9 4 16 5 21 11 17 19 8 20 3 14Z M9 4 11 11 8 20 M16 5 11 11 21 11',
 lithium:'M8 3h8v2h-8z M6 6h12v15H6z M13 8l-4 6h4l-2 5 6-8h-4z',
 coal:'M3 14 6 6 14 3 21 8 19 18 11 22 4 19Z M6 6l7 8 8-6 M13 14l-2 8 M4 19l9-5',
 limestone:'M3 6h18v5H3z M3 13h18v5H3z M10 6v5 M16 13v5',
 ironore:'M4 4v10c0 9 16 9 16 0V4h-5v10c0 3-6 3-6 0V4z M4 8h5 M15 8h5',
 magnetite:'M4 4v10c0 9 16 9 16 0V4h-5v10c0 3-6 3-6 0V4z M4 8h5 M15 8h5',
 manganese:'M3 19l4-13 5 8 5-8 4 13 M6 17h12 M10 9l2 5 2-5',
 mica:'M4 8l13-5 4 6-13 5z M4 12l13-5 M4 16l13-5 M4 20l13-5',
 gypsum:'M5 21 8 4 13 7 11 20 M11 20 16 2 20 6 17 20 M3 21h18',
 kaolin:'M7 5h10 M9 5v4c-6 3-5 11 3 12 8-1 9-9 3-12V5 M7 15h10',
 clay:'M3 9h18v12H3z M3 14h18 M11 9v5 M7 14v7 M16 14v7',
 granite:'M2 18 6 6 13 3 22 12 20 21H5z M6 6l7 9 9-3 M13 15l-1 6',
 barite:'M3 21 6 6 10 3 13 6 16 2 20 8 22 21z M6 6l3 15 M16 2l1 19 M13 6l4 3',
 quartz:'M6 20 5 8 10 2h6l4 6-1 12-7 3z M10 2v11l2 10 M16 2l-4 11 7 7 M5 8l7 5 8-5',
 quartzite:'M4 19 6 7 12 3 19 8 20 19 12 22z M6 7l6 10 7-9 M12 17v5',
 feldspar:'M3 7 9 3 19 6 21 18 9 21 3 15z M9 3v18 M3 15l18 3 M9 12l10-6',
 graphite:'M3 8l9-5 9 5-9 5z M3 12l9 5 9-5 M3 16l9 5 9-5',
 goldnugget:'M5 9 9 4 16 5 21 11 17 19 8 20 3 14Z M9 4 11 11 8 20',
 amethyst:'M12 2 18 7 21 14 12 22 3 14 6 7Z M6 7h12 M3 14h18 M12 2v20 M6 7l6 7 6-7',
 sapphire:'M12 2 5 9 5 16 12 22 19 16 19 9z M5 9h14 M5 16h14 M12 2v20',
 tourmaline:'M8 2h8l4 5-2 15H6L4 7z M8 2l-1 20 M16 2l1 20 M4 7h16',
 topaz:'M12 2 18 5 21 13 12 22 3 13 6 5z M6 5l6 8 6-8 M3 13h18 M12 13v9',
 ruby:'M12 2 19 8 17 18 12 22 7 18 5 8z M5 8h14 M12 2v20',
 talc:'M4 9l7-6 10 4-2 12-8 3-8-5z M4 9l15 10 M11 3l0 19',
 copper:'M12 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z M12 18v4 M9 21h6 M6 8l12 6',
 lead:'M6 3h12l3 18H3z M9 8h6 M10 12h4 M9 17h6',
 zinc:'M4 5h16M4 19h16 M19 5 5 19 M5 5l14 14',
 tin:'M4 5h16l-3 15H7z M8 9h8 M8 13h8 M9 17h6',
 dolomite:'M3 8l6-5 12 5-2 11-10 2-6-7z M9 3v18 M3 8l16 11',
 bentonite:'M3 7q9-6 18 0 M3 12q9-6 18 0 M3 17q9-6 18 0 M3 21q9-6 18 0',
 fluorite:'M12 3 21 8v9l-9 5-9-5V8z M12 3v10 M3 8l9 5 9-5 M12 13v9',
 laterite:'M3 18 6 7l8-4 7 9-3 9H7z M6 7l12 14 M14 3v12',
 beryl:'M7 3h10l4 6-4 12H7L3 9z M7 3l3 7-3 11 M17 3l-3 7 3 11 M3 9h18',
 sharp_sand:'M3 20 6 11 10 18 14 9 18 17 21 10 M3 20h18 M5 6h1 M13 3h1 M19 6h1',
 asbestos:'M4 4q8 5 16 0 M4 9q8 5 16 0 M4 14q8 5 16 0 M4 19q8 5 16 0',
 kyanite:'M5 3l6 2 4-2 5 5-4 13H8L4 8z M11 5l0 16 M5 11h13',
 ballclay:'M3 8h18l-3 12H6z M3 8q9-10 18 0 M8 15h8',
 columbite:'M3 7l8-4 10 5-5 13-10-3z M11 3l1 12-6 3 M12 15l9-7',
 gemstone:'M5 4h14l4 7-11 11L1 11z M5 4l7 7 7-7 M1 11h22 M12 11v11',
 hydrocarbon:'M12 2Q4 12 4 16a8 8 0 0 0 16 0Q20 12 12 2z M8 15q0 5 5 5',
 marl:'M3 7h18 M3 11h18 M3 15h18 M3 19h18 M6 7l4 12 M15 7l3 12',
 phosphate:'M12 2v6 M12 16v6 M2 12h6 M16 12h6 M5 5l5 5 M14 14l5 5 M19 5l-5 5 M10 14l-5 5 M9 9h6v6H9z',
 smokyquartz:'M7 21 5 9 11 2h5l4 8-2 11z M11 2v11l2 9 M16 2l-3 11 5 8 M5 9l8 4 7-3',
 zircon:'M12 2l7 5 2 11-9 4-9-4L5 7z M5 7h14 M12 2v20 M3 18l9-7 9 7',
 monazite:'M12 2l9 8-3 11H6L3 10z M12 2v19 M3 10h18 M6 21l15-11',
 wolframite:'M3 5h18l-5 16H8z M3 5l8 16 M21 5l-8 16 M8 11h8',
 tantalite:'M5 2h14l3 10-3 10H5L2 12z M8 6h8 M7 12h10 M8 18h8',
 uranium:'M12 3a3 3 0 1 0 0 6 3 3 0 0 0 0-6z M12 10l-9 6 3 5 6-4 6 4 3-5z',
 ginger:'M10 3q-3 3 0 6l-6 2q-3 3 2 6l4-1 2 6 6-2-2-5 5-3-4-4-3 2z',
 cowpea:'M12 3C3 4 2 18 12 21c10-3 9-17 0-18z M8 10q4-4 8 0 M9 15q3 3 6 0',
 pepper:'M12 4q-8 0-8 8 0 8 6 10 7-3 10-11 0-7-8-7z M12 4l2-3 M13 4l6-1',
 plantain:'M5 3q-5 12 4 18 10 4 12-8Q13 19 5 3z M8 4q0 9 9 11',
 palmoil:'M12 21V8 M12 9L3 3 M12 9l9-6 M12 9 3 10 M12 9l9 1 M7 20h10',
 fish:'M2 12q6-8 14-5l6 5-6 5q-8 3-14-5z M9 12h.5 M16 7v10',
 elephants:'M5 3h13l3 7-3 10h-4v-6h-3v6H7v-7H4z M10 7h.5 M18 9v7',
 gumarabic:'M12 2 6 8l4 5-4 6 6 3 6-3-4-6 4-5z M12 10v12',
 locustbean:'M4 5q9-4 16 2 0 13-16 12Q0 14 4 5z M8 11h1 M12 14h1 M16 10h1',
 irrigationscheme:'M4 22V4h4v18 M15 22V8h5v14 M4 10h16 M4 15q4-3 8 0t8 0',
 soildegradation:'M2 5h20 M5 10l5 5-4 6 M12 10l6 8 4-4 M3 22h19',
 dam:'M3 4v17 M21 4v17 M7 7h10l-2 14H9z M7 11h10 M9 16h6 M2 23q4-3 8 0t8 0t5 0',
 borehole:'M10 3h4v11h-4z M7 14h10v3H7z M12 17v5 M4 22h16 M7 5l-4 3',
 lake:'M2 10q5-5 10 0t10 0 M2 15q5-5 10 0t10 0 M2 20q5-5 10 0t10 0',
 river:'M4 2q14 5 0 10t0 10 M10 2q14 5 0 10t0 10',
 spring:'M12 3v7 M7 6l5 4 5-4 M4 13q4-4 8 0t8 0 M4 18q4-4 8 0t8 0',
 reservoir:'M3 20V7l9-4 9 4v13 M3 15q4-4 9 0t9 0 M3 20q4-4 9 0t9 0',
 wetland:'M3 21q4-3 9 0t9 0 M7 19V7 M7 12l-3-4 M7 10l4-4 M16 19V5 M16 10l4-4 M16 12l-4-4',
 fishing:'M2 12q6-8 14-5l6 5-6 5q-8 3-14-5z M9 12h.5 M16 7v10',
 grazing:'M3 19l5-5 4 3 4-7 5 9 M5 5v6 M2 8h6 M18 3v8 M15 6h6',
 grazingreserve:'M3 20V4h18v16z M8 19l4-6 4 6 M8 8h8 M12 4v7',
 forestreserve:'M12 2 4 13h5L3 19h18l-6-6h5z M12 18v4',
 forest:'M12 2 4 13h5L3 19h18l-6-6h5z M12 18v4',
 nationalpark:'M3 20 9 4l5 9 4-7 3 14z M7 17h12',
 wildlife:'M5 9 3 6 7 5l5 3 5-3 4 1-2 3-2 7-5 5-5-5z M9 13h.5 M15 13h.5',
 crocodilepond:'M2 14q5-8 15-4l5 4-5 4q-10 3-15-4z M4 14l4-1 2 2 2-2 2 2 2-2',
 hotsprings:'M4 19q4-4 8 0t8 0 M8 15q-4-3 0-6t0-6 M14 15q-4-3 0-6t0-6',
 flooding:'M3 4h18v6H3z M3 15q4-4 9 0t9 0 M3 20q4-4 9 0t9 0 M12 5v5',
 erosion:'M3 6h18 M3 10h10l-4 4 3 5 M15 10l6 3-3 8 M3 21h9',
 drought:'M12 2a7 7 0 1 1 0 14 7 7 0 0 1 0-14z M3 22l5-4 4 3 4-3 5 4',
 deforestation:'M12 3 5 14h5l-6 6h16l-6-6h5z M12 16v5 M3 3l18 18',
 siltation:'M3 4h18v7H3z M3 12q5 5 9 0t9 0 M3 18q5-3 9 0t9 0',
 waterpollution:'M12 2Q3 13 3 16a9 9 0 0 0 18 0Q21 13 12 2z M7 17h10 M9 13h1 M15 13h1',
 landdegradation:'M3 4l7 7-4 5 7 5 8-7-5-4 3-6 M3 21h18',
 desertification:'M3 19q5-5 10-2t8-3 M4 21h17 M14 4v8 M10 8h8 M7 6l2 2',
 rice:'M12 22V3 M12 7 5 4 M12 11 19 7 M12 15 5 12 M12 19l7-4 M5 4l2 3 M19 7l-2 3 M5 12l2 3',
 maize:'M12 3c-4 3-6 7-5 12l5 6 5-6c1-5-1-9-5-12z M9 8h6 M9 12h6 M10 16h4 M7 17 3 8 M17 17l4-9',
 millet:'M12 22V3 M12 4l-5 3 M12 7l5 2 M12 10l-5 3 M12 13l5 3 M12 16l-5 3 M5 5l2 2 M17 7l-2 2',
 sorghum:'M12 22v-9 M12 13l-8-5 M12 12l7-7 M12 9l-5-5 M8 3l4 4 4-4 M4 8l2 5 M19 5l1 6',
 soybeans:'M5 7q7-7 14 0t0 10q-7 7-14 0T5 7z M8 11h1 M12 14h1 M16 10h1',
 cassava:'M12 3v7 M3 7l9 4 9-4 M12 11l-6 10 M12 11l6 10 M12 11v11',
 yam:'M7 3c-4 3-4 10-2 15 3 6 12 4 14-2 3-9-3-16-12-13z M8 9l5 3 M9 16l5-2',
 groundnut:'M10 3c-6 0-6 9-2 10-5 5-2 10 4 9 6 1 9-4 4-9 4-2 4-10-2-10-3 0-4 2-6 2z M9 7l7 10',
 sesame:'M12 22V3 M8 6l-4 3 4 3 4-3z M16 10l4 3-4 3-4-3z',
 cotton:'M12 8c-4-6-9-3-8 3-6 2-2 11 4 8 5 5 10 1 8-3 8-2 5-10 0-9z M12 18v4',
 banana:'M5 3q-5 12 4 18 10 4 12-8Q13 19 5 3z',
 tomato:'M12 5C2 4 1 21 12 22c11-1 10-18 0-17z M12 6l-4-4 M12 6l4-4 M5 6l7 0 7 0',
 onion:'M12 3C3 8 3 18 12 22c9-4 9-14 0-19z M12 3V1 M8 9q4 6 0 12 M16 9q-4 6 0 12',
 cocoa:'M12 2c-10 5-9 17 0 20 9-3 10-15 0-20z M12 2v20 M7 7l10 10 M17 7 7 17',
 wheat:'M12 22V3 M12 6l-5-3 M12 9l5-3 M12 12l-5-3 M12 15l5-3 M12 18l-5-3',
 sugarcane:'M9 22V3 M15 22V3 M8 8h8 M8 14h8 M9 7l-5-3 M15 12l6-4',
 sheabutter:'M12 3c-8 2-10 12-5 17 4 4 10 1 11-4 2-7-1-12-6-13z M9 9q6 6 3 10',
 peanut:'M10 3c-6 0-6 9-2 10-5 5-2 10 4 9 6 1 9-4 4-9 4-2 4-10-2-10-3 0-4 2-6 2z'
};
const a=Object.freeze({
 barite:'barite',baryte:'barite',barites:'barite',barytes:'barite',
 'iron ore':'ironore','iron deposits':'ironore','shea butter':'sheabutter',shea:'sheabutter',wetlands:'wetland',pollution:'waterpollution',
 'grazing reserve':'grazingreserve','forest reserve':'forestreserve',
 'water pollution':'waterpollution','land degradation':'landdegradation',
 'hot springs':'hotsprings','silica sand':'sharp_sand','sharp sand':'sharp_sand',
 'palm oil':'palmoil','bambara nuts':'cowpea',
 'ball clay':'ballclay','smoky quartz':'smokyquartz','soybean':'soybeans','sharp sand':'sharp_sand',
 'soil degradation':'soildegradation','irrigation scheme':'irrigationscheme',
 'gum arabic':'gumarabic','locust bean':'locustbean',
 'fisheries':'fish','fish':'fish','elephants':'elephants',
 'pepper':'pepper','plantain':'plantain',
 'iron':'ironore','flood':'flooding'
});
const defaults={mineral:'quartz',crop:'wheat',ecology:'forestreserve',water:'river',pressure:'erosion'};
const bg={mineral:'#916125',crop:'#2c854b',ecology:'#186b59',water:'#2475a3',pressure:'#b34a39'};
function normalized(name){return String(name||'').toLowerCase().replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim()}
function canonical(name){
 const value=normalized(name);
 if(['baryte','barites','barite','barytes'].includes(value))return 'Barite';
 if(value==='soybean'||value==='soybeans')return 'Soybeans';
 if(value==='wetlands'||value==='wetland')return 'Wetland';
 return String(name||'').trim();
}
function keyFor(r){
 let key=normalized(canonical(r?.name||'')); key=a[key]||key.replace(/\s+/g,'');
 if(P[key])return key;
 if(r?.category==='ecology' && /grazing/.test(key))return 'grazingreserve';
 if(r?.category==='ecology' && /forest/.test(key))return 'forestreserve';
 if(r?.category==='pressure' && /pollution/.test(key))return 'waterpollution';
 if(r?.category==='water' && /dam/.test(key))return 'dam';
 if(r?.category==='crop' && /nut/.test(key))return 'groundnut';
 return defaults[r?.category]||'quartz';
}
/* Named resources use distinct editorial marker colors, not inferred mineral or crop properties.
   Outer silhouettes still identify the five resource categories, even without color vision. */
const categoryPalette=Object.freeze({
 mineral:['#a66724','#946022','#ad752b'],
 crop:['#28793d','#318b46','#247448'],
 ecology:['#08766d','#0f8276','#11695f'],
 water:['#176db5','#257dc1','#145f9e'],
 pressure:['#bc3e3e','#aa373b','#c64f38']
});
const namedPalette=Object.freeze({
 // High-frequency mineral commodities: separate contrasting hues at actual 27px map scale.
 gold:'#bf830e',ironore:'#a14934',lithium:'#6658ae',clay:'#bc694b',
 limestone:'#416f79',granite:'#68718a',lead:'#44546a',tin:'#396a91',
 columbite:'#51489c',kaolin:'#867343',monazite:'#91517b',barite:'#8b6743',
 coal:'#44464c',gypsum:'#7864a0',copper:'#ae5b3c',zinc:'#587779',
 // Crops: stronger differences than multiple near-identical green circles.
 cassava:'#437a2b',rice:'#b08c27',sheabutter:'#9b6330',
 yam:'#815238',ginger:'#bb712c',sesame:'#6e8535',sugarcane:'#1e795d',
 maize:'#b1831c',groundnut:'#985c40',millet:'#6a8a3b',
 // Preserve thematic meaning for ecology, water and pressure.
 wetland:'#138b91',forestreserve:'#237858',grazingreserve:'#6e8451',
 river:'#2379b8',lake:'#257fa2',dam:'#2d72ac',
 flooding:'#b74834',erosion:'#a94e37',drought:'#af7b2c',
 deforestation:'#974536',waterpollution:'#a1395a'
});
function tint(r){
 const key=keyFor(r);
 if(namedPalette[key])return namedPalette[key];
 const colors=categoryPalette[r?.category]||categoryPalette.mineral;
 let hash=0;for(let i=0;i<key.length;i++)hash=(hash*31+key.charCodeAt(i))>>>0;
 return colors[hash%colors.length];
}
function shapeFor(r){return ['mineral','crop','ecology','water','pressure'].includes(r?.category)?r.category:'mineral'}
function traceShape(ctx,category,half){
 ctx.beginPath();
 if(category==='crop'){ctx.arc(0,0,half,0,2*Math.PI)}
 else if(category==='ecology'){
  for(let i=0;i<6;i++){const a=(Math.PI/3)*i-Math.PI/2,x=Math.cos(a)*half,y=Math.sin(a)*half;i?ctx.lineTo(x,y):ctx.moveTo(x,y)}
  ctx.closePath();
 }else if(category==='pressure'){
  ctx.moveTo(0,-half);ctx.lineTo(half,0);ctx.lineTo(0,half);ctx.lineTo(-half,0);ctx.closePath();
 }else if(category==='water'){
  ctx.moveTo(0,-half);
  ctx.bezierCurveTo(-half*.25,-half*.47,-half*.91,-half*.13,-half*.91,half*.24);
  ctx.bezierCurveTo(-half*.91,half*.8,-half*.47,half,0,half);
  ctx.bezierCurveTo(half*.47,half,half*.91,half*.8,half*.91,half*.24);
  ctx.bezierCurveTo(half*.91,-half*.13,half*.25,-half*.47,0,-half);
  ctx.closePath();
 }else{ctx.roundRect(-half,-half,half*2,half*2,4)}
}

function markup(r,cls=''){
 const key=keyFor(r),path=P[key],label=canonical(r?.name||key);
 const color=tint(r);return '<span class="bnIcon bnIcon--'+shapeFor(r)+' '+cls+'" style="background:'+color+'" title="'+String(label).replace(/[<>"]/g,'')+'" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><path d="'+path+'"/></svg></span>';
}
const pathCache=new Map();
function draw(ctx,r,x,y,size=26,selected=false){
 const key=keyFor(r),path=P[key];if(!pathCache.has(key))pathCache.set(key,new Path2D(path));
 const color=tint(r),half=size/2,shape=shapeFor(r);
 ctx.save();ctx.translate(x,y);
 ctx.shadowColor='rgba(0,25,25,.25)';ctx.shadowBlur=selected?7:3;ctx.shadowOffsetY=1;
 ctx.fillStyle=color;traceShape(ctx,shape,half);ctx.fill();
 ctx.shadowBlur=0;ctx.shadowOffsetY=0;
 ctx.strokeStyle=selected?'#f7f8ce':'#f8faf6';ctx.lineWidth=selected?2.8:1.4;ctx.stroke();
 const scale=size/27;ctx.scale(scale,scale);ctx.translate(-12,-12);
 ctx.strokeStyle='#fff';ctx.lineWidth=2.35;ctx.lineJoin='round';ctx.lineCap='round';
 ctx.stroke(pathCache.get(key));ctx.restore();
}
window.BNResourceIcons=Object.freeze({markup,draw,canonical,keyFor,tint,shapeFor,paths:P});
})();