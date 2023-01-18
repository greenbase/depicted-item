import unittest
import sys
sys.path.append("C:/Users/dmansfel/Anaconda3/envs/depicted-item/Library/bin")
import freecad
import FreeCAD
import main
import numpy as np
import os
from pathlib import Path
import math

# add root dir to pythonpath; relative to file location
os.chdir(Path(__file__).parent)
sys.path.append(os.path.realpath("."))


class TestLoadModel(unittest.TestCase):

    def test_step_file(self):
        path_test_step_file = Path("M4-Nut.step")
        result = main.load_model(path_test_step_file.as_posix())
        self.assertIsInstance(result,FreeCAD.Document)


class TestGetRotationAngels(unittest.TestCase):

    def test_angels_differ(self):
        """
        Test if at least one angel differs by at least 10 degrees to each other unvalid angel around the same axis.
        """
        angels_not_valid = [[math.pi]*3]
        angels_not_valid_array = np.array(angels_not_valid[0])

        # test x call of function to account for random selection of angels
        for _ in range(1000):
            result = main.get_rotation_angels(angels_used=angels_not_valid)
            result = np.array(result)

            # check if at least one angel differs by more than 10 degrees when
            # comared to the corresponding unvalid (already used) angel
            diff = np.abs(angels_not_valid_array - result)
            self.assertTrue(any(diff > (10*math.pi/180) ))


class TestRotateModel(unittest.TestCase):

    def test_list_of_int(self):
        # define input
        freecad_document = main.load_model("M4-Nut.step")
        angels = [10,10,10]

        # rotate loaded model
        main.rotate_model(freecad_document, angels)

        # get placement of model after rotation as a tupel
        placement = freecad_document.ActiveObject.Placement.toMatrix().A
        

        placement_true = (0.704041030906696, -0.7048033701048229, -0.08705421465225388, 0.0, 0.4564726253638138, 0.5430331037628842, -0.7048033701048229, 0.0, 0.5440211108893698, 0.4564726253638138, 0.704041030906696, 0.0, 0.0, 0.0, 0.0, 1.0)

        for new_value, true_value in zip(placement, placement_true):
            self.assertAlmostEquals(new_value, true_value)
        
            

if __name__ == '__main__':
    unittest.main()