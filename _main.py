"""
Minecraft in Python, with Ursina, tut 11
Petter Amland :)
3.2) Dictionary for stepping onto built blocks
4) Caves
5) Layers of terrain
DONE 6) Axe model
7) Fog darkens/changes colour as we descend height
DONE 8) Trees

...
DONE near future) axe draw bug
DONE future) (very basic) Mining!
"""

from random import randrange
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor, abs, sin, cos, radians
import time
from perlin_noise import PerlinNoise
from nMap import nMap
from cave_system import Caves
from tree_system import Trees

app = Ursina()

# Create a cave system object. It's called anush.
anush = Caves()
# Same again, but for trees :)
sol4r = Trees()

window.color = color.rgb(0, 200, 211)
window.exit_button.visible = False

prevTime = time.time()

scene.fog_color = color.rgb(0, 222, 0)
scene.fog_density = 0.02

# Load in textures and models.
grassStrokeTex = 'grass_14.png'
monoTex = 'stroke_mono.png'
wireTex = 'wireframe.png'
stoneTex = 'grass_mono.png'

cubeTex = 'block_texture.png'

cubeModel = 'moonCube'

axoTex = 'axolotl.png'
axoModel = 'axolotl.obj'

axeModel = 'Diamond-Pickaxe'
axeTex = 'diamond_axe_tex'

# Building code...
bte = Entity(model='cube', texture=wireTex, scale=1.01)
# distance of build (Thanks, Ethan!)
build_distance = 3
# To rotate type of material(color) to build
ii = 1

class BTYPE:
    STONE = color.rgb(255, 255, 255)
    GRASS = color.rgb(0, 255, 0)
    SOIL = color.rgb(255, 80, 100)
    RUBY = color.rgb(255, 0, 0)


blockType = BTYPE.SOIL
buildMode = -1  # -1 is OFF, 1 is ON.


def buildTool():
    global build_distance
    if buildMode == -1:
        bte.visible = False
        return
    else:
        bte.visible = True
    bte.position = round(subject.position +
                         camera.forward * build_distance)
    bte.y += 2
    bte.y = round(bte.y)
    bte.x = round(bte.x)
    bte.z = round(bte.z)
    bte.color = blockType


def build():
    # e = duplicate(bte)
    e = Entity(model='cube', position=bte.position)
    e.collider = 'box'
    e.texture = stoneTex
    e.color = blockType
    e.shake(duration=0.5, speed=0.01)


def mine():
    e = mouse.hovered_entity
    destroy(e)
    # Our real mining of the terrain :)
    # Iterate over all the subsets that we have...
    for s in range(len(subsets)):
        vChange = False
        totalY = 0
        for v in subsets[s].model.vertices:
            # Is the vertex close enough to
            # where we want to mine (bte position)?
            if (v[0] >= bte.x - 0.5 and
                    v[0] <= bte.x + 0.5 and
                    v[1] >= bte.y - 0.5 and
                    v[1] <= bte.y + 0.5 and
                    v[2] >= bte.z - 0.5 and
                    v[2] <= bte.z + 0.5):
                # Yes!
                v[1] -= 1
                # Note that we have made change.
                # Gather average height for cave dic.
                totalY += v[1]
                vChange = True
        subsets[s].model.generate()
        # Record change of height in cave dictionary :)
        if vChange == True:
            totalY = floor(totalY / 8)
            anush.makeCave(bte.x, bte.z, bte.y - 1)


def input(key):
    global blockType, buildMode, generating, ii
    global canGenerate
    global build_distance

    # scroll down to build closer or
    # scroll up to build further
    # Thanks again, Ethanalos! :)
    if key == 'scroll up':
        build_distance += 1
    if key == 'scroll down':
        build_distance -= 1

    if key == 'q' or key == 'escape':
        quit()
    if key == 'g':
        generating *= -1
        canGenerate *= -1

    if buildMode == 1 and key == 'left mouse up':
        build()
    elif buildMode == 1 and key == 'right mouse up':
        mine()

    if key == 'f': buildMode *= -1

    if key == '1': blockType = BTYPE.SOIL
    if key == '2': blockType = BTYPE.GRASS
    if key == '3': blockType = BTYPE.STONE
    if key == '4': blockType = BTYPE.RUBY

    # Binding key for linkers
    if key == '1':
        blockType = BTYPE.SOIL
        ii = 1
    if key == '2':
        blockType = BTYPE.GRASS
        ii = 2
    if key == '3':
        blockType = BTYPE.STONE
        ii = 3
    if key == '4':
        blockType = BTYPE.RUBY
        ii = 4
    input_handler.rebind('page down', 'd')
    input_handler.rebind('delete', 'a')
    input_handler.rebind('home', 'w')
    input_handler.rebind('right control', 'space')
    input_handler.rebind('end', 's')
    input_handler.rebind('enter', 'f')
    input_handler.rebind('backspace', 'q')
    input_handler.rebind('page up', 'g')
    input_handler.rebind('insert', str(ii + 1), )


def update():
    global prevZ, prevX, prevTime, genSpeed, perCycle
    global rad, origin, generating, canGenerate
    if abs(subject.z - prevZ) > 1 or \
            abs(subject.x - prevX) > 1:
        origin = subject.position
        rad = 0
        theta = 0
        generating = 1 * canGenerate
        prevZ = subject.z
        prevX = subject.x

    generateShell()

    if time.time() - prevTime > genSpeed:
        for i in range(perCycle):
            genTerrain()
        prevTime = time.time()

    vincent.look_at(subject, 'forward')
    # vincent.rotation_x = 0

    buildTool()


