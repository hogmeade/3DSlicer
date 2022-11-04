def toggleSelectSegment():
  import slicer
  # show the module SegmentEditor
  slicer.util.mainWindow().moduleSelector().selectModule('SegmentEditor')
  try:
      segmentationNode = slicer.util.getNode("Segmentation")
  except slicer.util.MRMLNodeNotFoundException:
  # In case the ID segment name is unknown
      segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")

  segmentation = segmentationNode.GetSegmentation()
  numberOfSegments = segmentation.GetNumberOfSegments()

  segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
  segmentEditorNode = segmentEditorWidget.mrmlSegmentEditorNode()

  # Get current selected node
  selectedSegmentID = segmentEditorNode.GetSelectedSegmentID()
  for i in range(numberOfSegments):
    if selectedSegmentID == segmentation.GetNthSegmentID(i):
      index = i
  # If there is only one segment , it will toggle the visibility of this single segment
  if numberOfSegments == 1:
    selectedSegmentID = segmentation.GetNthSegmentID(0)
    segmentationDisplayNode = segmentationNode.GetDisplayNode()
    # Get current display status
    displayStatus = segmentationDisplayNode.GetSegmentVisibility(selectedSegmentID)
    segmentationDisplayNode.SetSegmentVisibility(selectedSegmentID,not displayStatus)

  else: 
    # select the next segment (index + 1) in order
    selectedSegmentID = segmentation.GetNthSegmentID((index+1)%numberOfSegments)
    segmentEditorNode.SetSelectedSegmentID(selectedSegmentID)
    # set visibility the next segment
    segmentationDisplayNode = segmentationNode.GetDisplayNode()
    #segmentationDisplayNode.SetAllSegmentsVisibility(False)
    segmentationDisplayNode.SetSegmentVisibility(selectedSegmentID, True)
    
  segmentationDisplayNode.SetOpacity(0.3)
  segmentationDisplayNode.SetOpacity2DOutline(1)
  return
def exportLabelmap(outputPath):
  import slicer
  listVolumeNodes = slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')
  for volumeNode in listVolumeNodes:
    if "beta" in volumeNode.GetName():
      referenceVolumeNode = volumeNode
  segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
  #referenceVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
  labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
  slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode, referenceVolumeNode)
  filepathSeg = outputPath + "/" + referenceVolumeNode.GetName() + "/" + referenceVolumeNode.GetName()[:30] + "_reviewed.seg.nrrd"
  filepathVol = outputPath + "/" + referenceVolumeNode.GetName() + "/" + referenceVolumeNode.GetName()[:30] + ".nrrd"
  slicer.util.saveNode(labelmapVolumeNode, filepathSeg)
  slicer.util.saveNode(referenceVolumeNode, filepathVol)
  slicer.mrmlScene.RemoveNode(labelmapVolumeNode.GetDisplayNode().GetColorNode())
  slicer.mrmlScene.RemoveNode(labelmapVolumeNode)
  slicer.util.delayDisplay("Segmentation saved to " + filepathSeg + "\n" + "Volume saved to " + filepathVol)
