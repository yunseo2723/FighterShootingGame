import pygame
from pygame.locals import *
import sys
import random
import time

padwidth = 430  # 게임화면 가로 크기
padHeight = 660  # 게임화면 세로 크기
EnemyImage = ['Shooting/Image/Enemy01.png', 'Shooting/Image/Enemy02.png', 'Shooting/Image/Enemy03.png', 'Shooting/Image/Enemy04.png', 'Shooting/Image/Enemy05.png', 'Shooting/Image/Enemy06.png', 'Shooting/Image/Enemy07.png', 'Shooting/Image/Enemy08.png', 'Shooting/Image/Enemy09.png']
explosionSound = ['Shooting/music/explosionsound.mp3', 'Shooting/music/explosionsound02.mp3']
highCount = 0
def drawobject(obj, x, y):
    global gamePad
    gamePad.blit(obj, (x, y))


def initGame():
    global gamePad, clock, background, background02, fighter, fighterWidth, fighterHeight, missile, explosion, missileSound, gameOverSound, item, itemWidth, itemHeight, Enemy, EnemyHeight, EnemyWidth, destroySound, itemSound, missileHeight, missileWidth
    pygame.init()
    gamePad = pygame.display.set_mode((padwidth, padHeight))
    pygame.display.set_caption('PyShooting')  # 게임 이름
    background = pygame.image.load('Shooting/Image/background.png')  # 배경 그림
    background02 = pygame.image.load('Shooting/Image/background02.png')  # 배경 그림
    fighter = pygame.image.load('Shooting/Image/fighter.png')        # 전투기 그림
    fighter = pygame.transform.scale(fighter, (80, 80))  # 전투기 크기 조정
    fighterWidth = fighter.get_rect().size[0]           # 전투기 가로길이
    fighterHeight = fighter.get_rect().size[1]          # 전투기 세로길이
    missile = pygame.image.load('Shooting/Image/missile.png')           # 미사일 그림
    missile = pygame.transform.scale(missile, (15, 45))  # 미사일 크기 조정
    
    missileWidth = missile.get_rect().size[0]
    missileHeight = missile.get_rect().size[1]
    explosion = pygame.image.load('Shooting/Image/explosion.png')       # 폭발 그림
    item = pygame.image.load('Shooting/Image/item.png')       # 아이템 그림
    item = pygame.transform.scale(item, (30, 30))  # 아이템 크기조정
    itemWidth = item.get_rect().size[0]
    itemHeight = item.get_rect().size[1]
    pygame.mixer.music.load('Shooting/music/music.mp3')                 # 배경 음악
    pygame.mixer.music.play(0)                           # 배경 음악 재생
    missileSound = pygame.mixer.Sound('Shooting/music/missile.mp3')     # 미사일 사운드
    itemSound = pygame.mixer.Sound('Shooting/music/itemGet.mp3')     # 아이템 먹는 사운드
    gameOverSound = pygame.mixer.Sound('Shooting/music/gameover.mp3')   # 게임 오버 사운드
    clock = pygame.time.Clock()
    
    Enemy = pygame.image.load(random.choice(EnemyImage))
    Enemy = pygame.transform.scale(Enemy, (75, 75))  # 적기 크기 조정
    EnemyWidth = Enemy.get_rect().size[0]
    EnemyHeight = Enemy.get_rect().size[1]
    destroySound = pygame.mixer.Sound(random.choice(explosionSound))

# 적기를 맞춘 개수 계산
def writeScore(count, highCount):
    global gamePad
    font = pygame.font.SysFont("malgungothic", 20)
    text = font.render('스코어:' + str(count), True, (255,255,255))
    gamePad.blit(text, (10, 0))
    highScoreText = font.render('최고기록: ' + str(highCount), True, (255, 255, 255))
    gamePad.blit(highScoreText, (10, 30))

