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

Edit the parameters at the top of the file and then\
For one image and one ROI
```
python CropMerge_SingleImageAndRoi.py
```
or for one dataset
```
python CropMerge_SingleImageAndRoi.py
```

## References

#### imread: 
Coelho, Luis Pedro. (2012). Mahotas: Open source software for scriptable computer vision. Journal of Open Research Software. DOI: 10.5334/jors.ac. 
#### OMERO:
Allan, C., Burel, JM., Moore, J. et al. OMERO: flexible, model-driven data management for experimental biology. Nat Methods 9, 245–253 (2012). https://doi.org/10.1038/nmeth.1896
#### NumPy:
Harris, C.R., Millman, K.J., van der Walt, S.J. et al. Array programming with NumPy. Nature 585, 357–362 (2020). DOI: 0.1038/s41586-020-2649-2

