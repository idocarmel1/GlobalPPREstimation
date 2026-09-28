import math,json
import numpy as np
import pandas as pd
from ModelData import ModelData
from PPRCalculator import PPRCalculator
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(x):
    if isinstance(x,PPRCalculator):return {'type':'PPRCalculator','attributes':encode(vars(x))}
    if isinstance(x,ModelData):return {'type':'ModelData','attributes':encode(vars(x))}
    if isinstance(x,pd.DataFrame): return {'type':'DataFrame','index':encode(list(x.index)),'columns':encode(list(x.columns)),'values':encode(x.to_numpy().tolist()),'dtypes':[str(t) for t in x.dtypes]}
    if isinstance(x,pd.Series): return {'type':'Series','index':encode(list(x.index)),'values':encode(x.tolist()),'name':encode(x.name)}
    if isinstance(x,np.ndarray): return {'type':'ndarray','values':encode(x.tolist())}
    if isinstance(x,dict): return {'type':'dict','items':[[encode(k),encode(v)] for k,v in x.items()]}
    if isinstance(x,tuple): return {'type':'tuple','values':[encode(v) for v in x]}
    if isinstance(x,list): return [encode(v) for v in x]
    if isinstance(x,np.generic): x=x.item()
    if isinstance(x,float) and not math.isfinite(x):return {'type':'float','value':str(x)}
    if x is None or isinstance(x,(str,int,float,bool)):return x
    raise TypeError(type(x))
def decode(x):
    if isinstance(x,list):return [decode(v) for v in x]
    if not isinstance(x,dict):return x
    t=x['type']
    if t in ('ModelData','PPRCalculator'):
        cls=ModelData if t=='ModelData' else PPRCalculator
        obj=cls.__new__(cls);obj.__dict__.update(decode(x['attributes']));return obj
    if t=='dict':return {decode(k):decode(v) for k,v in x['items']}
    if t=='DataFrame':
        df=pd.DataFrame(decode(x['values']),index=decode(x['index']),columns=decode(x['columns']),dtype=object)
        for col,dtype in zip(df.columns,x.get('dtypes',[])):df[col]=df[col].astype(dtype)
        return df
    if t=='Series':return pd.Series(decode(x['values']),index=decode(x['index']),name=decode(x['name']))
    if t=='ndarray':return np.array(decode(x['values']))
    if t=='tuple':return tuple(decode(x['values']))
    if t=='float':return float(x['value'])
    raise ValueError(t)
