from abaqus import mdb
from abaqusConstants import *
import os

root=os.path.abspath(os.path.join(os.getcwd(),'..','.agents','plugins','abaqus-cae','scripts'))
exec(compile(open(os.path.join(root,'create_pool_game.py'),'rb').read(),'create_pool_game.py','exec'))
target=os.path.join(os.getcwd(),'ThreeShotPoolGame.cae')
if os.path.exists(target): raise RuntimeError('Safety refusal: '+target)
corner=mdb.models['PoolTableGame']
mdb.Model(name='ShotSidePocket',objectToCopy=corner)
mdb.Model(name='BreakRack',objectToCopy=corner)

def move(a,name,old,new):
    a.translate(instanceList=(name,),vector=(new[0]-old[0],new[1]-old[1],0.0))

old_obj=(700.0,350.0)
q=(517.0**2+232.0**2)**0.5
old_cue=(700.0-400.0*517.0/q,350.0-400.0*232.0/q)

side=mdb.models['ShotSidePocket']; a=side.rootAssembly
move(a,'ObjectBallRed',old_obj,(700.0,-350.0)); move(a,'CueBallWhite',old_cue,(old_cue[0],-old_cue[1]))
side.predefinedFields['CueStrike'].setValues(velocity1=1400.0*517.0/q,velocity2=-1400.0*232.0/q)
side.steps['Shot'].setValues(timePeriod=0.98)

br=mdb.models['BreakRack']; a=br.rootAssembly
move(a,'CueBallWhite',old_cue,(-300.0,0.0)); move(a,'ObjectBallRed',old_obj,(420.0,0.0))
br.predefinedFields['CueStrike'].setValues(velocity1=4000.0,velocity2=0.0)
br.steps['Shot'].setValues(timePeriod=1.80)
ball=br.parts['Ball3D']; spacing=57.8; n=2
palette=('YELLOW','BLUE','PURPLE','ORANGE','GREEN','MAROON','BLACK')
for row in range(1,5):
    x=420.0+row*spacing*0.866
    for j in range(row+1):
        y=(j-row/2.0)*spacing; name='RackBall%02d'%n; color=palette[(n-2)%len(palette)]
        sec=color+'_SECTION_%02d'%n; br.HomogeneousSolidSection(name=sec,material='GameBall')
        colored=br.Part(name=color+'_BALL_%02d'%n,objectToCopy=ball); colored.sectionAssignments[0].setValues(sectionName=sec)
        a.Instance(name=name,part=colored,dependent=ON)
        a.translate(instanceList=(name,),vector=(x,y,29.575)); n+=1

for old in list(mdb.jobs.keys()): del mdb.jobs[old]
for jn,mn in (('01_BreakRack','BreakRack'),('02_SidePocket','ShotSidePocket'),('03_CornerPocket','PoolTableGame')):
    j=mdb.Job(name=jn,model=mn,type=ANALYSIS,explicitPrecision=SINGLE,nodalOutputPrecision=SINGLE,numCpus=1,numDomains=1)
    j.writeInput(consistencyChecking=OFF)
mdb.saveAs(pathName=target)
print('CREATED '+target)
