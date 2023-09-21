from random import randrange

from direct.showbase.ShowBaseGlobal import globalClock
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor, abs, sin, cos, radians
import time
from perlin_noise import PerlinNoise
from nMap import nMap
from cave_system import Caves
from tree_system import Trees

app = Ursina()

anush = Caves()
sol4r = Trees()

window.color = color.rgb(0, 200, 211)
window.exit_button.visible = False
# window.fullscreen = True
# window.show_ursina_splash = True

prevTime = time.time()

scene.fog_color = color.rgb(0, 222, 0)
scene.fog_density = .02

# Built material
strokeGrassTex = 'stroke_grass_14.png'
monoTex = 'stroke_mono.png'
wireTex = 'wireframe.png'
stoneTex = 'grass_mono.png'
cubeTex = 'block_texture.png'
cubeMod = 'moonCube',
blockTex = 'block_texture.png'
imgTex = 'img.png'
grassTex = 'grass_block_side.png'
axoTex = 'axolotl.png'
axoModel = 'axolotl'
pickaxeTex = 'diamond_pickaxe.png'
axeTex = 'diamond_axe_tex.png'
axeMod = 'Diamond-Pickaxe'
strippedTex = 'stripped_birch_log.png'
# To rotate type of material(color) to build
ii = 1


class BTYPE:
    STONE = color.rgb(255, 255, 255)
    GRASS = color.rgb(0, 255, 0)
    SOIL = color.rgb(255, 80, 100)
    RUBY = color.rgb(255, 0, 0)


blockType = BTYPE.STONE
buildMode = -1  # -1 is OFF, 1 is ON

# Our mining tool
bte = Entity(model='cube', texture=wireTex)
build_distance = 3


def buildTool():
    global build_distance
    if buildMode == -1:
        bte.visible = False
    else:
        bte.visible = True
    bte.position = round(subject.position + camera.forward * build_distance)
    bte.y += 2
    bte.x = round(bte.x)
    bte.y = round(bte.y)
    bte.z = round(bte.z)
    bte.color = blockType


e_grass_tex = None


# Build new cube
def build():
    global e_grass_tex
    # e = duplicate(bte)
    e = Entity(model='cube', position=bte.position)
    e.collider = 'box'
    e.texture = grassTex
    e.model = 'cube'
    e.color = blockType
    e.shake(duration=.5, speed=.01)


# Mine a cube
def mine():
    e = mouse.hovered_entity
    destroy(e)
    # Iterate over all the subsets that we have
    # for s in range(len(subsets)):
    #     vCount = 0
        # var = subsets[s].
        # print(var)
        # for v in subsets[s].model.vertices:
        #     if (bte.x - 0.5 <= v[0] <= bte.x + 0.5 and
        #             bte.y - 0.5 <= v[1] <= bte.y + 0.5 and
        #             bte.z - 0.5 <= v[2] <= bte.z + 0.5):
        #         # Yes!
        #         v[1] -= 1
        #         vCount += 1
        # print('Hola, estoy minando!')
        # subsets[s].model.generate()

def input(key):
    global blockType, buildMode, generating, canGenerate, ii, build_distance
    if key == 'q' or key == 'escape':
        quit()
    # Toogle generating the terrin
    if key == 'g':
        generating *= -1
        canGenerate *= -1
    if buildMode == 1 and key == 'left mouse up':
        build()
    elif buildMode == 1 and key == 'right mouse up':
        mine()
    if key == 'scroll up':
        build_distance += 1
        # build_distance += 1
    if key == 'scroll down':
        build_distance -= 1
        # build_distance -= 1
    if key == 'f':
        buildMode *= -1
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

    # Binding key for linkers
    input_handler.rebind('page down', 'd')
    input_handler.rebind('delete', 'a')
    input_handler.rebind('home', 'w')
    input_handler.rebind('right control', 'space')
    input_handler.rebind('end', 's')
    input_handler.rebind('enter', 'f')
    input_handler.rebind('backspace', 'q')
    input_handler.rebind('\\', 'g')
    input_handler.rebind('insert', str(ii + 1), )


