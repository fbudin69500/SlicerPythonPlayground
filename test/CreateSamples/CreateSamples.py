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

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
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

    # Add vertical spacer
    self.layout.addStretch(1)


  def cleanup(self):
    pass

  def onLabelButton(self):
    logic = CreateSamplesLogic()
    logic.createLabelMap()

  def onVolumeButton(self):
    logic = CreateSamplesLogic()
    logic.createVolumeMap()

  def onModelButton(self):
    logic = CreateSamplesLogic()
    logic.createModelMap()
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

  # Create sample labelmap with same geometry as input volume
  def createLabelMap(self ):
    outputImageData = vtk.vtkImageData()
    outputImageData.SetOrigin(50,50,50)
    outputImageData.SetSpacing(.5,.5,.5)
    outputImageData.SetDimensions(10,5,15)
    outputImageData.SetOrigin(1,3,8)
    outputImageData.AllocateScalars(vtk.VTK_DOUBLE, 1);
    volumeNode = slicer.vtkMRMLScalarVolumeNode()
    volumeNode.SetAndObserveImageData(outputImageData)
    label = 1
    sampleLabelmapNode = slicer.vtkMRMLScalarVolumeNode()
    sampleLabelmapNode.SetName("SampleLabelMap")
    sampleLabelmapNode.SetLabelMap(1)
    sampleLabelmapNode = slicer.mrmlScene.AddNode(sampleLabelmapNode)
    sampleLabelmapNode.Copy(volumeNode)
    imageData = vtk.vtkImageData()
    imageData.DeepCopy(volumeNode.GetImageData())
    sampleLabelmapNode.SetAndObserveImageData(imageData)
    extent = imageData.GetExtent()
    for x in xrange(extent[0], extent[1]+1):
        for y in xrange(extent[2], extent[3]+1):
            for z in xrange(extent[4], extent[5]+1):
                if (x >= (extent[1]/4) and x <= (extent[1]/4) * 3) and (y >= (extent[3]/4) and y <= (extent[3]/4) * 3) and (z >= (extent[5]/4) and z <= (extent[5]/4) * 3):
                    imageData.SetScalarComponentFromDouble(x,y,z,0,label)
                else:
                    imageData.SetScalarComponentFromDouble(x,y,z,0,0)
    # Display labelmap
    labelmapVolumeDisplayNode = slicer.vtkMRMLLabelMapVolumeDisplayNode()
    slicer.mrmlScene.AddNode(labelmapVolumeDisplayNode)
    colorNode = slicer.util.getNode('GenericAnatomyColors')
    #self.assertTrue( colorNode != None )
    labelmapVolumeDisplayNode.SetAndObserveColorNodeID(colorNode.GetID())
    labelmapVolumeDisplayNode.VisibilityOn()
    sampleLabelmapNode.SetAndObserveDisplayNodeID(labelmapVolumeDisplayNode.GetID())
    return True

  def createVolumeMap(self):
      print "plop"

  def createModelMap(self):
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
