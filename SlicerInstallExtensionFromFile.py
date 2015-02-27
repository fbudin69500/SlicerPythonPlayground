#!/usr/bin/env python
import sys
import argparse
import os
import subprocess

def PlatformCheck(currentPlatform,name):
  #Compare extension platform with current platform
  extensionRev,extensionOS,extensionArch=name.split('-')[:3]
  for var in ('Rev','OS','Arch'):
    currentVar=currentPlatform.get(var)
    extensionVar=locals()['extension'+var]
    if extensionVar != currentVar:
      print(var+": "+currentVar+"(Slicer) "+extensionVar+"(extension)")
      return False
  return True

def GetCurrentPlatform(SlicerExecPath):
  currentPlatform=RunScript(SlicerExecPath ,
                       '''print slicer.app.repositoryRevision+","+slicer.app.os+","+slicer.app.arch'''
  )
  currentPlatformLines=currentPlatform.split('\n')
  currentRev,currentOS,currentArch=currentPlatformLines[len(currentPlatformLines)-1].split(',')[:3]
  return {'Rev':currentRev,'OS':currentOS,'Arch':currentArch}

def RunScript(SlicerExecPath , script ):
  process=subprocess.Popen([SlicerExecPath,"-c","--launcher-no-splash",script],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  process.wait()
  output,error=process.communicate()
  if process.returncode != 0 or output.find("Failed") != -1:
    raise Exception('Error: while executing '+script, [output, error] )
  return output.strip()

#http://stackoverflow.com/questions/17277566/check-os-path-isfilefilename-with-case-sensitive-in-python
def CheckFileExistsCaseSensitive(filename):
  if not os.path.isfile(filename):
    return False   # exit early, file does not exist (not even with wrong case)
  directory, filename = os.path.split(filename)
  return filename in os.listdir(directory)

def CheckExecCaseSensitive(filename):
  if not CheckFileExistsCaseSensitive(filename):
    return False
  return os.access(filename, os.X_OK)

def FindSlicerExecutable(manualSlicerPath):
  #Searches for Slicer on the system
  try:
    if len(manualSlicerPath) > 1:
      raise Exception("Error: Slicer path can be specified only once")
    SlicerExecPath=manualSlicerPath[0]
    if not CheckExecCaseSensitive(SlicerExecPath):
      raise Exception("Given executable for Slicer does not exist or is not an executable file")
    else:
      return SlicerExecPath
  #In case no slicer path was given as an argument in the command line,
  #len(manualSlicerPath) raises an error that we catch here and continue as nothing bad has happened
  except TypeError:
    pass
  except Exception as e:
    raise e
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
    raise Exception( "Error: Slicer executable not found on the system")
  return SlicerExecPath

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
                prog=sys.argv[0],
                description="This script starts Slicer and directly loads the data specified in the command line.",
                usage=sys.argv[0]+''' [<args>]

      To specify the Slicer executable path you can either:
      1) Specify Slicer executable path in the command line
      2) Add SLICERPATH to your environment
      3) Add the directory that contains Slicer executable to PATH
''')
  parser.add_argument("-e","--extension", help="Extensions to install",action='append')
  parser.add_argument("-s","--slicer", help="Slicer executable",action='append')
  parser.add_argument("--version",help="Script version",action='store_true')
  args = parser.parse_args()
  if args.version:
    print os.path.basename(sys.argv[0])+" version 1.0"
    sys.exit(0)
  #Searches for Slicer on the system
  try:
    SlicerExecPath=FindSlicerExecutable(args.slicer)
  except Exception as e:
    print e
    sys.exit(1)
  #Get current platform
  try:
    currentPlatform=GetCurrentPlatform(SlicerExecPath)
  except:
    print sys.exc_info()
    sys.exit(1)
  #Check that extension files the user wants to install actually exist
  try:
    for name in args.extension:
      if not CheckFileExistsCaseSensitive(name):
        raise Exception("Error: "+name+" does not exist")
      if not PlatformCheck(currentPlatform,os.path.basename(name)):
        raise Exception( "Error: "+name+" is for the wrong platform")
  except NameError:
    print "Error: No extension to install"
    sys.exit(0)
  except Exception as e:
    print e
    sys.exit(1)
  #Install extensions
  try:
    for name in args.extension:
      RunScript(SlicerExecPath , '''slicer.app.extensionsManagerModel().installExtension("'''+os.path.abspath(name)+'''")''' )
  except Exception as e:
    print e
    sys.exit(1)

