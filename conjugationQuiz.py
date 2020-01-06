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

englishHints = {
        'singular':{
            'first-person': 'I',
            'second-person': 'you(sg)',
            'third-person': 'he/she',
            },
        'plural':{
            'first-person': 'we',
            'second-person': 'you(pl)',
            'third-person': 'they',
            }
    }

polishHints = {
        'singular':{
            'first-person': 'ja',
            'second-person': 'ty',
            'third-person': 'on / ona',
            },
        'plural':{
            'first-person': 'my',
            'second-person': 'wy',
            'third-person': 'oni / one',
            }
    }

def getListFromDict(dictionary):
    answers = []
    for pluralityKey in dictionary.keys():
        for personKey in dictionary[pluralityKey].keys():
            answers.append(dictionary[pluralityKey][personKey])
    return answers

def mainFont(size=50):
    return pygame.font.SysFont('calibri', size)


class Quiz():
    def __init__(self, polishWordDict):
        self.wordSource = polishWordDict
        self.engHints = englishHints
        self.polHints = polishHints
        self.__sessionCorrectAnswers = None
        self.__quizType = None
        self.correctPolishWord = None
        self.correctPolishLemma = None
        self.correctEnglishPronoun = None
        self.correctPolishPronoun = None

        self.__polishWordLabels = None
        self.__englishPronounLabels = None
        self.__polishPronounLabels = None

        self.labels = None
        self.labelRects = None

    
    def setSessionCorrectAnswers(self): # Sets all correct words
        answers = self.getSessionCorrectAnswers()
        self.correctPolishWord = answers['polishWord']
        self.correctPolishLemma = answers['polishWordLemmas']
        self.correctEnglishPronoun = answers['engPronoun']
        self.correctPolishPronoun = answers['polPronoun']
    
    def getSessionCorrectAnswers(self): # Use this to cycle the correct answers.
        '''
        Chooses a random word, the matching pronoun in English and in Polish
        '''
        chosenWord = random.choice(list(self.wordSource.keys())) # Chooses which Polish word form to use
        chosenPlurality = random.choice(list(self.wordSource[chosenWord].keys())) #chooses which plurality to use
        chosenPerson = random.choice(list(self.wordSource[chosenWord][chosenPlurality].keys())) #Chooses which person to use
        chosenRightAnswer = self.wordSource[chosenWord][chosenPlurality][chosenPerson]
        randomDict = {
            'polishWord': chosenRightAnswer,
            'engPronoun': englishHints[chosenPlurality][chosenPerson],
            'polPronoun': polishHints[chosenPlurality][chosenPerson],
            'polishWordLemmas': chosenWord
        }
        return randomDict

    @property
    def quizType(self):
        return self.__quizType
    
    @quizType.setter
    def quizType(self, setType):
        self.__quizType = setType

    @property
    def polishWordLabels(self):
        chosenWordDict = self.wordSource[self.correctPolishLemma]
        return getListFromDict(chosenWordDict)

    @property
    def englishPronounLabels(self):
        return getListFromDict(englishHints)
    
    @property
    def polishPronounLabels(self):
        return getListFromDict(polishHints)
    
    def drawQuestionBox(self, x, y, inSurface):
        quizType = self.quizType
        if quizType == 'VCasePresent':
            questionText = self.correctPolishLemma
            # hintText = f'{self.correctEnglishPronoun} - {self.correctPolishPronoun}'
        elif quizType in  ('Pronoun', 'EngPro'): 
            questionText = self.correctPolishWord
        
        surfaceWidth = 300
        surfaceHeight = 50

        questionSurface = pygame.Surface((surfaceWidth, surfaceHeight), pygame.SRCALPHA)
        questionSurface.fill(BKGCOLOR)

        messageSurf = mainFont(30).render(questionText, 1, MAINTEXTCOLOR)
        messageRect = messageSurf.get_rect()
        messageRect.center = (surfaceWidth/2, surfaceHeight/2)

        questionSurface.blit(messageSurf, messageRect)
        questionRect = questionSurface.get_rect()
        questionRect.center = (x, y)
        inSurface.blit(questionSurface, questionRect)

    def drawHintBox(self, x, y, inSurface):
        if self.quizType == 'VCasePresent':
            hintText = f'{self.correctEnglishPronoun} - {self.correctPolishPronoun}'
        elif self.quizType in ('Pronoun', 'EngPro'):
            hintText = f'{self.correctPolishLemma}'

        surfaceWidth = 300
        surfaceHeight = 50

        hintSurface = pygame.Surface((surfaceWidth, surfaceHeight), pygame.SRCALPHA)
        hintSurface.fill(BKGCOLOR)

        messageSurf = mainFont(20).render(hintText, 1, MAINTEXTCOLOR)
        messageRect = messageSurf.get_rect()
        messageRect.center = (surfaceWidth/2, surfaceHeight/2)

        hintSurface.blit(messageSurf, messageRect)
        hintRect = hintSurface.get_rect()
        hintRect.center = (x, y)
        inSurface.blit(hintSurface, hintRect)            

    def shuffleAnswerLabels(self):
        if self.quizType == 'VCasePresent':
            labelSet = self.polishWordLabels
        elif self.quizType == 'Pronoun':
            labelSet = self.polishPronounLabels
        elif self.quizType == 'EngPro':
            labelSet = self.englishPronounLabels
        random.shuffle(labelSet)
        self.labels = labelSet



    def drawAnswerLabels(self, x, y, inSurface):
        answerBoxWidth = 100
        answerBoxHeight = 40
        answerButtonRects = []

        buttonsY = (WINDOWHEIGHT/3)*2
        buttonSpacing = WINDOWWIDTH/7
        buttonXMargin = WINDOWWIDTH/7

        for number, answer in enumerate(self.labels):
            answerButtonSurf = pygame.Surface((answerBoxWidth, answerBoxHeight))
            answerButtonSurf.fill(LIGHTGREY)
            answerTextSurf = mainFont(20).render(answer, 1, MAINTEXTCOLOR)
            answerTextRect = answerTextSurf.get_rect()
            answerTextRect.center = (answerBoxWidth/2, answerBoxHeight/2)
            answerButtonSurf.blit(answerTextSurf, answerTextRect)
            answerButtonRect = answerButtonSurf.get_rect()
            answerButtonRect.centery = y
            answerButtonRect.centerx = (x + (buttonSpacing*number+1))
            answerButtonRects.append(answerButtonRect)
            inSurface.blit(answerButtonSurf, answerButtonRect)

        self.labelRects = answerButtonRects
        

    def checkCorrect(self, candidate):
        if self.quizType == 'VCasePresent':
            correct = self.correctPolishWord
        elif self.quizType == 'Pronoun':
            correct = self.correctPolishPronoun
        elif self.quizType == 'EngPro':
            correct = self.correctEnglishPronoun
        # print(f'test: {correct}, you chose {candidate}')

        if correct == candidate:
            return True
        else:
            return False    

    

