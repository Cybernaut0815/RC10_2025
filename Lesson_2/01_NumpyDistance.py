# %%
import numpy as np
import matplotlib.pyplot as plt
# %%

# Implementation 1: Loop-based approach
# Iterates through each point, calculates distances, tracks closest point indices,
# then applies influences based on which point is nearest to each position
field = np.zeros((50, 50)) + 0.1
pts = np.array([[10, 10], [20, 30], [40, 35]])
influences = np.array([0.5, 1.0, 0.5])

# Create coordinate grids
y_coords, x_coords = np.mgrid[0:50, 0:50]

# Calculate minimum distance and track which point is closest
min_distances = None
closest_point_indices = None

for i in range(pts.shape[0]):
    distance = np.sqrt((x_coords - pts[i, 0])**2 + (y_coords - pts[i, 1])**2)
    if i == 0:
        min_distances = distance
        closest_point_indices = np.zeros_like(distance, dtype=int)
    else:
        mask = distance < min_distances
        min_distances = np.where(mask, distance, min_distances)
        closest_point_indices = np.where(mask, i, closest_point_indices)

# Apply influences based on closest point
field = min_distances * influences[closest_point_indices]

# %%

plt.figure(figsize=(10, 10))
plt.imshow(field)
plt.colorbar()
plt.show()
# %%


# Implementation 2: Vectorized approach using broadcasting
# Calculates all distances at once using broadcasting with None indexing,
# applies influences to all distance arrays, then finds minimum across points axis
# %%

# DETAILED EXPLANATION:
# 
# Step 1: Setup
pts = np.array([[10, 10], [20, 30], [40, 35]])  # Shape: (3, 2) - 3 points with x,y coordinates
influences = np.array([0.5, 1.0, 0.5])           # Shape: (3,) - influence value for each point

# Step 2: Create coordinate grids
y, x = np.mgrid[0:50, 0:50]                      # Both shape: (50, 50) - grid of all positions

# Step 3: Add dimensions using None indexing for broadcasting
# x[None, :, :] reshapes from (50, 50) to (1, 50, 50)
# pts[:, 0, None, None] reshapes from (3,) to (3, 1, 1) - extracts x-coordinates of all points
# Broadcasting allows subtraction: (1, 50, 50) - (3, 1, 1) = (3, 50, 50)
# This creates 3 layers (one per point), each containing x-differences for all grid positions

# Step 4: Calculate distances to all points simultaneously
dists = np.sqrt((x[None, :, :] - pts[:, 0, None, None])**2 + (y[None, :, :] - pts[:, 1, None, None])**2)
# Result shape: (3, 50, 50) - distance from each of 3 points to all 50x50 grid positions

# Step 5: Apply influences and find minimum
# influences[:, None, None] reshapes from (3,) to (3, 1, 1)
# Multiplying: (3, 50, 50) * (3, 1, 1) = (3, 50, 50) - each distance layer multiplied by its influence
# .min(axis=0) reduces along first axis, keeping minimum across the 3 points
field = (dists * influences[:, None, None]).min(axis=0)
# Result shape: (50, 50) - minimum influenced distance at each position

# %%

plt.figure(figsize=(10, 10))
plt.imshow(field)
plt.colorbar()
plt.show()
