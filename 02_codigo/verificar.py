"""Reconstruye resultados desde insumos originales y comprueba el método."""
from pathlib import Path
import json,hashlib,itertools,sys
import numpy as np,pandas as pd,rasterio,geopandas as gpd
r=Path(__file__).resolve().parent.parent;out=r/'03_resultados'/'escenario_base'
a=json.loads((out/'auditoria.json').read_text(encoding='utf-8'));c=pd.read_csv(out/'celdas.csv.gz');m=pd.read_csv(out/'municipios.csv');ind=pd.read_csv(out/'indicadores.csv');sen=pd.read_csv(out/'sensibilidad.csv');im=json.loads((out/'tasas_imputadas.json').read_text(encoding='utf-8'));checks={}
checks['celdas_unicas']=bool(c.celda.is_unique and not c.duplicated(['fila','columna']).any());checks['valores_finitos']=bool(np.isfinite(c[['total','pobre','no_pobre','rwi']].to_numpy()).all());checks['subconjuntos']=bool((c.pobre>=-1e-8).all() and (c.no_pobre>=-1e-8).all() and (c.pobre<=c.total+1e-8).all());checks['error_identidad_celdas']=float(abs(c.total-c.pobre-c.no_pobre).max())
with rasterio.open(r/'01_insumos'/'poblacion'/'slv_pop_2025_CN_100m_R2025A_v1.tif') as src:
 p=src.read(1,masked=True);valid=(~np.ma.getmaskarray(p))&np.isfinite(p.data)&(p.data>0);checks['todas_celdas_positivas']=int(valid.sum())==len(c);checks['error_poblacion_fuente']=float(abs(p.data[c.fila.to_numpy(),c.columna.to_numpy()].astype(float)-c.total.to_numpy()).max())
# Independent reconstruction of municipal ranking through a pandas grouped table.
g=c.groupby(['codigo_municipal','rwi'],sort=True).agg(p=('total','sum'),poor=('pobre','sum')).reset_index();rates=m.set_index('ADM2_PCODE').POVERTY_RATE/100;g['rate']=g.codigo_municipal.map(rates);g['total_m']=g.groupby('codigo_municipal').p.transform('sum');g['before']=g.groupby('codigo_municipal').p.cumsum()-g.p;g['expected']=np.minimum(g.p,np.maximum(0,g.rate*g.total_m-g.before));checks['error_calibracion_por_nivel_rwi']=float(abs(g.poor-g.expected).max());shares=c.pobre/c.total;tie=c.assign(fraccion=shares).groupby(['codigo_municipal','rwi']).fraccion.agg(['min','max']);checks['error_igualdad_empates']=float((tie['max']-tie['min']).max())
orig=pd.read_csv(r/'01_insumos'/'pobreza'/'slv_pov_2.csv');checks['tasas_originales_preservadas']=bool(np.allclose(m.set_index('ADM2_PCODE').loc[orig.loc[orig.POVERTY_RATE.notna(),'ADM2_PCODE'],'POVERTY_RATE'],orig.loc[orig.POVERTY_RATE.notna(),'POVERTY_RATE']));checks['error_promedios_imputados']=max(abs(z['tasa']-np.mean(z['tasas_vecinos'])) for z in im)
print('Población, calibración y tasas verificadas',flush=True)
# Full independent resampling against source rasters, followed by all aggregates.
masks={};cache={};levels={'inundacion':[.1,.15,.3,.5],'sismo':[.05,.1,.15,.2,.25],'viento':[20,25,33],'calor':[28,30,32]}
for h,config in a['parametros'].items():
 fn={'inundacion':'Inundacion_PR100.tif','sismo':'Sismo_PR100.tif','viento':'Viento_PR100.tif','calor':'Teperature_PR100.tif'}[h]
 with rasterio.open(r/'01_insumos'/'amenazas'/fn) as src:
  assert src.crs.to_epsg()==4326
  inv=~src.transform;ccf,rrf=inv*(c.longitud.to_numpy(),c.latitud.to_numpy());rr=np.floor(rrf).astype(int);cc=np.floor(ccf).astype(int);inside=(rr>=0)&(cc>=0)&(rr<src.height)&(cc<src.width);b=src.read(1,masked=True);v=np.zeros(len(c),b.dtype);ok=np.zeros(len(c),bool);v[inside]=b.data[rr[inside],cc[inside]];ok[inside]=~np.ma.getmaskarray(b)[rr[inside],cc[inside]];ok &= np.isfinite(v)
  for th in levels[h]:cache[h,th]=ok&((v>th) if h=='calor' else (v>=np.float32(th)))
  masks[h]=cache[h,config['umbral']];checks[h+'_diferencias_mascara']=int(np.count_nonzero(masks[h]!=c['exp_'+h]));checks[h+'_diferencias_cobertura']=int(np.count_nonzero(ok!=c['dato_valido_'+h]))
