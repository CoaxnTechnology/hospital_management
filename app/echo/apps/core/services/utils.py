import datetime

import cv2
import numpy as np
import png
import pydicom
from PIL import Image
from pydicom import FileDataset
from typing import Callable, Dict, List, Optional, Union, cast
from datetime import datetime
from pydicom.datadict import dictionary_VM, dictionary_VR
from pydicom.dataset import FileDataset, Dataset
from dataclasses import dataclass
from pydicom.multival import MultiValue
from pydicom.pixel_data_handlers import convert_color_space
from pydicom.sequence import Sequence
from pydicom.sr.codedict import codes
from logging import getLogger, basicConfig, DEBUG

basicConfig(filename='./logs/storage_scp.log', level=DEBUG)
logger = getLogger()
logger.setLevel("DEBUG")


def ds_to_png(ds, dest):
    print(f'ds_to_png {dest}')
    shape = ds.pixel_array.shape

    # Convert to float to avoid overflow or underflow losses.
    image_2d = ds.pixel_array.astype(float)

    # Rescaling grey scale between 0-255
    image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0

    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)

    # Write the PNG file
    with open(dest, 'wb') as png_file:
        w = png.Writer(shape[1], shape[0], greyscale=True)
        w.write(png_file, image_2d_scaled)


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
    norm = (img.astype(float) - img.min()) * 255.0 / (img.max() - img.min())
    img_mem = Image.fromarray(norm.astype(np.uint8))
    print('Image mode', img_mem.mode)
    if img_mem.mode != 'RGB':
        img_mem = img_mem.convert('RGB')
    img_mem.save(dest)


ParsedElementValue_ = Union[str, float, int, datetime]
ParsedElementValue = Union[List[ParsedElementValue_], ParsedElementValue_]


@dataclass
class ServiceClassProviderConfig:
    implementation_class_uid: str
    port: int


def to_dicom_tag(tag: int, padding: int = 10) -> str:
    return f"{tag:#0{padding}x}"


def parse_da_vr(value: str) -> Optional[datetime]:
    for format in ("%Y%m%d", "%Y-%m-%d", "%Y:%m:%d"):
        try:
            return datetime.strptime(value, format)
        except ValueError:
            pass
    return None


DicomVRParseDictionary: Dict[str, Callable[[str], Optional[ParsedElementValue_]]] = {
    "DA": parse_da_vr,
    "DS": lambda value: float(value),
    "TM": lambda value: float(value),
    "US": lambda value: int(value),
    "IS": lambda value: int(value),
    "PN": lambda value: value.encode("utf-8").decode("utf-8"),
}


def safe_get_(dcm: FileDataset, tag: int) -> Optional[ParsedElementValue]:
    try:
        element = dcm[tag]
        VR, element_value = dictionary_VR(tag), element.value

        if element_value == "" or element_value is None:
            return None

        vr_parser = DicomVRParseDictionary.get(VR, lambda value: value)
        if isinstance(element_value, MultiValue) is not isinstance(element_value, Sequence):
            return cast(ParsedElementValue, [vr_parser(item) for item in element_value])

        return vr_parser(element_value)
    except KeyError:
        logger.debug(f"Cannot find element using for tag={to_dicom_tag(tag)}")
        return None
    except ValueError as error:
        logger.warning(f"Encountered ValueError extracting element for tag={to_dicom_tag(tag)} - err={error}")
        return None


def safe_get(dcm: FileDataset, tag: int) -> Optional[ParsedElementValue]:
    element = safe_get_(dcm, tag)
    VM: str = dictionary_VM(tag)
    return [] if element is None and VM != "1" else element


if __name__ == '__main__':
    ds = pydicom.dcmread('./img_97584793.dcm')
    ds_to_jpeg(ds, "img.jpg")