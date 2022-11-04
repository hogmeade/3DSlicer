def rectum_seg(rootDir):  
  import os 
  import qt
  import slicer
  import pandas as pd
  # Clean up workspace
  slicer.mrmlScene.Clear(0)

  # Change height of Python Interactor
  pyConsoleDockWidget = slicer.util.mainWindow().findChildren('QDockWidget','PythonConsoleDockWidget')[0]
  slicer.util.mainWindow().resizeDocks([pyConsoleDockWidget],[1000], qt.Qt.Vertical)

  # Get all scan directories
  subDirs = []
  for rootdir, dirs, files in os.walk(rootDir):
    for subDir in dirs:
      if "setra" in subDir:
        subDirs.append(os.path.join(rootdir, subDir))
        #subDirs.append(rootDir.split("/")[5]+"/"+subDir)
  # Sort out the directory names by their initial
  subDirs = sorted(subDirs, key=lambda x: int(x.split("/")[9][-4:]))
  # rootdir.split("/")[9][-4:])
  # Please out Scan IDs
  for i in range(len(subDirs)):
    print("%d - %s"%(i,subDirs[i]))

  # Choose Scan number
  #scanNumber = int(input("Choose scan number... "))
  #print("Choosen number: %s"%(scanNumber))
  #print("Loaded Scan ID: %s"%(subDirs[scanNumber]))
  hisFile = os.path.join(rootDir,"rectum","his.csv")

  if not os.path.exists(os.path.join(rootDir,"rectum")):
      os.makedirs(os.path.join(rootDir,"rectum"))
  if os.path.isfile(hisFile):
    df = pd.read_csv(hisFile)
    scanNumber = df["done"].iloc[-1] + 1
  else:
    df = pd.DataFrame({"done":[0]})
    scanNumber = 0
    df.to_csv(hisFile, index = False)

  # Change height of Python Interactor
  slicer.util.mainWindow().resizeDocks([pyConsoleDockWidget],[200], qt.Qt.Vertical) 

  # Input folder with DICOM files
  dicomDataDir = subDirs[scanNumber]

  # This list will contain the list of all loaded node IDs
  loadedNodeIDs = []  

  from DICOMLib import DICOMUtils
  with DICOMUtils.TemporaryDICOMDatabase() as db:
    DICOMUtils.clearDatabase(db)
    DICOMUtils.importDicom(dicomDataDir, db)
    patientUIDs = db.patients()
    for patientUID in patientUIDs:
      loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))

  # Open segment editor view
  slicer.util.mainWindow().moduleSelector().selectModule('SegmentEditor')

  # Create segments
  segmentationNode = slicer.util.getNode('Segmentation')

  # Create segments and their opacity
  seedsID = segmentationNode.GetSegmentation().AddEmptySegment("Seeds")
  boundariesID = segmentationNode.GetSegmentation().AddEmptySegment("Boundaries")

  # Set opacity
  segmentationDisplayNode = segmentationNode.GetDisplayNode()
  segmentationDisplayNode.SetOpacity(0.5)
  segmentationDisplayNode.SetOpacity2DOutline(1)

  # Choose the paint effect and its size
  segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
  segmentEditorWidget.setActiveEffectByName("Paint")

  # Change brush size
  paintEffect = segmentEditorWidget.effectByName("Paint")
  paintEffect.setCommonParameter("BrushRelativeDiameter", 2)
  
  # Select the segment
  segmentEditorNode = segmentEditorWidget.mrmlSegmentEditorNode()
  segmentEditorNode.SetSelectedSegmentID(seedsID)
  # selectedStartSegmentID = segmentEditorNode.GetSelectedSegmentID() 

  print("Working on case number: ", scanNumber)
  print("Please draw the seeds and boundaries of the segmentation.")
  try:
    pressedKey = input("Press Enter to continue to image processing...")
  except:
    pass

  ################################################ Image Processing ##########################################################

  # Create segment editor to get access to effects
  segmentationNode  = slicer.util.getNode('Segmentation')
  segmentEditorNode = slicer.util.getNode('SegmentEditor')
  masterVolumeNode  = segmentEditorNode.GetMasterVolumeNode()
  
  # This should be the name of "name.nrrd" segmentation
  segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()

  # To show segment editor widget (useful for debugging): segmentEditorWidget.show()
  segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
  segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
  slicer.mrmlScene.AddNode(segmentEditorNode)
  segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)

  segmentEditorWidget.setSegmentationNode(segmentationNode)
  segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)

  #segmentEditorWidget.setActiveEffectByName("Paint")
  #effect = segmentEditorWidget.activeEffect()
  #effect.setParameter("BrushAbsoluteDiameter","5")

  # set visibility for 2 segments for growing region
  segmentationDisplayNode.SetAllSegmentsVisibility(True)

  # Run segmentation - Grow from seeds
  segmentEditorWidget.setActiveEffectByName("Grow from seeds")
  effect = segmentEditorWidget.activeEffect()
  effect.self().onPreview()
  effect.self().onApply()

  # Delete Islands
  segmentEditorWidget.setActiveEffectByName("Islands")
  effect = segmentEditorWidget.activeEffect()
  effect.setParameter("MinimumSize","1000")
  effect.setParameter("Operation","KEEP_LARGEST_ISLAND")
  effect.self().onApply()

  # Gaussian Smoothing
  segmentEditorWidget.setActiveEffectByName("Smoothing")
  effect = segmentEditorWidget.activeEffect()
  effect.setParameter("SmoothingMethod", "GAUSSIAN")
  effect.setParameter("KernelSizeMm", 2)
  effect.self().onApply()
  
  # Growing segmentation to return to original size after smoothing
  #segmentEditorWidget.setActiveEffectByName("Margin")
  #effect = segmentEditorWidget.activeEffect()
  #effect.setParameter("Operation", "GROW")
  #effect.setParameter("MarginSizeMm", 3)
  #effect.self().onApply()

  # Turn off visibility of all segment and turn on the one we need only
  
  segmentationDisplayNode.SetAllSegmentsVisibility(False)
  segmentationDisplayNode.SetSegmentVisibility(seedsID, True)

  # Set the opacity of segment to review
  segmentationDisplayNode.SetSegmentOpacity(seedsID, 0.2)
  segmentationDisplayNode.SetSegmentOpacity2DOutline(seedsID, 1)

  # Select segments to edit
  segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
  segmentEditorNode = segmentEditorWidget.mrmlSegmentEditorNode()
  segmentEditorNode.SetSelectedSegmentID(seedsID)

  # Select erase
  # segmentEditorWidget.setActiveEffectByName("Erase")

  print("Please review and edit the segmentation.")
  try:
    pressedKey = input("Press Enter to save...")
  except:
    pass
  ############################################### Save file ##########################################################

  # Create label map
  listVolumeNodes = slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')
  for volumeNode in listVolumeNodes:
    if "t2" in volumeNode.GetName():
      referenceVolumeNode = volumeNode
  labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
  slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode, referenceVolumeNode)

  # Export seg.nrrd
  segmentDir = os.path.join(rootDir,"rectum", subDirs[scanNumber].split("/")[9]+subDirs[scanNumber][-6:])
  if not os.path.exists(segmentDir):
      os.makedirs(segmentDir)
  print(scanNumber)
  # Save segmentation and its dicom files as .nrrd
  segmentPath = os.path.join(segmentDir,subDirs[scanNumber].split("/")[9][-4:] + ".seg.nrrd")
  volumnPath  = os.path.join(segmentDir,subDirs[scanNumber].split("/")[9][- 4:] + ".nrrd")


  slicer.util.saveNode(labelmapVolumeNode, segmentPath)
  slicer.util.saveNode(masterVolumeNode, volumnPath)

  print("Saved segmentation as: %s"%(segmentPath))
  print("Saved input data as: %s"%(volumnPath))
  print(df)
  # Switch to Segmentations just to switch it back to Segment Editor
  # Segment Editor will automatically choose "Segmentation" and reference volume
  df.loc[len(df.index)] = [scanNumber]
  df.to_csv(hisFile,index = False)

  slicer.util.mainWindow().moduleSelector().selectModule('Segmentations')
  return
  
