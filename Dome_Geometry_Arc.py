# FEM Code for Dome Bistbale Map
# Juan Camilo Osorio
# Programmable Structures Lab - Purdue University
# 10/18/2022
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
## Simulation
##=======================================================================================================================
filename = 'Dome_Geometry_1'

##=======================================================================================================================
## MODEL
##=======================================================================================================================
mdb.Model(modelType=STANDARD_EXPLICIT, name=filename)
dome_model = mdb.models[filename]

##=======================================================================================================================
## INPUT PARAMETERS
##=======================================================================================================================
th = 0.6			# [mm] Thickness
H = 6.0                         # [mm] Dome height
base = 16.0                     # [mm] Dome base diameter
Unit_Cell = 22.0

R_ch = 8.5

##=======================================================================================================================
## GEOMETRIC PARAMETERS
##=======================================================================================================================
Outer_Ring = Unit_Cell              # [mm] Chamber base diameter
mesh_size = base/15
inv_time = 10
relax_time = 1
vel_factor = 2.3

##=======================================================================================================================
## MATERIAL PARAMETERS
##=======================================================================================================================
nameM1 = "Material"
Elas = 12.0  # Elastic Modulus [MPa]
vp = 0.35  # Poisson Ratio [-]
rho = 1.22e-9  # Material Density [Ton/mm^3]

##=======================================================================================================================
## GEOMETRY CONSTRUCTION (DOME)
##=======================================================================================================================
sketch1 = dome_model.ConstrainedSketch(name='Dome_Geo', sheetSize=200.0)
sketch1.setPrimaryObject(option=STANDALONE)

G = sketch1.geometry
V = sketch1.vertices

# CALCULATE DOME RADIUS
R1 = (H**2 + (base / 2) ** 2) / (2 * H)

# CALCULATE ARCHES MIDDLE POINTS
theta1 = np.arcsin((base / 2) / R1)

x1 = R1 * np.sin(theta1 / 2)
y1 = R1 * np.cos(theta1 / 2) - (R1 - H)

## CONSTRUCTION LINES
sketch1.ConstructionLine(point1=(0.0, 0.0), point2=(0.0, 20.0))
sketch1.Line(point1=(base / 2, 0), point2=(Outer_Ring, 0))
sketch1.Arc3Points(point1=(0.0, H), point2=(base / 2, 0.0), point3=(x1, y1))

## REVOLUTION -------------------------------------------------------
P = dome_model.Part(name="Dome", dimensionality=THREE_D, type=DEFORMABLE_BODY)
P.BaseShellRevolve(sketch=sketch1, angle=360.0, flipRevolveDirection=OFF)
del dome_model.sketches['Dome_Geo']

## CUT UNITCELL  -------------------------------------------------------
p = dome_model.parts["Dome"]
f, e, d = p.faces, p.edges, p.datums
f_cut = f.getClosest(coordinates=(((Outer_Ring/2,0,Outer_Ring/2)),))
e_cut = e.getClosest(coordinates=(((Outer_Ring/2,0,Outer_Ring/2)),))

t = p.MakeSketchTransform(sketchPlane=f[f_cut[0][0].index], sketchUpEdge=e[e_cut[0][0].index], 
        sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0, 
        0.0, 0))
s = dome_model.ConstrainedSketch(name='unit_cell_cut', 
        sheetSize=84.85, gridSpacing=2.12, transform=t)
s.rectangle(point1=(-Unit_Cell/2, -Unit_Cell/2), point2=(Unit_Cell/2, Unit_Cell/2))
s.CircleByCenterPerimeter(center=(0, 0), point1=(Outer_Ring, 0))
p.CutExtrude(sketchPlane=f[f_cut[0][0].index], sketchUpEdge=e[e_cut[0][0].index], sketchPlaneSide=SIDE1, 
        sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)

del dome_model.sketches['unit_cell_cut']


## CREATE DOME BASED PARTITION -------------------------------------------------------
t = P.MakeSketchTransform(
sketchPlane=f.findAt((-base/2-0.1,0,0,)), 
sketchUpEdge=e.findAt((-Unit_Cell/2,0,0,)), sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0)
)

s_partition = dome_model.ConstrainedSketch(
name="Base_Sketch", sheetSize=67.88, gridSpacing=1.69, transform=t
)

s_partition.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, R_ch))

s_partition.Line(point1=(-Unit_Cell/2, 0.0), point2=(Unit_Cell/2, 0.0))
s_partition.Line(point1=(0.0, -Unit_Cell/2), point2=(0.0, Unit_Cell/2))

pickedFaces = f.findAt(
(
        Unit_Cell / 2,
        0,
        Unit_Cell / 2,
)
)
P.PartitionFaceBySketch(sketchUpEdge=e.findAt((-Unit_Cell/2,0,0,)), 
                        faces=pickedFaces, sketch=s_partition)

del dome_model.sketches['Base_Sketch']

