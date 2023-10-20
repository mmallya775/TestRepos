import RAPIDCodeGenerator
from Geometry3 import GeometryImport
import time

if __name__ == "__main__":

    FILE_PATH = "NewConeCirc.STL"
    start_time = time.time()
    g2 = GeometryImport(filepath=FILE_PATH)
    pointcloud = g2.generate_sequential_contour_points(layer_height=1, alpha_value=0.2)
    end_time = time.time()
    print("Total Processing Time: ", end_time-start_time)
    
    print(pointcloud)

    rg = RAPIDCodeGenerator.RAPIDGenerator()

    for point in pointcloud:
        rg.robotarget_generator(translation=point)

    with open("Module1.mod", "w") as file:
        file.write(rg.print_path())
