"""Sensibilidad factorial completa; sin optimización contra un porcentaje objetivo."""
from pathlib import Path
import itertools,json
import numpy as np,pandas as pd,rasterio
from analizar import BASE,ROOT,HAZARDS,exposure_mask,dump

def main():
 out=ROOT/'03_resultados'/'escenario_base'; df=pd.read_csv(out/'celdas.csv.gz'); xs=df.longitud.to_numpy();ys=df.latitud.to_numpy();p=df.total.to_numpy();weights={g:df[g].to_numpy() for g in ['total','pobre','no_pobre']}
 # Niveles del documento metodológico y del intercambio previo. No se buscan
 # puntos de quiebre de los datos ni umbrales que reproduzcan un objetivo.
 levels={'inundacion':[0.1,0.2,0.3],'sismo':[0.1,0.2,0.3],'viento':[20,25,33],'calor':[28,30,32]}
 cached={}
 for key,(file,threshold,op,unit) in HAZARDS.items():
  with rasterio.open(ROOT/'01_insumos'/'amenazas'/file) as s:
   if s.crs is None or s.crs.to_epsg()!=4326: raise ValueError('La sensibilidad de este caso requiere mapas en EPSG:4326: '+file)
   rr,cc=rasterio.transform.rowcol(s.transform,xs,ys);rr=np.array(rr);cc=np.array(cc);inside=(rr>=0)&(rr<s.height)&(cc>=0)&(cc<s.width);a=s.read(1,masked=True);v=np.zeros(len(p),dtype=a.dtype);ok=np.zeros(len(p),bool);v[inside]=a.data[rr[inside],cc[inside]];ok[inside]=~np.ma.getmaskarray(a)[rr[inside],cc[inside]];ok &= np.isfinite(v)
   for value in levels[key]:cached[key,value]=exposure_mask(v,ok,value,op).astype('uint8')
 rows=[]
 for combination in itertools.product(*levels.values()):
  count=sum(cached[key,val] for key,val in zip(levels,combination)); row={key:float(val) for key,val in zip(levels,combination)};row['principal']=combination==tuple(HAZARDS[k][1] for k in levels)
  for group,w in weights.items():
   denom=w.sum()
   for label,mask in [('una_o_mas',count>=1),('dos_o_mas',count>=2),*[(h,cached[h,row[h]].astype(bool)) for h in levels],*[(f'numero_{k}',count==k) for k in range(5)]]:
    amount=float(w[mask].sum());row[f'{label}_{group}']=amount;row[f'pct_{label}_{group}']=100*amount/denom
  rows.append(row)
 result=pd.DataFrame(rows)
 categories=['una_o_mas','dos_o_mas',*levels,*[f'numero_{k}' for k in range(5)]]
 for key in categories:
  assert np.allclose(result[key+'_total'],result[key+'_pobre']+result[key+'_no_pobre'],rtol=0,atol=1e-6),key
  for group,w in weights.items():
   assert result[key+'_'+group].between(-1e-7,float(w.sum())+1e-6).all(),(key,group)
 for group in weights:
  assert np.allclose(sum(result[f'numero_{k}_{group}'] for k in range(5)),weights[group].sum(),rtol=0,atol=1e-6)
  assert np.allclose(sum(result[f'numero_{k}_{group}'] for k in range(1,5)),result['una_o_mas_'+group],rtol=0,atol=1e-6)
 principal=result.loc[result.principal].iloc[0]
 for h in levels:
  mask=df['exp_'+h].to_numpy(dtype=bool)
  for group,w in weights.items():assert abs(principal[h+'_'+group]-w[mask].sum())<1e-6
 result.to_csv(out/'sensibilidad.csv',index=False,encoding='utf-8-sig')
 summary={'diseno':'Factorial completo de niveles documentados; no calibrado a un porcentaje objetivo','niveles':levels,'combinaciones':len(rows),'principal':result.loc[result.principal].to_dict('records')[0],'min_pct_una_o_mas':float(result.pct_una_o_mas_total.min()),'max_pct_una_o_mas':float(result.pct_una_o_mas_total.max()),'min_pct_dos_o_mas':float(result.pct_dos_o_mas_total.min()),'max_pct_dos_o_mas':float(result.pct_dos_o_mas_total.max()),'nota':'Los umbrales sísmicos 0,10 y 0,20 g están por debajo del mínimo válido del mapa (0,20139 g) y generan la misma máscara. El escenario base usa 0,10 g; el nivel de 0,30 g reduce la exposición sísmica. La sensibilidad no constituye una validación del modelo de amenaza.'}
 dump(out/'sensibilidad_resumen.json',summary)
 (BASE/'dashboard'/'sensibilidad.js').write_text('window.GAIA_SENSITIVITY='+json.dumps({'resumen':summary,'escenarios':rows},ensure_ascii=False,allow_nan=False)+';',encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
