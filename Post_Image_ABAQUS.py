from abaqus import *
from abaqusConstants import *

import __main__
import visualization
import xyPlot
import displayGroupOdbToolset as dgo


# ---------------------------------------------------------------------
# LEGEND FONT SIZE
Font_size = 12

# TRIAD POSITON AND SIZE
x, y = 80, 15
Font_size_triad = 18
triad_size = 15

# COLORMAP
#colormap = 'Rainbow'
colormap = 'viridis'
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# OBJECTS
# ---------------------------------------------------------------------
viewport = session.viewports["Viewport: 1"]
gOption = session.graphicsOptions

# ---------------------------------------------------------------------
# ADD COLOR MAPS
# ---------------------------------------------------------------------
# Perceptually uniform sequential colormaps
colormaps = {'viridis': ['#440154', '#46317e', '#365c8d', '#277f8e', '#1fa287', '#49c26d', '#a0da39', '#fee724'],
             'plasma':  ['#0c0787', '#5301a3', '#8b09a5', '#b93289', '#dc5c68', '#f48849', '#febd2a', '#f0f921'],
             'inferno': ['#000003', '#270b53', '#65156e', '#9f2a63', '#d54841', '#f67d15', '#fbc228', '#fdffa5'],
             'magma':   ['#000003', '#221150', '#5f177f', '#982c80', '#d4436e', '#f9765c', '#ffbb81', '#fcfdbf'],
             'cividis': ['#00224e', '#213b6e', '#4c556c', '#6c6e72', '#8e8978', '#b2a570', '#d9c55c', '#fee837']}
 
# Colormaps are Spectrum objects in Abaqus/CAE
for name, colors in colormaps.items():
 
    # Spectrum with the colors in order
    session.Spectrum(name=name, colors=colors)
 
# Colormaps are Spectrum objects in Abaqus/CAE
for name, colors in colormaps.items():
 
    # Spectrum with the colors in reversed order
    session.Spectrum(name=name + 'R', colors=colors[::-1])

# ---------------------------------------------------------------------
# CONTOUR
# ---------------------------------------------------------------------
# DEFORMATION PLOT, legend style and font
viewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))
viewport.viewportAnnotationOptions.setValues(
    legendDecimalPlaces=2, legendNumberFormat=FIXED, legendBackgroundStyle=MATCH
)
viewport.viewportAnnotationOptions.setValues(
    triadFont="-*-verdana-bold-r-normal-*-*-"+str(Font_size_triad)+"0-*-*-p-*-*-*",
    legendFont="-*-verdana-bold-r-normal-*-*-"+str(Font_size)+"0-*-*-p-*-*-*",
)

viewport.viewportAnnotationOptions.setValues(legendBox=OFF, legendBackgroundStyle=TRANSPARENT)

# REMOVE MESH (Feature Edges)
viewport.odbDisplay.commonOptions.setValues(visibleEdges=FEATURE)
viewport.odbDisplay.basicOptions.setValues(curveRefinementLevel=EXTRA_FINE)

# ADD CONTINIUS CONTOUR
viewport.odbDisplay.contourOptions.setValues(contourStyle=CONTINUOUS)
viewport.odbDisplay.contourOptions.setValues(spectrum=colormap)

# ---------------------------------------------------------------------
# PLOT STYLE
# ---------------------------------------------------------------------
# TRIAD POSITON
viewport.viewportAnnotationOptions.setValues(triadPosition=(x, y))

# TRIAD SIZE
viewport.viewportAnnotationOptions.setValues(triadSize=triad_size)

# BACKGROUND COLOR (WHITE)
gOption.setValues(backgroundStyle=SOLID, backgroundColor="#FFFFFF")

# REMOVE EXTRA STUFF
viewport.viewportAnnotationOptions.setValues(title=OFF)
viewport.viewportAnnotationOptions.setValues(state=OFF)
viewport.viewportAnnotationOptions.setValues(compass=OFF)

# CHANGE VIEW
viewport.view.setValues(session.views['Iso'])
