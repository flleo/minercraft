from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = 'grass',
            color = color.rgb(255,255,255),
            hightlight_color = color.lime,
        )

    def input(self, key):
        if self.hovered:
            if key == "right mouse down":
                voxel = Voxel(position= self.position * mouse.normal)
            if key == "left mouse down":
                destroy(self)

chunkSize = 56

for z in  range(chunkSize):
    for x in range(chunkSize):
        voxel = Voxel(position=(x, 0, z))

player = FirstPersonController()
app.run()