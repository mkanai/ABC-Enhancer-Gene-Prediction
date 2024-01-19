import os
import sys
import time
import unittest

import hicstraw
import pandas as pd

SCRIPTS_DIR = os.path.abspath("workflow/scripts")
sys.path.insert(0, SCRIPTS_DIR)
from predictor import add_hic_from_hic_file, determine_num_rows_to_fetch

HIC_FILE = "https://www.encodeproject.org/files/ENCFF621AIY/@@download/ENCFF621AIY.hic"
hic = hicstraw.HiCFile(HIC_FILE)
chromosome = "chr22"
matrix_object = hic.getMatrixZoomData(
    chromosome, chromosome, "observed", "SCALE", "BP", 5000
)
print("getting matrix")
# 11617893
mat = matrix_object.getRecordsAsMatrix(10677253, 11627893, 0, 50818468)
print(mat.shape)
time.sleep(5)
