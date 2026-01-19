
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = f"{BASE_DIR}/GTSRB/Training"


for directory_name in os.listdir(DATA_DIR):
    directory_path = f"{DATA_DIR}/{directory_name}"
    
    if not os.path.isdir(directory_path):
        print(directory_name)