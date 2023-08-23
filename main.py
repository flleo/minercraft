from random import randrange
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor, abs, sin, cos, radians
import time
from perlin_noise import PerlinNoise
from nMap import nMap
# from safe_combine import safe_combine

app = Ursina()

window.color = color.rgb(0, 200, 211)
window.exit_button.visible = False
# window.fullscreen = True
# window.show_ursina_splash = True

prevTime = time.time()

scene.fog_color = color.rgb(0, 222, 0)
scene.fog_density = .02

strokeGrassTex = 'stroke_grass_14.png'
monoTex = 'stroke_mono.png'
wireTex = 'wireframe.png'
stoneTex = 'grass_mono.png'
cubeTex = 'moonCube.png'
cubeMod = 'moonCube'
blockTex = 'block_texture.png'
imgTex = 'img.png'
grassTex = 'grass_block_side.png'
axoTex = 'axolotl.png'
axoModel = 'axolotl'
pickaxeTex = 'diamond_pickaxe.png'
axeTex = 'diamond_axe_tex.png'
pickaxeMod = 'Diamond-Pickaxe'

ii = 1

# Built material


class BTYPE:
    STONE = color.rgb(255, 255, 255)
    GRASS = color.rgb(0, 255, 0)
    SOIL = color.rgb(255, 80, 100)
    RUBY = color.rgb(255, 0, 0)


blockType = BTYPE.STONE
buildMode = -1  # -1 is OFF, 1 is ON

bte = Entity(model='cube', texture=grassTex)


def buildTool():
    if buildMode == -1:
        bte.visible = False
    else:
        bte.visible = True
    bte.position = round(subject.position + camera.forward * 2)
    bte.y += 2
    bte.x = round(bte.x)
    bte.y = round(bte.y)
    bte.z = round(bte.z)
    bte.color = blockType

# Build new cube
def build():
    e = duplicate(bte)
    e.collider = 'cube'
    e.color = blockType
    e.shake(duration=.5, speed=.01)


# Keep the cursor inside the game
class Voxel(Button):
    def input(self, key):
        if self.hovered:
            if key == "right mouse down":
                voxel = Voxel(position= self.position * mouse.normal)
            if key == "left mouse down":
                destroy(self)



def input(key):
    global blockType, buildMode, generating, canGenerate, ii
    if key == 'q' or key == 'escape':
        quit()
    if key == 'g':
        generating *= -1
        canGenerate *= -1
    if buildMode == 1 and key == 'left mouse up':
        build()
    elif buildMode == 1 and key == 'right mouse up':
        e = mouse.hovered_entity
        destroy(e)

    if key == 'f': buildMode *= -1

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
    input_handler.rebind('insert', str(ii+1),)



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
numSubsets = 420     # I.e. how many combined into a megaset?
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


def genPerlin(_x, _z):
    y = 0
    freq = 64
    amp = 42
    y += ((noise([_x / freq, _z / freq])) * amp)
    freq = 32
    amp = 21
    y += ((noise([_x / freq, _z / freq])) * amp)
    return floor(y)


def genTerrain():
    global currentCube, theta, rad, currentSubset, generating, numSubCubes, cubeMod, blockTex

    if generating == -1: return
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
        y = subCubes[currentCube].y = genPerlin(x, z)
        g = nMap(y, -8, 21, 132, 212)
        g += random.randint(-32, 32)
        subCubes[currentCube].color = color.rgb(g, g, g)
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
                currentSubset = 0
                print('Megaset #' + str(len(megasets))+'!')

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


def generateShell():
    # global subject
    # target_y = genPerlin(subject.x, subject.z) + 4
    # subject.y = lerp(subject.y, target_y, .1)
    global shellWidth
    for i in range(len(shellies)):
        x = shellies[i].x = floor((i / shellWidth) + subject.x - 0.5 * shellWidth)
        z = shellies[i].z = floor((i % shellWidth) + subject.z - 0.5 * shellWidth)
        shellies[i].y = genPerlin(x, z)


subject = FirstPersonController()
subject.cursor.visible = False
subject.gravity = 0.5
subject.x = subject.z = 5
subject.y = 32
prevZ = subject.z
prevX = subject.x
origin = subject.position  # Vec3 object? .x .y .z

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