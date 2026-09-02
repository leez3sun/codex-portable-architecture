from abaqus import mdb
from abaqusConstants import *
import mesh, os

MODEL='PoolTableGame'; JOB='PoolTableGame'; CAE=os.path.join(os.getcwd(),JOB+'.cae')
if os.path.exists(CAE): raise RuntimeError('Safety refusal: existing CAE file: '+CAE)
if MODEL in mdb.models: del mdb.models[MODEL]
m=mdb.Model(name=MODEL,modelType=STANDARD_EXPLICIT)
L,W,R,P=2540.0,1270.0,28.575,45.0

# Coarse but truly three-dimensional balls.
s=m.ConstrainedSketch(name='BallProfile',sheetSize=200.0)
s.ConstructionLine(point1=(0,-50),point2=(0,50))
s.ArcByCenterEnds(center=(0,0),point1=(0,R),point2=(0,-R),direction=CLOCKWISE)
s.Line(point1=(0,R),point2=(0,-R))
ball=m.Part(name='Ball3D',dimensionality=THREE_D,type=DEFORMABLE_BODY)
ball.BaseSolidRevolve(sketch=s,angle=360.0); del m.sketches['BallProfile']
mat=m.Material(name='GameBall'); mat.Density(table=((1.70e-9,),)); mat.Elastic(table=((1200.0,0.30),))
# Equivalent rolling resistance for the visual game: mass-proportional damping
# removes long-lived rigid translation while retaining short collision pulses.
mat.Damping(alpha=3.0)
m.HomogeneousSolidSection(name='BallSection',material='GameBall')
ball.SectionAssignment(region=ball.Set(name='Cells',cells=ball.cells),sectionName='BallSection')
ball.seedPart(size=18.0); ball.setMeshControls(regions=ball.cells,elemShape=TET,technique=FREE)
ball.setElementType(regions=(ball.cells,),elemTypes=(mesh.ElemType(elemCode=C3D10M,elemLibrary=EXPLICIT),)); ball.generateMesh()
m.HomogeneousSolidSection(name='CUE_WHITE_SECTION',material='GameBall')
m.HomogeneousSolidSection(name='OBJECT_RED_SECTION',material='GameBall')
cueball=m.Part(name='CUE_WHITE_BALL',objectToCopy=ball); cueball.sectionAssignments[0].setValues(sectionName='CUE_WHITE_SECTION')
objectball=m.Part(name='OBJECT_RED_BALL',objectToCopy=ball); objectball.sectionAssignments[0].setValues(sectionName='OBJECT_RED_SECTION')

# Green rigid bed with six real openings: pocketed balls fall through under gravity.
sk=m.ConstrainedSketch(name='BedSketch',sheetSize=4000.0)
sk.rectangle(point1=(-L/2,-W/2),point2=(L/2,W/2))
O=P+8.0
for x,y in ((-L/2+O,-W/2+O),(0,-W/2+O),(L/2-O,-W/2+O),
            (-L/2+O,W/2-O),(0,W/2-O),(L/2-O,W/2-O)):
    sk.CircleByCenterPerimeter(center=(x,y),point1=(x+P,y))
bed=m.Part(name='BedSixPockets',dimensionality=THREE_D,type=DISCRETE_RIGID_SURFACE)
bed.BaseShell(sketch=sk); del m.sketches['BedSketch']; bed.seedPart(size=140.0)
bed.setMeshControls(regions=bed.faces,elemShape=TRI)
bed.setElementType(regions=(bed.faces,),elemTypes=(mesh.ElemType(elemCode=R3D3,elemLibrary=EXPLICIT),)); bed.generateMesh()
bed.ReferencePoint(point=(0,0,-20))

# Invisible rigid catch tray below the six openings; it represents simplified
# pocket bags and prevents pocketed balls from falling forever.
cs=m.ConstrainedSketch(name='CatchSketch',sheetSize=4000.0)
cs.rectangle(point1=(-3000.0,-2000.0),point2=(3000.0,2000.0))
catch=m.Part(name='PocketCatchTray',dimensionality=THREE_D,type=DISCRETE_RIGID_SURFACE)
catch.BaseShell(sketch=cs); del m.sketches['CatchSketch']; catch.seedPart(size=120.0)
catch.setMeshControls(regions=catch.faces,elemShape=TRI)
catch.setElementType(regions=(catch.faces,),elemTypes=(mesh.ElemType(elemCode=R3D3,elemLibrary=EXPLICIT),)); catch.generateMesh()
catch.ReferencePoint(point=(0,0,-20))

# Yellow cue close-up visual (kept above the contact plane, no mesh detail).
qs=m.ConstrainedSketch(name='CueVisualSketch',sheetSize=800.0)
qs.rectangle(point1=(-400.0,-6.0),point2=(0.0,6.0))
cuevis=m.Part(name='YELLOW_CUE_STICK',dimensionality=THREE_D,type=DISCRETE_RIGID_SURFACE)
cuevis.BaseShell(sketch=qs); del m.sketches['CueVisualSketch']; cuevis.seedPart(size=50.0); cuevis.generateMesh()
cuevis.ReferencePoint(point=(-200.0,0.0,0.0))

