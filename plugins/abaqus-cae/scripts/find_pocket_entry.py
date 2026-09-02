from odbAccess import openOdb
import sys
odb=openOdb(sys.argv[1],readOnly=True)
for stepname,target in (('Shot2_ToPocket','RACKBALL11'),('Shot3_ToPocket','RACKBALL15')):
    if stepname not in odb.steps: continue
    inst=odb.rootAssembly.instances[target]; coords={n.label:n.coordinates for n in inst.nodes}
    for k,f in enumerate(odb.steps[stepname].frames):
        vals=f.fieldOutputs['U'].getSubset(region=inst).values; z=sum(coords[v.nodeLabel][2]+v.data[2] for v in vals)/len(vals)
        if z<20.0:
            print('%s entry_frame=%d step_time=%.4f z=%.2f'%(target,k,f.frameValue,z)); break
odb.close()
