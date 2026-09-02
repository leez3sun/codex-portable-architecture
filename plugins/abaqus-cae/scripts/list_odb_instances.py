from odbAccess import openOdb
o=openOdb('ContinuousThreeShots.odb',readOnly=True)
for n in o.rootAssembly.instances.keys(): print(n)
o.close()