# ## CREATE DOME PARTITION -------------------------------------------------------
t = P.MakeSketchTransform(
sketchPlane=f.findAt((-base/2-0.1,0,0,)), 
sketchUpEdge=e.findAt((-Unit_Cell/2,0,0,)), sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0)
)

s_partition = dome_model.ConstrainedSketch(
name="Base_Sketch", sheetSize=67.88, gridSpacing=1.69, transform=t
)

s_partition.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, R_ch))

s_partition.Line(point1=(-Unit_Cell/2, 0.0), point2=(Unit_Cell/2, 0.0))
s_partition.Line(point1=(0.0, -Unit_Cell/2), point2=(0.0, Unit_Cell/2))

pickedFaces = f.getByBoundingCylinder(
        center1=(0.0, -0.1, 0.0), center2=(0.0, H, 0.0), radius=base/2 + 0.1)

p.PartitionFaceBySketchThruAll(sketchPlane=f.findAt((-base/2-0.1,0,0,)), sketchUpEdge=e.findAt((-Unit_Cell/2,0,0,)), 
faces=pickedFaces, sketchPlaneSide=SIDE1, sketch=s_partition)


del dome_model.sketches['Base_Sketch']

# =======================================================================================================================
# MATERIAL
# =======================================================================================================================
dome_model.Material(name=nameM1)
dome_model.materials[nameM1].Density(table=((rho,),))
dome_model.materials[nameM1].Elastic(table=((Elas, vp),))

##=======================================================================================================================
## MESH AND PARTITIONS
##=======================================================================================================================
mesh_size_metasheet = 1.0
dome_seeds_size = 0.75

seeds_tip = 6
seeds_wall = 6

seeds_inv_base_ring = 4
seeds_inv_base_ring_out = 2
seeds_top_wall = 6

shell_int_points = 5

##=======================================================================================================================
## CREATE SECTIONS
##=======================================================================================================================
dome_model.HomogeneousShellSection(name='Dome', 
       preIntegrate=OFF, material=nameM1, thicknessType=UNIFORM, thickness=th, 
       thicknessField='', nodalThicknessField='', 
       idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT, 
       thicknessModulus=None, temperature=GRADIENT, useDensity=OFF, 
       integrationRule=GAUSS, numIntPts=11)

##=======================================================================================================================
## SECTION ASSIGMENT
##=======================================================================================================================
f = P.faces

facesDome = f.getByBoundingBox(-Unit_Cell/2,-10,-Unit_Cell/2,Unit_Cell/2,2*H,Unit_Cell/2)
region = P.Set(faces=facesDome, name='Dome')
P.SectionAssignment(region=region, sectionName='Dome', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)

##=======================================================================================================================
## ASSEMBLY
##=======================================================================================================================
a = dome_model.rootAssembly
a.DatumCsysByDefault(CARTESIAN)

## DOME ========================
a.Instance(name='Dome_Assembly', part=P, dependent=ON)

##=======================================================================================================================
## BOUNDARY CONDITIONS SETS 
##=======================================================================================================================
BC_Dome = a.instances['Dome_Assembly']
e = BC_Dome.edges
v = BC_Dome.vertices

# BASE INVERSION
base_1 = e.findAt(((-Unit_Cell/2,0,Unit_Cell/4),))
base_2 = e.findAt(((-Unit_Cell/2,0,-Unit_Cell/4),))

base_3 = e.findAt(((Unit_Cell/2,0,Unit_Cell/4),))
base_4 = e.findAt(((Unit_Cell/2,0,-Unit_Cell/4),))

base_5 = e.findAt(((Unit_Cell/4,0,-Unit_Cell/2),))
base_6 = e.findAt(((-Unit_Cell/4,0,-Unit_Cell/2),))

base_7 = e.findAt(((Unit_Cell/4,0,Unit_Cell/2),))
base_8 = e.findAt(((-Unit_Cell/4,0,Unit_Cell/2),))

a.Set(edges=base_1 + base_2 + base_3 + base_4 + base_5 + base_6 + base_7 + base_8, name='UC_Base')

# Dome Tip RP
a.ReferencePoint(point=(0.0, H+1, 0.0))
RP_S = a.referencePoints
refPoints1=(RP_S[5], )
a.Set(referencePoints=refPoints1, name='Tip_RP')

##=======================================================================================================================
## SIMULATION STEP
##=======================================================================================================================
# STEP 1 -> Inversion
regionDef=dome_model.rootAssembly.sets['Tip_RP']
dome_model.StaticRiksStep(name='Inversion', previous='Initial',
    nodeOn=ON, maximumDisplacement=-2.0*H, region=regionDef, dof=2,
    maxNumInc=10000, initialArcInc=0.001, minArcInc=1e-8, maxArcInc=0.05,
    nlgeom=ON)

# Request OUTPUTS in these case we reduce the field variables to work with smaller files
save_n = 1 # Save every n time steps
dome_model.fieldOutputRequests['F-Output-1'].setValues(variables=(
        'S', 'EE', 'U', 'LE'),frequency=save_n)

##=======================================================================================================================
## COUPLING
##=======================================================================================================================
region1=a.sets['Tip_RP']
f_assem = a.instances['Dome_Assembly'].faces

