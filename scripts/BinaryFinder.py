"""Script for filtering the bins in the bf."""

import contextlib
import os
import shutil

from LYN.LynTML import LynTML

os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

for file in os.listdir("./input"):
    if os.path.isfile("./input/" + file):
        tml = LynTML()
        with contextlib.suppress(Exception):
            tml.deserialize("./input/" + file, True)
        if tml.CodeName != "":
            shutil.copy("./input/" + file, f"./output/({tml.CodeName}){file}")
