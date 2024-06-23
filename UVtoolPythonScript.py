__author__ = "Veenxz"
__version__ = "2024.06.23"

import cv2
import shutil
from glob import glob
from datetime import datetime
import matplotlib.pyplot as plt
from UVtoolsBootstrap import *
from UVtools.Core.Operations import OperationProgress
from System.Collections.ObjectModel import RangeObservableCollection
from UVtools.Core.Objects import GenericFileRepresentation

# Print Head
print('\n', 5*'* ', 'UVtool python script DLP parameters modification', 5*'* ', '\n',
      12*'* ', datetime.now().strftime('%Y-%m-%d %H:%M:%S '), 12*'* ', '\n')


# Import PNG images using cv2
def import_pngs_with(folder_path):
    pattern = f"{folder_path}/*.png"
    png_files = glob(pattern)
    images = []
    for file_path in png_files:
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            images.append(img)
        else:
            print(f"Failed to open {file_path}")
    return images


# Import images from the specified folder
folder_path = './Pic'
images = import_pngs_with(folder_path)
image = images[0]

# Import dl2p file
file_name = 'Focus.dl2p'
slicerFile = FileFormat.Open(file_name)

# Extract basic file information
start_layer = slicerFile.FirstLayerIndex
normal_layer = slicerFile.FirstNormalLayer.Index
end_layer = slicerFile.LastLayerIndex
layer_count = slicerFile.Count
res_high = slicerFile.ResolutionX
res_width = slicerFile.ResolutionY

# Print file basic info
print(f"File Name: {file_name}")
print(f"Start Layer Index: {start_layer}")
print(f"First Normal Layer Index: {normal_layer}")
print(f"End Layer Index: {end_layer}")
print(f"Layer Count: {layer_count}")

# Update DLP parameters
# light power
slicerFile.BottomLightPWM = int(255*0.9)
slicerFile.LightPWM = int(255*0.8)
# exposure time [s]
slicerFile.BottomExposureTime = 25
slicerFile.ExposureTime = 30
# BottomLayers and TransitionLayers
slicerFile.BottomLayerCount = 3
slicerFile.TransitionLayerCount = 0
# wait time [s]
slicerFile.BottomWaitTimeBeforeCure = 0
slicerFile.WaitTimeBeforeCure = 1
slicerFile.BottomWaitTimeAfterCure = 0
slicerFile.WaitTimeAfterCure = 1
# lift hight [s] and speed [mm/min]
slicerFile.BottomLiftHeight = 3
slicerFile.BottomLiftSpeed = 60
slicerFile.LiftHeight = 2
slicerFile.LiftSpeed = 60
slicerFile.BottomLiftHeight2 = 0
slicerFile.BottomLiftSpeed2 = 120
slicerFile.LiftHeight2 = 0
slicerFile.LiftSpeed2 = 120
slicerFile.BottomWaitTimeAfterLift = 0
slicerFile.WaitTimeAfterLift = 0
slicerFile.BottomRetractSpeed = 180
slicerFile.RetractSpeed = 180
slicerFile.BottomRetractHeight2 = 0
slicerFile.BottomRetractSpeed2 = 180
slicerFile.RetractHeight2 = 0
slicerFile.RetractSpeed2 = 180

# get layer info
i = 10
print(f"Layer ExposureTime {i} is: {slicerFile[i].ExposureTime} s")
# print(dir(slicerFile))
# print(dir(slicerFile[10]))

layer = slicerFile[10]

# RemoveRange(index, count)
slicerFile.RemoveRange(0, layer_count)
print(f"Layer Count After Remove Layers: {slicerFile.LayerCount}")

# Import new layers
import_layer = OperationLayerImport(slicerFile)
ImportType = OperationLayerImport.ImportTypes.Insert
import_layer.set_ImportType(ImportType)
import_layer.set_StartLayerIndex(0)
# Create a new RangeObservableCollection of GenericFileRepresentation
files_collection = RangeObservableCollection[GenericFileRepresentation]()
folder_path = './Pic'
pattern = f"{folder_path}/*.png"
png_files = glob(pattern)
print(f"NLayers to Add: {len(png_files)}")
# Populate the collection with GenericFileRepresentation instances
for file_path in png_files:
    # Assuming GenericFileRepresentation has a constructor that takes a file path
    file_representation = GenericFileRepresentation(file_path)
    files_collection.Add(file_representation)

# Use the populated collection with set_Files
import_layer.set_Files(files_collection)
import_layer.Execute()

print(f"Layer Count After Add Layers: {slicerFile.LayerCount}")


# Move ROI
MarginTop = 300
MarginBottom = 0
MarginLeft = 300
MarginRight = 0
move = OperationMove(slicerFile)
move.set_MarginTop(MarginTop)
move.set_MarginBottom(MarginBottom)
move.set_MarginLeft(MarginLeft)
move.set_MarginRight(MarginRight)
move.Execute()


# Export images
LayerIndexStart = 0
LayerIndexEnd = 5
OutputFolder = './Target'
OutputFilename = 'slice'
PNG = FileFormat.DATATYPE_PNG
export_image = OperationLayerExportImage(slicerFile)
export_image.LayerExportImageTypes = PNG
operation_progress = OperationProgress()
export_image.set_OutputFolder(OutputFolder)
export_image.set_Filename(OutputFilename)
export_image.set_LayerIndexStart(LayerIndexStart)
export_image.set_LayerIndexEnd(LayerIndexEnd)
export_image.ExecuteInternally(operation_progress)


# Visualize a specific layer
# visulize with mat_object = slicerFile[0].LayerMat ?
index = 8
LayerIndexStart = index
LayerIndexEnd = index
OutputFolder = './temp'  # Use a temporary folder
OutputFilename = 'slice'
PNG = FileFormat.DATATYPE_PNG

# Assuming slicerFile is defined and OperationLayerExportImage, OperationProgress are available
export_image = OperationLayerExportImage(slicerFile)
export_image.LayerExportImageTypes = PNG
operation_progress = OperationProgress()
export_image.set_OutputFolder(OutputFolder)
export_image.set_Filename(OutputFilename)
export_image.set_LayerIndexStart(LayerIndexStart)
export_image.set_LayerIndexEnd(LayerIndexEnd)
export_image.ExecuteInternally(operation_progress)

# Construct the full path to the exported image
image_path = glob(f"{OutputFolder}/*.png")
# Read the image using OpenCV
image = cv2.imread(image_path[0])
# Delete the temporary folder and its contents
shutil.rmtree(OutputFolder)


# Show the image
# Create a figure with the calculated size
dpi = 300
plt.figure(figsize=(res_width/dpi, res_high/dpi))
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()

# write file
slicerFile.SaveAs('output.dl2p')
print('\n', 12*'* ', 'Modification finished! ', 12*'* ')
