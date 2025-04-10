# LyN Engine
LyN engine, used in Just Dance 2-3-4 and spin-offs.

This engine uses BigFile bundles (.*BF).

The module has a LyNTML class that will deserialize this file for later processing.

In the tools folder you will find "BinFinder.py" which will filter the songs bins on the bf,
and "LYNtml.py" which will deserialize the bins for lately use in ubiart

## Functionalities

- Generates both .tml (xml) LyN timeline format and JSON BlueStar format, if the [BlueStar](https://github.com/MZommer/BlueStar) module is available, it will generate the UAF folder.
- Generates generic MoveSpaceModels and "decompress" the classifiers, LiveMoveClassifier (LMC) or GestureClassifier (Kinect Classifier) if available.
- Generates Placeholder pictograms it's respective names.
- It deserializes all events (XML only).
