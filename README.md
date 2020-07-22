# archive-big-data-dropbox
Upload large volume (PB) of data to Dropbox seamlessly

## Introduction
Dropbox has started a [paid plans](https://www.dropbox.com/business/pricing) which provide unlimited data storage space to its subscribers. This can be useful for small to medium sized businesses which generate large amount of data and do not wish to invest on building their own servers for archiving. However, uploading hundreds of terabytes of data to Dropbox servers can be challenging and time consuming primarily due to three reasons -

1. *If the number of files synchronized to Dropbox exceeds 300,000 the [performance](https://help.dropbox.com/accounts-billing/space-storage/file-storage-limit) of the desktop application may decline.* To solve this problem, it is recommended to make a zip file from a folder containing a large number of small files.
2. *Dropbox is not good at synchronizing [terabytes of data](https://help.dropbox.com/installs-integrations/desktop/unexpected-quit) at a time.* To solve this problem it is recommended to synchronize the data to Dropbox in small batches (a few hundred GB)
3. *Dropbox desktop app cannot synchronize very large files.*
 Contrary to their claim, Dropbox app cannot synchronize single files if they exceed 1 TB (This number could be smaller but I have done tests on a 1 TB file.) A way to resolve this is to split the large file into smaller chunks and then upload it to Dropbox. The split files can be downloaded and joined together using the python script "joinFiles.py".

This package provides a complete solution to seamlessly archive your data to Dropbox.

## Requirements
* Windows 10
* [Dropbox application](https://www.dropbox.com/install) installed on your computer and linked to the desired account
* [7zip](https://www.7-zip.org/)
* [Microsoft Office](https://www.office.com)/[Libre Office](https://www.libreoffice.org)/[Open Office](https://www.openoffice.org)/[WPS Office](https://www.wps.com)
* python >= 3.6.9
    * numpy 1.17.2
    * pandas 0.25.1
    * xlrd 1.2.0
    * tqdm 4.36.1
    * psutil 5.4.2
    * dropbox 10.2.0
    
## Usage
As of now the package is divided into two parts - 1. data archiving, and 2. data preparation and uploading
### APP
1. Fill out the dropboxAPP sheet in inputs.xlsx.
2. Run app.py

The script looks at the all the files that need to be uploaded. If any file is bigger than fileSizeLimit_GB (default is 100 GB), it is split into smaller pieces. After the data preparation is done the files are uploaded to Dropbox in batches of size batchSize_GB (default is 200 GB). If at any point during the upload the physical hard drive gets full, the program is paused asking to make space on Dropbox drive. In addition to this if Drobox crashes, the program is paused until you restart Dropbox. A log file is generated at the end and placed in logs folder.

### API
1. Fill out the dropboxAPI sheet in inputs.xlsx. The upload directory should correspond to location on Dropbox.
2. Run app.py

You will need to generate an access token to your Dropbox by creating a [developer app](https://www.dropbox.com/developers/apps). You can also change the chunkSize_MB (default is 128 MB), but note that it should be less than 150 MB. The data preparation is done exactly the same way but the data is uploaded directly to Dropbox. This method is slightly slower. A log file is generated at the end and placed in logs folder. 
