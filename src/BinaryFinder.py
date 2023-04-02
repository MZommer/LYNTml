"""Script for filtering the bins in the bf"""

from LynTML import LynTML
import os
import shutil

for file in os.listdir("./input"):
    if os.path.isfile("./input/" + file):
        print(file)
        tml = LynTML()
        try:
            tml.Deserialize("./input/" + file)
        except:
            pass
        if tml.CodeName != "":
            print(f"{tml.CodeName} Found!")
            shutil.copy("./input/" + file, f"./output/({tml.CodeName}){file}")