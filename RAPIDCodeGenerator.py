"""
A python library to generate RAPID program from the points generated using an object of the Geometry class.

"""
import numpy as np


class RAPIDGenerator:
    i = 1
    def __init__(self):
        self.ModuleStart = 'MODULE Module1 \n'
        self.RobTargets = ''
        self.ProcMain = 'PROC main() \n'
        self.CallProc = 'Path; \n'
        self.EndProc = 'ENDPROC \n'
        self.PathProc = 'PROC Path() \n'
        self.EndModule = 'ENDMODULE \n'

    def robotarget_generator(self,translation, rotation=np.array([0, 0, 1, 0]), configuration=np.array([0, 0, 0, 0]),
              externalaxes=np.array(['9E9', '9E9', '9E9', '9E9', '9E9', '9E9'])) -> None:
        
        trn = f"[{translation[0] + 1500}, {translation[1]}, {translation[2] + 1000}]"
        rot = f"[{rotation[0]}, {rotation[1]}, {rotation[2]}, {rotation[3]}]"
        conf = f"[{configuration[0]}, {configuration[1]}, {configuration[2]}, {configuration[3]}]"
        ext = f"[{externalaxes[0]}, {externalaxes[1]}, {externalaxes[2]}, {externalaxes[3]}, {externalaxes[4]}, {externalaxes[5]}]"
        
        self.ModuleStart += f"    CONST robtarget p{self.i}:= [{trn}, {rot}, {conf}, {ext}]; \n"
        self.PathProc += f"    MoveL p{self.i}, v50, z50, MyTool\WObj:=wobj0; \n"
        self.i += 1

    def print_path(self):
        
        print(self.ModuleStart+ self.ProcMain + self.CallProc + self.EndProc + self.PathProc + self.EndProc +
              self.EndModule)
        return (self.ModuleStart + self.ProcMain + self.CallProc + self.EndProc + self.PathProc + self.EndProc +
                self.EndModule)
    