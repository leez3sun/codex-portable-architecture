from odbAccess import openOdb
odb=openOdb('ContinuousThreeShots.odb',readOnly=True)
targets={'Shot2_PocketedStill':'RACKBALL11','Shot3_PocketedStill':'RACKBALL15'}
for sn,step in odb.steps.items():
    f=step.frames[-1]; speeds=[]
    for name,inst in odb.rootAssembly.instances.items():
        if 'BALL' not in name: continue
        vals=f.fieldOutputs['V'].getSubset(region=inst).values
        sp=sum((v.data[0]**2+v.data[1]**2+v.data[2]**2)**0.5 for v in vals)/len(vals); speeds.append(sp)
    line='%s frames=%d max_speed=%.4f'%(sn,len(step.frames),max(speeds))
    if sn in targets:
        inst=odb.rootAssembly.instances[targets[sn]]; coords={n.label:n.coordinates for n in inst.nodes}
        vals=f.fieldOutputs['U'].getSubset(region=inst).values; pts=[]
        for v in vals:
            c=coords[v.nodeLabel]; pts.append((c[0]+v.data[0],c[1]+v.data[1],c[2]+v.data[2]))
        ctr=tuple(sum(p[i] for p in pts)/len(pts) for i in range(3)); line+=' center=(%.1f,%.1f,%.1f)'%ctr
    print(line)
odb.close()