def quizRound(initObjects, gameObjects, score):


    screen = initObjects[0]
    FPSCLOCK = initObjects[1]
    DISPLAYSURF = initObjects[2]
    DISPLAYRECT = initObjects[3]
    wordDictionary = initObjects[4]

    gameLength = gameObjects[0]
    startTime = gameObjects[1]
    typeOfGame = gameObjects[2]

    sessionQuestion = Quiz(wordDictionary)
    sessionQuestion.quizType = typeOfGame
    sessionQuestion.setSessionCorrectAnswers()
    sessionQuestion.shuffleAnswerLabels()

    while True:
        checkForQuit()
        
        #Center the screen on resizing
        mouseX, mouseY = pygame.mouse.get_pos()


        mouseClicked = False
        newDim = None
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == VIDEORESIZE:
                newDim = event.size
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:
                mouseClicked = True
        
        if newDim:
            bgWIDTH, bgHEIGHT = newDim[0], newDim[1]
            screen = pygame.display.set_mode((bgWIDTH, bgHEIGHT), pygame.RESIZABLE, display=0)
            DISPLAYRECT.center = (bgWIDTH/2, bgHEIGHT/2)


        # Clear the screen before blitting images onto it
        screen.fill(BLACK)
        DISPLAYSURF.fill(BKGCOLOR)

        
        sessionQuestion.drawQuestionBox(WINDOWWIDTH/2, WINDOWHEIGHT/3, DISPLAYSURF)

        sessionQuestion.drawHintBox(WINDOWWIDTH/2, WINDOWHEIGHT/2, DISPLAYSURF)


        sessionQuestion.drawAnswerLabels(WINDOWWIDTH/7, (WINDOWHEIGHT/3*2), DISPLAYSURF)


        # Is the timer up?
        currentTime = time.time()
        timeElapsed = gameLength - round(currentTime - startTime)

        if timeElapsed <= 0:
            return False, score

        timerSurf = mainFont(25).render(str(timeElapsed), 1, MAINTEXTCOLOR)
        timerRect = timerSurf.get_rect()
        timerRect.topright = (WINDOWWIDTH-20, 20)
        DISPLAYSURF.blit(timerSurf, timerRect)

        scoreSurf = mainFont(25).render(str(score), 1, MAINTEXTCOLOR)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (20, 20)
        DISPLAYSURF.blit(scoreSurf, scoreRect)
        



        selectedAnswer = None
        if mouseClicked:
            for index, button in enumerate(sessionQuestion.labelRects):

                if button.collidepoint(mouseX, mouseY):
                    selectedAnswer = sessionQuestion.labels[index]
                    if sessionQuestion.checkCorrect(selectedAnswer):
                        score += 1
                        return True, score
                    else:
                        score -= 1
        



        # Draw the main surface on the background surface
        screen.blit(DISPLAYSURF, DISPLAYRECT)


        pygame.display.update()
        FPSCLOCK.tick(FPS)

