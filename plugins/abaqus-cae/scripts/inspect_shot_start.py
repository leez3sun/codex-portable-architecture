from odbAccess import openOdb
odb=openOdb('ContinuousThreeShots.odb',readOnly=True)
for stepname,target in (('Shot2_CueStrike','RACKBALL11'),('Shot3_CueStrike','RACKBALL15')):
 f=odb.steps[stepname].frames[0]; inst=odb.rootAssembly.instances[target]; c={n.label:n.coordinates for n in inst.nodes}; u=f.fieldOutputs['U'].getSubset(region=inst).values
 p=[(c[v.nodeLabel][0]+v.data[0],c[v.nodeLabel][1]+v.data[1],c[v.nodeLabel][2]+v.data[2]) for v in u]
 ctr=tuple(sum(x[i] for x in p)/len(p) for i in range(3)); print(stepname,target,ctr)
odb.close()
