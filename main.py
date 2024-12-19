"""
DICOM ROI Extractor

@author Emilio Garzia, 2024
"""

from dicom_manager import *
import os

# Parser
parser = ap.ArgumentParser()
parser.add_argument("-i", "--input_dir", required=True, help="Specify the path of the directory images")
parser.add_argument("-o", "--output_dir", required=False, default="output" ,help="Specify the path of the directory output images")
parser.add_argument("-s", "--size", type=string_to_tuple, default=None, help="Specify the size of the output image as w,h")
parser.add_argument("-r", "--raster", action="store_true", help="Save the ROI ecography even as raster image png")
parser.add_argument("-d", "--dicom", action="store_true", help="Specify that the input are DICOM files")
args = parser.parse_args() 
args = vars(args)

# Handle possible errors about directories
if not os.path.exists(args["output_dir"]):
    os.mkdir(args["output_dir"])
if not os.path.exists(args["input_dir"]):
    print("Specified input directory not found!")
    sys.exit()

width, height = args["size"] if args["size"] else (None, None)
input_directory = args["input_dir"]
output_directory = args["output_dir"]


# Driver code
if __name__ == "__main__":
    images = [image for image in os.listdir(input_directory)]

    for image in images:
        extracted_eco = extract_roi_ecography(f"{input_directory}/{image}", dicom=args["dicom"])
        
        if args["size"]:
            extracted_eco = cv.resize(src=extracted_eco, dsize=(width, height), interpolation=cv.INTER_CUBIC)

        if not args["dicom"]:
            cv.imwrite(f"{output_directory}/{image}", extracted_eco)
        else:
            # Save ROI as DICOM
            original_dicom_file = pydicom.dcmread(f"{input_directory}/{image}")
            metadata = extract_metadata(dicom_file=original_dicom_file)
            save_image_as_dicom(image=extracted_eco, filename=image, metadata=metadata, output_path=output_directory)
        
        # Export the DICOM images even as png
        if args["raster"] and ".dcm" in image:
            os.makedirs(f"{output_directory}/raster", exist_ok=True)
            cv.imwrite(f"{output_directory}/raster/{image[:-4]}.png", extracted_eco)

    # De-comment the statement below to visualize a DICOM image
    #visualize_dicom("image-00000.dcm", metadata=True)
