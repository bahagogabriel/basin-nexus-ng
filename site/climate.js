/* Basin Nexus NG / NASA POWER 2005–2025 source point-climate explorer.
   Not a catchment-average, gauge observation, water balance or flood estimate. */
(function(){
"use strict";
const state={climate:null,register:null,active:null};
const $=id=>document.getElementById(id);
const clean=s=>String(s||"").normalize("NFKD").toLowerCase().replace(/[^a-z0-9]/g,"");
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function validate(climate,register,source){
 if(!climate||!register||climate.schema_version!=="BN_STAGE3D_BO_POWER_LABEL_POINT_CLIMATE_2005_2025_V1"
   ||climate.data_status!=="NASA_POWER_MODELED_POINT_SAMPLE_NOT_CATCHMENT_MEAN"
   ||climate.period_start!==2005||climate.period_end!==2025||climate.catchment_point_count!==20
   ||register.schema_version!=="BN_STAGE3D_BQ_UNIFIED_CATCHMENT_REGISTER_2005_2025_V1"
   ||register.catchment_count!==20||!Array.isArray(climate.records)||climate.records.length!==20
   ||!Array.isArray(register.rows)||register.rows.length!==20
   ||!Array.isArray(source)||source.length!==20)return false;
 const seen=new Set();
 for(let i=0;i<20;i++){
  const r=climate.records[i],t=register.rows[i],o=source[i];
  if(!r||!t||!o||r.catchment_id!==o.id||t.catchment_id!==o.id
   ||r.catchment_name!==o.name||t.catchment_name!==o.name
   ||r.sample_lon!==o.label_lon||r.sample_lat!==o.label_lat
   ||t.label_lon!==o.label_lon||t.label_lat!==o.label_lat
   ||t.climate_spatial_basis!=="NASA_POWER_MAP_LABEL_POINT_NOT_CATCHMENT_MEAN"
   ||!(/^[a-f0-9]{64}$/).test(r.nasa_power_snapshot_sha256)
   ||!Array.isArray(r.annual)||r.annual.length!==21
   ||!Array.isArray(r.monthly_climatology)||r.monthly_climatology.length!==12
   ||seen.has(r.catchment_id)
   ||!Number.isFinite(r.mean_annual_precip_mm_2005_2025)||r.mean_annual_precip_mm_2005_2025<=0
   ||!Number.isFinite(r.mean_t2m_c_2005_2025)
   ||r.recent_2025?.year!==2025
   ||t.nasa_power_mean_annual_precip_mm_2005_2025!==r.mean_annual_precip_mm_2005_2025
   ||t.nasa_power_precip_mm_2025!==r.recent_2025.precip_mm
   ||t.nasa_power_mean_temp_c_2005_2025!==r.mean_t2m_c_2005_2025
   ||t.nasa_power_mean_temp_c_2025!==r.recent_2025.mean_t2m_c)return false;
  seen.add(o.id);
  for(let j=0;j<21;j++){
   const y=r.annual[j];
   if(y.year!==2005+j||!Number.isFinite(y.precip_mm)||y.precip_mm<0
    ||!Number.isFinite(y.mean_t2m_c)||y.mean_t2m_c<0||y.mean_t2m_c>45)return false;
  }
  for(let j=0;j<12;j++){
   const m=r.monthly_climatology[j];
   if(m.month!==j+1||!Number.isFinite(m.mean_monthly_precip_mm)
    ||m.mean_monthly_precip_mm<0||!Number.isFinite(m.mean_t2m_c))return false;
  }
 }
 return seen.size===20;
}
function profileHTML(c){
 const r=state.climate?.records.find(x=>x.catchment_id===c.id);
 if(!r)return "";
 return '<div class="admin-panel" id="profileClimate"><span class="apill">NASA POWER · MODELED POINT SAMPLE</span><h3>Historical climate, 2005–2025</h3>'+
  '<p class="admin-summary"><b>'+r.mean_annual_precip_mm_2005_2025.toLocaleString()+' mm/year</b> estimated historical mean precipitation · <b>'+r.mean_t2m_c_2005_2025.toFixed(2)+'°C</b> modeled mean air temperature.</p>'+
  '<p class="admin-summary">2025 modeled precipitation: <b>'+r.recent_2025.precip_mm.toLocaleString()+' mm</b>. Historical wettest month at this point: '+months[r.wettest_mean_precip_month-1]+'.</p>'+
  '<p class="captionline">One NASA POWER grid point sampled near the registered map-label coordinate ('+r.sample_lat.toFixed(3)+'° N, '+r.sample_lon.toFixed(3)+'° E). NOT a catchment rainfall average, station gauge or observed river-flow indicator.</p>'+
  '<button type="button" data-nasa-profile="'+esc(c.id)+'">Inspect annual rainfall and seasonality</button></div>';
}
function render(){
 const tbody=$("climateRows"),status=$("climateStatus"),detail=$("climateDetail");
 if(!tbody||!status||!detail)return;
 if(!state.climate||!state.register){
  status.textContent="NASA POWER climate integration unavailable or source validation failed";
  tbody.innerHTML='<tr><td colspan="6">Representative point-climate data unavailable.</td></tr>';detail.innerHTML="";return;
 }
 const query=clean($("climateSearch")?.value),sort=$("climateSort")?.value||"name";
 let rows=state.climate.records.filter(x=>!query||clean(x.catchment_name+" "+x.catchment_id).includes(query));
 rows.sort((a,b)=>sort==="rain"?b.mean_annual_precip_mm_2005_2025-a.mean_annual_precip_mm_2005_2025
  :sort==="recent"?b.recent_2025.precip_mm-a.recent_2025.precip_mm
  :sort==="temp"?b.mean_t2m_c_2005_2025-a.mean_t2m_c_2005_2025
  :a.catchment_name.localeCompare(b.catchment_name));
 status.textContent=rows.length+" of 20 modeled NASA POWER representative grid-point samples · 2005–2025 · NOT catchment mean rainfall";
 tbody.innerHTML=rows.length?rows.map(r=>'<tr><td><button type="button" data-climate-open="'+esc(r.catchment_id)+'">'+esc(r.catchment_name)+'</button></td>'+
 '<td>'+r.mean_annual_precip_mm_2005_2025.toFixed(1)+'</td>'+
 '<td>'+r.recent_2025.precip_mm.toFixed(1)+'</td>'+
 '<td>'+r.mean_t2m_c_2005_2025.toFixed(2)+'</td>'+
 '<td>'+r.recent_2025.mean_t2m_c.toFixed(2)+'</td>'+
 '<td>'+months[r.wettest_mean_precip_month-1]+'</td></tr>').join(""):
 '<tr><td colspan="6">No climate records match your search.</td></tr>';
 const current=state.climate.records.find(r=>r.catchment_id===state.active);
 if(!current){detail.innerHTML='<p class="captionline">Select a catchment to see all 21 annual values and the 12-month seasonal climate profile.</p>';return}
 const max=Math.max(1,...current.monthly_climatology.map(x=>x.mean_monthly_precip_mm));
 detail.innerHTML='<div class="admin-panel"><h3>'+esc(current.catchment_name)+' · NASA POWER modeled representative point</h3>'+
 '<p class="captionline">Grid-point sample near '+current.sample_lat.toFixed(4)+'° N, '+current.sample_lon.toFixed(4)+'° E. Original monthly precipitation unit mm/day; estimated total mm is daily mean × calendar days. NOT a whole-basin average.</p>'+
 '<div class="faoLinksScroll"><table aria-label="Historical 12-month seasonality at sampled NASA POWER point"><thead><tr><th>Month</th><th>Mean precipitation (mm/month)</th><th>Mean temperature (°C)</th><th>Seasonal precipitation</th></tr></thead><tbody>'+
 current.monthly_climatology.map(m=>'<tr><td>'+months[m.month-1]+'</td><td>'+m.mean_monthly_precip_mm.toFixed(1)+'</td><td>'+m.mean_t2m_c.toFixed(2)+'</td>'+
 '<td><div style="height:9px;min-width:3px;width:'+Math.max(2,Math.round(100*m.mean_monthly_precip_mm/max))+'%;background:#367c76;border-radius:3px"></div></td></tr>').join("")+'</tbody></table></div>'+
 '<h4>Annual modeled point-climate series, 2005–2025</h4><div class="faoLinksScroll"><table aria-label="Annual NASA POWER modeled point rainfall and temperature"><thead><tr><th>Year</th><th>Estimated annual precipitation (mm)</th><th>Annual mean temperature (°C)</th></tr></thead><tbody>'+
 current.annual.map(y=>'<tr><td>'+y.year+'</td><td>'+y.precip_mm.toFixed(1)+'</td><td>'+y.mean_t2m_c.toFixed(2)+'</td></tr>').join("")+'</tbody></table></div>'+
 '<button type="button" data-climate-map="'+esc(current.catchment_id)+'">Locate catchment on map</button></div>';
}
function open(cid){
 if(!state.climate)return;
 state.active=cid;
 document.getElementById("navData")?.click();
 render();
 $("climateComparison")?.scrollIntoView({block:"start"});
}
document.addEventListener("click",e=>{
 const fromProfile=e.target.closest("[data-nasa-profile]");
 if(fromProfile){open(fromProfile.dataset.nasaProfile);return}
 const table=e.target.closest("[data-climate-open]");
 if(table){state.active=table.dataset.climateOpen;render();$("climateDetail")?.scrollIntoView({block:"nearest"});return}
 const locate=e.target.closest("[data-climate-map]");
 if(locate){
  const id=locate.dataset.climateMap;
  const mapButton=document.querySelector('#catchmentList [data-id="'+id+'"]');
  if(mapButton)mapButton.click();
  else if(typeof window.choose==="function"){document.getElementById("navExplore")?.click();window.choose(id,true)}
 }
});
window.BNClimate={profileHTML,open,get ready(){return !!state.climate},get count(){return state.climate?.records.length||0}};
document.addEventListener("DOMContentLoaded",async()=>{
 $("climateSearch")?.addEventListener("input",render);
 $("climateSort")?.addEventListener("change",render);
 try{
  const paths=["data/registry.json","data/nasa_power_20_catchment_point_climate_2005_2025.json",
      "data/integrated_catchment_indicator_register.json"];
  const [source,climate,register]=await Promise.all(paths.map(async u=>{
     const res=await fetch(u);if(!res.ok)throw Error("NASA climate source unavailable");
     return res.json();
  }));
  if(!validate(climate,register,source))throw Error("Climate/source lineage incompatible");
  state.climate=climate;state.register=register;
  render();
  window.dispatchEvent(new Event("bn:climate-ready"));
 }catch(err){render()}
});
})();
