#SlicerPythonPlayground

##What is it?

This repository contains python scripts built to work with Slicer.

###SlicerLoadFiles###
* Load images and models directly from the command line
* Print the usage:
```
SlicerLoadFiles --help
```
* Load a volume:
```
SlicerLoadFiles -v path_to_the_colume
```
###SlicerInstallExtensionFromFile.py###
* Install a Slicer extension directory from the command line, giving the path to an extension package (*.tar.gz or *.zip)
* Print the usage:
```
SlicerInstallExtensionFromFile --help
```
* Install an extension:
```
SlicerInstallExtensionFromFile -e path_to_extension_archive
```
###For all scripts, specify Slicer path with###
* -s or --slicer in the command line
* Add the environment variable SLICERPATH and set it to the directory that contains Slicer
* Add Slicer path to your PATH environment variable


##License

See License.txt

##More information

More information about Slicer on http://www.slicer.org/


