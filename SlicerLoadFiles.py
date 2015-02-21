#!/usr/bin/env python
import sys
import argparse
import os

#http://stackoverflow.com/questions/17277566/check-os-path-isfilefilename-with-case-sensitive-in-python
def CheckExecCaseSensitive(filename):
    if not os.path.isfile(filename): return False   # exit early, file does not exist (not even with wrong case)
    if not os.access(filename, os.X_OK): return False #exit early, file exists but is not executable
    directory, filename = os.path.split(filename)
    return filename in os.listdir(directory)

def LoadDataPythonCodeCreator( dataType , args ):
  print( "Reading data type: "+dataType)
  CLArgs=""
  try:
    listFileNames=getattr(args,dataType,list())
    for filename in listFileNames:
      if not os.path.isfile(filename):
        print "Error: "+filename+" does not exist"
        sys.exit(1)
      print( "Loading: "+filename )
      CLArgs+="slicer.util.load"+dataType+"(\""+filename+"\");"
  except SystemExit:
    sys.exit(1)
  except:
    print( "No "+dataType)
    pass
  return CLArgs

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
                prog=sys.argv[0],
                description="This script starts Slicer and directly loads the data specified in the command line.",
                usage=sys.argv[0]+''' [<args>]
      
      To specify the Slicer executable path you can either:
      1) Add SLICERPATH to your environment
      2) Add the directory that contains Slicer executable to PATH
''')
  parser.add_argument("-v","--volume", help="Volume file name",action='append',dest="Volume")
  parser.add_argument("-m","--model", help="Model file name",action='append',dest="Model")
  parser.add_argument("-l","--Label", help="Label volume file name",action='append',dest="LabelVolume")
  parser.add_argument("-t","--Transform", help="transform file name",action='append',dest="Transform")
  parser.add_argument("-f","--fiber", help="Fiber bundle file name",action='append',dest="FiberBundle")
  args = parser.parse_args()
  #Searches for Slicer on the system
  SlicerExecPath=""
  pathList=os.environ["PATH"].split(os.pathsep)
  pathList.insert(0,os.getenv('SLICERPATH',''))
  for path in pathList:
    path = path.strip('"')
    exe_file = os.path.join(path, "Slicer")
    if CheckExecCaseSensitive(exe_file):
      SlicerExecPath=exe_file
      break
  if SlicerExecPath == '' :
    print( "Error: Slicer executable not found on the system")
    exit(1)
  #change current module in Slicer to 'Data'
  CLArgs=" --python-code 'button=qt.QRadioButton(\"Loading\");button.show();slicer.util.mainWindow().moduleSelector().selectModule(\"Data\");"
  #Write python code to load the data
  for dataType in ["Volume","Model","LabelVolume","Transform","FiberBundle"]:
    CLArgs+=LoadDataPythonCodeCreator(dataType,args)
  CLArgs+="button.hide()'"
  os.system(SlicerExecPath+CLArgs)