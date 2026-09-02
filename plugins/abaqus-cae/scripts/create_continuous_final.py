from abaqus import mdb
from abaqusConstants import *
import os, math

root=os.path.abspath(os.path.join(os.getcwd(),'..','.agents','plugins','abaqus-cae','scripts'))
exec(compile(open(os.path.join(root,'create_three_shot_game.py'),'rb').read(),'create_three_shot_game.py','exec'))
m=mdb.models['BreakRack']; a=m.rootAssembly
for j in list(mdb.jobs.keys()): del mdb.jobs[j]

# Actual stable locations measured from the corrected break calibration ODB.
shots=[('RackBall11',(803.8496,-178.8035),(1264.5,-565.7)),
       ('RackBall15',(929.5556,413.9118),(1217.0,582.0))]
previous='Shot'
travel_times={2:0.42,3:0.18}
for index,(ballname,pos,pocket) in enumerate(shots,2):
    pulse='Shot%d_CueStrike'%index; motion='Shot%d_ToPocket'%index; freeze='Shot%d_PocketedStill'%index
    m.ExplicitDynamicsStep(name=pulse,previous=previous,timePeriod=0.02,improvedDtMethod=ON)
    m.ExplicitDynamicsStep(name=motion,previous=pulse,timePeriod=travel_times[index],improvedDtMethod=ON)
    m.ExplicitDynamicsStep(name=freeze,previous=motion,timePeriod=1.20,improvedDtMethod=ON)
    inst=a.instances[ballname]; region=a.Set(name='Shot%dBall'%index,cells=inst.cells)
    nodes=a.Set(name='Shot%dBallNodes'%index,nodes=inst.nodes)
    dx,dy=pocket[0]-pos[0],pocket[1]-pos[1]; q=(dx*dx+dy*dy)**0.5
    # Separate yellow cue visual for each later stroke. It is 70 mm above the
    # cloth, so it is clearly visible but cannot disturb ball contact.
    cname='YELLOW_CUE_SHOT%d'%index; cinst=a.Instance(name=cname,part=m.parts['YELLOW_CUE_STICK'],dependent=ON)
    angle=math.degrees(math.atan2(dy,dx)); a.rotate(instanceList=(cname,),axisPoint=(0,0,0),axisDirection=(0,0,1),angle=angle)
    tip=(pos[0]-35.0*dx/q,pos[1]-35.0*dy/q,70.0); a.translate(instanceList=(cname,),vector=tip)
    crp=tuple(cinst.referencePoints.values())[0]; creg=a.Set(name=cname+'_RP',referencePoints=(crp,))
    bc=m.DisplacementBC(name=cname+'_MOVE',createStepName='Initial',region=creg,u1=0.0,u2=0.0,u3=0.0,ur1=0.0,ur2=0.0,ur3=0.0)
    bc.setValuesInStep(stepName=pulse,u1=80.0*dx/q,u2=80.0*dy/q)
    # density * acceleration; produces about 2.0 m/s over the 0.02 s pulse.
    bf=2.5e-4
    load=m.BodyForce(name='CuePulse%d'%index,createStepName=pulse,region=region,comp1=bf*dx/q,comp2=bf*dy/q)
    load.deactivate(motion)
    m.VelocityBC(name='PocketStop%d'%index,createStepName=freeze,region=nodes,v1=0.0,v2=0.0,v3=0.0)
    previous=freeze

job=mdb.Job(name='ContinuousThreeShots',model='BreakRack',type=ANALYSIS,
            explicitPrecision=SINGLE,nodalOutputPrecision=SINGLE,numCpus=1,numDomains=1)
target=os.path.join(os.getcwd(),'ContinuousThreeShots.cae')
mdb.saveAs(pathName=target); job.writeInput(consistencyChecking=OFF)
print('CREATED '+target)
