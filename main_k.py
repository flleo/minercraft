from pynput import keyboard as kb
from ursina import Button


def pulsa(tecla):
    print('Se ha pulsado la tecla ' + str(tecla))


with kb.Listener(pulsa) as escuchador:
    escuchador.join()



class Voxel(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__()

    def input(self, key):

        if self.hovered:
            if key == "left mouse down":
                voxel = Voxel(position=self.position * mouse.normal)
            if key == "right mouse down":
                print('bye')


def input(key):
    if key == 'v':
        voxel = Voxel(position=(0, -100, 0), )
