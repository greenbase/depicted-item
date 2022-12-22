"""
This script automatically generates png-images of CAD models provided as a step
file.

To use it place your step files in the models directory. Then run this script.
For each model the specified amount of images will be generated and stored in 
the images directory. The images will have the same name as the model with a
suffix indicating the number of the image. For each image the model will be
rotated randomly and the zoom level will be randomly adjusted. At least one
rotation angel will differ by at least 10° for every image.

You can alter the settings below to meet your requirements.

The script is using the FreeCAD API. Note that it is assumed that there is only
one root object in the FreeCAD document into which the step file is loaded. If
there are multiple root objects they will not be rotated!
Also the FreeCAD window will flash up then the script is run. This is might to 
be improved on.
"""

# ****************** SETTINGS **********************

# Amount of images to be made per model. 
IMAGES_TOTAL = 5  # Max. 36**3

# resolution and background of images to be saved
RESOLUTION_X = 500
RESOLUTION_Y = 500
BACKGROUND = 'Transparent'  # 'White', 'Black', 'Transparent', 'Current"

# Zoom level interval (refers to the height of the camera over the model)
camera_height_factor_min = 0.5 
camera_height_factor_max = 1.5

# **************************************************

import math
import random
from pathlib import Path

import freecad
import FreeCAD
import FreeCADGui
import Import
import numpy as np

# # setup logger
# import logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(levelname)s %(asctime)s - %(message)s')
# file_handler = logging.FileHandler("main.log", "w")
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)

# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.WARNING)
# stream_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


def load_model(path:str):
    """
    Load a model from a step file into a FreeCAD document.

    Args:
        path (str): The file location of the step file.

    Returns:
        freecad_document (FreeCAD.Document)
    """
    Import.open(path)
    return FreeCAD.ActiveDocument

def get_rotation_angels(angels_used:list[list[float]]) -> list[float]:
    """
    Get new set of rotation angels in radians for which at least one differs by at least 10° to all other rotation around that axis used previously.

    Args:
        angels_used (list[list[float]]): list of list with x,y,z-angels in radians.

    Returns:
        new_angels (list[float]): list of float. New valid angels in radians.    
    """
    new_angels_valid = False

    # get new set of angels if not at least one differs more than 10° from each # other previously used for rotation on this axis
    while not new_angels_valid:
        rotation_angel_x = random.vonmisesvariate(math.pi, 0)
        rotation_angel_y = random.vonmisesvariate(math.pi, 0)
        rotation_angel_z = random.vonmisesvariate(math.pi, 0)
        new_angels = np.array([rotation_angel_x, rotation_angel_y, rotation_angel_z])
        
        # check if set of angels has not been used on model before
        if len(angels_used) == 0:
            new_angels_valid = True
        for angels in angels_used:
            angels = np.array(angels)
            new_angels_valid = any(abs(new_angels - angels) > 10*math.pi/180)
            if not new_angels_valid:
                break

    return list(new_angels)
        
def rotate_model(freecad_doc, angels:list[float]) -> None:
    """
    Rotate the model in the given freecad document around all three axes for the given rotation angels [x,y,z]. 

    Note: In `freecad_doc` only the first root object is rotated.

    Args:
        freecad_doc (FreeCAD.Document) 
        angels (list[float]): Angels by which to rotate the model around all three axes

    Returns:
        None
    """
    # get object placement as matrix 
    new_placement_matrix = freecad_doc.RootObjects[0].Placement.toMatrix()
    
    # transform matrix by rotating it around xyz
    new_placement_matrix.rotateX(angels[0])
    new_placement_matrix.rotateY(angels[1])
    new_placement_matrix.rotateZ(angels[2])

    # assign new placement to model 
    new_placement = FreeCAD.Placement(new_placement_matrix)
    freecad_doc.RootObjects[0].Placement = new_placement



def main():
    ROOT = Path(".")
    PICTURES_DIR = ROOT/"images"
    MODELS_DIR = ROOT/"models"
    model_paths = MODELS_DIR.glob("*.step")
    
    # setup FreeCADGui. During runtime the empty window will be showing
    FreeCADGui.showMainWindow()

    for model_path in model_paths:
        load_model(model_path.as_posix())
        doc = FreeCAD.ActiveDocument
        camera = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
        view = FreeCADGui.ActiveDocument.ActiveView
        angels_used = []  
        placement_original = doc.RootObjects[0].Placement


        # rotate model and take pictures
        for image_index in range(IMAGES_TOTAL):
            # reset placement
            doc.RootObjects[0].Placement = placement_original

            # rotate model
            angels = get_rotation_angels(angels_used)
            angels_used.append(angels)
            rotate_model(doc, angels)

            # assure model is centered and is fit to whole screen
            # resets camera height (zoom)
            FreeCADGui.ActiveDocument.ActiveView.fitAll()

            # alter camera zoom
            zoom_factor = random.uniform(camera_height_factor_min, camera_height_factor_max)
            camera.scaleHeight(zoom_factor)

            # save image
            image_name = f"{model_path.stem}_#{image_index}.png"
            image_target_path = PICTURES_DIR/image_name
            view.saveImage(
                image_target_path.as_posix(),
                RESOLUTION_X,
                RESOLUTION_Y,
                BACKGROUND,
                )

        FreeCAD.closeDocument(doc.Name)


if __name__ == "__main__":
    main()