# LyN Engine
LyN engine, used in Just Dance 2-3-4 and spin-offs.

This engine uses BigFile bundles (.*BF).

The module has a LyNTML class that will deserialize this file for later proccessing.

In the tools folder you will find "BinFinder.py" which will filter the songs bins on the bf,
and "LYNtml.py" which will deserialize the bins for lately use in ubiart

## Functionalities

- Generates generic MoveSpaceModels and "decompress" the classifiers, LiveMoveClassifier (LMC) or GestureClassifier (Kinect Classifier) if available.
- Generates Placeholder pictograms it's respective names.
- If the [BlueStar](https://github.com/MZommer/BlueStar) module is available, it will generate the UAF folder.
- It tries to deserialize all events.

## TODOS:
- Make it deserialize in the XML format that the TML has.
- Refactor the Timeline class.
- Make decorator for the repetitive Hash and SizeOf parts.

### If you found it usefull remember to star repo <3