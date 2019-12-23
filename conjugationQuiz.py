import time, sys, pygame, random, shelve
from pygame.locals import *


FPS = 30
WINDOWWIDTH = 800
WINDOWHEIGHT = 600

BLACK           =(  0,   0,   0)
WHITE           =(255, 255, 255)
LIGHTGREY       =(200, 200, 200)

BKGCOLOR = WHITE
MAINTEXTCOLOR = BLACK



# Fetch words from shelf
def openShelf():
    with shelve.open('polVerbConj') as shelveFile:
        openWhat = shelveFile['verb conjugations']
    return openWhat


# For closing the game
def terminate():
    print('Terminating game...')
    pygame.quit()
    sys.exit()
def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate()
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)


# For getting the new size of a resized window
def checkForResize():
    newScreenWidth = None
    newScreenHeight = None

    for event in pygame.event.get(VIDEORESIZE):
        newSize = event.size
        return newSize


# Random choice of word from source dict. Create QuizQuestion object for it. Run every round.
def getQuizQuestion(polishVerbDict):

    englishHints = {
        'singular':{
            'first-person': 'I - Ja',
            'second-person': 'You - Ty',
            'third-person': 'He/She - On/Ona',
            },
        'plural':{
            'first-person': 'We - My',
            'second-person': 'You - Wy',
            'third-person': 'They - Oni/One',
            }
    }

    chosenWord = random.choice(list(polishVerbDict.keys()))
    chosenPlurality = random.choice(list(polishVerbDict[chosenWord].keys())) #Use this to get english hint 'question'
    chosenPerson = random.choice(list(polishVerbDict[chosenWord][chosenPlurality].keys())) 

    chosenRightAnswer = polishVerbDict[chosenWord][chosenPlurality][chosenPerson].capitalize()
    chosenQuestion = englishHints[chosenPlurality][chosenPerson]

    answers = []
    for pluralityKey in polishVerbDict[chosenWord].keys():
        for personKey in polishVerbDict[chosenWord][pluralityKey].keys():
            answers.append(polishVerbDict[chosenWord][pluralityKey][personKey].capitalize())
    
    return QuizQuestion(chosenQuestion, chosenWord, chosenRightAnswer, answers)


class QuizQuestion():
    def __init__(self, question, hint, rightAnswer, answers):
        self.question = question
        self.hint = hint
        self.rightAnswer = rightAnswer
        self.answers = answers

    def checkCorrect(self, toCheck):
        if toCheck == self.rightAnswer:
            return True
        else:
            return False

def mainFont(size=50):
    return pygame.font.SysFont('calibri', size)

class QuestionDisplay():
    def __init__(self, qqObject):
        self.qq = qqObject
        self.__hintSurface = None
        self.hintRect = self.makeRect(self.hintSurface)
        self.answerButtons = self.makeAnswerButtons()
        self.answerButtonRects = [self.makeRect(ansButton) for ansButton in self.answerButtons]
        self.__questionSurface = None
        self.questionRect = self.makeRect(self.questionSurface)



    @property
    def hintSurface(self):
        surfaceWidth = 200
        surfaceHeight = 50

        self.__hintSurface = pygame.Surface((surfaceWidth, surfaceHeight), pygame.SRCALPHA)
        self.__hintSurface.fill(BKGCOLOR)

        message = self.qq.hint
        messageSurf = mainFont().render(message, 1, MAINTEXTCOLOR)
        messageRect = messageSurf.get_rect()
        messageRect.center = (surfaceWidth/2, surfaceHeight/2)

        self.__hintSurface.blit(messageSurf, messageRect)

        return self.__hintSurface


    def makeRect(self, surface):
        return surface.get_rect()

    @property
    def questionSurface(self):

        surfaceWidth = 300
        surfaceHeight = 50

        self.__questionSurface = pygame.Surface((surfaceWidth, surfaceHeight), pygame.SRCALPHA)
        self.__questionSurface.fill(BKGCOLOR)

        message = self.qq.question
        messageSurf = mainFont(30).render(message, 1, MAINTEXTCOLOR)
        messageRect = messageSurf.get_rect()
        messageRect.center = (surfaceWidth/2, surfaceHeight/2)

        self.__questionSurface.blit(messageSurf, messageRect)

        return self.__questionSurface

    
    def makeAnswerButtons(self):
        answerBoxWidth = 100
        answerBoxHeight = 40
        answerButtons = []
        random.shuffle(self.qq.answers)
        for answer in self.qq.answers:
            answerButtonSurf = pygame.Surface((answerBoxWidth, answerBoxHeight))
            answerButtonSurf.fill(LIGHTGREY)
            answerTextSurf = mainFont(20).render(answer, 1, MAINTEXTCOLOR)
            answerTextRect = answerTextSurf.get_rect()
            answerTextRect.center = (answerBoxWidth/2, answerBoxHeight/2)
            answerButtonSurf.blit(answerTextSurf, answerTextRect)
            answerButtons.append(answerButtonSurf)
        return answerButtons