noise = PerlinNoise(octaves=1, seed=99)

megasets = []
subsets = []
subCubes = []
# New variables :)
generating = 1  # -1 if off.
canGenerate = 1  # -1 if off.
genSpeed = 0
perCycle = 64
currentCube = 0
currentSubset = 0
numSubCubes = 64
numSubsets = 420  # I.e. how many combined into a megaset?
theta = 0
rad = 0
# Dictionary for recording whether terrain blocks exist
# at location specified in key.
subDic = {}

# Instantiate our 'ghost' subset cubes.
for i in range(numSubCubes):
    bud = Entity(model=cubeModel, texture=cubeTex)
    bud.scale *= 0.99999
    bud.rotation_y = random.randint(1, 4) * 90
    bud.disable()
    subCubes.append(bud)

# Instantiate our empty subsets.
for i in range(numSubsets):
    bud = Entity(model=cubeModel)
    bud.texture = cubeTex
    bud.disable()
    subsets.append(bud)


def genPerlin(_x, _z, plantTree=False):
    y = 0
    freq = 64
    amp = 42
    y += ((noise([_x / freq, _z / freq])) * amp)
    freq = 32
    amp = 21
    y += ((noise([_x / freq, _z / freq])) * amp)

    # Is there are cave-gap here?
    # If so, lower the cube by 32...or something ;)
    whatCaveHeight = anush.checkCave(_x, _z)
    if whatCaveHeight != None:
        y = whatCaveHeight
    elif plantTree == True:
        sol4r.checkTree(_x, y, _z)

    return floor(y)


def genTerrain():
    global currentCube, theta, rad, currentSubset
    global generating

    if generating == -1: return

    # Decide where to place new terrain cube!
    x = floor(origin.x + sin(radians(theta)) * rad)
    z = floor(origin.z + cos(radians(theta)) * rad)
    # Check whether there is terrain here already...
    if subDic.get('x' + str(x) + 'z' + str(z)) != 'i':
        subCubes[currentCube].enable()
        subCubes[currentCube].x = x
        subCubes[currentCube].z = z
        subDic['x' + str(x) + 'z' + str(z)] = 'i'
        subCubes[currentCube].parent = subsets[currentSubset]
        y = subCubes[currentCube].y = genPerlin(x, z, True)
        # OK -- time to decide colours :D
        c = nMap(y, -8, 21, 132, 212)
        c += random.randint(-32, 32)
        subCubes[currentCube].color = color.rgb(c, c, c)
        subCubes[currentCube].disable()
        currentCube += 1

        # Ready to build a subset?
        if currentCube == numSubCubes:
            subsets[currentSubset].combine(auto_destroy=False)
            subsets[currentSubset].enable()
            currentSubset += 1
            currentCube = 0

            # And ready to build a megaset?
            if currentSubset == numSubsets:
                megasets.append(Entity(model=cubeModel,
                                       texture=cubeTex))
                # Parent all subsets to our new megaset.
                for s in subsets:
                    s.parent = megasets[-1]
                # In case user has Ursina version 3.6.0.
                # safe_combine(megasets[-1],auto_destroy=False)
                megasets[-1].combine(auto_destroy=False)
                for s in subsets:
                    s.parent = scene
                currentSubset = 0
                print('Megaset #' + str(len(megasets)) + '!')

    else:
        pass
        # There was terrain already there, so
        # continue rotation to find new terrain spot.

    if rad > 0:
        theta += 45 / rad
    else:
        rad += 0.5

    if theta >= 360:
        theta = 0
        rad += 0.5


shellies = []
shellWidth = 3
for i in range(shellWidth * shellWidth):
    bud = Entity(model='cube', collider='box')
    bud.visible = False
    shellies.append(bud)


# Our new gravity system for moving the subject :)
def generateShell():
    global subject, grav_speed, grav_acc

    # How high or low can we step/drop?
    step_height = 5

    # What y is the terrain at this position?
    target_y = genPerlin(subject.x, subject.z) + 2

    # How far are we from the target y?
    target_dist = target_y - subject.y
    # Can we step up or down?
    if target_dist < step_height and target_dist > -step_height:
        subject.y = lerp(subject.y, target_y, 9.807 * time.dt)
    elif target_dist < -step_height:
        # This means we're falling!
        grav_speed += (grav_acc * time.dt)
        subject.y -= grav_speed

    # global shellWidth
    # for i in range(len(shellies)):
    #     x = shellies[i].x = floor((i/shellWidth) +
    #                         subject.x - 0.5*shellWidth)
    #     z = shellies[i].z = floor((i%shellWidth) +
    #                         subject.z - 0.5*shellWidth)
    #     shellies[i].y = genPerlin(x,z)


subject = FirstPersonController()
subject.cursor.visible = False
subject.gravity = 0
grav_speed = 0
grav_acc = 0.1
subject.x = subject.z = 5
subject.y = 32
prevZ = subject.z
prevX = subject.x
origin = subject.position  # Vec3 object? .x .y .z
# Our axe :D
axe = Entity(model=axeModel,
             texture=axeTex,
             scale=0.07,
             position=subject.position,
             always_on_top=True)
axe.x -= 3
axe.z -= 2.2
axe.y -= subject.y
axe.rotation_z = 90
axe.rotation_y = 180
axe.parent = camera

chickenModel = load_model('chicken.obj')
vincent = Entity(model=chickenModel, scale=1,
                 x=22, z=16, y=4,
                 texture='chicken.png',
                 double_sided=True)

baby = Entity(model=axoModel, scale=10,
              x=-22, z=16, y=4,
              texture=axoTex,
              double_sided=True)

generateShell()

app.run()