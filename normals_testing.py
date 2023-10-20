import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load a mesh
# Ensure the STL file is in your working directory or provide the full path
mesh = trimesh.load_mesh('NewConeCirc.STL')  

# Sample points and normals
points, idx = trimesh.sample.sample_surface(mesh, count=50000)
normals = mesh.face_normals[idx]

# Offset points by 5mm along their normals
offset_distance = 5.0  # in mm
offset_points = points + offset_distance * normals

# Create a plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

points = points[points[:,0] < 60.0]
points = points[points[:,1] < 50.0]
offset_points = offset_points[offset_points[:,0] < 60.0]
offset_points = offset_points[offset_points[:,1] < 60.0]

# Plot original points
ax.scatter(points[:,0], points[:,1], points[:,2], s=0.1, c='b', label='Original')

# Plot offset points
ax.scatter(offset_points[:,0], offset_points[:,1], offset_points[:,2], s=0.1, c='r', label='Offset (5mm)')

# Set plot limits
max_range = np.array([points[:,0].max()-points[:,0].min(),
                      points[:,1].max()-points[:,1].min(),
                      points[:,2].max()-points[:,2].min()]).max() / 2.0

mid_x = (points[:,0].max()+points[:,0].min()) * 0.5
mid_y = (points[:,1].max()+points[:,1].min()) * 0.5
mid_z = (points[:,2].max()+points[:,2].min()) * 0.5

ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

# Add a legend
ax.legend()

# Add grid and labels if needed
ax.grid(True)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Show the plot

plt.show()
