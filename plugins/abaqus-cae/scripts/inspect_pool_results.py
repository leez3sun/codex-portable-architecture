from odbAccess import openOdb
import os

odb=openOdb('PoolTableGame.odb',readOnly=True)
step=odb.steps['Shot']; frame=step.frames[-1]
for name in ('CUEBALLWHITE','OBJECTBALLRED'):
    inst=odb.rootAssembly.instances[name]
    u=frame.fieldOutputs['U'].getSubset(region=inst)
    coords={n.label:n.coordinates for n in inst.nodes}
    pts=[]
    for v in u.values:
        c=coords[v.nodeLabel]; pts.append((c[0]+v.data[0],c[1]+v.data[1],c[2]+v.data[2]))
    center=tuple(sum(p[i] for p in pts)/len(pts) for i in range(3))
    print('%s_CENTER %.3f %.3f %.3f'%((name,)+center))
for region in step.historyRegions.values():
    if 'ALLKE' in region.historyOutputs:
        data=region.historyOutputs['ALLKE'].data
        print('KINETIC_ENERGY_INITIAL %.6g'%data[0][1]); print('KINETIC_ENERGY_FINAL %.6g'%data[-1][1]); break
odb.close()
