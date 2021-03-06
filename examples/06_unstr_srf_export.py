import numpy as np
import matplotlib.pyplot as pt
from gstools import SRF, Exponential
from gstools.random import MasterRNG
from gstools import vtk_export

# creating our own unstructured grid
seed = MasterRNG(19970221)
rng = np.random.RandomState(seed())
x = rng.randint(0, 100, size=10000)
y = rng.randint(0, 100, size=10000)

model = Exponential(dim=2, var=1, len_scale=[12., 3.], angles=np.pi/8.)

srf = SRF(model, seed=20170519)

field = srf((x, y))

vtk_export('field', (x, y), field)

pt.tricontourf(x, y, field.T)
pt.axes().set_aspect('equal')
pt.show()