# 적기가 화면 아래로 통과한 개수
def writePassed(count):
    global gamePad
    font = pygame.font.SysFont("malgungothic", 20)
    text = font.render('놓친 적기:' + str(count), True, (255,0,0))
    gamePad.blit(text, (320,0))


def runGame():
    global gamePad, clock, background, background02, fighter, fighterWidth, fighterHeight, missile, missileHeight, missileWidth, explosion, score, missileSound, highCount,shotCount, Enemy, EnemyHeight, EnemyWidth, destroySound

    initGame()

    # 전투기 초기 위치
    x = padwidth * 0.41
    y = padHeight * 0.9
    fighterX = 0
    move_left = False   # 왼쪽 이동 상태 변수
    move_right = False  # 오른쪽 이동 상태 변수

    # 미사일 좌표 리스트
    missileXY = []

    # 적기 초기 위치 설정
    EnemyX = random.randrange(0, padwidth - EnemyWidth)
    EnemyY = 0
    EnemySpeed = 1 #적기 속도 설정

        # 아이템 박스 초기 위치 설정
    itemX = random.randrange(0, padwidth - itemWidth)
    itemY = -75
    itemSpeed = 2

    # 전투기 미사일에 적기가 맞았을 경우 True
    isShot = False

    shotCount = 0
    EnemyPassed = 0

    # 점수 변수 초기화
    score = 0

    onGame = False
    item_box_collected = 0
    collision_sound_playing = False  # 충돌 사운드 재생 중인지 여부

    while not onGame:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 게임 프로그램 종료
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:      # 전투기 왼쪽으로 이동
                    move_left = True

                elif event.key == pygame.K_RIGHT:   # 전투기 오른쪽으로 이동
                    move_right = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:      # 왼쪽 버튼 떼기
                    move_left = False
                elif event.key == pygame.K_RIGHT:   # 오른쪽 버튼 떼기
                    move_right = False

                # 충돌 상태를 검사하고 미사일 발사 동작을 수행하는 부분
                elif event.key == pygame.K_SPACE:  # 미사일 발사
                    missileSound.play()  # 미사일 사운드 재생
                    missile_positions = []  # 미사일 위치를 저장할 배열

                    if item_box_collected == 1:
                        # 충돌 상태에서는 2발씩 미사일 발사
                        missileX1 = x + fighterWidth / 3 - missileWidth / 2  # 첫 번째 미사일 가로 위치
                        missileY1 = y - fighterHeight / 2.5  # 첫 번째 미사일 세로 위치
                        missile_positions.append([missileX1, missileY1])

                        missileX2 = x + fighterWidth * 2 / 3 - missileWidth / 2  # 두 번째 미사일 가로 위치
                        missileY2 = y - fighterHeight / 2.5  # 두 번째 미사일 세로 위치
                        missile_positions.append([missileX2, missileY2])

                        missileXY.extend(missile_positions)  # 발사된 미사일 위치를 기존 미사일 배열에 추가
                    elif item_box_collected >= 2:
                        missile_positions.clear()  # 미사일 위치 배열을 초기화합니다.
                        missileX1 = x + fighterWidth / 4 - missileWidth / 2
                        missileY1 = y - fighterHeight / 2.5
                        missile_positions.append([missileX1, missileY1])

                        missileX2 = x + fighterWidth / 2 - missileWidth / 2
                        missileY2 = y - fighterHeight / 2.5
                        missile_positions.append([missileX2, missileY2])

                        missileX3 = x + fighterWidth * 3 / 4 - missileWidth / 2
                        missileY3 = y - fighterHeight / 2.5
                        missile_positions.append([missileX3, missileY3])

                        missileXY.extend(missile_positions)
                    else:
                            missileX1 = x + fighterWidth / 2.5
                            missileY1 = y - fighterHeight / 2.5
                            missileXY.append([missileX1, missileY1])

        # 충돌 상태를 검사하고 미사일 발사 동작을 수행하는 부분
        if ((itemY + itemHeight) >= y):
            if (itemX >= x and itemX + itemWidth <= x + fighterWidth) or (itemX + itemWidth >= x and itemX <= x + fighterWidth):
                if not collision_sound_playing:  # 충돌 사운드가 재생 중이 아닌 경우에만 재생
                    itemSound.play()  # 적기 폭발 사운드 재생                          
                    collision_sound_playing = True  # 충돌 사운드 재생 중 상태로 설정
                item_box_collected += 1
                itemY = -75
                collision_sound_playing = False

        if move_left and not move_right:  # 왼쪽으로 이동
            fighterX = -3
        elif move_right and not move_left:  # 오른쪽으로 이동
            fighterX = 3
        else:  # 멈춤
            fighterX = 0

        gamePad.blit(background, (0, 0))  # 배경 화면 그리기

        if shotCount > 10:
            gamePad.blit(background02, (0, 0))  # 10기 이상 처치시 배경 화면 변경

        x += fighterX
        if x < 0:
            x = 0
        elif x > padwidth - fighterWidth:
            x = padwidth - fighterWidth

        gamePad.blit(fighter, (x, y))  # 전투기 그리기

        # 미사일 발사 화면에 그리기
        if len(missileXY) != 0:
            for i, bxy in enumerate(missileXY):  # 미사일 요소에 대해 반복함
                bxy[1] -= 10   # 총알 속도
                missileXY[i][1] = bxy[1]

                # 미사일이 적기를 맞추었을 경우
                if bxy[1] < EnemyY + EnemyHeight and bxy[0] > EnemyX and bxy[0] < EnemyX + EnemyWidth:
                    missileXY.remove(bxy)
                    isShot = True
                    shotCount += 1
                    score += 100
                if shotCount > highCount:
                    highCount = shotCount

                if bxy[1] <= 0:  # 미사일이 화면 밖을 벗어나면
                    try:
                        missileXY.remove(bxy)  # 미사일 제거
                    except:
                        pass
 
        if len(missileXY) != 0:
            for bx, by in missileXY:
                drawobject(missile, bx, by)

        EnemyY += EnemySpeed  # 적기 아래로 움직임

        drawobject(item, itemX, itemY)

        if isShot:
            if (random.random() < 0.8 and not (-75 < itemY < padHeight)) :
            # 80%의 확률로 Y 좌표를 0으로 지정(아이템이 내려오도록 설정)
                itemY = 0 
        
        if itemY >= 0:
            itemY += itemSpeed  # 아이템 박스 아래로 움직임

        # 아이템 박스가 화면을 벗어났을 때
        if itemY > padHeight:
            itemY = -75  # Y 좌표를 -75로 다시 지정
        if item_box_collected == 2:
            itemY = -100
         

        # 적기 맞춘 점수 표시
        writeScore(shotCount, highCount)

        # 놓친 적기 수 표시
        writePassed(EnemyPassed)

        # 폭발 애니메이션 변수
        explosionFrame = 0  # 현재 폭발 애니메이션 프레임
        explosionTime = 1  # 폭발 애니메이션 시간
        isExploding = False  # 폭발 중인지 여부를 나타내는 변수

        # 적기를 격추하지 못한 경우
        if not isShot:
            drawobject(Enemy, EnemyX, EnemyY)

            if EnemyY > padHeight or itemY > padHeight:
                EnemyPassed += 1
                EnemyX = random.randrange(0, padwidth - EnemyWidth)
                EnemyY = 0

        # 전투기 위치 재조정
        x += fighterX
        if x < 0:
            x = 0
        elif x > padwidth - fighterWidth:
            x = padwidth - fighterWidth

        # 전투기가 적기와 충돌했는지 체크
        if y < EnemyY + EnemyHeight:
            if(EnemyX > x and EnemyX < x + fighterWidth) or \
                    (EnemyX + EnemyWidth > x and EnemyX + EnemyWidth < x + EnemyWidth):
                crash()

            drawobject(fighter, x, y)

        if EnemyPassed == 10:
            gameOver()

        # 적기를 맞춘 경우
        if isShot:
            # 적기 폭발
            drawobject(explosion, EnemyX, EnemyY)    # 적기 폭발 그리기
            explosionTime += 10
            destroySound.play()                      # 적기 폭발 사운드 재생

            # 적기 맞추면 속도 증가
            EnemySpeed += 0.05
            if  EnemySpeed >= 1000:
                EnemySpeed = 1000

            if explosionTime > 0.1 :  # 폭발 이펙트 지속 시간 설정 (30 프레임 이후 종료)
                if shotCount >= 0:
                    Enemy = pygame.image.load(random.choice(EnemyImage))
                    Enemy = pygame.transform.scale(Enemy, (75, 75))  # 적기 크기 조정
                    EnemyWidth = Enemy.get_rect().size[0]
                    EnemyHeight = Enemy.get_rect().size[1]
                    EnemyX = random.randrange(0, padwidth - EnemyWidth)
                    EnemyY = 0
                    destroySound = pygame.mixer.Sound(random.choice(explosionSound) )
                    isShot = False

        pygame.display.update()
        clock.tick(60)  # 게임 화면의 초당 프레임 수를 60으로 설정


