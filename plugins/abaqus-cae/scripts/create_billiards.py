from abaqus import mdb
from abaqusConstants import *
import mesh
import os

MODEL = 'BilliardCollision'
target = os.path.join(os.getcwd(), 'BilliardCollision.cae')
if os.path.exists(target):
    raise RuntimeError('Safety refusal: existing CAE file will not be modified: ' + target)
if MODEL in mdb.models: del mdb.models[MODEL]
m = mdb.Model(name=MODEL, modelType=STANDARD_EXPLICIT)

# SI-like millimetre-tonne-second units: 57.15 mm ball, 0.17 kg mass.
r = 28.575
s = m.ConstrainedSketch(name='BallProfile', sheetSize=200.0)
s.ConstructionLine(point1=(0.0, -50.0), point2=(0.0, 50.0))
s.ArcByCenterEnds(center=(0.0, 0.0), point1=(0.0, r), point2=(0.0, -r), direction=CLOCKWISE)
s.Line(point1=(0.0, r), point2=(0.0, -r))
p = m.Part(name='Ball', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseSolidRevolve(sketch=s, angle=360.0)
del m.sketches['BallProfile']

mat = m.Material(name='PhenolicResin')
mat.Density(table=((1.70e-9,),))
mat.Elastic(table=((9000.0, 0.30),))
m.HomogeneousSolidSection(name='BallSection', material='PhenolicResin')
p.SectionAssignment(region=p.Set(name='BallCells', cells=p.cells), sectionName='BallSection')
p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
p.setMeshControls(regions=p.cells, elemShape=TET, technique=FREE)
p.setElementType(regions=(p.cells,), elemTypes=(mesh.ElemType(elemCode=C3D10M, elemLibrary=EXPLICIT),))
p.generateMesh()

a = m.rootAssembly
a.DatumCsysByDefault(CARTESIAN)
i1 = a.Instance(name='CueBall', part=p, dependent=ON)
i2 = a.Instance(name='ObjectBall', part=p, dependent=ON)
a.translate(instanceList=('CueBall',), vector=(-31.0, 0.0, 0.0))
a.translate(instanceList=('ObjectBall',), vector=(31.0, 0.0, 0.0))
a.Set(name='CueBallAll', cells=i1.cells)
a.Set(name='ObjectBallAll', cells=i2.cells)

m.ExplicitDynamicsStep(name='Collision', previous='Initial', timePeriod=0.006, improvedDtMethod=ON)
m.ContactProperty('BallContact')
m.interactionProperties['BallContact'].TangentialBehavior(formulation=PENALTY, table=((0.05,),), maximumElasticSlip=FRACTION, fraction=0.005)
m.interactionProperties['BallContact'].NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON)
m.ContactExp(name='GeneralContact', createStepName='Initial')
m.interactions['GeneralContact'].includedPairs.setValuesInStep(stepName='Initial', useAllstar=ON)
m.interactions['GeneralContact'].contactPropertyAssignments.appendInStep(stepName='Initial', assignments=((GLOBAL, SELF, 'BallContact'),))
m.Velocity(name='CueVelocity', region=a.sets['CueBallAll'], velocity1=2000.0)

job = mdb.Job(name='BilliardCollision', model=MODEL, type=ANALYSIS, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, numCpus=2, numDomains=2)
mdb.saveAs(pathName=target)
job.writeInput(consistencyChecking=OFF)
print('CREATED: ' + os.path.join(os.getcwd(), 'BilliardCollision.cae'))
print('CREATED: ' + os.path.join(os.getcwd(), 'BilliardCollision.inp'))
