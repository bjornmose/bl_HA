import sys
import os
import bpy

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import BVT
import OszHAV2


import importlib
importlib.reload(BVT)
importlib.reload(OszHAV2)

