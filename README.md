# archive-big-data-dropbox
Upload large volume (PB) of data to Dropbox seamlessly

## Introduction
Dropbox has started [paid plans](https://www.dropbox.com/business/pricing) which provide unlimited data storage space to its subscribers. This can be useful for small to medium sized businesses which generate large amount of data and do not wish to invest on building their own servers for archiving. However, uploading hundreds of terabytes of data to Dropbox servers can be challenging and time consuming primarily due to three reasons -

1. *If the number of files synchronized to [Dropbox exceeds 300,000](https://help.dropbox.com/accounts-billing/space-storage/file-storage-limit) the performance of the desktop application may decline.* To solve this problem, it is recommended to make a zip file from a folder containing a large number of small files.
2. *Dropbox is not good at synchronizing [terabytes of data](https://help.dropbox.com/installs-integrations/desktop/unexpected-quit) at a time.* To solve this problem it is recommended to synchronize the data to Dropbox in small batches (a few hundred GB)
3. *Dropbox desktop app cannot synchronize very large files.*
 Contrary to their claim, Dropbox app cannot synchronize single files if they exceed 600 GB (This number could be smaller but I have done tests on a 600 GB file.) A way to resolve this is to split the large file into smaller chunks and then upload it to Dropbox. The split files can be downloaded and joined together using the python script "joinFiles.py".

This package provides a complete solution to seamlessly archive your data to Dropbox.

## Requirements
* Windows 10
* [Dropbox application](https://www.dropbox.com/install) installed on your computer and linked to the Business account
* [7zip](https://www.7-zip.org/)
* Any office package which can edit and save .xlsx files - [Microsoft Office](https://www.office.com)/[Libre Office](https://www.libreoffice.org)/[Open Office](https://www.openoffice.org)/[WPS Office](https://www.wps.com)
* python >= 3.6.9
    * numpy 1.17.2
    * pandas 0.25.1
    * xlrd 1.2.0
    * tqdm 4.36.1
    * psutil 5.4.2
    * dropbox 10.2.0
    
## Usage
As of now the package is divided into two parts - 1. data archiving, and 2. data preparation followed by uploading

### Data archiving
1. Open inputs.xlsx and go to the sheet "archiveFolder" and list down all the directories you want to zip before uploading to Dropbox. The first column is the name of the directory, and the second column is a flag value to delete the original files after zipping (Default is to delete the files after zip is complete).
2. Run the python script "archiveFolder.py".

### Uploading to Dropbox
This can be done using the Dropbox Windows Desktop application, or using Dropbox's API to upload directly to Dropbox.

#### APP
1. Fill out the dropboxAPP sheet in inputs.xlsx. The first column can be a directory or a file you want to upload. The second column in the Dropbox directory where you want to upload the data.  
2. Open the python scripy "app.py" and make sure the variable *sheetName* is set as 'dropboxUpload_APP'. Enter the location of *dropboxDir*, and you can change the default values for *fileSizeLimit_GB*, *chunkSizeSplit_MB*, *batchSize_GB*, *sleepTime_s* (not recommended), and *r_wSpeedCutOff* (not recommended).  
3. Run "app.py".

The script looks at the all the files that need to be uploaded. If any file is bigger than *fileSizeLimit_GB* (default is 100 GB), it is split into smaller pieces. After the data preparation is done the files are uploaded to Dropbox in batches of size *batchSize_GB* (default is 200 GB). The script pauses if
* Dropbox physical hard drive gets full
* Drobox crashes
* TODO - Dropbox quota reached

A log file is generated at the end and placed in logs folder.

#### API
1. Fill out the dropboxAPI sheet in inputs.xlsx. The first column can be a directory or a file you want to upload. The second column in the Dropbox directory where you want to upload the data.  
2. Open the python scripy "app.py" and make sure the variable *sheetName* is set as 'dropboxUpload_API'.  
3. Run "app.py".

You will need to generate an access token to your Dropbox by creating a [developer app](https://www.dropbox.com/developers/apps). You can also change the chunkSize_MB (default is 128 MB, maximum 150 MB). The data preparation is done exactly the same way but the data is uploaded directly to Dropbox. This method is slightly slower. The script pauses if **Dropbox quota reached (TODO)**. A log file is generated at the end and placed in logs folder.

### Downloading from Dropbox
Downloading the files from Dropbox is easy. One can select the file and change its Smart Sync status to Local. After downloading all the corresponding split files, they can be joined together using the script "joinFiles.py". Only the name of the first split file needs to be entered, and the script will look for all the subsequent splits and join the files together. After joining the files the zip archive is unzipped and the combined file is deleted. 
