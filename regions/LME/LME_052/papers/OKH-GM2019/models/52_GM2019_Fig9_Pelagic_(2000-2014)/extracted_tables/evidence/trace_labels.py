from pathlib import Path
import json, math
from trace_raster import trace
HERE=Path(__file__).resolve().parent
labels=[
 ('r0015',.0015,820,635),('r055a',.055,400,704),('r241',.241,688,692),('r015',.015,859,702),('r003a',.003,850,712),
 ('r0025',.0025,575,754),('r0024',.0024,1001,762),('r0046',.0046,953,834),('r0085',.0085,241,878),('r005',.005,318,884),
 ('r046a',.046,450,861),('r003b',.003,587,836),('r011',.011,543,884),('r018',.018,783,889),('r0114a',.0114,1015,889),
 ('r00001a',.00001,1124,886),('r156',.156,120,835),('r685',.685,191,980),('r139',.139,172,994),('r0138',.0138,123,1083),
 ('r114a',.114,308,1081),('r0963',.0963,470,1013),('r055b',.055,542,984),('r021',.021,697,1003),('r046b',.046,793,1019),
 ('r00001b',.00001,522,1058),('r003c',.003,653,1079),('r114b',.114,480,1084),('r57',.57,682,1084),('r114c',.114,910,1057),
 ('r001',.001,1000,1083),('r0006',.0006,1172,1004),('r0122a',.0122,1220,1120),('r024',.024,476,1126),('r006a',.006,649,1187),
 ('r0005',.0005,864,1250),('r00014a',.00014,158,1196),('r00014b',.00014,456,1257),('r023',None,253,1304),
 ('r057a',.057,302,1314),('r057b',.057,755,1341),('r057c',.057,1036,1287),('r588',.588,1137,1260),
 ('r0122b',.0122,1260,1230),('r0122c',.0122,1053,1351),('r042a',.042,1047,1401),('r2',.2,413,1418),
]
nodes={
 'hyperiids':(120,768,316,834),'chaetognaths':(378,766,576,834),'salmon':(665,768,844,833),'squid_III':(987,768,1162,838),
 'herring':(117,892,240,958),'smelt':(282,892,476,960),'pollock_small':(504,891,770,963),'capelin':(817,892,919,962),'jellyfish':(961,893,1161,962),
 'pollock_medium':(155,1095,446,1161),'squid_IV':(554,1096,769,1163),'predatory_salmon':(896,1094,1170,1162),
 'baleen_whales':(555,1254,785,1319),'pollock_large':(116,1373,380,1441),'predatory_fish':(561,1454,793,1521),'predatory_mammals':(895,1513,1158,1625),
 'copepods':(249,406,509,474),'euphausiids':(802,406,1062,473)
}
def closest(p):
 def d(bb):
  x,y=p;a,b,c,d=bb
  return math.hypot(max(a-x,0,x-c),max(b-y,0,y-d))
 name=min(nodes,key=lambda k:d(nodes[k]))
 return name,round(d(nodes[name]),1)
out=[]
for name,value,x,y in labels:
 t=trace('red',(x,y),name,save=True)
 out.append(dict(label_id=name,value=value,seed=[x,y],end_candidates=[closest(p) for p in t['ends']],endpoints=t['ends']))
 print(name,value,t['ends'],[closest(p) for p in t['ends']])
(HERE/'audit/automatic_trace_candidates.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
