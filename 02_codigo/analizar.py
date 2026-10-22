"""Exposición RP100 y calibración de pobreza por CDF de RWI poblacional."""
from pathlib import Path
import argparse, hashlib, json, sys, time
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from scipy.spatial import cKDTree

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
METRIC_CRS = 32616
HAZARDS = {
 'inundacion': ('Inundacion_PR100.tif', 0.1, '>=', 'm'),
 'sismo': ('Sismo_PR100.tif', 0.10, '>=', 'g'),
 'viento': ('Viento_PR100.tif', 20.0, '>=', 'm/s'),
 'calor': ('Teperature_PR100.tif', 30.0, '>=', '°C WBGT'),
}

def calibrate(population, rwi, rate):
 """Misma fracción para todos los empates del RWI de corte."""
 p=np.asarray(population,dtype=float); r=np.asarray(rwi,dtype=float)
 if len(p)==0: return np.array([],float), None
 if not (np.isfinite(p).all() and (p>=0).all() and np.isfinite(r).all() and 0<=rate<=1):
  raise ValueError('Población, RWI o tasa inválidos')
 levels, inv=np.unique(r,return_inverse=True)
 mass=np.bincount(inv,weights=p,minlength=len(levels)); total=mass.sum()
 target=total*rate
 if target==0: return np.zeros(len(p)), None
 if rate==1: return np.ones(len(p)), float(levels[-1])
 cumulative=np.cumsum(mass); k=int(np.searchsorted(cumulative,target,side='left'))
 before=cumulative[k-1] if k else 0.0
 fraction=(target-before)/mass[k]
 shares=np.where(inv<k,1.,np.where(inv==k,fraction,0.))
 return shares, float(levels[k])

def exposure_mask(values, valid, threshold, operator):
 values=np.asarray(values)
 # Cast thresholds to native precision so a Float32 representation of a cutoff
 # is treated as equality, including the strict WBGT comparison.
 cutoff=np.asarray(threshold,dtype=values.dtype)
 return np.asarray(valid) & ((values>=cutoff) if operator=='>=' else (values>cutoff))

