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

englishHints = {
        'singular':{
            'first-person': 'I',
            'second-person': 'You(sg)',
            'third-person': 'He/She',
            },
        'plural':{
            'first-person': 'We',
            'second-person': 'You(pl)',
            'third-person': 'They',
            }
    }

polishHints = {
        'singular':{
            'first-person': 'Ja',
            'second-person': 'Ty',
            'third-person': 'On / Ona',
            },
        'plural':{
            'first-person': 'My',
            'second-person': 'Wy',
            'third-person': 'Oni / One',
            }
    }

def getListFromDict(dictionary):
    answers = []
    for pluralityKey in dictionary.keys():
        for personKey in dictionary[pluralityKey].keys():
            answers.append(dictionary[pluralityKey][personKey].capitalize())
    return answers




class Quiz():
    def __init__(self, polishWordDict):
        self.wordSource = polishWordDict
        self.engHints = englishHints
        self.polHints = polishHints
        self.__sessionCorrectAnswers = None
        self.correctPolishWord = None
        self.correctPolishLemma = None
        self.correctEnglishPronoun = None
        self.correctPolishPronoun = None

        self.__polishWordLabels = None
        self.__englishPronounLabels = None
        self.__polishPronounLabels = None

    
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
        chosenRightAnswer = self.wordSource[chosenWord][chosenPlurality][chosenPerson].capitalize()
        randomDict = {
            'polishWord': chosenRightAnswer,
            'engPronoun': englishHints[chosenPlurality][chosenPerson],
            'polPronoun': polishHints[chosenPlurality][chosenPerson],
            'polishWordLemmas': chosenWord
        }
        return randomDict

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
    
    

# Random choice of word from source dict. Create QuizQuestion object for it. Run every round.
def getQuizQuestion(polishVerbDict):

    englishHints = {
        'singular':{
            'first-person': 'I',
            'second-person': 'You(sg)',
            'third-person': 'He/She',
            },
        'plural':{
            'first-person': 'We',
            'second-person': 'You(pl)',
            'third-person': 'They',
            }
    }
    polishHints = {
        'singular':{
            'first-person': 'Ja',
            'second-person': 'Ty',
            'third-person': 'On / Ona',
            },
        'plural':{
            'first-person': 'My',
            'second-person': 'Wy',
            'third-person': 'Oni / One',
            }
    }

    chosenWord = random.choice(list(polishVerbDict.keys())) # Chooses which Polish word to use
    chosenPlurality = random.choice(list(polishVerbDict[chosenWord].keys())) #chooses which plurality to use
    chosenPerson = random.choice(list(polishVerbDict[chosenWord][chosenPlurality].keys())) #Chooses which person to use


    chosenRightAnswer = polishVerbDict[chosenWord][chosenPlurality][chosenPerson].capitalize()
    englishHint = englishHints[chosenPlurality][chosenPerson] 
    polishHint = polishHints[chosenPlurality][chosenPerson]
    chosenQuestion = f'{englishHint} - {polishHint}'

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
        
        mouseX, mouseY = pygame.mouse.get_pos()


        mouseClicked = False
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()
            elif event.type == MOUSEBUTTONUP:
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
        newDim = checkForResize()
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
        modes = ['Match the Verb Case - Present', 'Match the Pronoun']
        modeTypes = ['VCasePresent', 'Pronoun']

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


        mouseClicked = False
        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mouseClicked = True
        
        if mouseClicked:
            if gameTypeRect.collidepoint(mouseX, mouseY):
                modeIndex += 1
                if modeIndex >= len(modes):
                    modeIndex = 0
            elif startRect.collidepoint(mouseX, mouseY):
                if durationChoice:
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
        newDim = checkForResize()
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
    print(sessionQuiz.polishWordLabels)
        


if __name__ == "__main__":
    # mainQuiz()
    test()
