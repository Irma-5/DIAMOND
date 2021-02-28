import random, sys, copy, os, pygame
from pygame.locals import *
from settings import *

def main():
    # инициализация игры
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('DIAMOND RUSH')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    # ниже описаны списки с изображениями для печати карты
    IMAGESDICT = {'uncovered goal': pygame.image.load('RedSelector.png'), #1
                  'covered goal': pygame.image.load('Selector.png'), #1
                  'diamond': pygame.image.load('diamond.png'), #1
                  'corner': pygame.image.load('wall.png'), #1
                  'wall': pygame.image.load('wall.png'), #1
                  'inside floor': pygame.image.load('grave.png'), #1
                  'outside floor': pygame.image.load('grass.png'), #1
                  'title': pygame.image.load('diamond_title.png'), #1
                  'solved': pygame.image.load('diamond_solved.png'),  #1
                  'boy2': pygame.image.load('boy1.png'),  # пероснажи
                  'boy': pygame.image.load('boy.png'), #1
                  'among': pygame.image.load('among.png'), #1
                  'dino': pygame.image.load('dino.png'), #1
                  'girl': pygame.image.load('girl.png'), #1
                  'girl2': pygame.image.load('girl1.png'), #1
                  'rock': pygame.image.load('Rock.png'), #1
                  'short tree': pygame.image.load('Tree_Short.png'), # растительность
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png')}
    TILEMAPPING = {'x': IMAGESDICT['corner'],   # стены, пол и тд
                   '#': IMAGESDICT['wall'],
                   'o': IMAGESDICT['inside floor'],
                   ' ': IMAGESDICT['outside floor']}
    OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],  # декорации
                          '2': IMAGESDICT['short tree'],
                          '3': IMAGESDICT['tall tree'],
                          '4': IMAGESDICT['ugly tree']}
    currentImage = 0

    # персонажи
    PLAYERIMAGES = [IMAGESDICT['boy2'],
                    IMAGESDICT['boy'],
                    IMAGESDICT['girl'],
                    IMAGESDICT['girl2']]
    startScreen()
    levels = readLevelsFile('DiamondLevels.txt')
    # эта переменная отвечает за уровень, на котором мы сейчас находимся
    currentLevelIndex = 0
    while True:
        result = runLevel(levels, currentLevelIndex)
        # проверка изменилась ли карта
        if result in ('solved', 'next'):
            currentLevelIndex += 1  # автоперемещение в случае выигрыша
            if currentLevelIndex >= len(levels):
                currentLevelIndex = 0
        elif result == 'back':  # перемещение на предыдущий уровень, если игрок нажал соответствубщую клавишу
            currentLevelIndex -= 1
            if currentLevelIndex < 0:  # зацикливание уровей
                currentLevelIndex = len(levels) - 1
        elif result == 'reset':
            pass  # если ничего не изменилось


def runLevel(levels, levelNum):
    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True
    levelSurf = BASICFONT.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT
    levelIsComplete = False
    cameraOffsetX = 0
    cameraOffsetY = 0
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False
    while True:
        playerMoveTo = None
        keyPressed = False
        for event in pygame.event.get():  # проверка различных событий, в том числе перемещения, сдвига камеры и тд
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True
                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:  # Если пользователь захотел изменить персонажа (именно буква "P", потому что
                    # Person начинается с "P", поэтому кнопку проще запомнить)
                    currentImage += 1
                    if currentImage >= len(PLAYERIMAGES):
                        currentImage = 0
                    mapNeedsRedraw = True
            elif event.type == KEYUP:
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False
        if playerMoveTo != None and not levelIsComplete:
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)
            if moved:
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True
            if isLevelFinished(levelObj, gameStateObj):  # Конец уровня
                levelIsComplete = True
                keyPressed = False
        DISPLAYSURF.fill(BGCOLOR)
        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False
        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:  # Камера движется)
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX, HALF_WINHEIGHT + cameraOffsetY)
        DISPLAYSURF.blit(mapSurf, mapSurfRect)
        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)
        if levelIsComplete:  # Показ картинки решено (успешное прохождение уровня)
            solvedRect = IMAGESDICT['solved'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGESDICT['solved'], solvedRect)
            if keyPressed:
                return 'solved'
        pygame.display.update()  # обновление экрана
        FPSCLOCK.tick()


def isWall(mapObj, x, y):  # Проверка наличия стен
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False
    elif mapObj[x][y] in ('#', 'x'):
        return True
    return False


