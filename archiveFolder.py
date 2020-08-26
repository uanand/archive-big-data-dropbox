import pandas
import subprocess
import platform

############################################################
# READ THE INPUT EXCEL FILE AND ZIP ARCHIVE THE FOLDERS
############################################################
df = pandas.read_excel('inputs.xlsx',sheet_name='archiveFolder',names=['inputDir','deleteFlag'])

if (platform.system()=='Linux'):
    executable = '7za'
elif (platform.system()=='Windows'):
    executable = 'C:/Program Files/7-Zip/7z.exe'
for inputDir,deleteFlag in df.values:
    print ('Archiving the folder %s' %(inputDir))
    zipFileName = inputDir+'.zip'
    command = executable + zipFileName + ' ' + inputDir
    if (deleteFlag==0):
        subprocess.run([executable,'a',zipFileName,inputDir])
    else:
        subprocess.run([executable,'a',zipFileName,inputDir,'-sdel'])
############################################################
