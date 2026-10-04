"""Curve tracing aid. Outputs require visual checking, never supply diet data."""
from pathlib import Path
import math, json
from collections import deque
import numpy as np
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
im=Image.open(HERE/'audit/figure9_original.png').convert('RGB')
a=np.asarray(im).astype(int)
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]

def thin(mask):
 s=np.pad(mask,1).astype('uint8')
 while True:
  changed=0
  for second in [False,True]:
   p=s[1:-1,1:-1]
   ns=[s[:-2,1:-1],s[:-2,2:],s[1:-1,2:],s[2:,2:],s[2:,1:-1],s[2:,:-2],s[1:-1,:-2],s[:-2,:-2]]
   count=sum(ns)
   transitions=sum(((ns[i]==0)&(ns[(i+1)%8]==1)).astype('uint8') for i in range(8))
   if not second:
    trip1=ns[0]*ns[2]*ns[4]; trip2=ns[2]*ns[4]*ns[6]
   else:
    trip1=ns[0]*ns[2]*ns[6]; trip2=ns[0]*ns[4]*ns[6]
   erase=(p==1)&(count>=2)&(count<=6)&(transitions==1)&(trip1==0)&(trip2==0)
   changed+=int(erase.sum());p[erase]=0
  if not changed: return s[1:-1,1:-1]

def neighbors(p,pts):
 x,y=p;out=[]
 for dx in [-1,0,1]:
  for dy in [-1,0,1]:
   q=(x+dx,y+dy)
   if (dx or dy) and q in pts:
    if dx and dy and ((x+dx,y) in pts or (x,y+dy) in pts): continue
    out.append(q)
 return out

def unit(v):
 n=math.hypot(*v)
 return (v[0]/n,v[1]/n) if n else (0,0)
def dot(u,v):return u[0]*v[0]+u[1]*v[1]

for color,mask in dict(red=(r>180)&(g<130)&(b<140),blue=(b>150)&(b-r>80)&(g-r>40)).items():
 if (HERE/f'audit/{color}_trace_graph.json').exists():continue
 s=thin(mask)
 ys,xs=np.nonzero(s)
 pts=set(zip(xs.tolist(),ys.tolist()))
 graph={p:neighbors(p,pts) for p in pts}
 # Tangents at broken curve ends, estimated over 12 skeleton steps.
 ends=[p for p in pts if len(graph[p])==1]
 tangents={}
 for end in ends:
  seq=[end];prev=None;cur=end
  for _ in range(15):
   options=[p for p in graph[cur] if p!=prev]
   if len(options)!=1:break
   prev,cur=cur,options[0];seq.append(cur)
  if len(seq)>7:tangents[end]=unit((end[0]-seq[-1][0],end[1]-seq[-1][1]))
 # Bridge white number-label gaps only along mutually aligned tangents.
 options=[]
 for i,p in enumerate(ends):
  if p not in tangents:continue
  for q in ends[i+1:]:
   if q not in tangents:continue
   d=math.dist(p,q)
   if 3<d<95:
    direction=unit((q[0]-p[0],q[1]-p[1]))
    c1=dot(direction,tangents[p]);c2=dot((-direction[0],-direction[1]),tangents[q])
    if c1>0.94 and c2>0.94:
     options.append((d+300*(2-c1-c2),p,q))
 used=set();bridges=[]
 for score,p,q in sorted(options):
  if p in used or q in used:continue
  graph[p].append(q);graph[q].append(p);used.update([p,q]);bridges.append([p,q])
 (HERE/f'audit/{color}_trace_graph.json').write_text(json.dumps(dict(graph=[dict(p=p,n=ns) for p,ns in graph.items()],bridges=bridges)),encoding='utf-8')
 print(color,len(pts),'pixels',len(ends),'endpoints',len(bridges),'label bridges')

def trace(color,point,name,save=True):
 data=json.loads((HERE/f'audit/{color}_trace_graph.json').read_text())
 graph={tuple(x['p']):[tuple(n) for n in x['n']] for x in data['graph']}
 start=min(graph,key=lambda p:math.dist(p,point))
 paths=[]
 for first in graph[start]:
  path=[start,first];visited={start,first}
  for _ in range(6000):
   cur=path[-1];prev=path[-2]
   options=[p for p in graph[cur] if p!=prev and p not in visited]
   if not options:break
   last=path[max(0,len(path)-12)]
   direction=unit((cur[0]-last[0],cur[1]-last[1]))
   # Look ahead along each local branch to get a robust tangent.
   def score(q):
    lastp,now=cur,q
    for _ in range(8):
     opts=[x for x in graph[now] if x!=lastp]
     if len(opts)!=1:break
     lastp,now=now,opts[0]
    return dot(direction,unit((now[0]-cur[0],now[1]-cur[1])))
   q=max(options,key=score)
   if len(options)>1 and score(q)<0.2:break
   path.append(q);visited.add(q)
  paths.append(path)
 out=im.copy().convert('RGBA')
 overlay=Image.new('RGBA',im.size,(255,255,255,190));out=Image.alpha_composite(out,overlay)
 draw=ImageDraw.Draw(out)
 for path in paths:
  draw.line(path,fill=(200,0,200,255),width=5)
  draw.ellipse((path[-1][0]-10,path[-1][1]-10,path[-1][0]+10,path[-1][1]+10),outline='black',width=3)
 draw.ellipse((start[0]-9,start[1]-9,start[0]+9,start[1]+9),fill='yellow',outline='black',width=2)
 if save:out.convert('RGB').save(HERE/f'audit/trace_{name}.png')
 return dict(name=name,start=start,ends=[path[-1] for path in paths],paths=paths)

if __name__=='__main__':
 for args in [('red',(820,635),'0015'),('blue',(1265,965),'0141'),('blue',(1195,1330),'00075'),('red',(1043,1290),'0057vertical'),('red',(310,983),'0685')]:
  x=trace(*args);print(x['name'],x['start'],x['ends'])
