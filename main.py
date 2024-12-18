from dicom_manager import *
import os

# Parser
parser = ap.ArgumentParser()
parser.add_argument("-i", "--input_dir", required=True, help="Specify the path of the directory images")
parser.add_argument("-o", "--output_dir", required=False, default="output" ,help="Specify the path of the directory output images")
parser.add_argument("-s", "--size", type=string_to_tuple, default=None, help="Specify the size of the output image as w,h")
parser.add_argument("-r", "--raster", action="store_true", help="Save the ROI ecography even as raster image png")
args = parser.parse_args() 
args = vars(args)

if not os.path.exists(args["output_dir"]):
    print("Specified output directory not found!")
    sys.exit()
if not os.path.exists(args["input_dir"]):
    print("Specified input directory not found!")
    sys.exit()

width, height = args["size"] if args["size"] else (None, None)
input_directory = args["input_dir"]
output_directory = args["output_dir"]


# Driver code
if __name__ == "__main__":
    images = [image for image in os.listdir(input_directory) if image.endswith('.dcm')]

    for image in images:
        extracted_eco = extract_roi_ecography(f"{input_directory}/{image}")

        if args["size"]:
            extracted_eco = cv.resize(src=extracted_eco, dsize=(width, height), interpolation=cv.INTER_CUBIC)

        # Save ROI as DICOM
        original_dicom_file = pydicom.dcmread(f"{input_directory}/{image}")
        metadata = extract_metadata(dicom_file=original_dicom_file)
        save_image_as_dicom(image=extracted_eco, filename=image, metadata=metadata, output_path=output_directory)

        if args["raster"]:
            os.makedirs(f"{output_directory}/raster", exist_ok=True)
            cv.imwrite(f"{output_directory}/raster/{image[:-4]}.png", extracted_eco)

    visualize_dicom("output/image-00000.dcm", metadata=True)