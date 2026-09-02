from odbAccess import openOdb
import sys

for path in ('01_BreakRack.odb','02_SidePocket.odb','03_CornerPocket.odb'):
    odb=openOdb(path,readOnly=True); step=odb.steps['Shot']; first=step.frames[0]; last=step.frames[-1]
    moved=[]
    for name,inst in odb.rootAssembly.instances.items():
        if not ('BALL' in name): continue
        vals=last.fieldOutputs['U'].getSubset(region=inst).values
        mag=sum((v.data[0]**2+v.data[1]**2+v.data[2]**2)**0.5 for v in vals)/len(vals)
        moved.append((mag,name))
    obj=odb.rootAssembly.instances['OBJECTBALLRED']; u=last.fieldOutputs['U'].getSubset(region=obj)
    coords={n.label:n.coordinates for n in obj.nodes}; pts=[]
    for v in u.values:
        c=coords[v.nodeLabel]; pts.append((c[0]+v.data[0],c[1]+v.data[1],c[2]+v.data[2]))
    ctr=tuple(sum(p[i] for p in pts)/len(pts) for i in range(3))
    print('%s frames=%d moving_balls=%d object_center=(%.1f,%.1f,%.1f) max_move=%.1f'%
          (path,len(step.frames),sum(1 for x,n in moved if x>5.0),ctr[0],ctr[1],ctr[2],max(x for x,n in moved)))
    odb.close()
