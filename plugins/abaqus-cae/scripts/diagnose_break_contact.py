from odbAccess import openOdb
odb=openOdb('01_BreakRack.odb',readOnly=True); step=odb.steps['Shot']
names=('CUEBALLWHITE','OBJECTBALLRED')
for k,f in enumerate(step.frames):
    out=[]
    centers={}
    for name in names:
        inst=odb.rootAssembly.instances[name]; coords={n.label:n.coordinates for n in inst.nodes}
        u=f.fieldOutputs['U'].getSubset(region=inst); v=f.fieldOutputs['V'].getSubset(region=inst)
        pts=[(coords[z.nodeLabel][0]+z.data[0],coords[z.nodeLabel][1]+z.data[1],coords[z.nodeLabel][2]+z.data[2]) for z in u.values]
        c=tuple(sum(p[i] for p in pts)/len(pts) for i in range(3)); centers[name]=c
        sp=sum((z.data[0]**2+z.data[1]**2+z.data[2]**2)**0.5 for z in v.values)/len(v.values)
        out.append('%s x=%.1f v=%.1f'%(name,c[0],sp))
    a=centers[names[0]]; b=centers[names[1]]; gap=((a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2)**0.5-57.15
    print('frame=%02d t=%.3f gap=%.1f %s'%(k,f.frameValue,gap,' | '.join(out)))
odb.close()
