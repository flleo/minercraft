"""
This is our trees system.
It plants trees (if appropriate) having been
called from the genPerlin() function in our
main module.
"""
from perlin_noise import PerlinNoise
from ursina import Entity, color, Vec3, random


def plant_tree(_x, _y, _z):
    tree = Entity(model=None, position=Vec3(_x, _y, _z))
    crown = Entity(model='cube', scale=6, y=7, color=color.green)
    trunk = Entity(model='cube', scale_x=0.6, scale_z=0.6, scale_y=9, color=color.brown, collider='box')
    crown.parent = tree
    trunk.parent = tree
    tree.y += 4
    tree.rotation_y = random.randint(0, 360)


class Trees:
    def __init__(self):
        self.noise = PerlinNoise(seed=4)

    def checkTree(self, _x, _y, _z):
        freq = 3
        amp = 100
        tree_chance = (self.noise([_x / freq, _z / freq]) * amp)
        if tree_chance > 40:
            plant_tree(_x, _y, _z)
