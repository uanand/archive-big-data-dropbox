import numpy
import pandas
import os

inputDir = '/scratch/utkur/utkarsh/WettingLayer'
fileSizeLimit_GB = 500


############################################################
# STEP 1 - FIND OUT THE NUMBER OF FILES AND THEIR SIZE IN EACH
# DIRECTORY
outFile = open('directorySize.txt','w')
outFile.write('Directory\tNumber of files\tFile size (GB)\n')

for root,dirs,files in os.walk(inputDir):
    print ('Scanning %s' %(root))
    fileSize = 0
    numFiles = 0
    for name in files:
        fileName = os.path.join(root,name)
        numFiles += 1
        fileSize += os.path.getsize(fileName)
    fileSize /= (1024.0*1024*1024)
    outFile.write('%s\t%d\t%f\n' %(root,numFiles,fileSize))
outFile.close()
############################################################


############################################################
# STEP 2 - FIND THE TOTAL NUMBER OF FILES, SUBDIRECTORIES, AND
# SIZE OF EACH FOLDER
df = pandas.read_csv('directorySize.txt',delimiter='\t',names=['dirName','numFiles','size'],header=0)
[row,col] = df.shape

outFile = open('directoryStructure.txt','w')
outFile.write('Directory\tNumber of subdirectories\tNumber of files\tSize (GB)\n')
for i in range(row):
    parentDir = df['dirName'][i]
    parentNumFiles = df['numFiles'][i]
    parentFolderSize = df['size'][i]
    numSubDir = 0
    for j in range(i+1,row):
        daughterDir = df['dirName'][j]
        daughterNumFiles = df['numFiles'][j]
        daughterFolderSize = df['size'][j]
        if (parentDir in daughterDir):
            parentNumFiles += daughterNumFiles
            parentFolderSize += daughterFolderSize
            numSubDir += 1
        else:
            break
    if (parentFolderSize<=fileSizeLimit_GB):
        outFile.write('%s\t%d\t%d\t%.6f\n' %(parentDir,numSubDir,parentNumFiles,parentFolderSize))
outFile.close()
# ############################################################


############################################################
# STEP 3 - LIST THE FOLDERS YOU WANT TO ZIP
df = pandas.read_csv('directoryStructure.txt',delimiter='\t',names=['dirName','numSubDir','numFiles','size'],header=0)
[row,col] = df.shape

outFile = open('directoryZipList.txt','w')
outFile.write('Directory\tNumber of subdirectories\tNumber of files\tSize (GB)\n')

i = 0
while (i<row):
    parentDir = df['dirName'][i]
    parentNumSubDir = df['numSubDir'][i]
    parentNumFiles = df['numFiles'][i]
    parentFolderSize = df['size'][i]
    for j in range(i+1,row):
        daughterDir = df['dirName'][j]
        if (parentDir in daughterDir):
            pass
        else:
            break
    i = j
    outFile.write('%s\t%d\t%d\t%.6f\n' %(parentDir,parentNumSubDir,parentNumFiles,parentFolderSize))
    if (i==row-1):
        break
outFile.close()
############################################################


############################################################
# STEP 4 - DELETE EXCESS FILES
os.remove('directorySize.txt')
os.remove('directoryStructure.txt')
############################################################
