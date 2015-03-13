#!/usr/bin/env python
import sys
import argparse
import os
import glob

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
      globfiles=glob.glob(filename.replace("\*","*"))
      for globfilename in globfiles:
        if not os.path.isfile(globfilename):
          print "Error: "+globfilename+" does not exist"
          sys.exit(1)
        print( "Loading: "+globfilename )
        CLArgs+="slicer.util.load"+dataType+"(\""+globfilename+"\");"
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
      1) Specify Slicer executable path in the command line
      2) Add SLICERPATH to your environment
      3) Add the directory that contains Slicer executable to PATH

      To specify multiple files at once with the wildcard, write the file path
      in between single (') or double (") quotation marks and escape the wildcard with a backslash (\*):
      e.g.:'''+sys.argv[0]+''' -v my/file/path/my_prefix\*_my_suffix.my_extension'''
)
  parser.add_argument("-v","--volume", help="Volume file name",action='append',dest="Volume")
  parser.add_argument("-m","--model", help="Model file name",action='append',dest="Model")
  parser.add_argument("-l","--Label", help="Label volume file name",action='append',dest="LabelVolume")
  parser.add_argument("-t","--Transform", help="transform file name",action='append',dest="Transform")
  parser.add_argument("-f","--fiber", help="Fiber bundle file name",action='append',dest="FiberBundle")
  parser.add_argument("-s","--slicer", help="Slicer executable",action='append')
  parser.add_argument("-c","--create_MRML_scene", help="Create a MRML scene and exits Slicer",action='append')
  parser.add_argument("--fast",help="Only loads a few modules for Slicer",action='store_true')
  parser.add_argument("--show_errors",help="Print error messages in the terminal",action='store_true')
  parser.add_argument("--version",help="Script version",action='store_true')
  args = parser.parse_args()
  if args.version:
    print os.path.basename(sys.argv[0])+" version 1.1"
    sys.exit(0)
  #Searches for Slicer on the system
  try:
    if len(args.slicer) > 1:
      print( "Error: Slicer path can be specified only once" )
      sys.exit(1)
    SlicerExecPath=args.slicer[0]
    if not CheckExecCaseSensitive(SlicerExecPath):
      print("Given executable for Slicer does not exist or is not an executable file")
      sys.exit(1)
  except SystemExit:
    sys.exit(1)
  except:
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
      sys.exit(1)
  CLArgs=" --python-code '"
  create_MRML = True
  try:
    if len(args.create_MRML_scene) > 1:
      print( "Error: Only one output MRML scene file can be specified" )
      sys.exit(1)
  except:
    create_MRML = False
  if create_MRML == True:
    #Save loaded data into a MRML scene
    args.fast=True
    CLArgs+="slicer.util.mainWindow().hide();"
  else:
    #change current module in Slicer to 'Data'
    CLArgs+="button=qt.QRadioButton(\"Loading\");button.show();slicer.util.mainWindow().moduleSelector().selectModule(\"Data\");"
  #Write python code to load the data
  for dataType in ["Volume","Model","LabelVolume","Transform","FiberBundle"]:
    CLArgs+=LoadDataPythonCodeCreator(dataType,args)
  if create_MRML == True:
    CLArgs+="slicer.util.saveScene(\""+args.create_MRML_scene[0]+"\");slicer.util.quit()'"
  else:
    CLArgs+="button.hide();'"
  ##Command line
  additionalCLArgs=""
  if not args.show_errors:
    additionalCLArgs=" --disable-terminal-outputs "
  fastCLArgs = ""
  if args.fast:
    fastCLArgs = " --disable-scripted-loadable-modules --disable-cli-modules --no-splash"
  os.system(SlicerExecPath+additionalCLArgs+fastCLArgs+CLArgs)
