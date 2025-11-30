"""
NOTE:

- Reference to RhinoCommmon.dll is added by default

- You can specify your script requirements like:

    # r: <package-specifier> [, <package-specifier>]
    # requirements: <package-specifier> [, <package-specifier>]

    For example this line will ask the runtime to install
    the listed packages before running the script:

    # requirements: pytoml, keras

    You can install specific versions of a package
    using pip-like package specifiers:

    # r: pytoml==0.10.2, keras>=2.6.0

- Use env directive to add an environment path to sys.path automatically
    # env: /path/to/your/site-packages/
"""
#! python3

import rhinoscriptsyntax as rs
import scriptcontext as sc
import math

import System
import System.Collections.Generic
import Rhino


run_direct_add, run_memory_add, run_loop, run_nested_loop = False, False, False, True


# ------------------------------------------------------------
# Basic Types in Rhino
# ------------------------------------------------------------


# basic print function
print("Hello from python in Rhino! \n")


# python has no explicit types
# it has implicit types, but they don't have to be spefified on construction a value
a = 10                  # int
b = 4.2                 # float
c = [10, 23, 15]        # list
d = "Hello World!"      # string
e = (a, c)              # Tuple
f = {"object1": 15, "object2": b}

print(type(a), type(b), type(c), type(d), type(e), type(f))



item_0 = c[0]

# Accessing items from lists, tuples and dictionaries
print(f"Item at index 0: {item_0}, Item at indes 1: {c[2]}")
print("Length is " + str(len(c)) + "\n")



# ------------------------------------------------------------
# Creating Rhino Objects
# ------------------------------------------------------------


# There are 2 ways of creating geometry in Rhino:

########## 1. By adding it directly to the document: ##########
if run_direct_add:
    pointReference = rs.AddPoint(1, 1, 1) ###
    sphereReference = rs.AddSphere(pointReference, 3)

    # This will show a reference to the geometry
    print(type(pointReference), type(sphereReference))


########## 2. By creating it in memory ##########
# This cann be done bt using rhinoscriptsyntax.Rhino.Geometry methods
pointInMemory = rs.Rhino.Geometry.Point3d(-3, -3, -3)
sphereInMemory = rs.Rhino.Geometry.Sphere(pointInMemory, 1.5)

# This will show a reference to the geometry
print(type(pointInMemory), type(sphereInMemory))

if run_memory_add:
    # This is how we can add these objects to the scene:
    sphere_guid = sc.doc.Objects.AddSphere(sphereInMemory)


# ------------------------------------------------------------
# Creating objects in loops 
# ------------------------------------------------------------


# Now let's create a row of boxes that get larger and smaller peridically

import Rhino.Geometry as geom
from random import randint

boxes = []

# https://developer.rhino3d.com/api/rhinocommon/rhino.geometry.plane

# range loop
for i in range(0, 50): # with for i in range(0, 30, 2) that wouldn mean (start, end, stepsize)
    #scale = 2
    scale = math.sin(i*0.5) + 2

    pos = geom.Point3d(i*0.5,0,0)
    plane = geom.Plane(pos, geom.Vector3d(0,0,1))
    dim = [-0.5*scale, 0.5*scale]
    intervals = [geom.Interval(pos.X+dim[0], pos.X+dim[1]), geom.Interval(pos.Y+dim[0], pos.Y+dim[1]), geom.Interval(pos.Z+dim[0], pos.Z+dim[1])]

    box = geom.Box(plane, *intervals)
    boxes.append(box)

# for loop to add the boxes
if run_loop:
    for box in boxes:
        sc.doc.Objects.Add(box.ToBrep())

sc.doc.Views.Redraw()



# ------------------------------------------------------------
# Creating objects in nested loops 
# ------------------------------------------------------------
# Task: take what you saw above and use it to create a grid with varying sizes and/or colors based on points

points = [geom.Point3d(10, 10, 0), geom.Point3d(20, 40, 0), geom.Point3d(40, 35, 0)]
#influences = [0.5, 1., 0.5]
influences = [1., 1., 1.]
max_falloff_distance = None  # Optional: set to None for no limit

boxes = []
x_size, y_size = 50, 50

for x in range(0, x_size-1):
    for y in range(0, y_size-1):
        
        pos = geom.Point3d(x,y,0)
        min_distance = -1
        influence = 1
        
        for index in range(len(points)):
            distance = pos.DistanceTo(points[index])
            if distance < min_distance or min_distance < 0:
                min_distance = distance
                influence = influences[index]
        
        # Apply max falloff distance if specified
        if max_falloff_distance and min_distance > max_falloff_distance:
            scale = 1.0  # Minimum scale beyond falloff
        else:
            scale = (min_distance / 5 + 0.1) * influence
        
        plane = geom.Plane(pos, geom.Vector3d(0,0,1))
        dim = [-0.5*scale, 0.5*scale]
        intervals = [geom.Interval(pos.X+dim[0], pos.X+dim[1]), geom.Interval(pos.Y+dim[0], pos.Y+dim[1]), geom.Interval(pos.Z+dim[0], pos.Z+dim[1])]

        box = geom.Box(plane, *intervals)
        boxes.append(box)

if run_nested_loop:
    for box in boxes:
        sc.doc.Objects.Add(box.ToBrep())

sc.doc.Views.Redraw()