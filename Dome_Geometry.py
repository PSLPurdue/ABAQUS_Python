##=======================================================================================================================
from abaqus import *
from abaqusConstants import *
import __main__

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

import numpy as np
import csv
import sys

##=======================================================================================================================
## GEOMETRIC PARAMETERS
##=======================================================================================================================
H = 6.0                    # [mm] Dome height (H<=base/2)
th = 0.6			       # [mm] Dome thickness
base = 16.0                # [mm] Dome base diameter
Unit_Cell = 20.0           # [mm] Unit cell dimmension
base_dif = 20.0            # [mm] Ring for dome inversion

##=======================================================================================================================
## Simulation
##=======================================================================================================================
filename = 'Dome_Unit_Cell'

##=======================================================================================================================
## MODEL
##=======================================================================================================================
mdb.Model(modelType=STANDARD_EXPLICIT, name=filename)
dome_model = mdb.models[filename]

##=======================================================================================================================
## GEOMETRY CONSTRUCTION (DOME)
##=======================================================================================================================

sketch1 = dome_model.ConstrainedSketch(name='Dome_Sketch', sheetSize=200.0)
sketch1.setPrimaryObject(option=STANDALONE)

G = sketch1.geometry
V = sketch1.vertices

## CONSTRUCTION LINES
sketch1.ConstructionLine(point1=(0.0, 0.0), point2=(0.0, 20.0))
sketch1.ConstructionLine(point1=(0.0, 0.0), point2=(100.0, 0.0))
sketch1.ConstructionLine(point1=(0.0, H), point2=(100.0, H))

## BASE LINE
sketch1.Line(point1=(base/2, 0), point2=(Unit_Cell, 0))

## DOME ARC
sketch1.Arc3Points(point1=(0.0, H), point2=(base/2, 0.0), point3=(base/4, 0.8*H))
sketch1.TangentConstraint(entity1=G[4], entity2=G[6])

## REVOLUTION
sketch1.assignCenterline(line=G[2])
P = dome_model.Part(name='Dome', dimensionality=THREE_D, type=DEFORMABLE_BODY)
P.BaseShellRevolve(sketch=sketch1, angle=360.0, flipRevolveDirection=OFF)

## CUT UNIT CELL
f, e = P.faces, P.edges

t = P.MakeSketchTransform(sketchPlane=f[0], sketchUpEdge=e[0], 
        sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))

scut = dome_model.ConstrainedSketch(name='Cut_Profile', 
        sheetSize=140.0, gridSpacing=4.0, transform=t)

scut.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, -Unit_Cell))
scut.rectangle(point1=(-Unit_Cell/2, -Unit_Cell/2), point2=(Unit_Cell/2, Unit_Cell/2))

P.CutExtrude(sketchPlane=f[0], sketchUpEdge=e[0], sketchPlaneSide=SIDE1, 
        sketchOrientation=RIGHT, sketch=scut, flipExtrudeDirection=OFF)

## POINT PARTITION
pickedEdges = e.findAt(((-Unit_Cell/2,0,0),))
P.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)

pickedEdges = e.findAt(((0,0,-Unit_Cell/2),))
P.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)

pickedEdges = e.findAt(((0,0,Unit_Cell/2),))
P.PartitionEdgeByParam(edges=pickedEdges, parameter=0.5)
