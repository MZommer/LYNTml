"""Script for filtering the bins in the bf"""

import os
import shutil

from LYN.LynTML import LynTML

os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

for file in os.listdir("./input"):
    if os.path.isfile("./input/" + file):
        print(file)
        tml = LynTML()
        try:
            tml.deserialize("./input/" + file, True)
        except:
            pass
        if tml.CodeName != "":
            print(f"{tml.CodeName} Found!")
            shutil.copy("./input/" + file, f"./output/({tml.CodeName}){file}")
