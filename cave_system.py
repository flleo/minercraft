"""
Our cave system :)
Used by genPerlin() function.
"""


class Caves:
    def __init__(self):
        self.caveDic = {}
        self.buildCaves()

    def buildCaves(self):
        # Dictionary of cave 'gaps'
        self.caveDic = {
            'x9z9': -9,
            'x10z9': -9,
            'x11z9': -9,
            'x9z10': -9,
            'x9z11': -9}

    def checkCave(self, _x, _z):
        temp_str = self.caveDic.get('x'+str(int(_x))+'z'+str(int(_z)))
        return temp_str

    def makeCave(self, _x, _z, _height):
        temp_str = ('x'+str(int(_x))+'z'+str(int(_z)))
        self.caveDic[temp_str] = _height
    

