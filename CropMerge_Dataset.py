#!/usr/bin/env python
# coding: utf-8

# # Crop and merge ROIs from OMERO, must be connected to campus network
# 
# ## Laura Cooper 13/05/2021
# 
# #### Citation DOIs: 
# imread: 10.5334/jors.ac \
# omero: 10.1038/nmeth.1896 \
# numpy: 0.1038/s41586-020-2649-2 

from omero.gateway import BlitzGateway
import getpass
import numpy as np
import omero.model
import tempfile
import shutil
from imread import imsave
from os import system

# OMERO Paramters
username='username'
password='password'
server='server.name'
owner_id='0000'
datasetID=00000

#Parameters
width=200
height=200
slc=0
max_ch=0
slc_ch=1

# ## Define functions

def rect_roi_frm_ctr(image,ctr_x,ctr_y,width,height):
    """
    Create a rectangular ROI around the centre points
    If outside image boundaries, set boundary as outer edge
    Inputs:
        image: OMERO ImageWrapper
        ctr_x: float, x of centre point
        ctr_y: float, y of centre point
        width: int, width of rectangle
        height: int, height of rectangle
    Outputs:
        x: float, x corner of rectangle
        y: float, y corner of rectangle
        width: int, equal input or adjusted to be within image
        height: int, equal input or adjusted to be within image
    """
    #Check if ROI ends up outside image and adjust
    size_x = image.getSizeX()
    size_y = image.getSizeY()
    x=ctr_x-width/2
    y=ctr_y-height/2
    if ctr_x+width/2 > size_x:
        width=int(width/2+(size_x-ctr_x))
    if ctr_y+height/2 > size_y:
        height=int(height/2+(size_y-ctr_y))
    if x < 0:
        width=int(w+x)
        x=0
    if y < 0:
        height=int(h+y)
        y=0
    return x,y,width,height


def load_Z_stack(image,c,t,x,y,w,h):
    """
    Call planes in rectangle ROI from OMERO
    Inputs:
        image: OMERO ImageWrapper
        c: int, channel
        t: int, time point
        x: float, x corner of ROI
        y: float, y corner of ROI
        width: int, width of ROI
        height: int, height of ROI
    Outputs:
        stack: generator of image planes
    """
    size_z = image.getSizeZ()
    # list of [ (0,0,0,(x,y,w,h)), (1,0,0,(x,y,w,h)), (2,0,0,(x,y,w,h))... ]
    zct_list = [(iz, c, t,(x,y,w,h)) for iz in range(size_z)]
    pixels = image.getPrimaryPixels()
    stack = pixels.getTiles(zct_list)
    return stack


def max_proj(image,c,x,y,w,h):
    """
    Maximum projection of a ROI from a Z stack for each time point
    Inputs:
        image: OMERO ImageWrapper
        c: int, channel
        x: float, x corner of ROI
        y: float, y corner of ROI
        width: int, width of ROI
        height: int, height of ROI
    Outputs:
        max_proj: 3D nparray, maximum projection of each time point (t,x,y)
    """
    size_t = image.getSizeT()
    max_proj=[]
    for T in range(size_t):
        stack=load_Z_stack(image,c,T,x,y,w,h) #creates generator
        a = tuple((s,) for s in stack) #Reads in planes to tuple
        b=np.squeeze(a)# tuples to array
        b_MAX=np.max(b, axis=0)
        max_proj.append(b_MAX)
    max_proj = np.stack(max_proj, axis=0)
    return max_proj


def load_stack_plane(image,c,z,x,y,w,h):
    """
    Load ROI of a Z plane from every time point in OMERO image
    Inputs:
        image: OMERO ImageWrapper
        c: int, channel
        z: int, plane
        x: float, x corner of ROI
        y: float, y corner of ROI
        width: int, width of ROI
        height: int, height of ROI
    Outputs:
        b: 3D nparray, stack of same plane at each time point
    """
    size_t = image.getSizeT()
    # list of [ (0,0,0,(x,y,w,h)), (0,0,1,(x,y,w,h)), (0,0,2,(x,y,w,h))... ]
    zct_list = [(z, c, it,(x,y,w,h)) for it in range(size_t)]
    pixels = image.getPrimaryPixels()
    stack = pixels.getTiles(zct_list)
    a = tuple((s,) for s in stack)
    b=np.squeeze(a)# tuples to array
    return b


#Define imageJ metadata
_imagej_metadata = """ImageJ=1.53a
images={nr_images}
channels={nr_channels}
frames={nr_frames}
hyperstack=true
mode=color
loop=false"""

def output_hyperstack(zs, oname):
    '''
    Write out a hyperstack to oname
    source: https://metarabbit.wordpress.com/2014/04/30/building-imagej-hyperstacks-from-python/ 
    Inputs:
        zs : 4D ndarray, dimensions should be (c,t,x,y)
        oname : str, filename to write to
    Outputs
        tif file saved to current folder
    '''
    try:
        # We create a directory to save the results
        tmp_dir = tempfile.mkdtemp(prefix='hyperstack')

        # Channels are in first dimension
        nr_channels = zs.shape[0]
        nr_frames = zs.shape[1]
        nr_images = nr_channels*nr_frames
        metadata = _imagej_metadata.format(
                        nr_images=nr_images,
                        nr_frames=nr_frames,
                        nr_channels=nr_channels)
        frames = []
        next = 0
        for s1 in range(zs.shape[1]):
            for s0 in range(zs.shape[0]):
                fname = '{}/s{:03}.tiff'.format(tmp_dir,next)
                # Do not forget to output the metadata!
                imsave(fname, zs[s0,s1], metadata=metadata)
                frames.append(fname)
                next += 1
        cmd = "tiffcp {inputs} {tmp_dir}/stacked.tiff".format(inputs=" ".join(frames), tmp_dir=tmp_dir)
        r = system(cmd)
        if r != 0:
            raise IOError('tiffcp call failed')
        shutil.copy('{tmp_dir}/stacked.tiff'.format(tmp_dir=tmp_dir), oname)
    finally:
        shutil.rmtree(tmp_dir)

def main():
    try:
        conn = BlitzGateway(username, password, host=server, port=4064) 
        conn.connect() #Returns True when connected
        updateService = conn.getUpdateService()
        from omero.rtypes import rdouble, rint, rstring
        images = conn.getObjects("Image", opts={'owner': owner_id, 'dataset': datasetID}) 
        for image in images:
            imageId=image.getId()
            roi_service = conn.getRoiService()
            result = roi_service.findByImage(imageId, None)
            for roi in result.rois:
                print("ROI:  ID:", roi.getId().getValue())
                for s in roi.copyShapes():
                    if type(s) == omero.model.EllipseI:
                        ctr_x = s.getX().getValue()
                        ctr_y = s.getY().getValue()
                        x,y,w,h=rect_roi_frm_ctr(image,ctr_x,ctr_y,width,height)
                        MAX_GFP=max_proj(image,max_ch,x,y,w,h)
                        BFZ9=load_stack_plane(image,slc_ch,slc,x,y,w,h)  
                        hstk = np.stack((MAX_GFP, BFZ9), axis = 0)
                        tmp_str= 'output_'+str(imageId)+'_'+str(roi.getId().getValue())+'.tif'
                        output_hyperstack(hstk, tmp_str)
    finally:
        if conn:
            conn.close()
            
if __name__ == "__main__":
    main()