def update():
    global prevTime, prevZ, prevX, genSpeed, perCycle, origin, rad, generating, canGenerate, theta, ii
    if ii == 4:
        ii = 0
    if abs(subject.z - prevZ) > 1 or abs(subject.x - prevX) > 1:
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
    vincent.rotation_z = 0

    buildTool()


noise = PerlinNoise(octaves=1, seed=99)
megasets = []
subsets = []
subCubes = []

# New variables
generating = 1  # -1 if off
canGenerate = 1  # -1 is off
genSpeed = 0
perCycle = 160
currentCube = 0
currentSubset = 0
numSubCubes = 160
numSubsets = 210  # I.e. how many combined into a megaset?
theta = 0
rad = 0
# Dictionary for recording whether terrain blocks exist al location specified in key
subDic = {}

# Instantiate our 'ghost' subset cubes
for i in range(numSubCubes):
    bud = Entity(model='cube', texture=grassTex)
    bud.disable()
    subCubes.append(bud)

# Instantiate our empty subset
for i in range(numSubsets):
    bud = Entity(model='cube', texture=grassTex)
    bud.disable()
    subsets.append(bud)


def genPerlin(_x, _z, plant_tree=False):
    y = 0
    freq = 64
    amp = 42
    y += ((noise([_x / freq, _z / freq])) * amp)
    freq = 32
    amp = 21
    y += ((noise([_x / freq, _z / freq])) * amp)

    # is there are cave-gap here?
    # If so, lower the cube by 32...or something
    if anush.checkCave(_x, _z):
        y -= 9
    elif plant_tree:
        sol4r.checkTree(_x, y, _z)

    return floor(y)


def genTerrain():
    global currentCube, theta, rad, currentSubset, generating, numSubCubes, cubeMod, blockTex, e_grass_tex

    if generating == -1:
        return
    # Decide where to place new terrain cube
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

            # And ready to buyild a megaset?
            if currentSubset == numSubsets:
                megasets.append(Entity(model='cube', texture=grassTex))
                # Parent all subsets to our new megaset
                for s in subsets:
                    s.parent = megasets[-1]
                megasets[-1].combine(auto_destroy=False)
                for s in subsets:
                    s.parent = scene
                currentSubset = 0
                # print('Megaset #' + str(len(megasets))+'!')

    else:
        pass
    # There was terrain already there, so continue rotation to find new terrain spot.
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
    bud = Entity(model='cube', collider='cube')
    bud.visible = False
    shellies.append(bud)


# Our new gravity system for moving the subject
def generateShell():
    global subject, grav_speed, grav_ace
    delta_time = globalClock.getDt()
    step_height = 0
    # What y is the terrain at this position?
    target_y = genPerlin(subject.x, subject.z) + 2
    # subject.y = lerp(subject.y, target_y, 9.807 * delta_time)
    # How far are we from the target y?
    target_dist = target_y - subject.y
    if 0 < target_dist < 5:
        # To return to the original point to don't let us fall
        subject.y = lerp(subject.y, target_y, 9.807 * delta_time)
    # We are falling
    elif target_dist < -step_height:
        grav_speed += grav_ace * delta_time
        subject.y -= grav_speed
    # print('subject_y: ' + str(subject.y) + ';       target_y: ' + str(target_y))

    # global shellWidth
    # for i in range(len(shellies)):
    #     x = shellies[i].x = floor((i / shellWidth) + subject.x - 0.5 * shellWidth)
    #     z = shellies[i].z = floor((i % shellWidth) + subject.z - 0.5 * shellWidth)
    #     shellies[i].y = genPerlin(x, z)


# Subject First Person
subject = FirstPersonController()
subject.cursor.visible = False
subject.gravity = 0
grav_speed = 0
grav_ace = 0.1
subject.x = subject.z = 5
subject.y = 26
prevZ = subject.z
prevX = subject.x
origin = subject.position  # Vec3 object? .x .y .z
# Our axe
axe = Entity(model=axeMod, scale=0.1, texture=axeTex, position=subject.position, always_on_top=True)
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
                 double_sided=True,
                 colaider='mesh')
baby = Entity(model=axoModel, scale=10,
              x=-22, z=16, y=4,
              texture=axoTex,
              double_sided=True,
              colaider='mesh')

generateShell()

app.run()