count=sum(v.astype(int) for v in masks.values());checks['diferencias_numero_amenazas']=int(np.count_nonzero(count!=c.numero_amenazas));weights={g:c[g].to_numpy() for g in ['total','pobre','no_pobre']};selectors={'base':np.ones(len(c),bool),**masks,'union':count>=1,**{f'numero_{k}':count==k for k in range(5)}}
checks['error_agregados_nacionales']=max(abs(float(w[sel].sum())-float(a['totales'][key+'_'+group])) for key,sel in selectors.items() for group,w in weights.items())
err=0
for key,sel in selectors.items():
 grp=c.loc[sel].groupby('codigo_municipal')[['total','pobre','no_pobre']].sum();saved=ind[ind.categoria==key].set_index('codigo')
 for code in m.ADM2_PCODE:
  for name in weights:err=max(err,abs((float(grp.loc[code,name]) if code in grp.index else 0)-float(saved.loc[code,name])))
checks['error_agregados_municipales']=err
err=0
for _,row in sen.iterrows():
 n=sum(cache[h,row[h]].astype(int) for h in levels)
 for group,w in weights.items():
  for key,sel in [('una_o_mas',n>=1),('dos_o_mas',n>=2)]:err=max(err,abs(w[sel].sum()-row[key+'_'+group]))
checks['error_sensibilidad']=float(err);checks['escenarios_sensibilidad']=len(sen);checks['principal_unico']=int(sen.principal.sum())==1;checks['principal_correcto']=all(float(sen.loc[sen.principal,k].iloc[0])==cfg['umbral'] for k,cfg in a['parametros'].items())
# Verify the inputs in THIS checkout, preserving original paths as provenance.
from pathlib import PureWindowsPath
def local_input(record):
 parts=PureWindowsPath(record['ruta']).parts
 if '01_insumos' not in parts: raise ValueError('Insumo fuera de la estructura documentada')
 local=r.joinpath(*parts[parts.index('01_insumos'):]).resolve()
 if not local.is_relative_to((r/'01_insumos').resolve()): raise ValueError('Ruta de insumo fuera del proyecto')
 return local
checks['hashes_insumos_coinciden']=all(hashlib.sha256(local_input(z).read_bytes()).hexdigest()==z['sha256'] for z in a['archivos'])
report={'checks':checks,'celdas':len(c),'municipios':len(m),'total':float(c.total.sum()),'pobre':float(c.pobre.sum()),'imputaciones':[{'municipio':z['municipio'],'tasa':z['tasa'],'metodo':z['metodo']} for z in im]}
(out/'revision_independiente.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))



from pathlib import Path
import pandas as pd,numpy as np,geopandas as gpd,json
from scipy.spatial import cKDTree
r=Path(__file__).resolve().parent.parent;c=pd.read_csv(r/'03_resultados'/'escenario_base'/'celdas.csv.gz');p=gpd.GeoDataFrame(c[['celda']],geometry=gpd.points_from_xy(c.longitud,c.latitud),crs=4326);b=gpd.read_file(r/'01_insumos'/'pobreza'/'slv_pov_2.shp')[['ADM2_PCODE','geometry']];j=gpd.sjoin(p,b,how='left',predicate='within');assert not j.index.duplicated().any();ok=j.ADM2_PCODE.notna();checks={'asignaciones_contenidas_incorrectas':int((j.loc[ok,'ADM2_PCODE'].to_numpy()!=c.loc[ok,'codigo_municipal'].to_numpy()).sum()),'marcas_fuera_limites_incorrectas':int((~ok.to_numpy()!=c.municipio_por_cercania.to_numpy()).sum())};pm=p.to_crs(32616);bm=b.to_crs(32616);near=gpd.sjoin_nearest(pm.loc[~ok],bm,how='left',distance_col='d').sort_values(['celda','d','index_right']).drop_duplicates('celda');checks['asignaciones_cercanas_incorrectas']=int((near.ADM2_PCODE.to_numpy()!=c.loc[near.celda,'codigo_municipal'].to_numpy()).sum());checks['error_distancias_municipio']=float(abs(near.d.to_numpy()-c.loc[near.celda,'municipio_distancia_m'].to_numpy()).max());rw=pd.read_csv(r/'01_insumos'/'rwi'/'slv_relative_wealth_index.csv');rp=gpd.GeoDataFrame(rw,geometry=gpd.points_from_xy(rw.longitude,rw.latitude),crs=4326).to_crs(32616);dist,idx=cKDTree(np.column_stack([rp.geometry.x,rp.geometry.y])).query(np.column_stack([pm.geometry.x,pm.geometry.y]));checks['rwi_asignados_incorrectos']=int((rw.rwi.to_numpy()[idx]!=c.rwi.to_numpy()).sum());checks['error_distancias_rwi']=float(abs(dist-c.rwi_distancia_m.to_numpy()).max());report=json.loads((r/'03_resultados/escenario_base/revision_independiente.json').read_text(encoding='utf-8'));report['checks_espaciales']=checks;(r/'03_resultados/escenario_base/revision_independiente.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(checks,ensure_ascii=False,indent=2))

for key,value in report['checks'].items():
 if isinstance(value,bool): assert value,key
 elif key=='escenarios_sensibilidad': assert value==180
 else: assert abs(value)<1e-5,(key,value)
for key,value in checks.items(): assert abs(value)<1e-5,(key,value)
import subprocess
subprocess.run([sys.executable,'-s','-m','unittest','discover','-s','tests','-v'],cwd=Path(__file__).resolve().parent,check=True)
report['pruebas_unitarias']={'ejecutadas':6,'resultado':'OK'}
report['alcance']='Verificación de implementación y coherencia; no validación independiente de las fuentes.'
(out/'revision_independiente.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verificación independiente y pruebas completadas.')
