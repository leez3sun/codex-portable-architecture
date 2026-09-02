from abaqus import session
from abaqusConstants import *
import visualization, os

odb=session.openOdb(name=os.path.join(os.getcwd(),'ContinuousThreeShots.odb'))
vp=session.Viewport(name='PoolGame',origin=(0,0),width=240,height=140)
vp.setValues(displayedObject=odb); vp.odbDisplay.display.setValues(plotState=(DEFORMED,))
vp.odbDisplay.commonOptions.setValues(visibleEdges=NONE)
vp.view.setValues(cameraPosition=(0.0,0.0,6000.0),cameraTarget=(0.0,0.0,0.0),cameraUpVector=(0.0,1.0,0.0)); vp.view.fitView()
vp.enableMultipleColors(); vp.setColor(initialColor='#087F3D'); cmap=vp.colorMappings['Part instance']
colors={'CUEBALLWHITE':'#FFFFFF','OBJECTBALLRED':'#E53935','YELLOW_CUE_STICK':'#FFD600',
        'YELLOW_CUE_SHOT2':'#FFD600','YELLOW_CUE_SHOT3':'#FFD600','GREENCLOTH':'#087F3D',
        'TOPL':'#FFFFFF','TOPR':'#FFFFFF','BOTTOML':'#FFFFFF','BOTTOMR':'#FFFFFF','LEFT':'#FFFFFF','RIGHT':'#FFFFFF'}
palette=('#FDD835','#1E88E5','#8E24AA','#FB8C00','#43A047','#6D1B1B','#202020')
for i in range(2,16): colors['RACKBALL%02d'%i]=palette[(i-2)%len(palette)]
overrides={}
for key,color in colors.items(): overrides[key]=(True,color,'Default',color)
cmap.updateOverrides(overrides=overrides); vp.setColor(colorMapping=cmap); vp.disableMultipleColors()
session.printOptions.setValues(rendition=COLOR)
session.printToFile(fileName='PoolGame_ColorPreview',format=PNG,canvasObjects=(vp,))
print('CREATED '+os.path.join(os.getcwd(),'PoolGame_ColorPreview.png'))