def hash_file(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()

def dump(path,value):
 path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--inputs',type=Path,default=ROOT/'01_insumos'); args=parser.parse_args()
 inp=args.inputs; out=ROOT/'03_resultados'/'escenario_base'; out.mkdir(exist_ok=True); start=time.time()
 print('1/7 Leyendo y completando tasas municipales',flush=True)
 poverty_dir=inp/'pobreza'
 municipalities=gpd.read_file(poverty_dir/'slv_pov_2.shp').to_crs(4326)
 table=pd.read_csv(poverty_dir/'slv_pov_2.csv',dtype={'ADM2_PCODE':str})
 if not table.ADM2_PCODE.is_unique: raise ValueError('Códigos municipales duplicados')
 municipalities=municipalities[['ADM1_EN','ADM2_EN','ADM2_PCODE','geometry']].merge(table[['ADM2_PCODE','POVERTY_RATE']],on='ADM2_PCODE',validate='one_to_one')
 if (~municipalities.is_valid).any(): raise ValueError('Geometrías inválidas')
 metric=municipalities.to_crs(METRIC_CRS)
 original=municipalities.POVERTY_RATE.copy(); imputed=[]
 for i in municipalities.index[original.isna()]:
  # Shared boundary segment (rook). A 1 cm tolerance handles file precision.
  shared=np.array([metric.geometry.iloc[i].boundary.intersection(g.boundary).length for g in metric.geometry])
  neighbors=np.where((shared>0.01)&original.notna().to_numpy())[0]
  method='limite_compartido'
  if len(neighbors)==0:
   neighbors=np.where(np.array([metric.geometry.iloc[i].touches(g) for g in metric.geometry])&original.notna().to_numpy())[0]; method='contacto_en_limite'
  if len(neighbors)==0: raise ValueError(f'Sin vecinos con tasa: {municipalities.loc[i,"ADM2_EN"]}')
  value=float(original.iloc[neighbors].mean()); municipalities.loc[i,'POVERTY_RATE']=value
  imputed.append(dict(codigo=municipalities.loc[i,'ADM2_PCODE'],municipio=municipalities.loc[i,'ADM2_EN'],tasa=value,metodo=method,vecinos=municipalities.iloc[neighbors][['ADM2_PCODE','ADM2_EN']].to_dict('records'),tasas_vecinos=original.iloc[neighbors].tolist()))
 municipalities['tasa_imputada']=original.isna()
 if not municipalities.POVERTY_RATE.between(0,100).all(): raise ValueError('Tasas fuera de rango')

 print('2/7 Asignando WorldPop a municipios',flush=True)
 pop_path=inp/'poblacion'/'slv_pop_2025_CN_100m_R2025A_v1.tif'
 with rasterio.open(pop_path) as src:
  a=src.read(1,masked=True); rows,cols=np.where((~np.ma.getmaskarray(a))&np.isfinite(a.data)&(a.data>0)); population=a.data[rows,cols].astype('float64'); xs,ys=rasterio.transform.xy(src.transform,rows,cols); xs=np.asarray(xs); ys=np.asarray(ys); grid_meta=src.meta.copy(); raster_crs=src.crs
 points=gpd.GeoDataFrame({'cell_id':np.arange(len(population))},geometry=gpd.points_from_xy(xs,ys),crs=raster_crs).to_crs(4326)
 join=gpd.sjoin(points,municipalities[['geometry']],how='left',predicate='within')
 if join.index.duplicated().any(): raise ValueError('Centros poblacionales en múltiples municipios')
 assigned=join.index_right.to_numpy(); missing=np.isnan(assigned); distances=np.zeros(len(population)); pmetric=points.to_crs(METRIC_CRS)
 if missing.any():
  near=gpd.sjoin_nearest(pmetric.loc[missing],metric[['geometry']],how='left',distance_col='distance')
  near=near.sort_values(['cell_id','distance','index_right']).drop_duplicates('cell_id')
  assigned[near.cell_id.to_numpy(dtype=int)]=near.index_right.to_numpy(); distances[near.cell_id.to_numpy(dtype=int)]=near['distance'].to_numpy()
 assigned=assigned.astype(int)
 assert len(assigned)==len(population) and (assigned>=0).all()

 print('3/7 Asignando RWI y calibrando pobreza',flush=True)
 rwi_path=inp/'rwi'/'slv_relative_wealth_index.csv'; rw=pd.read_csv(rwi_path)
 if not np.isfinite(rw[['longitude','latitude','rwi']].to_numpy()).all(): raise ValueError('RWI inválido')
 rg=gpd.GeoDataFrame(rw,geometry=gpd.points_from_xy(rw.longitude,rw.latitude),crs=4326).to_crs(METRIC_CRS)
 coords=np.column_stack([rg.geometry.x,rg.geometry.y]); pc=np.column_stack([pmetric.geometry.x,pmetric.geometry.y]); tree=cKDTree(coords)
 rd,ri=tree.query(pc,k=1)
 # Equal nearest distances resolved by original CSV row, for reproducibility.
 ds,ii=tree.query(pc,k=2); ties=np.flatnonzero(np.isclose(ds[:,0],ds[:,1],rtol=0,atol=1e-8))
 for k in ties:
  candidates=tree.query_ball_point(pc[k],rd[k]+1e-8); exact=np.linalg.norm(coords[candidates]-pc[k],axis=1); ri[k]=min(np.asarray(candidates)[np.isclose(exact,rd[k],rtol=0,atol=1e-8)])
 rwi=rw.rwi.to_numpy()[ri]; poor_share=np.zeros(len(population)); cutoffs=[]
 for i in municipalities.index:
  idx=np.where(assigned==i)[0]; share,cutoff=calibrate(population[idx],rwi[idx],float(municipalities.loc[i,'POVERTY_RATE'])/100); poor_share[idx]=share; cutoffs.append(cutoff)
 poor=population*poor_share; nonpoor=population-poor

 print('4/7 Evaluando amenazas en sus grillas nativas',flush=True)
 masks={}; coverage={}; sampled={}; files=[pop_path,rwi_path,poverty_dir/'slv_pov_2.csv']+sorted(poverty_dir.glob('slv_pov_2.*'))
 for hazard,(filename,threshold,op,unit) in HAZARDS.items():
  path=inp/'amenazas'/filename; files.append(path)
  with rasterio.open(path) as src:
   hp=points.to_crs(src.crs); rr,cc=rasterio.transform.rowcol(src.transform,hp.geometry.x.to_numpy(),hp.geometry.y.to_numpy()); rr=np.asarray(rr);cc=np.asarray(cc)
   inside=(rr>=0)&(rr<src.height)&(cc>=0)&(cc<src.width); band=src.read(1,masked=True); values=np.zeros(len(population),dtype=band.dtype); valid=np.zeros(len(population),bool)
   values[inside]=band.data[rr[inside],cc[inside]];valid[inside]=~np.ma.getmaskarray(band)[rr[inside],cc[inside]];valid &= np.isfinite(values)
   mask=exposure_mask(values,valid,threshold,op); masks[hazard]=mask;sampled[hazard]=(values,valid)
   coverage[hazard]=dict(umbral=threshold,operador=op,unidad=unit,crs=str(src.crs),resolucion=list(src.res),dimensiones=[src.width,src.height],poblacion_sin_dato=float(population[~valid].sum()),poblacion_fuera_extension=float(population[~inside].sum()),celdas_sin_dato=int((~valid).sum()))
 count=sum(m.astype('uint8') for m in masks.values()); union=count>0
 selectors={**masks,'union':union,**{f'numero_{k}':count==k for k in range(5)}}

 print('5/7 Agregando y verificando balances',flush=True)
 weights={'total':population,'pobre':poor,'no_pobre':nonpoor}; n=len(municipalities); aggregates={}; records=[]
 for name,w in weights.items():
  aggregates[f'base_{name}']=np.bincount(assigned,weights=w,minlength=n)
  for key,sel in selectors.items(): aggregates[f'{key}_{name}']=np.bincount(assigned,weights=w*sel,minlength=n)
 for key,val in aggregates.items():municipalities[key]=val
 municipalities['rwi_corte']=cutoffs
 target=municipalities.POVERTY_RATE.to_numpy()/100*aggregates['base_total']; error=np.abs(aggregates['base_pobre']-target)
 checks={'calibracion_error_max_personas':float(error.max()),'conservacion_poblacion_error':float(abs(aggregates['base_total'].sum()-population.sum())),'identidad_grupos_error_max':float(max(np.abs(aggregates[f'{key}_total']-aggregates[f'{key}_pobre']-aggregates[f'{key}_no_pobre']).max() for key in ['base',*selectors])),'union_categorias_error_max':float(max(np.abs(sum(aggregates[f'numero_{k}_{g}'] for k in range(1,5))-aggregates[f'union_{g}']).max() for g in weights)),'categorias_base_error_max':float(max(np.abs(sum(aggregates[f'numero_{k}_{g}'] for k in range(5))-aggregates[f'base_{g}']).max() for g in weights))}
 assert all(v<1e-5 for v in checks.values()),checks
 assert np.all((poor_share>=0)&(poor_share<=1))
 for key in selectors:
  for g in weights:
   assert np.all(aggregates[f'{key}_{g}']<=aggregates[f'base_{g}']+1e-6)
 national={key:float(val.sum()) for key,val in aggregates.items()}
 for code,row in [('NACIONAL',national)]+[(r.ADM2_PCODE,r) for _,r in municipalities.iterrows()]:
  for category in ['base',*selectors]:
   rec={'codigo':code,'categoria':category}
   for g in weights:
    value=float(row[f'{category}_{g}']);denom=float(row[f'base_{g}']);rec[g]=value;rec[f'porcentaje_{g}']=100*value/denom if denom else None
   records.append(rec)
 pd.DataFrame(records).to_csv(out/'indicadores.csv',index=False,encoding='utf-8-sig')
 municipalities.drop(columns='geometry').to_csv(out/'municipios.csv',index=False,encoding='utf-8-sig')
 municipalities.to_file(out/'resultados_municipales.gpkg',layer='exposicion_rp100',driver='GPKG')
 pd.DataFrame([dict(celda=int(i),poblacion=float(population[i]),codigo_municipal=municipalities.loc[assigned[i],'ADM2_PCODE'],distancia_m=float(distances[i])) for i in np.where(missing)[0]]).to_csv(out/'asignaciones_fuera_limites.csv',index=False)
 dump(out/'tasas_imputadas.json',imputed)

 print('6/7 Guardando detalle espacial y trazabilidad',flush=True)
 df=pd.DataFrame(dict(celda=np.arange(len(population)),fila=rows,columna=cols,longitud=points.geometry.x,latitud=points.geometry.y,codigo_municipal=municipalities.ADM2_PCODE.to_numpy()[assigned],total=population,pobre=poor,no_pobre=nonpoor,rwi=rwi,rwi_distancia_m=rd,rwi_error=rw.error.to_numpy()[ri],municipio_por_cercania=missing,municipio_distancia_m=distances,numero_amenazas=count))
 for key,mask in masks.items():df[f'exp_{key}']=mask;df[f'dato_valido_{key}']=sampled[key][1]
 df.to_csv(out/'celdas.csv.gz',index=False,compression='gzip')
 # Compact raster stack retains original WorldPop grid, with explicit nodata.
 profile=grid_meta.copy();profile.update(driver='GTiff',count=5,dtype='float32',nodata=-99999,compress='deflate')
 with rasterio.open(out/'poblacion_y_exposicion.tif','w',**profile) as dst:
  for b,(name,values) in enumerate([('poblacion_total',population),('poblacion_pobre',poor),('poblacion_no_pobre',nonpoor),('numero_amenazas',count),('combinacion_bits_F1_S2_V4_C8',sum(m.astype('uint8')*(2**j) for j,m in enumerate(masks.values())))],1):
   arr=np.full(a.shape,-99999,dtype='float32');arr[rows,cols]=values;dst.write(arr,b);dst.set_band_description(b,name)
 manifest=dict(fecha_utc=datetime.now(timezone.utc).isoformat(),parametros=coverage,crs_distancias='EPSG:32616',soporte='Centros de celdas positivas WorldPop 2025; muestreo nativo por celda contenedora',nodata='Cero exposición; población conservada',pobreza='Ranking RWI ponderado por población y fracción común en empates del corte',fuente_pobreza='Mapa de pobreza (2019)',imputacion='Promedio simple de vecinos con tasa original y límite compartido',geografia='266 unidades de la capa de pobreza, incluidos cuerpos de agua; no implica geografía municipal vigente',asignacion_limites=dict(celdas=int(missing.sum()),poblacion=float(population[missing].sum()),distancia_max_m=float(distances.max())),rwi_distancias_m=dict(p50=float(np.percentile(rd,50)),p95=float(np.percentile(rd,95)),max=float(rd.max())),rwi_empates_cercania=int(len(ties)),verificaciones=checks,totales=national,archivos=[dict(ruta=str(f),sha256=hash_file(f),bytes=f.stat().st_size) for f in dict.fromkeys(files)],versiones=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__,geopandas=gpd.__version__,rasterio=rasterio.__version__),duracion_segundos=time.time()-start)
 dump(out/'auditoria.json',manifest)
 print('7/7 Preparando datos del dashboard',flush=True)
 # Equal-distance projected coordinates, simplified only for display, not analysis.
 display=municipalities.to_crs(METRIC_CRS);display.geometry=display.geometry.simplify(180,preserve_topology=True)
 display.rwi_corte=display.rwi_corte.astype(object).where(display.rwi_corte.notna(),None)
 features=json.loads(display.to_json(na='null',drop_id=True))
 payload=dict(nacional=national,municipios=features,imputaciones=imputed,auditoria={k:v for k,v in manifest.items() if k not in ['archivos','versiones']})
 payload['trazabilidad']={'archivos':[{'archivo':Path(f['ruta']).name,'sha256':f['sha256'],'bytes':f['bytes']} for f in manifest['archivos']],'versiones':manifest['versiones']}
 (BASE/'dashboard'/'datos.js').write_text('window.GAIA_DATA='+json.dumps(payload,ensure_ascii=False,allow_nan=False,separators=(',',':'))+';',encoding='utf-8')
 print(json.dumps({'totales':national,'verificaciones':checks,'segundos':time.time()-start},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()

