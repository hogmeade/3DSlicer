import os
import sys
# Directories
segDir = "/home/hp/slicer/prostate"
rootDir = "/home/hp/slicer/"
reviewDir = "/home/hp/slicer/anns07"
expDir = "/home/hp/slicer/anns08"
# Hot keys
restart_hotkey    	= "Ctrl+Shift+R" # Restart 3D Slicer
rectum_seg_hotkey 	= "Ctrl+Shift+A" # Run rectum segmentation
toggle_select_hotkey    = "T" # Toggle select segment and its visibility
review_segment_hotkey      = "Ctrl+Shift+Q"
export_hotkey = "Ctrl+Shift+S"

# Restart
shortcut = qt.QShortcut(qt.QKeySequence(restart_hotkey), slicer.util.mainWindow())
shortcut.connect('activated()', slicer.util.restart)

# Rectum segmentation
sys.path.append(os.path.abspath(rootDir))
from rectum_seg import rectum_seg
shortcut1 = qt.QShortcut(qt.QKeySequence(rectum_seg_hotkey), slicer.util.mainWindow())
shortcut1.connect('activated()', lambda: rectum_seg(segDir))

# Toggle select segment and its visibility
from utils import toggleSelectSegment
shortcut2 = qt.QShortcut(qt.QKeySequence(toggle_select_hotkey), slicer.util.mainWindow())
shortcut2.connect('activated()', lambda: toggleSelectSegment())

# Rectum segmentation review
sys.path.append(os.path.abspath(segDir))
from rectum_seg import review_rectum_seg_nrrd
shortcut3 = qt.QShortcut(qt.QKeySequence(review_segment_hotkey), slicer.util.mainWindow())
shortcut3.connect('activated()', lambda: review_rectum_seg_nrrd(reviewDir))

# Toggle select segment and its visibility
from utils import exportLabelmap
shortcut4 = qt.QShortcut(qt.QKeySequence(export_hotkey), slicer.util.mainWindow())
shortcut4.connect('activated()', lambda: exportLabelmap(expDir))

# Set maximum panel size, prevent autoscaling panel too big with long filename
mainWindow = slicer.util.mainWindow()
modulePanelDockWidget = mainWindow.findChildren('QDockWidget','PanelDockWidget')[0]
modulePanelDockWidget.setMaximumWidth(700)
modulePanelDockWidget.setMinimumWidth(0)

# Run python file in Python Interactor
# exec(open("/home/huong/Programs/Slicer 3D/rectum_seg.py").read())
