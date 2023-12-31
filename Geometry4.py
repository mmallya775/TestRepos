import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygeos
import trimesh
from scipy.spatial import Delaunay
from shapely.geometry import MultiPoint, Polygon
from shapely.wkb import loads
import multiprocessing

# Add a way to sort the final list of coordinates using the z coordinate and then store the sorted array in a separate
# np array


class GeometryImport:

    def __init__(self, filepath: str) -> None:
        self.filename = filepath

    def get_points(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

        mesh = trimesh.load_mesh(self.filename)
        number_sampling_points = 2_000_000
        pointcloud, _ = trimesh.sample.sample_surface(mesh, number_sampling_points)

        return self.shift_center(np.asarray(pointcloud[:, 0]), np.asarray(pointcloud[:, 1]), np.asarray(pointcloud[:, 2]
                                                                                                        ))

    @staticmethod
    def shift_center(x, y, z) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        mid_x = (max(x) + min(x)) / 2
        mid_y = (max(y) + min(y)) / 2
        mid_z = (max(z) + min(z)) / 2

        x = x - mid_x
        y = y - mid_y
        z = z - mid_z

        return x, y, z

    def points_visualization(self) -> None:
        common_array_x, common_array_y, common_array_z = self.get_points()
        # common_array = np.vstack((common_array_x, common_array_y, common_array_z))
        fig = plt.figure(figsize=(16, 9))
        ax1 = plt.axes(projection='3d')
        ax1.plot(common_array_x, common_array_y, common_array_z, marker='o', c='r')
        ax1.set_xlim(-120, 120)
        ax1.set_ylim(-120, 120)
        ax1.set_zlim(-120, 120)
        plt.show()

    def alpha_shape(self, points: np.ndarray, alpha: float) -> Polygon:
        """
        Computes the alpha shape (concave hull) of a set of points.

        :param points: np.ndarray, array containing the x and y coordinates of points.
        :param alpha: float, alpha value to determine the alpha shape.
        :return: Polygon, the computed alpha shape as a Shapely Polygon object.
        """
        if len(points) < 4:
            return MultiPoint(list(points)).convex_hull
        tri = Delaunay(points)
        triangles = points[tri.simplices]
        a = ((triangles[:, 0, 0] - triangles[:, 1, 0]) ** 2 + (triangles[:, 0, 1] - triangles[:, 1, 1]) ** 2) ** 0.5
        b = ((triangles[:, 1, 0] - triangles[:, 2, 0]) ** 2 + (triangles[:, 1, 1] - triangles[:, 2, 1]) ** 2) ** 0.5
        c = ((triangles[:, 2, 0] - triangles[:, 0, 0]) ** 2 + (triangles[:, 2, 1] - triangles[:, 0, 1]) ** 2) ** 0.5
        s = (a + b + c) / 2.0
        areas = (s * (s - a) * (s - b) * (s - c)) ** 0.5
        circum_r = a * b * c / (4.0 * areas)
        filters = circum_r < 1.0 / alpha
        triangles = triangles[filters]
        if len(triangles) == 0:
            return MultiPoint(list(points)).convex_hull
        polygons = [pygeos.polygons(triangle) for triangle in triangles]

        return loads(pygeos.to_wkb(pygeos.union_all(polygons)))

    def parallel_generate_sequential_contour_points(self, alpha_value=0.5, layer_height=1.0) -> np.ndarray:

        x, y, z = self.get_points()
        points = np.column_stack((x, y, z))

        z_min = np.min(points[:, 2])
        z_max = np.max(points[:, 2])

        z_values = list(np.arange(z_min, z_max, layer_height))
        if z_values[-1] != z_max:
            z_values.append(z_max)
        # Generating a list of z values where each layer will be generated

        print("Z_values list")
        print(z_values)
        n_processes = multiprocessing.cpu_count()

        # Dividing z_values into nearly equal chunks for each process
        chunks = [z_values[i::n_processes] for i in range(n_processes)]

        with multiprocessing.Pool(n_processes) as pool:
            args = [(self, chunks[i], alpha_value, layer_height) for i in range(n_processes)]
            results = pool.map(self._generate_contours, args)

        df = pd.DataFrame(data=np.vstack(results))
        df.to_excel("rapidtesting.xlsx")

        return np.vstack(results)

    @staticmethod
    def _generate_contours(args):
        instance, z_values, alpha_value, layer_height = args
        x, y, z = instance.get_points()
        points = np.column_stack((x, y, z))

        all_contour_points = []

        for z in z_values:
            layer = points[(points[:, 2] >= z) & (points[:, 2] < z + layer_height)]
            if len(layer) == 0:
                continue
            concave_hull = instance.alpha_shape(layer[:, :2], alpha=alpha_value)
            if concave_hull.is_empty:
                continue
            # z_layer = z + layer_height / 2
            z_layer = z
            if concave_hull.geom_type == 'Polygon':
                x, y = concave_hull.exterior.xy
                contour_points = np.column_stack((x, y, np.full_like(x, z_layer)))
                all_contour_points.append(contour_points)
            elif concave_hull.geom_type == 'MultiPolygon':
                for polygon in concave_hull:
                    x, y = polygon.exterior.xy
                    contour_points = np.column_stack((x, y, np.full_like(x, z_layer)))
                    all_contour_points.append(contour_points)

        if all_contour_points:
            return np.vstack(all_contour_points)
        else:
            return np.array([])  # Return an empty array if no contour points are generated.

    @staticmethod
    def plot_contours(data) -> None:

        """
        Plot outer contours with changing colors for each unique z value along with a color bar.

        Parameters
        ----------
        data : numpy.ndarray
        An ndarray of shape (n, 3) where each row represents (x, y, z) coordinates.

        Returns
        -------
        None
        """

        # Extract x, y, and z columns
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]

        print(f"Maximum z value: {max(z)}")
        print(f"Minimum z value: {min(z)}")

        # Create a figure and 3D axis
        fig = plt.figure(figsize=(16,9))
        ax = fig.add_subplot(111, projection='3d')

        # Get unique z values and assign a color to each
        unique_z = np.unique(z)
        colors = plt.cm.viridis(np.linspace(0, 1, len(unique_z)))

        # Plot the lines with changing colors
        for i, z_val in enumerate(unique_z):
            mask = (z == z_val)
            x_level = x[mask]
            y_level = y[mask]
            z_level = z[mask]
            print(i)
            # Connect the last and first points to form a closed contour
            x_level = np.append(x_level, x_level[0])
            y_level = np.append(y_level, y_level[0])
            z_level = np.append(z_level, z_level[0])

            ax.plot(x_level, y_level, z_level, color=colors[i])

        # Add labels and legend
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)
        ax.set_zlim(-100, 100)

        ax.grid(False)
        plt.show()
