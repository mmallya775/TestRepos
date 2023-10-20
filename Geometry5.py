import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the STL file
mesh = trimesh.load_mesh("NewConeCirc.STL")

# Sample 50,000 points from the surface
points, index = trimesh.sample.sample_surface(mesh, 50000)

# Group points by their Z-coordinate into 1mm layers
layers = {}
for i, point in enumerate(points):
    z_key = int(np.floor(point[2]))
    if z_key not in layers:
        layers[z_key] = {"points": [], "normals": []}
    layers[z_key]["points"].append(point)
    layers[z_key]["normals"].append(mesh.face_normals[index[i]])

# Visualization with Matplotlib
fig = plt.figure(figsize=(10, 5))
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122)

# Show original point cloud
ax1.scatter(points[:,0], points[:,1], points[:,2], s=1)
ax1.set_title("Original Point Cloud")

# Iterate and plot over the layers
z_vals = []
mean_angles = []

for key, layer in layers.items():
    layer_points = np.array(layer["points"])
    layer_normals = np.array(layer["normals"])
    
    z_vals.append(layer_points[:, 2].mean())
    
    # Calculating the local normal angles for each point in the layer
    local_angles = np.arccos(np.clip(np.sum(layer_normals * [0, 0, 1], axis=1), -1.0, 1.0))
    mean_angles.append(np.mean(local_angles))

angle_degrees = np.degrees(mean_angles)
# Show mean of local normal angles with increasing Z-value
ax2.plot(angle_degrees, z_vals, 'o')
ax2.set_title("Mean Local Normal Angles vs Z-Value")
ax2.set_ylabel("Z-Value")
ax2.set_xlabel("Mean Local Normal Angle (radians)")
ax2.set_xlim(0, 90)

plt.tight_layout()
plt.show()