def decorateMap(mapObj, startxy):  # в этой функции отрисовываются различные деревья и тд, дополняющие карту до
    # фиксированного размера
    startx, starty = startxy
    mapObjCopy = copy.deepcopy(mapObj)
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '
    floodFill(mapObjCopy, startx, starty, ' ', 'o')
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y - 1) and isWall(mapObjCopy, x + 1, y)) or \
                        (isWall(mapObjCopy, x + 1, y) and isWall(mapObjCopy, x, y + 1)) or \
                        (isWall(mapObjCopy, x, y + 1) and isWall(mapObjCopy, x - 1, y)) or \
                        (isWall(mapObjCopy, x - 1, y) and isWall(mapObjCopy, x, y - 1)):
                    mapObjCopy[x][y] = 'x'
            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(
                    OUTSIDEDECOMAPPING.keys()))  # для простоты декорации отрисовываются рандомно, таким образом,
                # при перезапуске уровня, декорации поменяются
    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):  # данная функция отвечает за возможность подвинуть алмаз
    if isWall(mapObj, x, y):
        return True
    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True
    elif (x, y) in gameStateObj['diamonds']:
        return True
    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):
    playerx, playery = gameStateObj['player']
    diamonds = gameStateObj['diamonds']
    if playerMoveTo == UP:  # проверка, куда игрок хочет пойти, и, в зависимости от этого, присваивание
        xOffset = 0  # предварительным значениям +- 1.
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0
    # проверка, можно ли присвоить эти значения окончательно
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in diamonds:
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset * 2), playery + (yOffset * 2)):
                ind = diamonds.index((playerx + xOffset, playery + yOffset))
                diamonds[ind] = (diamonds[ind][0] + xOffset, diamonds[ind][1] + yOffset)
            else:
                return False
        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True


def startScreen():  # Зарисовка начального экрана и правила
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50  #
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height
    instructionText = ['Доведите алмазики до цели, чтобы пройти уровень',
                       'WASD для управления',
                       'Backspace для обновления уровня, Esc для выхода.',
                       'N - седующий уровень, B - предыдущий.',
                       'P - Чтобы сменить персонажа']
    DISPLAYSURF.fill(BGCOLOR)
    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height
        DISPLAYSURF.blit(instSurf, instRect)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return
        pygame.display.update()
        FPSCLOCK.tick()


def readLevelsFile(filename): # эта функция отвечает за чтение карт из файла
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)  # Если файл не найден
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']  # чтение содержимого
    mapFile.close()
    levels = []
    levelNum = 0
    mapTextLines = []
    mapObj = []
    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')
        if ';' in line:  # для линий с номером уровня игнор
            line = line[:line.find(';')]
        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:  # тут поиск длиннейшей
            maxWidth = -1  # для красивой постройки карты
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])
            startx = None
            starty = None
            goals = []
            diamonds = []
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'): #где игрок
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        diamonds.append((x, y))
            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'diamonds': diamonds}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}
            levels.append(levelObj)
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter
    if x < len(mapObj) - 1 and mapObj[x + 1][y] == oldCharacter:
        floodFill(mapObj, x + 1, y, oldCharacter, newCharacter)
    if x > 0 and mapObj[x - 1][y] == oldCharacter:
        floodFill(mapObj, x - 1, y, oldCharacter, newCharacter)
    if y < len(mapObj[x]) - 1 and mapObj[x][y + 1] == oldCharacter:
        floodFill(mapObj, x, y + 1, oldCharacter, newCharacter)
    if y > 0 and mapObj[x][y - 1] == oldCharacter:
        floodFill(mapObj, x, y - 1, oldCharacter, newCharacter)


def drawMap(mapObj, gameStateObj, goals):  # Прорисовка карты уровня
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)
    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']
            mapSurf.blit(baseTile, spaceRect)
            if mapObj[x][y] in OUTSIDEDECOMAPPING:
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['diamonds']:
                if (x, y) in goals:
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                mapSurf.blit(IMAGESDICT['diamond'], spaceRect)
            elif (x, y) in goals:
                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect)
            if (x, y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES[currentImage], spaceRect)
    return mapSurf


def isLevelFinished(levelObj, gameStateObj):  # Конец уровня
    for goal in levelObj['goals']:
        if goal not in gameStateObj['diamonds']: # Проверка, на правильное положение
            return False
    return True


def terminate(): # функция выхода
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
   