side1Faces1 = f_assem.getByBoundingBox(-Unit_Cell/2,-10,-Unit_Cell/2,Unit_Cell/2,2*H,Unit_Cell/2)

region2=a.Surface(side1Faces=side1Faces1, name='Dome_Snap_Surface')
dome_model.Coupling(name='Coupling', controlPoint=region1, 
                    surface=region2, influenceRadius=H-th/2, couplingType=DISTRIBUTING, 
                    weightingMethod=LINEAR, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=OFF, ur2=OFF, ur3=OFF)

##=======================================================================================================================
## BOUNDARY CONDITIONS
##=======================================================================================================================
## BC Base ===================================
region = a.sets['UC_Base']
dome_model.DisplacementBC(name='UC_Base', createStepName='Inversion', region=region,u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, 
                          ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

region = a.sets['Tip_RP']
dome_model.DisplacementBC(name='Inversion', createStepName='Inversion',
    region=a.sets['Tip_RP'],
    u1=UNSET, u2=-vel_factor*H, u3=UNSET,
    ur1=UNSET, ur2=UNSET, ur3=UNSET,
    amplitude=UNSET, fixed=OFF, distributionType=UNIFORM,
    fieldName='', localCsys=None)


# =======================================================================================================================
# MESH
# =======================================================================================================================
p = dome_model.parts["Dome"]
p.seedPart(size=mesh_size_metasheet, deviationFactor=0.1, minSizeFactor=0.1)

f = p.faces
e = p.edges

# DOMAIN STRUCTURE
pickedRegions = f.getByBoundingBox(
    -Unit_Cell/2,
    -1,
    -Unit_Cell/2,
    Unit_Cell/2,
    H,
    Unit_Cell/2,
)
p.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED)



for theta_part in [0, 90, 180, 270]:

        # Inv base 1 and 2 Seeds
        x_pick = (base / 2 + 0.1) * np.cos(np.deg2rad(theta_part + 45))
        z_pick = (base / 2 + 0.1) * np.sin(np.deg2rad(theta_part + 45))

        pickedRegions = f.findAt(((x_pick, 0, z_pick),))
        p.setMeshControls(
        regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED
        )

        x_pick = (R_ch + 0.1) * np.cos(np.deg2rad(theta_part + 45))
        z_pick = (R_ch + 0.1) * np.sin(np.deg2rad(theta_part + 45))

        pickedRegions = f.findAt(((x_pick, 0, z_pick),))
        p.setMeshControls(
        regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED
        )

        # Dome Mesh Size
        x_pick = (base / 2) * np.cos(np.deg2rad(theta_part))
        z_pick = (base / 2) * np.sin(np.deg2rad(theta_part))

        pickedEdges = e.getClosest(
        coordinates=((x_pick, 0.01, z_pick),)
        )

        p.seedEdgeBySize(
        edges=(pickedEdges[0][0],),
        size=dome_seeds_size,
        deviationFactor=0.1,
        minSizeFactor=0.1,
        constraint=FINER,
        )

        x_pick = (base / 2) * np.cos(np.deg2rad(theta_part+45))
        z_pick = (base / 2) * np.sin(np.deg2rad(theta_part+45))

        pickedEdges = e.getClosest(
        coordinates=((x_pick, 0.0, z_pick),)
        )

        p.seedEdgeBySize(
        edges=(pickedEdges[0][0],),
        size=dome_seeds_size,
        deviationFactor=0.1,
        minSizeFactor=0.1,
        constraint=FINER,
        )


        # Circ base Seeds
        x_pick = (base / 2 + 0.1) * np.cos(np.deg2rad(theta_part))
        z_pick = (base / 2 + 0.1) * np.sin(np.deg2rad(theta_part))

        pickedEdges = e.getClosest(
        coordinates=((x_pick, 0, z_pick),)
        )
        p.seedEdgeByNumber(
        edges=(pickedEdges[0][0],), number=seeds_inv_base_ring, constraint=FINER
        )

        x_pick = (R_ch + 0.1) * np.cos(np.deg2rad(theta_part))
        z_pick = (R_ch + 0.1) * np.sin(np.deg2rad(theta_part))

        pickedEdges = e.getClosest(
        coordinates=((x_pick, 0, z_pick),)
        )
        p.seedEdgeByNumber(
        edges=(pickedEdges[0][0],), number=seeds_inv_base_ring_out, constraint=FINER
        )


p.generateMesh()


##=======================================================================================================================
## HISTORY REQUEST FOR ANALYSIS
##=======================================================================================================================
regionDef=dome_model.rootAssembly.sets['Tip_RP']
regionDef=dome_model.HistoryOutputRequest(name='H-Output-2', 
        createStepName='Inversion', variables=('U2', 'RF2'), frequency=1, 
        region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
        
##=======================================================================================================================
## JOB SUBMISSION
##=======================================================================================================================
mdb.Job(name=filename, model=filename, description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=4, 
    numDomains=4, numGPUs=0)
