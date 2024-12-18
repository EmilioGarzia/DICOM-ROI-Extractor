import cv2 as cv
import argparse as ap
import numpy as np
import os
import sys
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ImplicitVRLittleEndian, generate_uid
import matplotlib.pyplot as plt

# Convert arg string in tuple
def string_to_tuple(string):
    try:
        return tuple(map(int, string.strip("()").split(",")))
    except ValueError:
        raise argparse.ArgumentTypeError("The right format for the size is w,h")

def extract_metadata(dicom_file):
    metadata = {
        "PatientName": dicom_file.PatientName,
        "PatientID": dicom_file.PatientID,
        "StudyInstanceUID": dicom_file.StudyInstanceUID,
        "SeriesInstanceUID": dicom_file.SeriesInstanceUID,
        "StudyDate": dicom_file.StudyDate,
        "StudyTime": dicom_file.StudyTime,
        "Modality": dicom_file.Modality,
        "SOPClassUID": dicom_file.SOPClassUID,
        "SOPInstanceUID": dicom_file.SOPInstanceUID
    }
    return metadata

# Extract the ROI from ecography raw image
def extract_roi_ecography(input_path):
    # Read DICOM file
    dicom_file = pydicom.dcmread(input_path)
    img = dicom_file.pixel_array
    img = np.uint8(img / np.max(img) * 255)

    # Divide the foreground from the background
    _, threshold = cv.threshold(img, 30, 255, cv.THRESH_BINARY)
    # find contours
    contours, _ = cv.findContours(threshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # The ecography should be the bigger object, so pick the higher contour
    main_contour = max(contours, key=cv.contourArea)
    # Get the coordinates of the main contour
    x, y, w, h = cv.boundingRect(main_contour)
    # Region of interest (ROI)
    roi = img[y:y+h, x:x+w]
    return roi

# Save extracetd ROI as DICOM file
def save_image_as_dicom(image, filename, metadata, output_path, verbose=False):
    # Crea il dataset file meta
    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationVersion = b'\x00\x01'
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

    # Crea il dataset principale
    dicom_file = Dataset()
    dicom_file.file_meta = file_meta
    
    # Metadati paziente e studio
    dicom_file.PatientName = metadata.get("PatientName", "Unknown")
    dicom_file.PatientID = metadata.get("PatientID", "Unknown")
    dicom_file.StudyInstanceUID = metadata.get("StudyInstanceUID", generate_uid())
    dicom_file.SeriesInstanceUID = metadata.get("SeriesInstanceUID", generate_uid())
    dicom_file.StudyID = metadata.get("StudyID", "1")
    dicom_file.SeriesNumber = metadata.get("SeriesNumber", "1")
    dicom_file.InstanceNumber = metadata.get("InstanceNumber", "1")
    dicom_file.StudyDate = metadata.get("StudyDate", "20240101")
    dicom_file.StudyTime = metadata.get("StudyTime", "120000")
    dicom_file.Modality = metadata.get("Modality", "OT")
    dicom_file.SOPClassUID = metadata.get("SOPClassUID")
    dicom_file.SOPInstanceUID = metadata.get("SOPInstanceUID")

    # Metadati immagine
    dicom_file.ImageType = ['ORIGINAL', 'PRIMARY']
    dicom_file.SamplesPerPixel = 1
    dicom_file.PhotometricInterpretation = "MONOCHROME2"
    dicom_file.Rows, dicom_file.Columns = image.shape
    dicom_file.BitsAllocated = 8
    dicom_file.BitsStored = 8
    dicom_file.HighBit = 7
    dicom_file.PixelRepresentation = 0
    dicom_file.PixelData = image.tobytes()

    # Imposta attributi richiesti
    dicom_file.is_little_endian = True
    dicom_file.is_implicit_VR = True

    # Salva il file DICOM
    dicom_filepath = os.path.join(output_path, filename)
    dicom_file.save_as(dicom_filepath, write_like_original=False)

    if verbose:
        print(f"File DICOM salvato in: {dicom_filepath}")

# Plot DICOM image using MATPLOTLIB
def visualize_dicom(dicom_file_path, metadata=False):
    dicom_file = pydicom.dcmread(dicom_file_path, force=False)
    image_data = dicom_file.pixel_array
    plt.imshow(image_data, cmap='gray')
    plt.show()

    if metadata:
        metadatas = extract_metadata(dicom_file=dicom_file)
        print("______________________________________________")
        print(dicom_file_path)
        print("______________________________________________")
        print(f"|PatientName : {metadatas['PatientName']}")
        print(f"|PatientID : {metadatas['PatientID']}")
        print(f"|StudyInstanceUID : {metadatas['StudyInstanceUID']}")
        print(f"|SeriesInstanceUID : {metadatas['SeriesInstanceUID']}")
        print(f"|StudyDate : {metadatas['StudyDate']}")
        print(f"|StudyTime : {metadatas['StudyTime']}")
        print(f"|Modality : {metadatas['Modality']}")