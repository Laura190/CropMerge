# README

## CropMerge

Pull regions of interest from images on OMERO.\
Max project one channel, select plan from another channel\
Combine into hyperstack and save as .tif file

### Install packages, conda:

conda create -n myenv -c ome python=3.6 zeroc-ice36-python omero-py\
conda activate myenv\
pip install imread

### Install packages, venv:

python3 -m venv myenv\
. myenv/bin/activate\
pip install omero-py==5.8.1\
pip install imread

### To run:

Edit the parameters at the top of the file and then
For one image and one ROI
```
python CropMerge_SingleImageAndRoi.py
```
For one dataset
```
python CropMerge_SingleImageAndRoi.py
```