def quizRound(initObjects, gameObjects, score):


    screen = initObjects[0]
    FPSCLOCK = initObjects[1]
    DISPLAYSURF = initObjects[2]
    DISPLAYRECT = initObjects[3]
    wordDictionary = initObjects[4]

    gameLength = gameObjects[0]
    startTime = gameObjects[1]

    roundQuestion = getQuizQuestion(wordDictionary)
    displayQuestion = QuestionDisplay(roundQuestion)

    while True:
        checkForQuit()
        
        #Center the screen on resizing
        newDim = checkForResize()
        if newDim:
            bgWIDTH, bgHEIGHT = newDim[0], newDim[1]
            screen = pygame.display.set_mode((bgWIDTH, bgHEIGHT), pygame.RESIZABLE, display=0)
            DISPLAYRECT.center = (bgWIDTH/2, bgHEIGHT/2)

        # Clear the screen before blitting images onto it
        screen.fill(BLACK)
        DISPLAYSURF.fill(BKGCOLOR)

        
        displayQuestion.hintRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/3)
        DISPLAYSURF.blit(displayQuestion.hintSurface, displayQuestion.hintRect)

        displayQuestion.questionRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
        DISPLAYSURF.blit(displayQuestion.questionSurface, displayQuestion.questionRect)

        buttonsY = (WINDOWHEIGHT/3)*2
        buttonSpacing = WINDOWWIDTH/7
        buttonXMargin = WINDOWWIDTH/7

        for number, button in enumerate(displayQuestion.answerButtons):
            
            buttonRect = displayQuestion.answerButtonRects[number]
            buttonRect.centery = buttonsY
            buttonRect.centerx = (buttonXMargin + buttonSpacing * number)
            DISPLAYSURF.blit(button, buttonRect)

        # Is the timer up?
        currentTime = time.time()
        timeElapsed = round(currentTime - startTime)

        if timeElapsed > gameLength:
            return False, score

        timerSurf = mainFont(25).render(str(timeElapsed), 1, MAINTEXTCOLOR)
        timerRect = timerSurf.get_rect()
        timerRect.topright = (WINDOWWIDTH-20, 20)
        DISPLAYSURF.blit(timerSurf, timerRect)

        scoreSurf = mainFont(25).render(str(score), 1, MAINTEXTCOLOR)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (20, 20)
        DISPLAYSURF.blit(scoreSurf, scoreRect)
        
        mouseX, mouseY = pygame.mouse.get_pos()


        mouseClicked = False
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mouseClicked = True
        


        selectedAnswer = None
        if mouseClicked:
            for index, button in enumerate(displayQuestion.answerButtonRects):

                if button.collidepoint(mouseX, mouseY):
                    selectedAnswer = displayQuestion.qq.answers[index]
                    if displayQuestion.qq.checkCorrect(selectedAnswer):
                        score += 1
                        return True, score
                    else:
                        score -= 1
        



        # Draw the main surface on the background surface
        screen.blit(DISPLAYSURF, DISPLAYRECT)


        pygame.display.update()
        FPSCLOCK.tick(FPS)



def mainQuiz():
    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    # Set variables and surfaces to allow a resizable bkg and centred screen
    bgWIDTH = WINDOWWIDTH
    bgHEIGHT = WINDOWHEIGHT
    screen = pygame.display.set_mode((bgWIDTH, bgHEIGHT), pygame.RESIZABLE, display=0)
    screen.fill(BLACK)
    DISPLAYSURF = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
    DISPLAYRECT = DISPLAYSURF.get_rect()
    DISPLAYRECT.center = (bgWIDTH/2, bgHEIGHT/2)
    DISPLAYSURF.fill(BKGCOLOR)
    pygame.display.set_caption('Polish Conjugation Quiz')

    

    wordDictionary = openShelf() # Only needs to be done once.

    
    initObjects = [screen, FPSCLOCK, DISPLAYSURF, DISPLAYRECT, wordDictionary]
    startTime = time.time()
    gameLength = 60 # In seconds
    score = 0

    gameObjects = [gameLength, startTime]

    running = True
    while running:
        checkForQuit()
        running, score = quizRound(initObjects, gameObjects, score)

        

        

        


if __name__ == "__main__":
    mainQuiz()