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

  selectedSegmentID = segmentEditorNode.GetSelectedSegmentID()
  for i in range(numberOfSegments):
    if selectedSegmentID == segmentation.GetNthSegmentID(i):
      index = i
  if numberOfSegments == 1:
    selectedSegmentID = segmentation.GetNthSegmentID(0)
  else: 
    # select the next segment in order
    selectedSegmentID = segmentation.GetNthSegmentID((index+1)%numberOfSegments)
  segmentEditorNode.SetSelectedSegmentID(selectedSegmentID)
  # set visibility the next segment
  segmentationDisplayNode = segmentationNode.GetDisplayNode()
  #segmentationDisplayNode.SetAllSegmentsVisibility(False)
  segmentationDisplayNode.SetSegmentVisibility(selectedSegmentID, True)
  segmentationDisplayNode.SetOpacity(0.2)
  segmentationDisplayNode.SetOpacity2DOutline(1)
  return
def exportLabelmap(outputPath):
  import slicer
  segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
  referenceVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
  labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
  slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode, referenceVolumeNode)
  filepath = outputPath + "/" + referenceVolumeNode.GetName() + "/" + referenceVolumeNode.GetName() + "-rectum.seg.nrrd"
  slicer.util.saveNode(labelmapVolumeNode, filepath)
  slicer.mrmlScene.RemoveNode(labelmapVolumeNode.GetDisplayNode().GetColorNode())
  slicer.mrmlScene.RemoveNode(labelmapVolumeNode)
  slicer.util.delayDisplay("Segmentation saved to " + filepath)