def initMenu(initObjects):
    screen = initObjects[0]
    FPSCLOCK = initObjects[1]
    DISPLAYSURF = initObjects[2]
    DISPLAYRECT = initObjects[3]


    durationChoice, durationHighlight = None, None
    modeChoice, modeIndex = None, 0


    gameTypeChoice = None
    while True:
        checkForQuit()
        
        #Center the screen on resizing
        mouseClicked = False
        newDim = None
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == VIDEORESIZE:
                newDim = event.size
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:
                mouseClicked = True
        
        if newDim:
            bgWIDTH, bgHEIGHT = newDim[0], newDim[1]
            screen = pygame.display.set_mode((bgWIDTH, bgHEIGHT), pygame.RESIZABLE, display=0)
            DISPLAYRECT.center = (bgWIDTH/2, bgHEIGHT/2)

        # Clear the screen before blitting images onto it
        screen.fill(BLACK)
        DISPLAYSURF.fill(BKGCOLOR)

        # Drawing the introduction message
        introMessage = 'Polish Conjugation Quiz'
        introMessageSurf = mainFont().render(introMessage, 1, MAINTEXTCOLOR)
        introMessageRect = introMessageSurf.get_rect()
        introMessageRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/4)

        DISPLAYSURF.blit(introMessageSurf, introMessageRect)

        #Drawing the menu buttons
        durationOptions = [30, 60, 90, 120, 300, 'seconds']
        modes = ['Match the Verb Case - Present', 'Match the Polish Pronoun', 'Match the English Pronoun']
        modeTypes = ['VCasePresent', 'Pronoun', 'EngPro']

        buttonsY = (WINDOWHEIGHT/3)*2
        buttonSpacing = WINDOWWIDTH/7
        buttonXMargin = WINDOWWIDTH/7

        #Drawing duration options
        durationButtons = []
        for number, button in enumerate(durationOptions):
            if durationChoice and highlightBox == number:
                highlight = LIGHTGREY
            else:
                highlight = None
            buttonSurf = mainFont(30).render(str(button), 1, MAINTEXTCOLOR, highlight)
            buttonRect = buttonSurf.get_rect()
            buttonRect.centery = buttonsY
            buttonRect.centerx = (buttonXMargin + buttonSpacing * number)
            DISPLAYSURF.blit(buttonSurf, buttonRect)
            durationButtons.append(buttonRect)
        
        #Drawing game type options
        gameTypeSurf = mainFont(30).render(modes[modeIndex], 1, MAINTEXTCOLOR)
        gameTypeRect = gameTypeSurf.get_rect()
        gameTypeRect.center = (WINDOWWIDTH/2 ,(WINDOWHEIGHT/3*2 - 100))
        DISPLAYSURF.blit(gameTypeSurf, gameTypeRect)

        #Drawing start button
        startSurf = mainFont(35).render('Start!', 1, MAINTEXTCOLOR, LIGHTGREY)
        startRect = startSurf.get_rect()
        startRect.center = (WINDOWWIDTH/2, (WINDOWHEIGHT/3*2 + 100))
        DISPLAYSURF.blit(startSurf, startRect)

        mouseX, mouseY = pygame.mouse.get_pos()

        if mouseClicked:
            if gameTypeRect.collidepoint(mouseX, mouseY):
                modeIndex += 1
                if modeIndex >= len(modes):
                    modeIndex = 0
            elif startRect.collidepoint(mouseX, mouseY):
                if durationChoice:
                    print(durationChoice, modeTypes[modeIndex])
                    return durationChoice, modeTypes[modeIndex]
            else:

                for index, button in enumerate(durationButtons[:5]):
                    if button.collidepoint(mouseX, mouseY):
                        highlightBox = index
                        durationChoice = durationOptions[index]
                        # return durationOptions[index]
            

        


        


        # Draw the main surface on the background surface
        screen.blit(DISPLAYSURF, DISPLAYRECT)


        pygame.display.update()
        FPSCLOCK.tick(FPS)