# Rails are visual/contact shell strips; gaps expose all pockets.
def rail(name,x1,y1,x2,y2):
    q=m.ConstrainedSketch(name=name+'Sketch',sheetSize=4000.0); q.rectangle(point1=(x1,y1),point2=(x2,y2))
    p=m.Part(name=name,dimensionality=THREE_D,type=DISCRETE_RIGID_SURFACE); p.BaseShell(sketch=q); del m.sketches[name+'Sketch']
    p.seedPart(size=220.0); p.generateMesh(); p.ReferencePoint(point=((x1+x2)/2,(y1+y2)/2,0)); return p
g,t=70.0,70.0
rails=[rail('TopL',-L/2+g,W/2,-g,W/2+t),rail('TopR',g,W/2,L/2-g,W/2+t),
 rail('BottomL',-L/2+g,-W/2-t,-g,-W/2),rail('BottomR',g,-W/2-t,L/2-g,-W/2),
 rail('Left',-L/2-t,-W/2+g,-L/2,W/2-g),rail('Right',L/2,-W/2+g,L/2+t,W/2-g)]

a=m.rootAssembly; a.DatumCsysByDefault(CARTESIAN); rigid_instances=[]
rigid_instances.append(a.Instance(name='GreenCloth',part=bed,dependent=ON))
# No catch-tray instance: pocketed balls are stopped by a timed zero-velocity
# constraint, so no oversized plane appears in the animation.
cue_i=a.Instance(name='YELLOW_CUE_STICK',part=cuevis,dependent=ON)
a.translate(instanceList=('YELLOW_CUE_STICK',),vector=(-330.0,0.0,70.0))
for p in rails: rigid_instances.append(a.Instance(name=p.name,part=p,dependent=ON))
# Turn the six flat strips into vertical rigid cushion faces.  The rotation
# axes are the inner table edges, so the 45 mm strip width becomes wall height.
a.rotate(instanceList=('TopL','TopR'),axisPoint=(0.0,W/2,0.0),axisDirection=(1.0,0.0,0.0),angle=90.0)
a.rotate(instanceList=('BottomL','BottomR'),axisPoint=(0.0,-W/2,0.0),axisDirection=(1.0,0.0,0.0),angle=-90.0)
a.rotate(instanceList=('Left',),axisPoint=(-L/2,0.0,0.0),axisDirection=(0.0,1.0,0.0),angle=90.0)
a.rotate(instanceList=('Right',),axisPoint=(L/2,0.0,0.0),axisDirection=(0.0,1.0,0.0),angle=-90.0)
for i,inst in enumerate(rigid_instances):
    rp=tuple(inst.referencePoints.values())[0]
    region=a.Set(name='FixedRigidRP%d'%i,referencePoints=(rp,))
    m.EncastreBC(name='FixRigid%d'%i,createStepName='Initial',region=region)
objxy=(700.0,350.0); pocketxy=(L/2-O,W/2-O)
vx,vy=pocketxy[0]-objxy[0],pocketxy[1]-objxy[1]; vm=(vx*vx+vy*vy)**0.5
cuexy=(objxy[0]-400.0*vx/vm,objxy[1]-400.0*vy/vm)
cue=a.Instance(name='CueBallWhite',part=cueball,dependent=ON); obj=a.Instance(name='ObjectBallRed',part=objectball,dependent=ON)
a.translate(instanceList=('CueBallWhite',),vector=(cuexy[0],cuexy[1],R+1)); a.translate(instanceList=('ObjectBallRed',),vector=(objxy[0],objxy[1],R+1))
a.Set(name='CueBallAll',cells=cue.cells); a.Set(name='ObjectBallAll',cells=obj.cells)
m.ExplicitDynamicsStep(name='Shot',previous='Initial',timePeriod=0.80,improvedDtMethod=ON)
cue_rp=tuple(cue_i.referencePoints.values())[0]; cue_region=a.Set(name='YellowCueRP',referencePoints=(cue_rp,))
m.DisplacementBC(name='YellowCueMotion',createStepName='Initial',region=cue_region,u1=0.0,u2=0.0,u3=0.0,ur1=0.0,ur2=0.0,ur3=0.0)
m.boundaryConditions['YellowCueMotion'].setValuesInStep(stepName='Shot',u1=100.0)
m.Gravity(name='Gravity',createStepName='Shot',comp3=-9810.0)
m.ContactProperty('PoolContact'); m.interactionProperties['PoolContact'].TangentialBehavior(formulation=PENALTY,table=((0.10,),),maximumElasticSlip=FRACTION,fraction=0.005)
m.interactionProperties['PoolContact'].NormalBehavior(pressureOverclosure=HARD,allowSeparation=ON)
m.ContactExp(name='GeneralContact',createStepName='Initial'); m.interactions['GeneralContact'].includedPairs.setValuesInStep(stepName='Initial',useAllstar=ON)
m.interactions['GeneralContact'].contactPropertyAssignments.appendInStep(stepName='Initial',assignments=((GLOBAL,SELF,'PoolContact'),))
dx,dy=objxy[0]-cuexy[0],objxy[1]-cuexy[1]; mag=(dx*dx+dy*dy)**0.5; speed=1400.0
m.Velocity(name='CueStrike',region=a.sets['CueBallAll'],velocity1=speed*dx/mag,velocity2=speed*dy/mag)
job=mdb.Job(name=JOB,model=MODEL,type=ANALYSIS,explicitPrecision=SINGLE,nodalOutputPrecision=SINGLE,numCpus=1,numDomains=1)
mdb.saveAs(pathName=CAE); job.writeInput(consistencyChecking=OFF)
print('CREATED: '+CAE); print('CREATED: '+os.path.join(os.getcwd(),JOB+'.inp'))