# 게임 메시지 출력
def writeMessage(message):
    global gamePad, gameOverSound
    font = pygame.font.SysFont("malgungothic", 40)
    lines = message.split('\n')  # 메시지를 줄바꿈 기호("\n")를 기준으로 나눔
    textpos_y = padHeight/2 - (len(lines) * font.get_height())/2  # 메시지의 세로 위치 계산

    for line in lines:
        text = font.render(line, True, (255, 0, 0))
        textpos = text.get_rect(center=(padwidth/2, textpos_y))
        gamePad.blit(text, textpos)
        textpos_y += font.get_height()  # 다음 줄로 이동

    pygame.display.update()

    # 재시도 버튼 그리기
    restartButton = pygame.image.load('Shooting/Image/Retry.png')  # 재시도 버튼 이미지 로드
    restartButton = pygame.transform.scale(restartButton, (150, 50))  # 재시도 버튼 크기 조정
    restartButtonRect = restartButton.get_rect()
    restartButtonRect.center = (padwidth/2, padHeight/2 + 100)
    gamePad.blit(restartButton, restartButtonRect)

    # 종료 버튼 그리기
    exitButton = pygame.image.load('Shooting/Image/Exit.png')  # 종료 버튼 이미지 로드
    exitButton = pygame.transform.scale(exitButton, (150, 50))  # 종료 버튼 크기 조정
    exitButtonRect = exitButton.get_rect()
    exitButtonRect.center = (padwidth/2, padHeight/2 + 200)
    gamePad.blit(exitButton, exitButtonRect)

    pygame.display.update()
    pygame.mixer.music.stop()       # 배경 음악 정지
    gameOverSound.play()            # 게임 오버 사운드 재생
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restartButtonRect.collidepoint(mouse_pos):  # 재시도 버튼 클릭
                    pygame.mixer.music.stop()
                    gameOverSound.stop()
                    runGame()
                elif exitButtonRect.collidepoint(mouse_pos):  # 종료 버튼 클릭
                    pygame.quit()
                    sys.exit()

# 전투기가 적기와 충돌했을 때 메시지 출력
def crash():
    global gamePad, gameOverSound
    pygame.display.update()  # 게임화면을 다시 그림
    pygame.mixer.music.stop()  # 배경 음악 정지
    if highCount == shotCount :
        writeMessage('신기록 달성!!\n\n전투기 파괴!')
    writeMessage('전투기 파괴!')
    gameOverSound.stop()


# 게임 오버 메시지 보이기
def gameOver():
    global gamePad, gameOverSound
    pygame.display.update()  # 게임화면을 다시 그림
    pygame.mixer.music.stop()   # 배경 음악 정지
    writeMessage('게임 오버')
    gameOverSound.stop()

initGame()
runGame()