def gameOver(initObjects, gameObjects, score):
    screen = initObjects[0]
    FPSCLOCK = initObjects[1]
    DISPLAYSURF = initObjects[2]
    DISPLAYRECT = initObjects[3]

    gameLength = gameObjects[0]


    while True:
        checkForQuit()
        
        #Center the screen on resizing
        newDim = None
        for event in pygame.event.get(VIDEORESIZE):
            newDim = event.size
        if newDim:
            bgWIDTH, bgHEIGHT = newDim[0], newDim[1]
            screen = pygame.display.set_mode((bgWIDTH, bgHEIGHT), pygame.RESIZABLE, display=0)
            DISPLAYRECT.center = (bgWIDTH/2, bgHEIGHT/2)

        # Clear the screen before blitting images onto it
        screen.fill(BLACK)
        DISPLAYSURF.fill(BKGCOLOR)

        # Drawing the Game Over message
        gameOverMessage = 'Time Up'
        gameOverMessageSurf = mainFont().render(gameOverMessage, 1, MAINTEXTCOLOR)
        gameOverMessageRect = gameOverMessageSurf.get_rect()
        gameOverMessageRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/4)

        correctRate = round(gameLength / score, 2)
        resultMessages = [
            f'You played for {gameLength} seconds,',
            f'and made {score} correct answers.',
            f"That's a rate of {correctRate} seconds per answer."
        ]
        
        
        for line, rMessage in enumerate(resultMessages):
            messageY = WINDOWHEIGHT / 2 + (50 * line+1) # To get the lines to show up on different... lines
            resultMessageSurf = mainFont(30).render(rMessage, 1, MAINTEXTCOLOR)
            resultMessageRect = resultMessageSurf.get_rect()
            resultMessageRect.center = (WINDOWWIDTH/2, messageY)
            DISPLAYSURF.blit(resultMessageSurf, resultMessageRect)


        DISPLAYSURF.blit(gameOverMessageSurf, gameOverMessageRect)
        






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
    
    gameLength = 60 # In seconds
    score = 0
    gameLength, gameType = initMenu(initObjects)
    startTime = time.time()
    gameObjects = [gameLength, startTime, gameType]

    running = True #Is the game session running?
    while running:
        checkForQuit()
        running, score = quizRound(initObjects, gameObjects, score)
    gameOver(initObjects, gameObjects, score)
    

        

        
def test():
    wordDictionary = openShelf()
    sessionQuiz = Quiz(wordDictionary)
    sessionQuiz.setSessionCorrectAnswers()


    print(sessionQuiz.correctPolishWord)
    print(sessionQuiz.correctPolishPronoun)
    print(sessionQuiz.correctEnglishPronoun)

    print(sessionQuiz.polishPronounLabels)
    print(sessionQuiz.englishPronounLabels)
    print(sessionQuiz.polishWordLabels)
        


if __name__ == "__main__":
    mainQuiz()
    # test()
