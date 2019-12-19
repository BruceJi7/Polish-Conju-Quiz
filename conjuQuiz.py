import os, codecs, webbrowser
import requests as req
import bs4
import pprint

headers = {'User-Agent' : 'Chrome/70.0.3538.77'}
polDictURL = r'https://en.wiktionary.org/wiki/'


#You need to work with the imperative else it may not find the word!
#I could use DIKI to get the imperative... maybe.


quizWords=['pływać', 'leżeć', 'nieść', 'czekać', 'jeść']


def getVerbConjugation(listOfWordsToGet):
    
    wordDeclensions = {}

    
    for word in listOfWordsToGet:

        conjugationTable = {
        'singular':{
            'first-person': None,
            'second-person': None,
            'third-person': None,
            },
        'plural':{
            'first-person': None,
            'second-person': None,
            'third-person': None,
            }
        }
        

        if word in ('', '\n', '\t'):
            continue
        else:
    
            print(f'Searching for conjugations of word: {word}...')
            searchURL = polDictURL + word

            res = req.get(searchURL, headers=headers)
            res.raise_for_status()

            soup = bs4.BeautifulSoup(res.text, features='lxml')

            # First parsing search, for table in page    
            SOUPConjugationTables = soup.findAll('table', class_="wikitable inflection-table")
                    
            ## Print the entire table        
            # print(SOUPConjugationTables)


            for table in SOUPConjugationTables:
                # In case there are multiple tables on the page, this will extract the Polish table                        
                declensionTableIsPolishCandidate = table.find('span', lang='pl')
                if declensionTableIsPolishCandidate:                      
                    SOUPPolishTable = table
                else:
                    continue
            if not SOUPPolishTable:
                print('Failed to find Polish table on this page.')
                continue # Move onto next potential word
            else:
                print('Found Polish Verb Table')


                
            SOUPTableRows = SOUPPolishTable.findAll('tr') # Find all rows - can select useful ones from within here.

            # This selection extracts only the present tense rows.
            # 3 = 1st, 4 = 2nd, 5 = 3rd person conjugations.

            SOUPPresentTenseRows = SOUPTableRows[3:6]
            

            allVerbForms = []
            for number, row in enumerate(SOUPPresentTenseRows):
                #Enumerate to help fill in first dictionary later

                
                SOUPVerbCells = row.findAll('span')
                SOUPWordTypes = [cell.get_text().strip() for cell in SOUPVerbCells]
                allVerbForms.append(SOUPWordTypes)
                
            zippedVerbForms = list(zip(*allVerbForms)) # Arrange verbs into groups based on plurality instead of case
            

            for columnIndex in range(len(zippedVerbForms)): #Working on the two plurality columns
                relatedDictPluralityKey = list(conjugationTable.keys())[columnIndex]
                
                for rowIndex in range(len((zippedVerbForms[columnIndex]))): #Working on the 1/2/3 person rows
                    relatedDictPersonKey = list(conjugationTable[relatedDictPluralityKey].keys())[rowIndex]

                    workingVerbForm = zippedVerbForms[columnIndex][rowIndex]
                    conjugationTable[relatedDictPluralityKey][relatedDictPersonKey] = workingVerbForm

                           
        wordDeclensions[word] = conjugationTable


    return wordDeclensions    



                



         

quizConjugations = getVerbConjugation(quizWords)

pprint.pprint(quizConjugations)

