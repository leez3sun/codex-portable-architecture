from odbAccess import openOdb
import math, json

odb=openOdb('01_BreakRack.odb',readOnly=True); step=odb.steps['Shot']; f=step.frames[-1]
pockets=[(-1217,-582),(0,-582),(1217,-582),(-1217,582),(0,582),(1217,582)]
balls=[]
for name,inst in odb.rootAssembly.instances.items():
    if 'BALL' not in name or name=='CUEBALLWHITE': continue
    coords={n.label:n.coordinates for n in inst.nodes}
    u=f.fieldOutputs['U'].getSubset(region=inst); v=f.fieldOutputs['V'].getSubset(region=inst)
    pts=[]
    for z in u.values:
        c=coords[z.nodeLabel]; pts.append((c[0]+z.data[0],c[1]+z.data[1],c[2]+z.data[2]))
    ctr=tuple(sum(p[i] for p in pts)/len(pts) for i in range(3))
    vel=sum((z.data[0]**2+z.data[1]**2+z.data[2]**2)**0.5 for z in v.values)/len(v.values)
    if abs(ctr[0])<1180 and abs(ctr[1])<545 and ctr[2]>0: balls.append({'name':name,'center':ctr,'speed':vel})

candidates=[]
for b in balls:
    for p in pockets:
        dx=p[0]-b['center'][0]; dy=p[1]-b['center'][1]; d=(dx*dx+dy*dy)**0.5
        blocked=False
        for o in balls:
            if o is b: continue
            ox=o['center'][0]-b['center'][0]; oy=o['center'][1]-b['center'][1]
            t=(ox*dx+oy*dy)/(d*d)
            if 0<t<1 and ((ox-t*dx)**2+(oy-t*dy)**2)**0.5<65: blocked=True
        if not blocked: candidates.append((d,b,p))
candidates.sort(key=lambda x:x[0])
chosen=[]; used=set()
for d,b,p in candidates:
    if b['name'] not in used:
        chosen.append({'ball':b['name'],'center':b['center'],'pocket':p,'distance':d}); used.add(b['name'])
    if len(chosen)==2: break
print(json.dumps({'balls':balls,'shots':chosen},indent=2))
odb.close()
