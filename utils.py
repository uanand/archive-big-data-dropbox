import os
import platform

############################################################
def getFileName(inputFile):
    if (platform.system()=='Linux'):
        fileName = inputFile.split('/')[-1]
    elif (platform.system()=='Windows'):
        fileName = inputFile.split('\\')[-1]
    return fileName
############################################################

############################################################
def getDirName(inputFile,name):
    if (platform.system()=='Linux'):
        outputDir = inputFile.replace('/'+name,'')
    elif (platform.system()=='Windows'):
        outputDir = inputFile.replace('\\'+name,'')
    return outputDir
############################################################

############################################################
def mkdirs(dirNameList):
    for dirName in dirNameList:
        if (os.path.exists(dirName)==False):
            os.makedirs(dirName)
############################################################
