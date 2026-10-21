"""Distribuciones reales por RWI para explicar la calibración, sin recalcularla."""
import csv,gzip,json,math
from collections import defaultdict

def generar_calibracion(out,dashboard):
 groups=defaultdict(lambda:defaultdict(lambda:[0.,0.]))
 with gzip.open(out/'celdas.csv.gz','rt',encoding='utf-8-sig',newline='') as f:
  for c in csv.DictReader(f):
   g=groups[c['codigo_municipal']][float(c['rwi'])];g[0]+=float(c['total']);g[1]+=float(c['pobre'])
 rows=[]
 with (out/'municipios.csv').open(encoding='utf-8-sig',newline='') as f:
  for m in csv.DictReader(f):
   levels=[[r,*v] for r,v in sorted(groups[m['ADM2_PCODE']].items())]
   total=float(m['base_total']);poor=float(m['base_pobre']);rate=float(m['POVERTY_RATE'])
   assert abs(sum(v[1] for v in levels)-total)<1e-5
   assert abs(sum(v[2] for v in levels)-poor)<1e-5
   assert abs(poor-total*rate/100)<1e-5
   cutoff=float(m['rwi_corte']) if m['rwi_corte'] else None
   for r,p,q in levels:
    expected=1 if cutoff is not None and r<cutoff else 0 if cutoff is None or r>cutoff else q/p
    assert abs(q-p*expected)<1e-5
   cut=next((v for v in levels if v[0]==cutoff),None)
   before=sum(v[1] for v in levels if cutoff is not None and v[0]<cutoff)
   if cut: assert abs(before+cut[2]-poor)<1e-5
   rows.append(dict(codigo=m['ADM2_PCODE'],municipio=m['ADM2_EN'],departamento=m['ADM1_EN'],tasa=rate,imputada=m['tasa_imputada']=='True',total=total,pobre=poor,no_pobre=float(m['base_no_pobre']),corte=cutoff,antes_corte=before,grupo_corte=cut,niveles=levels,error_personas=abs(poor-total*rate/100)))
 payload=dict(municipios=rows,resumen=dict(unidades=len(rows),con_poblacion=sum(r['total']>0 for r in rows),imputadas_con_poblacion=[r['municipio'] for r in rows if r['imputada'] and r['total']>0],sin_poblacion=[r['municipio'] for r in rows if not r['total']],error_max_personas=max(r['error_personas'] for r in rows)))
 text=json.dumps(payload,ensure_ascii=False,allow_nan=False,separators=(',',':'))
 (dashboard/'calibracion_datos.js').write_text('window.GAIA_CALIBRACION='+text+';',encoding='utf-8')
 (out/'calibracion_municipal.json').write_text(text,encoding='utf-8')
 print('Calibración verificada:',payload['resumen'])
