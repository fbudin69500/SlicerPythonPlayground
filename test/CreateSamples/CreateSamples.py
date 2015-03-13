import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# CreateSamples
#

class CreateSamples(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "CreateSamples" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# CreateSamplesWidget
#

class CreateSamplesWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    generalParametersCollapsibleButton = ctk.ctkCollapsibleButton()
    generalParametersCollapsibleButton.text = "General parameters"
    self.layout.addWidget(generalParametersCollapsibleButton)

    # Layout within the dummy collapsible button
    hlayout = qt.QHBoxLayout(generalParametersCollapsibleButton)
    self.label=qt.QLabel("Volume Name:")
    hlayout.addWidget(self.label)
    self.volumeNameLine=qt.QLineEdit()
    hlayout.addWidget(self.volumeNameLine)
    self.volumeNameLine.connect('textChanged(QString)', self.onLabelChanged)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Sample From Nothing"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Sample Label map Button
    #
    self.labelButton = qt.QPushButton("Create Sample Label Map")
    self.labelButton.toolTip = "Create sample label map."
    self.labelButton.enabled = True
    parametersFormLayout.addRow(self.labelButton)

    #
    # Sample Volume Button
    #
    self.volumeButton = qt.QPushButton("Create Sample Volume")
    self.volumeButton.toolTip = "Create sample volume."
    self.volumeButton.enabled = True
    parametersFormLayout.addRow(self.volumeButton)

    #
    # Sample model Button
    #
    self.modelButton = qt.QPushButton("Create Sample Model")
    self.modelButton.toolTip = "Create sample Model."
    self.modelButton.enabled = True
    parametersFormLayout.addRow(self.modelButton)


    # connections
    self.labelButton.connect('clicked(bool)', self.onLabelButton)
    self.volumeButton.connect('clicked(bool)', self.onVolumeButton)
    self.modelButton.connect('clicked(bool)', self.onModelButton)

    parametersCollapsibleButton2 = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton2.text = "Sample From example"
    self.layout.addWidget(parametersCollapsibleButton2)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton2)
    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    # Keep the following line as an example
    #self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = True
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "reference image." )
    parametersFormLayout.addRow("Reference Volume: ", self.inputSelector)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSampleFromReferenceSelect)

    #
    # Sample From reference Button
    #
    self.referenceButton = qt.QPushButton("Create Sample Model from a reference")
    self.referenceButton.toolTip = "Create sample Model from a reference."
    parametersFormLayout.addRow(self.referenceButton)
    self.referenceButton.connect('clicked(bool)', self.onReferenceButton)


    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onLabelChanged(self.volumeNameLine.text)

  def ButtonsClickable(self, value):
    self.labelButton.setEnabled(value)
    self.volumeButton.setEnabled(value)
    self.modelButton.setEnabled(value)
    self.onSampleFromReferenceSelect()

  def cleanup(self):
    pass

  def onLabelChanged(self,myString):
      if not myString=='':
          self.ButtonsClickable(True)
      else:
          self.ButtonsClickable(False)

  def onSampleFromReferenceSelect(self):
    self.referenceButton.enabled = self.inputSelector.currentNode() and self.volumeNameLine.text != ''

  def onLabelButton(self):
    logic = CreateSamplesLogic()
    logic.createVolume(self.volumeNameLine.text, labelmap=True)

  def onVolumeButton(self):
    logic = CreateSamplesLogic()
    logic.createVolume(self.volumeNameLine.text)

  def onModelButton(self):
    logic = CreateSamplesLogic()
    logic.createModel()

  def onReferenceButton(self):
      logic = CreateSamplesLogic()
      logic.createVolume(self.volumeNameLine.text, labelmap=True, reference=self.inputSelector.currentNode())
#
# CreateSamplesLogic
#

class CreateSamplesLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def setVolumeAsBackgroundImage(self, node):
    count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceCompositeNode')
    for n in xrange(count):
      compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceCompositeNode')
      compNode.SetBackgroundVolumeID(node.GetID())
    return True

  # Create sample labelmap with same geometry as input volume
  def createVolume(self , volumeName, labelmap=False, reference=None):
    if volumeName == '':
        raise Exception('The name of the output volume cannot be empty')
    value = 1
    sampleVolumeNode = slicer.vtkMRMLScalarVolumeNode()
    sampleVolumeNode = slicer.mrmlScene.AddNode(sampleVolumeNode)
    imageData = vtk.vtkImageData()
    if reference == None:
        mySpacing = (0.5,0.6,0.5)
        myOrigin = (20,50,50)
        # Do NOT set the spacing and the origin of imageData (vtkImageData)
        # The spacing and the origin should only be set in the vtkMRMLScalarVolumeNode!!!!!!
        imageData.SetDimensions(30,5,15)
        imageData.AllocateScalars(vtk.VTK_DOUBLE, 1)
        sampleVolumeNode.SetSpacing(mySpacing[0],mySpacing[1],mySpacing[2])
        sampleVolumeNode.SetOrigin(myOrigin[0],myOrigin[1],myOrigin[2])
    else:
        sampleVolumeNode.Copy(reference)
        imageData.DeepCopy(reference.GetImageData())
    sampleVolumeNode.SetName(volumeName)
    sampleVolumeNode.SetAndObserveImageData(imageData)
    extent = imageData.GetExtent()
    for x in xrange(extent[0], extent[1]+1):
        for y in xrange(extent[2], extent[3]+1):
            for z in xrange(extent[4], extent[5]+1):
                if (x >= (extent[1]/4) and x <= (extent[1]/4) * 3) and (y >= (extent[3]/4) and y <= (extent[3]/4) * 3) and (z >= (extent[5]/4) and z <= (extent[5]/4) * 3):
                    imageData.SetScalarComponentFromDouble(x,y,z,0,value)
                else:
                    imageData.SetScalarComponentFromDouble(x,y,z,0,0)
    # Display labelmap
    if labelmap:
        sampleVolumeNode.SetLabelMap(1)
        labelmapVolumeDisplayNode = slicer.vtkMRMLLabelMapVolumeDisplayNode()
        slicer.mrmlScene.AddNode(labelmapVolumeDisplayNode)
        colorNode = slicer.util.getNode('GenericAnatomyColors')
        labelmapVolumeDisplayNode.SetAndObserveColorNodeID(colorNode.GetID())
        labelmapVolumeDisplayNode.VisibilityOn()
        sampleVolumeNode.SetAndObserveDisplayNodeID(labelmapVolumeDisplayNode.GetID())
    else:
        volumeDisplayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
        slicer.mrmlScene.AddNode(volumeDisplayNode)
        colorNode = slicer.util.getNode('Grey')
        volumeDisplayNode.SetAndObserveColorNodeID(colorNode.GetID())
        volumeDisplayNode.VisibilityOn()
        sampleVolumeNode.SetAndObserveDisplayNodeID(volumeDisplayNode.GetID())
    self.setVolumeAsBackgroundImage(sampleVolumeNode)
    return True


  def createModel(self):
      print "model"

class CreateSamplesTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