def review_rectum_seg_nrrd(rootDir):  
  import os 
  import qt
  import slicer
  from utils import toggleSelectSegment

  # Clean up workspace
  slicer.mrmlScene.Clear(0)

  # Change height of Python Interactor
  pyConsoleDockWidget = slicer.util.mainWindow().findChildren('QDockWidget','PythonConsoleDockWidget')[0]
  slicer.util.mainWindow().resizeDocks([pyConsoleDockWidget],[1000], qt.Qt.Vertical)

  # Get all scan directories
  subDirs = []
  for rootdir, dirs, files in os.walk(rootDir):
    for subDir in dirs:
      if "beta" in subDir:
        subDirs.append(subDir)

  # Sort out the directory names by their initial
  subDirs = sorted(subDirs, key=lambda x: int(x.split('beta')[0]))

  # Please out Scan IDs
  for i in range(len(subDirs)):
    print("%d - %s"%(i,subDirs[i]))

  # Choose Scan number
  scanNumber = int(input("Choose scan number... "))
  print("Choosen number: %s"%(scanNumber))
  print("Loaded Scan ID: %s"%(subDirs[scanNumber]))

  # Change height of Python Interactor
  slicer.util.mainWindow().resizeDocks([pyConsoleDockWidget],[200], qt.Qt.Vertical) 

  # Input folder with DICOM files
  volumneDataDir = os.path.join(rootDir, subDirs[scanNumber] , subDirs[scanNumber] + ".nrrd") 
  # segDataDir = os.path.join(rootDir, subDirs[scanNumber] , subDirs[scanNumber][:30] +"_reviewed.seg.nrrd") 
  segDataDir = os.path.join(rootDir, subDirs[scanNumber] , subDirs[scanNumber][:30] +".seg.nrrd") 

  slicer.util.loadSegmentation(segDataDir)
  slicer.util.loadVolume(volumneDataDir)
  
  slicer.util.mainWindow().moduleSelector().selectModule('Segmentations')
  #toggleSelectSegment()

  return
