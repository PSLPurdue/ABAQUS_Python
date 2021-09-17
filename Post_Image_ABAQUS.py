from abaqus import *
from abaqusConstants import *

import __main__
import visualization
import xyPlot
import displayGroupOdbToolset as dgo

# LEGEND AND TRIAD FONT SIZE
Font_size = 12
# TRIAD POSITON (Change at will)
x, y = 8, 50

# ---------------------------------------------------------------------
# OBJECTS
# ---------------------------------------------------------------------
viewport = session.viewports["Viewport: 1"]
gOption = session.graphicsOptions

# ---------------------------------------------------------------------
# CONTOUR
# ---------------------------------------------------------------------

# DEFORMATION PLOT, legend style and font
viewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))
viewport.viewportAnnotationOptions.setValues(
    legendDecimalPlaces=2, legendNumberFormat=FIXED, legendBackgroundStyle=MATCH
)
viewport.viewportAnnotationOptions.setValues(
    triadFont="-*-verdana-bold-r-normal-*-*-"+str(Font_size)+"0-*-*-p-*-*-*",
    legendFont="-*-verdana-bold-r-normal-*-*-"+str(Font_size)+"0-*-*-p-*-*-*",
)
# REMOVE MESH (Feature Edges)
viewport.odbDisplay.commonOptions.setValues(visibleEdges=FEATURE)

# ---------------------------------------------------------------------
# PLOT STYLE
# ---------------------------------------------------------------------
# TRIAD POSITON
viewport.viewportAnnotationOptions.setValues(triadPosition=(x, y))

# BACKGROUND COLOR (WHITE)
gOption.setValues(backgroundStyle=SOLID, backgroundColor="#FFFFFF")

# REMOVE EXTRA STUFF
viewport.viewportAnnotationOptions.setValues(title=OFF)
viewport.viewportAnnotationOptions.setValues(state=OFF)
viewport.viewportAnnotationOptions.setValues(compass=OFF)
