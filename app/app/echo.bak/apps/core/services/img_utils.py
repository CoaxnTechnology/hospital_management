import os
import sys

import gdcm as gdcm
import numpy as np
import png
import pydicom
import cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
from pydicom.pixel_data_handlers import gdcm_handler, apply_color_lut, convert_color_space



def dicom2png(source_folder, output_folder):
    list_of_files = os.listdir(source_folder)
    for file in list_of_files:
        try:
            ds = pydicom.dcmread(os.path.join(source_folder, file))
            shape = ds.pixel_array.shape

            # Convert to float to avoid overflow or underflow losses.
            image_2d = ds.pixel_array.astype(float)

            # Rescaling grey scale between 0-255
            image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0

            # Convert to uint
            image_2d_scaled = np.uint8(image_2d_scaled)

            # Write the PNG file
            with open(os.path.join(output_folder, file) + '.png', 'wb') as png_file:
                w = png.Writer(shape[1], shape[0], greyscale=True)
                w.write(png_file, image_2d_scaled)
        except:
            print('Could not convert: ', file)


def ds_to_jpeg(ds, dest):
    print(f'ds_to_jpeg {dest}')
    color = ds[0x00280004]
    print('Color space', color.value)
    img = ds.pixel_array  # get image array
    if color.value != 'RGB':
        img = convert_color_space(img, color.value, 'RGB')
        cv2.imwrite(dest, img)
        return
    # Normalise to range 0..255
    norm = (img.astype(np.float) - img.min()) * 255.0 / (img.max() - img.min())
    img_mem = Image.fromarray(norm.astype(np.uint8))
    print('Image mode', img_mem.mode)
    if img_mem.mode != 'RGB':
        img_mem = img_mem.convert('RGB')
    img_mem.save(dest)


def get_gdcm_to_numpy_typemap():
    """Returns the GDCM Pixel Format to numpy array type mapping."""
    _gdcm_np = {gdcm.PixelFormat.UINT8: np.int8,
                gdcm.PixelFormat.INT8: np.uint8,
                gdcm.PixelFormat.UINT16: np.uint16,
                gdcm.PixelFormat.INT16: np.int16,
                gdcm.PixelFormat.UINT32: np.uint32,
                gdcm.PixelFormat.INT32: np.int32,
                gdcm.PixelFormat.FLOAT32: np.float32,
                gdcm.PixelFormat.FLOAT64: np.float64}
    return _gdcm_np


def get_numpy_array_type(gdcm_pixel_format):
    """Returns a numpy array typecode given a GDCM Pixel Format."""
    return get_gdcm_to_numpy_typemap()[gdcm_pixel_format]


def gdcm_to_numpy(image):
    """Converts a GDCM image to a numpy array.
    """
    pf = image.GetPixelFormat().GetScalarType()
    print('pf', pf)
    print(image.GetPixelFormat().GetScalarTypeAsString())
    assert pf in get_gdcm_to_numpy_typemap().keys(), \
        "Unsupported array type %s" % pf
    d = image.GetDimension(0), image.GetDimension(1)
    print('Image Size: %d x %d' % (d[0], d[1]))
    dtype = get_numpy_array_type(pf)
    gdcm_array = image.GetBuffer()
    result = np.frombuffer(gdcm_array, dtype=dtype)
    maxV = float(result[result.argmax()])
    ## linear gamma adjust
    # result = result + .5*(maxV-result)
    ## log gamma
    result = np.log(result + 50)  ## 50 is apprx background level
    maxV = float(result[result.argmax()])
    result = result * (2. ** 8 / maxV)  ## histogram stretch
    result.shape = d
    return result


if __name__ == '__main__':
    outfile = f'./data/obstetrique/img_ge.jpg'
    infile = './data/obstetrique/img_ge_anim.dcm'
    ds = pydicom.dcmread(infile)
    ds_to_jpeg(ds, outfile)
    exit()

    r = gdcm.ImageReader()
    r.SetFileName(infile)
    ret = r.Read()

    numpy_array = gdcm_to_numpy(r.GetImage())
    ## L is 8 bit grey
    ## http://www.pythonware.com/library/pil/handbook/concepts.htm
    pilImage = Image.frombuffer('L',
                                numpy_array.shape,
                                numpy_array.astype(np.uint8),
                                'raw', 'L', 0, 1)
    ## cutoff removes background noise and spikes
    pilImage = ImageOps.autocontrast(pilImage, cutoff=.1)
    pilImage.save(outfile)

    exit()

    # check GetFragment API:
    pd = r.GetFile().GetDataSet().GetDataElement(gdcm.Tag(0x7fe0, 0x0010))
    frags = pd.GetSequenceOfFragments()
    frags.GetFragment(0)

    ir = r.GetImage()
    w = gdcm.ImageWriter()
    image = w.GetImage()

    image.SetNumberOfDimensions(ir.GetNumberOfDimensions())
    dims = ir.GetDimensions()
    print(ir.GetDimension(0))
    print(ir.GetDimension(1))
    print("Dims:", dims)

    image.SetDimension(0, ir.GetDimension(0))
    image.SetDimension(1, ir.GetDimension(1))

    pixeltype = ir.GetPixelFormat()
    image.SetPixelFormat(pixeltype)

    pi = ir.GetPhotometricInterpretation()
    image.SetPhotometricInterpretation(pi)

    pixeldata = gdcm.DataElement(gdcm.Tag(0x7fe0, 0x0010))
    str1 = ir.GetBuffer()
    print("Str1 ", type(str1))
    print(ir.GetBufferLength())
    # pixeldata.SetByteStringValue(str1)
    pixeldata.SetByteValue(str1, gdcm.VL(len(str1)))
    image.SetDataElement(pixeldata)

    w.SetFileName(outfile)
    w.SetFile(r.GetFile())
    w.SetImage(image)
    if not w.Write():
        sys.exit(1)

    """
    shape = ds.pixel_array.shape
    # Convert to float to avoid overflow or underflow losses.
    image_2d = ds.pixel_array.astype(float)
    # Rescaling grey scale between 0-255
    image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)
    with open(outfile, 'wb') as png_file:
        w = png.Writer(shape[1], shape[0], greyscale=True)
        w.write(png_file, image_2d_scaled)
    """
