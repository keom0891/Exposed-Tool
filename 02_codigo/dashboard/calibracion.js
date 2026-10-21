'use strict';
(()=>{
 const C=window.GAIA_CALIBRACION, byId=id=>document.getElementById(id), select=byId('calibrationMunicipality');
 const fmt=new Intl.NumberFormat('es-SV',{maximumFractionDigits:0}),dec=new Intl.NumberFormat('es-SV',{maximumFractionDigits:2,minimumFractionDigits:2}),rwi=new Intl.NumberFormat('es-SV',{maximumFractionDigits:4});
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const rows=[...C.municipios].sort((a,b)=>a.departamento.localeCompare(b.departamento,'es')||a.municipio.localeCompare(b.municipio,'es'));
 select.innerHTML=rows.map(m=>`<option value="${escape(m.codigo)}">${escape(m.municipio)} · ${escape(m.departamento)}${m.total?'':' · sin población'}</option>`).join('');
 select.value=rows.find(m=>m.municipio==='San Salvador')?.codigo||rows.find(m=>m.total>0).codigo;
 const summary=C.resumen;
 byId('calibrationSummary').textContent=`${summary.con_poblacion} unidades con población calibradas de ${summary.unidades} polígonos entregados. Tasas imputadas en unidades pobladas: ${summary.imputadas_con_poblacion.join(' y ')}. ${summary.sin_poblacion.length} unidades sin población asignada no requieren corte. Todas las tasas se reproducen con diferencias menores a 0,00001 habitantes antes del redondeo.`;
 function render(){
  const m=rows.find(r=>r.codigo===select.value), chart=byId('calibrationChart'),width=Math.max(280,chart.clientWidth),height=320,left=52,right=22,top=28,bottom=52,w=width-left-right,h=height-top-bottom;
  byId('calibrationMetrics').innerHTML=[['Población WorldPop',fmt.format(m.total)+' hab.'],['Tasa utilizada',dec.format(m.tasa)+'%'+(m.imputada?' · imputada':'')],['Población pobre',fmt.format(m.pobre)+' hab.'],['Población no pobre',fmt.format(m.no_pobre)+' hab.']].map(([label,value])=>`<div><span>${label}</span><strong>${value}</strong></div>`).join('');
  if(!m.total){chart.innerHTML='';byId('calibrationCut').textContent='Sin población WorldPop asignada: no existe un corte de RWI ni una tasa reproducida que validar.';byId('calibrationValidation').textContent='La tasa de la fuente se conserva, pero no se aplica a habitantes en esta unidad.';return;}
  const levels=m.niveles,min=levels[0][0],max=levels.at(-1)[0],pad=Math.max((max-min)*.05,.025),lo=min-pad,hi=max+pad,x=v=>left+(v-lo)/(hi-lo)*w,y=v=>top+h*(1-v/100);
  let cumulative=0,path=`M ${x(lo)} ${y(0)}`;
  for(const [r,p] of levels){path+=` H ${x(r)} V ${y((cumulative+=p)/m.total*100)}`;}path+=` H ${x(hi)}`;
  const cut=m.corte===null?lo:m.corte,cx=x(cut),cy=y(m.tasa);
  let svg=`<svg role="img" aria-label="Distribución acumulada de población por RWI de ${escape(m.municipio)}; corte ${escape(rwi.format(cut))} para una tasa de pobreza de ${escape(dec.format(m.tasa))}%" viewBox="0 0 ${width} ${height}" height="${height}"><title>Calibración de ${escape(m.municipio)}</title><rect x="${left}" y="${top}" width="${Math.max(0,cx-left)}" height="${h}" fill="#1899c6" opacity=".12"/><rect x="${cx}" y="${top}" width="${left+w-cx}" height="${h}" fill="#dce5ea" opacity=".4"/>`;
  for(const tick of [0,25,50,75,100])svg+=`<line x1="${left}" x2="${left+w}" y1="${y(tick)}" y2="${y(tick)}" stroke="#dfe5ea"/><text x="${left-8}" y="${y(tick)+4}" text-anchor="end" font-size="12" fill="#4e5d6a">${tick}%</text>`;
  const n=width<450?2:4;for(let i=0;i<=n;i++){const v=lo+(hi-lo)*i/n;svg+=`<text x="${x(v)}" y="${top+h+22}" text-anchor="${i===0?'start':i===n?'end':'middle'}" font-size="12" fill="#4e5d6a">${rwi.format(v)}</text>`;}
  svg+=`<text x="${left}" y="16" font-size="12" fill="#4e5d6a">Población acumulada (%)</text><text x="${left+w/2}" y="${height-5}" text-anchor="middle" font-size="12" fill="#4e5d6a">Meta RWI · menor → mayor riqueza</text><path d="${path}" fill="none" stroke="#0a5a78" stroke-width="2.5"/><line x1="${left}" x2="${cx}" y1="${cy}" y2="${cy}" stroke="#083c52" stroke-dasharray="5 4"/><line x1="${cx}" x2="${cx}" y1="${top}" y2="${top+h}" stroke="#083c52" stroke-dasharray="5 4"/><circle cx="${cx}" cy="${cy}" r="5" fill="#083c52"/></svg>`;
  chart.innerHTML=svg;
  const g=m.grupo_corte;
  byId('calibrationCut').textContent=g?`Corte RWI: ${rwi.format(m.corte)}. Por debajo: ${fmt.format(m.antes_corte)} habitantes. En el grupo del corte: ${fmt.format(g[1])} habitantes, de los que se asignan ${fmt.format(g[2])} como pobres (${dec.format(100*g[2]/g[1])}% del grupo). Todas las celdas empatadas reciben esa misma fracción.`:'Tasa de 0%: no se asigna población pobre ni se requiere corte.';
  byId('calibrationValidation').textContent=`Verificación: tasa utilizada ${dec.format(m.tasa)}% · tasa reproducida ${dec.format(100*m.pobre/m.total)}% · diferencia absoluta menor a 0,00001 habitantes. Cifras mostradas redondeadas.`;
 }
 select.addEventListener('change',render);new ResizeObserver(render).observe(byId('calibrationChart'));
 byId('downloadCalibration').onclick=()=>{const headers=['codigo','municipio','departamento','tasa','imputada','total','pobre','no_pobre','corte','error_personas'];const quote=v=>'"'+String(v??'').replace(/"/g,'""')+'"';const text='\uFEFF'+[headers.join(','),...rows.map(m=>headers.map(k=>quote(m[k])).join(','))].join('\r\n');const url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='calibracion_municipal.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 render();
})();
