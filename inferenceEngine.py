import os.path
import os
import collections
import itertools
import copy
import re
from collections import OrderedDict

kb1=[]

# after removing redundant paranthesis
kb2=[]

# after standardising variables
standardisedKb = []
capitalVars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
counter = 0


def add_parenthesis(sentence):
    if '=>' in sentence:
        index = sentence.index('=>')
        antecedent = '(' + sentence[:index].strip() + ')'
        consequent = sentence[index:].strip()
        return antecedent + ' ' + consequent
    else:
        return '(' + sentence.strip() + ')'


def addNegation(sN, fH):
    return fH[:sN] + '(~' + fH[sN:] + ')'

def findUnmatchedOpen(sentence):
    length = len(sentence)
    opens = []
    closes = []
    for i in range(length - 1, -1, -1):
        if sentence[i] == '(':
            opens.append(i)
        if sentence[i] == ')':
            closes.append(i)
        if len(opens) > len(closes):
            return opens[len(opens) - 1]
    return -1



def replaceImpliesWithOr(startOfNegation, firstHalf, secondHalf):
    if firstHalf.startswith('(') and firstHalf.endswith(')'):
        modifiedFH = addNegation(startOfNegation, firstHalf[1:-1])
    else:
        modifiedFH = addNegation(startOfNegation, firstHalf)
    s = modifiedFH + "|" + secondHalf
    return s

def replaceImplies(sentence):
    countOfImplies = sentence.count('=>')
    for i in range(countOfImplies):
        index = sentence.find('=>')
        unmatchedOpenIndex = findUnmatchedOpen(sentence[:index])
        sentence = replaceImpliesWithOr(unmatchedOpenIndex + 1, sentence[:index], sentence[index + 2:])
    return sentence

def pickInnermostPair(pairs, length):
    innermostPairStart = 0
    innerMostPairEnd = length
    for eachKey, eachVal in pairs.items():
        if eachKey > innermostPairStart and eachVal < innerMostPairEnd:
            innermostPairStart = eachKey
            innerMostPairEnd = eachVal
    return [innermostPairStart, innerMostPairEnd]

def findUnmatchedClose(sentence):
    length = len(sentence)
    opens = []
    closes = []
    for i in range(length):
        if sentence[i] == '(':
            opens.append(i)
        if sentence[i] == ')':
            closes.append(i)
        if len(closes) > len(opens):
            return closes[len(closes) - 1]

def findAllPossiblePairsOfNot(sentence, pattern):
    pairs = collections.OrderedDict()
    for i in range(len(sentence)):
        if i + 1 != len(sentence) and sentence[i] + sentence[i + 1] == pattern:
            pairs[i] = i + 2 + findUnmatchedClose(sentence[i + 2:])
    return pairs



#finds the outermost '&' in a sentence
def findOuterMostAnd(sentence):
    list = []
    outermostIndex = -1
    for i in range(len(sentence)):
        if sentence[i] == '&' and len(list) == 1 and list[len(list) - 1] == '(':
            outermostIndex = i
            break
        elif sentence[i] == ')' and len(list) != 0:
            list.pop()
        elif sentence[i] == '(':
            list.append(sentence[i])
    return outermostIndex

#finds the outermost '|' in a sentence
def findOuterMostOr(sentence):
    list = []
    outermostIndex = -1
    for i in range(len(sentence)):
        if sentence[i] == '|' and len(list) == 1 and list[len(list) - 1] == '(':
            outermostIndex = i
            break
        elif sentence[i] == ')' and len(list) != 0:
            list.pop()
        elif sentence[i] == '(':
            list.append(sentence[i])
    return outermostIndex

def negatePredicates(predicate1, operator, predicate2):
    #if predicate already contains negation, then remove negation else add negation
    if predicate1[0] + predicate1[1] == '(~':
        predicate1 = predicate1[2:len(predicate1) - 1]
    else:
        predicate1 = '(~' + predicate1 + ')'
    if predicate2[0] + predicate2[1] == '(~':
        predicate2 = predicate2[2:len(predicate2) - 1]
    else:
        predicate2 = '(~' + predicate2 + ')'
    sentence = predicate1 + operator + predicate2
    return sentence

def moveNot(sentence):
    #if sentence only contains one '(' and ')' and no negation, simply add '~' and return
    if sentence[0] != '~' and sentence.count('(') == 1 and sentence.count(')') == 1 and sentence.count(
            '&') == 0 and sentence.count('|') == 0:
        return '~' + sentence
    #if sentence only contains one '(' and ')' and one negation, simply remove '~' and return
    elif sentence[0] == '~' and sentence.count('(') == 1 and sentence.count(')') == 1 and sentence.count(
            '&') == 0 and sentence.count('|') == 0:
        return sentence[1:]
    # if sentence only contains one '&' or '!' and one negation, find predicates around the oprators and negate them. Also flip '&' to '|' and '|' to '&'
    elif sentence.count('&') > 0 or sentence.count('|') > 0:
        indexOfOperator = -1
        outermostAnd = findOuterMostAnd('(' + sentence + ')')
        outermostOr = findOuterMostOr('(' + sentence + ')')
        listSen = list(sentence)
        if outermostAnd != -1:
            indexOfOperator = outermostAnd - 1
            listSen[outermostAnd - 1] = '|'
        elif outermostOr != -1:
            indexOfOperator = outermostOr - 1
            listSen[outermostOr - 1] = '&'
        sentence = "".join(listSen)
        sentence = negatePredicates(sentence[:indexOfOperator], sentence[indexOfOperator],
                                    sentence[indexOfOperator + 1:])
        return sentence

#This function moves the negation in through the sentence
def moveNegationInside(sentence):
    while sentence.count('~(') != 0:
        pairs = findAllPossiblePairsOfNot(sentence, '~(')
        innermostPair = []
        if len(pairs.keys()) == 1:
            innermostPair = [list(pairs.keys())[0], pairs[list(pairs.keys())[0]]]
        else:
            innermostPair = pickInnermostPair(pairs, len(sentence))
        thirdPart = ""
        if innermostPair[1] + 1 != len(sentence):
            thirdPart = sentence[innermostPair[1] + 1:]
        sentence = sentence[:innermostPair[0]] + moveNot(sentence[innermostPair[0] + 2:innermostPair[1]]) + thirdPart
        moveNegationInside(sentence)
    return sentence

def findAllPossiblePairsOfNot(sentence, pattern):
    pairs = collections.OrderedDict()
    for i in range(len(sentence)):
        if i + 1 != len(sentence) and sentence[i] + sentence[i + 1] == pattern:
            pairs[i] = i + 2 + findUnmatchedClose(sentence[i + 2:])
    return pairs

#This function removes parantheses if the sentence only had one '(', ')' and no '~'
def removeSinglePredicateParantheses(sentence):
    index = -1
    while index < len(sentence):
        indexOfOpen = sentence.find('(', index)
        if indexOfOpen != -1 and capitalVars.find(sentence[indexOfOpen + 1]) != -1:
            indeOfUnmatchedClose = findUnmatchedClose(sentence[indexOfOpen + 1:])
            sentenceAfterOpen = sentence[indexOfOpen + 1:indexOfOpen + indeOfUnmatchedClose + 1]
            if sentenceAfterOpen.count('(') == 1 and sentenceAfterOpen.count(')'):
                listSen = list(sentence)
                newSentence = ""
                for i, val in enumerate(listSen):
                    if i != indexOfOpen and i != indexOfOpen + 1 + indeOfUnmatchedClose:
                        newSentence += val
                sentence = newSentence
                index = 0
            else:
                index += 1
        else:
            index = index + 1
    return sentence

#This function removes parantheses if the sentence only had one '(', ')' and one '~'
def removeSingleNotPredicateParantheses(sentence):
    index = 0
    while index < len(sentence):
        pairs = findAllPossiblePairsOfNot(sentence, '(~')
        if len(pairs) != 0:
            for pair in pairs.items():
                eachKey = pair[0]
                eachVal = pair[1]
                sen = sentence[eachKey + 1:eachVal]
                if sen.count('(') == 1 and sen.count(')') == 1 and sen.count('&') == 0 and sen.count('|') == 0:
                    sentence = sentence[:eachKey] + sen + sentence[eachVal + 1:]
                    break
                else:
                    index += 1
        else:
            break
    return sentence

def findChar(sentence, ch):
    return [i for i, ltr in enumerate(sentence) if ltr == ch]

def findIndexOfAnds(sentence):
    indexOfAnds = findChar(sentence, '&')
    return indexOfAnds

def distributeOrOverAnd(sentence):
    type1 = distributeOrOverAndType1(sentence)
    type2 = distributeOrOverAndType2(type1)
    if type1 == type2:
        final = type1
    else:
        final = distributeOrOverAnd(type2)
    return final

def findPredicatesAroundAndType(sentence, index):
    predicate1 = sentence[:index]
    predicate2 = sentence[index + 1:]
    unmatchedOpen = findUnmatchedOpen(predicate1)
    predicate1 = predicate1[unmatchedOpen + 1:]
    unmatchedClose = findUnmatchedClose(predicate2)
    predicate2 = predicate2[:unmatchedClose]
    return [predicate1, predicate2]

#a | (b & c) = (a | b) & (a | c)
def distributeOrOverAndType1(sentence):
    index = 0
    while index < len(sentence):
        if sentence[index] == '|':
            leftSide = sentence[:index]
            rightSide = sentence[index + 1:]
            unmatchedOpen = findUnmatchedOpen(sentence[:index])
            front = sentence[:unmatchedOpen + 1]
            orPredicate = sentence[unmatchedOpen + 1:index]
            unmatchedClose = findUnmatchedClose(rightSide)
            indexOfAnds = findIndexOfAnds(rightSide[:unmatchedClose])
            rear = rightSide[unmatchedClose:]
            if len(indexOfAnds) != 0:
                rightAndOperands = rightSide[:unmatchedClose]
                indexOfAnd = findOuterMostAnd(rightAndOperands)
                if indexOfAnd != -1:
                    andPredicates = findPredicatesAroundAndType(rightAndOperands, indexOfAnd)
                    distributedPredicates = '(' + orPredicate + '|' + andPredicates[0] + ')&(' + orPredicate + '|' + \
                                            andPredicates[1] + ')'
                    sentence = front + distributedPredicates + rear
                    index = 0
                else:
                    index += 1
            else:
                index += 1
        else:
            index += 1
    return sentence

#(a & b) | c = (a | c) & (b | c)
def distributeOrOverAndType2(sentence):
    index = 0
    while index < len(sentence):
        if sentence[index] == '|':
            leftSide = sentence[:index]
            rightSide = sentence[index + 1:]
            unmatchedClose = findUnmatchedClose(sentence[index + 1:])
            orPredicate = rightSide[:unmatchedClose]
            rear = rightSide[unmatchedClose:]
            unmatchedOpen = findUnmatchedOpen(leftSide)
            front = sentence[:unmatchedOpen + 1]
            indexOfAnds = findIndexOfAnds(leftSide[unmatchedOpen + 1:])
            if len(indexOfAnds) != 0:
                leftAndOperands = leftSide[unmatchedOpen + 1:]
                indexOfAnd = findOuterMostAnd(leftAndOperands)
                if indexOfAnd != -1:
                    andPredicates = findPredicatesAroundAndType(leftAndOperands, indexOfAnd)
                    distributedPredicates = '(' + andPredicates[0] + '|' + orPredicate + ')&(' + andPredicates[
                        1] + '|' + orPredicate + ')'
                    sentence = front + distributedPredicates + rear
                    index = 0
                else:
                    index += 1
            else:
                index += 1
        else:
            index += 1
    return sentence

def findOuterMostAnd2(sentence):
    count = 0
    for i in range(len(sentence)):
        if sentence[i] == '(':
            count += 1
        elif sentence[i] == ')':
            count -= 1
        elif sentence[i] == '&' and count == 0:
            return i
    return -1

def splitSentenceAtAnds(sentence):
    index = findOuterMostAnd2(sentence)
    if index == -1:
        kb1.append(sentence)
    else:
        left = sentence[:index]
        left1 = left[findUnmatchedOpen(left) + 1:]
        right = sentence[index + 1:]
        right1 = right[:findUnmatchedClose(right)]
        splitSentenceAtAnds(left1)
        splitSentenceAtAnds(right1)

def findMatchingClose(start, sentence):
    count = 0
    for i in range(start, len(sentence)):
        if sentence[i] == '(':
            count += 1
        elif sentence[i] == ')':
            count -= 1
            if count == 0:
                return i
    return -1
def check_next_char(s):
    for k in range(len(s)):
        if(s[k]==')'):
            if(k+1<len(s)):
                if(s[k+1]==" "):
                    if((k+2)<len(s)):
                        if(s[k+2] not in ['&', '|', "(", ")"]):
                            #print("error at", k)
                            s=s[:k+1]
                            return s
    return s

#removes parantheses around '|' because of associativity i.e. ((a|b)|c) is just a|b|c
def dropParantheses(sentence):
    i = 0
    value = ""
    while i < len(sentence):
        if sentence[i] == '|':
            left = sentence[:i]
            right = sentence[i:]
            indexOfUnmatchedOpen = findUnmatchedOpen(left)
            indexOfUnmatchedClose = findUnmatchedClose(right)
            if indexOfUnmatchedClose is not None:
                indexOfUnmatchedClose += len(left)
                value = ""
                for j, val in enumerate(sentence):
                    if j != indexOfUnmatchedOpen and j != indexOfUnmatchedClose:
                        value = value + val
                sentence = value
            else:
                # Handle case where no unmatched closing parenthesis was found
                value = sentence
        i += 1
    if value == "":
        kb2.append(sentence)
    else:
        kb2.append(value)
    
def group_expression(expression):
    clauses = expression.split('|')
    sentence = ""
    #print("clauses are", clauses)
    if(len(clauses)>1):
        index=-1
        for i in range(len(clauses)):
            for j, char in enumerate(clauses[i]):
                if char.isalpha():
                    index = j
                    #print("index is", j)
                    break
            if("&" in clauses[i] or "|" in clauses[i]):
                clauses[i] =  clauses[i][:index-1] + '(' + clauses[i][index-1:]
                clauses[i] = clauses[i] + ")"
        
        #print("clauses now", clauses)
    
        for i in range(len(clauses)-1):
            sentence = sentence + clauses[i] + "|"
        sentence = sentence + clauses[len(clauses)-1]
        return sentence
    else:
        return expression
    
    
# (~((Likes(x,y) & Likes(y,x) )|( Meet(x,y,z)) ))|( Hangout(x,y))
# (~((Likes(x,y) & Likes(y,x)) | Meet(x,y,z)) )| Hangout(x,y)
# ((~(Likes(x,y) & Likes(y,x) )|( Meet(x,y,z)) ))|( Hangout(x,y))



#NEW SET OF FUNCTIONS FOR RESOLUTION
#Checks if a value is a constant
def isConstant(str):
    if capitalVars.find(str[0]) != -1:
        return True
    else:
        return False

#finds a replacement for variable with another variable or constant
def replaceParam(paramArray, x, y):
    for index, eachVal in enumerate(paramArray):
        if eachVal == x:
            paramArray[index] = y
    return paramArray

#Unification
def unifyParameters(params1, params2):
    newParams = collections.OrderedDict()
    for i in range(len(params1)):
        if params1[i] != params2[i] and isConstant(params1[i]) and isConstant(params2[i]):
            return []
        elif params1[i] == params2[i] and isConstant(params1[i]) and isConstant(params2[i]):
            if params1[i] not in newParams.keys():
                newParams[params1[i]] = params2[i]
        elif isConstant(params1[i]) and not isConstant(params2[i]):
            if params2[i] not in newParams.keys():
                newParams[params2[i]] = params1[i]
                params2 = replaceParam(params2, params2[i], params1[i])
        elif not isConstant(params1[i]) and isConstant(params2[i]):
            if params1[i] not in newParams.keys():
                newParams[params1[i]] = params2[i]
                params1 = replaceParam(params1, params1[i], params2[i])
        elif not isConstant(params1[i]) and not isConstant(params2[i]):
            if params1[i] not in newParams.keys():
                newParams[params1[i]] = params2[i]
                params1 = replaceParam(params1, params1[i], params2[i])
    return newParams

#Checks if the sentence contradicts with any other sentence in kb
def checkContradiction(newSentence, stdKb):
    if newSentence.count("(") == 1 and newSentence.count(")") == 1:
        negatedSentence = negateQuery(newSentence)
        for sen in stdKb:
            if sen == negatedSentence:
                newSentenceMap = collections.OrderedDict()
                newSentenceMap = findPredicates(newSentence)
                oldSentenceMap = collections.OrderedDict()
                oldSentenceMap = findPredicates(sen)
                answer1 = True
                answer2 = True
                for k, v in newSentenceMap.items():
                    for val in v:
                        for val1 in val:
                            if not isConstant(val1):
                                answer1 = False
                                break
                for k, v in oldSentenceMap.items():
                    for val in v:
                        for val1 in val:
                            if not isConstant(val1):
                                answer2 = False
                                break
                return answer1 | answer2
        return False
    else:
        return False

#negates a query to be added ot the kb and then perform resolution
def negateQuery(query):
    if query[0] == '~':
        query = query[1:]
    else:
        query = '~' + query
    return query

#checks if all params in a predicate are constants
def checkIfAllParamsAreConstants(params):
    areConstants = True
    for k, v in params.items():
        if not isConstant(v):
            areConstants = False
            break
    return areConstants

def replace_variables(value1, sentence):

    
    # sentence = "~Stocked(a) |~Seated(b) | Order(b, a)"

    # find the lowercase string inside the brackets and replace it with value1
    pattern = r'\(([a-z]+)\)(?!.*\([^()]*\))'
    new_sentence = re.sub(pattern, f'({value1})', sentence, count=1)

    # find all other occurrences of the same lowercase string and replace them
    pattern = r'\b(' + re.escape(re.search(r'\(([a-z]+)\)', sentence).group(1)) + r')\b'
    new_sentence = re.sub(pattern, value1, new_sentence)
    return new_sentence





#creates combinations of variables for standardization
varArray = list("abcdefghijklmnopqrstuvwxyz")
varArray2 = []
varArray3 = []
for eachComb in itertools.permutations(varArray, 2):
    varArray2.append(eachComb[0] + eachComb[1])
for eachComb in itertools.permutations(varArray, 3):
    varArray3.append(eachComb[0] + eachComb[1] + eachComb[2])
varArray = varArray + varArray2 + varArray3

#finds all unique variables in a sentence
def findAllVarsInSentence(sentence):
    vars = set()
    varPositions = collections.OrderedDict()
    for i in range(len(sentence)):
        if (sentence[i - 1] == '(' or sentence[i - 1] == ',') and capitalVars.find(sentence[i]) == -1:
            vars.add(sentence[i])
            varPositions[i] = sentence[i]
    return [vars, varPositions]

#Standardize variables in a sentence
def standardiseVars(vars):
    global counter
    correspondingVars = collections.OrderedDict()
    for eachVar in vars:
        correspondingVars[eachVar] = varArray[counter]
        counter = counter + 1
    return correspondingVars

#finds the predicates in a sentence and creates a map of where the predicates occur in the kb according to line numbers
def findPredicates(sentence):
    predicateMap = collections.OrderedDict()
    i = 0
    start = 0
    while i != -1:
        i = sentence.find('(')
        if i != -1:
            predicate = sentence[start:i]
            sentence = sentence[i:]
            closeIndex = sentence.find(')')
            vars = sentence[1:closeIndex].split(",")
            if predicate not in predicateMap.keys():
                predicateMap[predicate] = [vars]
            else:
                v = predicateMap[predicate]
                v.append(vars)
                predicateMap[predicate] = v
            i = sentence.find('|')
            if i != -1:
                i += 1
                sentence = sentence[i:len(sentence)]
    return predicateMap

#finds the predicates in a sentence and creates a map of where the predicates occur in the kb according to line numbers
def findPredicates(sentence):
    predicateMap = collections.OrderedDict()
    i = 0
    start = 0
    while i != -1:
        i = sentence.find('(')
        if i != -1:
            predicate = sentence[start:i]
            sentence = sentence[i:]
            closeIndex = sentence.find(')')
            vars = sentence[1:closeIndex].split(",")
            if predicate not in predicateMap.keys():
                predicateMap[predicate] = [vars]
            else:
                v = predicateMap[predicate]
                v.append(vars)
                predicateMap[predicate] = v
            i = sentence.find('|')
            if i != -1:
                i += 1
                sentence = sentence[i:len(sentence)]
    return predicateMap


def remove_unmatched_parenthesis(s):
    stack = []
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)
        elif c == ')':
            if not stack:
                s = s[:i] + s[i+1:]
            else:
                stack.pop()
    while stack:
        if not stack:
            break
        idx = stack.pop()
        if idx < len(s) - 1:
            s = s[:idx] + s[idx+1:]
        else:
            s = s[:idx]
    if s.endswith(')') and s.count('(') != s.count(')'):
        s = s.rstrip(')')
    return s

#FUNCTION TO CHECK IF SENTENCE HAS ONLY &, and IF SO SEPARATE
def andSeparator(sentence):
    # Split the sentence into substrings at "&"
    substrings = re.split(r'\s*&\s*', sentence)
    # Check that there are at least two substrings and none of them contain "|"
    if len(substrings) >= 2 and not any('|' in s for s in substrings):
        for i in range(len(substrings)):
            substrings[i] = remove_unmatched_parenthesis(substrings[i])        
        return substrings
    else:
        return [sentence]



with open('input.txt', 'r') as file:
    lines = file.readlines()

query = lines[0].strip()
number_of_sentences = int(lines[1])
sentences = [line.strip() for line in lines[2:]]

#print("query is", query)
#print("number of sentences is", number_of_sentences)


for sentence in sentences:
    #print("sentence is", sentence, "\n")
    demo = sentence.split("=>")
    counter =0
    if('&' in demo[0]):
        counter = counter +1
    if('|' in demo[0]):
        counter = counter +1
    sentence=add_parenthesis(sentence)
    sentence=replaceImplies(sentence)
    #print("Sentence after implies is", sentence)
    # sentence = moveNegationInside('(((~(Likes(x,y) & Likes(y,x) ))|((~( Meet(x,y,z)) ))))|((~( Hangout(x,y))))')
    if(counter==2):
        sentence = group_expression(sentence)
        #print("sentence after group expression is", sentence)
    sentence = moveNegationInside(sentence)
    #print("Sentence after move negation is", sentence)
    sentence = removeSingleNotPredicateParantheses(sentence)
    #print("Sentence after para1", sentence)
    sentence = removeSinglePredicateParantheses(sentence)
    #print("Sentence after para2", sentence)
    sentence = distributeOrOverAnd(sentence)
    #print("Sentence after distribute", sentence)
    splitSentenceAtAnds(sentence)


for i in range(len(kb1)):
    sent = kb1[i]
    sent = check_next_char(sent)
    kb1[i]=sent


#print("kb1 is", kb1)

for sentence in kb1:
    # kb2 is created which removes unwanted paranthesis
    dropParantheses(sentence)

#print("kb2 is", kb2)


for sentence in kb2:
    varsInSentence = findAllVarsInSentence(sentence)
    vars = varsInSentence[0]
    correspondingVar = standardiseVars(vars)
    varPositions = varsInSentence[1]
    listSen = list(sentence)
    for eachPosition, eachVar in varPositions.items():
        listSen[eachPosition] = correspondingVar[eachVar]
    sentencedjoined = "".join(listSen)
    print("sentence joined is", sentencedjoined)
    res_list = andSeparator(sentencedjoined)
    print("RESLIST IS", res_list)
    if(len(res_list)==1):
        standardisedKb.append("".join(res_list))
    else:
        for element in res_list:
            standardisedKb.append(element)

print("standarised KB is", standardisedKb)


kbMap = []
allPredicates = collections.defaultdict(list)
for index, eachSentence in enumerate(standardisedKb):
    sentenceMap = collections.OrderedDict()
    sentenceMap = findPredicates(eachSentence)
    for i in sentenceMap.keys():
        allPredicates[i].append(index)
    kbMap.append(sentenceMap)


#CREATED KBMAP AND ALLPREDICATES
#print("kbmap is", kbMap, "\n\n")
#print("all pred is", allPredicates)


#STARTING RESOLUTION

allPredicatescpy = copy.deepcopy(allPredicates)
result = False
flagBreak=0
standardisedKbcpy = copy.deepcopy(standardisedKb)
kbMapcpy = copy.deepcopy(kbMap)

query = query.replace(" ", "")
query1 = negateQuery(query)
#appending the negated query to KB
standardisedKbcpy.append(query1)
standardisedKb.append(query1)

senMap = collections.OrderedDict()
senMap = findPredicates(query1)
#print("senMap updated is", senMap)
kbMapcpy.append(senMap)

#print("KBMAP updated is", kbMapcpy)

for iMap1 in senMap.keys():
    allPredicatescpy[iMap1].append(len(kbMapcpy) - 1)

#print("Allpredicates updated is", allPredicatescpy)


i = 0
iter=-1
print("\n\n\nlength initial  is", len(kbMapcpy))

while i < len(kbMapcpy) and i < 40000:
    iter = iter + 1
    print("allpredicates cpy is", len(allPredicatescpy), "iteration number", iter)
    
    if flagBreak == 1:
        break
    sentenceMap1 = kbMapcpy[i]

    #print("\n\n sentenceMap1 here is", sentenceMap1)
    #print("actual sentence is", standardisedKbcpy[iter])
    for predicate1, parameters1 in sentenceMap1.items():
        #print("pred1 is", predicate1)
        #print("parameters1 is", parameters1)
        if flagBreak == 1:
            break
        for p1Index, p1 in enumerate(parameters1):
            if flagBreak == 1:
                break
            #allPredicates1[negateQuery(predicate1)] - this gives a list with the indexes in kbmap where the negation of the predicate1 can be found 
            # print("parameters1 is", parameters1)
            # print("predicate1 is", predicate1)
            ll = len(allPredicatescpy[negateQuery(predicate1)])
            #print("allpredcpy", allPredicatescpy[negateQuery(predicate1)])
            #print("ll is", ll)
            j=0
            while j < ll and ll < 100:
                if flagBreak == 1:
                    break

                #sentenceMap2 contains the OrderedDict which has predicate as the negateQuery(predicate1)
                sentenceMap2 = kbMapcpy[allPredicatescpy[negateQuery(predicate1)][j]]
                #print("i is", i)
                
                #print("sentencemap2 is", sentenceMap2)

                for predicate2, parameters2 in sentenceMap2.items():

                    # #print("parameters2 is", parameters2) has list of list of parameters in sentenceMap2 eg. [['Restaurant']]
                    if flagBreak == 1:
    
                        break
                    for p2Index, p2 in enumerate(parameters2):
                        if((predicate1 == negateQuery(predicate2))  and sentenceMap!=sentenceMap2 ):
                            #print("Yes")
                            #print("actual sentence is", standardisedKbcpy[iter])
                            newParams = unifyParameters(copy.deepcopy(p1), copy.deepcopy(p2))
                            #print("new params is", newParams)
                            if len(newParams) != 0:
                                newSentence = ""
                                replace_val=""
                                for k, v in sentenceMap1.items():
                                    #print("sentenceMap1 is",sentenceMap1.items() )
                                    #print("\n\n")
                                    for kIndex, value in enumerate(v):
                                        #print("k is", k)
                                        #print("predicate1 is", predicate1)
                                        #print("pindex is", p1Index)
                                        if k == predicate1 and p1Index == kIndex:
                                            continue
                                        else:
                                            #print("value", value)
                                            #print("k is", k)
                                            # value_concat = "".join(value)
                                            # replace_val = replace_variables(value_concat, standardisedKb[i])
                                            # #print("value replaced thro regex", replace_variables(value_concat, standardisedKb[i]))

                                            newSentence += k + ' ( ' + " , ".join(value) + ' ) |'
                                            #print("new sent is", newSentence)
                                for k1, v1 in sentenceMap2.items():
                                    for k1Index, value1 in enumerate(v1):
                                        if k1 == predicate2 and p2Index == k1Index:
                                            continue
                                        else:   
                                            #print("k1 is", k1)
                                            #print("value1 is", value1)
                                            newSentence += k1 + ' ( ' + " , ".join(value1) + ' ) |'
                                            # value1_concat = "".join(value1)
                                            # #print("value1 concat is", value1_concat)
                                            # #print("val replaced thro regex", replace_variables(value1_concat, replace_val))
                                            #print("new sent iss", newSentence)
                                newSentence = newSentence[:len(newSentence) - 1]
                                
                                #print("New sentence here is", newSentence)
                                listSentence = newSentence.split()
                                for k2, v2 in newParams.items():
                                    for indexOfVal, val in enumerate(listSentence):
                                        # #print("val is", val)
                                        # #print("k2 is", k2)
                                        # #print("v2 is", v2)
                                        if val == k2:
                                            listSentence[indexOfVal] = v2
                                newSentence = "".join(listSentence)
                                #print("original sentence is", standardisedKbcpy[iter])
                                #print("NEW SENTENCE FINAL IS", newSentence)
                                if newSentence == "" and checkIfAllParamsAreConstants(newParams):
                                    #print("HELLO")
                                    #print("RESULT IS TRUE")
                                    result= True
                                else:
                                    print("CHECKING FOR CONTRADICTION")
                                    result = checkContradiction(newSentence, standardisedKbcpy)
                                    print("RESULT IS", result)
                                if result:
                                    flagBreak = 1
                                    print("BREAKING SINCE RESULT IS TRUE")
                                else:
                                    if newSentence != "":
                                        noMatch = True
                                        newSentenceMap = collections.OrderedDict()
                                        newSentenceMap = findPredicates(newSentence)
                                        for eachMap in kbMapcpy:
                                            if eachMap == newSentenceMap:
                                                noMatch = False
                                                break
                                        if noMatch:
                                            print("APPENDING TO KB")
                                            if(newSentence not in standardisedKbcpy):
                                                standardisedKbcpy.append(newSentence)
                                                kbMapcpy.append(newSentenceMap)
                                                
                                                for iMap in newSentenceMap.keys():
                                                    allPredicatescpy[iMap].append(len(kbMapcpy) - 1)
                                            else:
                                                print("already present")

                                                                     
                j=j+1
    i=i+1


if result:
    output = "TRUE"
else:
    output = "FALSE"

print("standarisedKB is", standardisedKbcpy)

if os.path.exists("output.txt"):
    with open("output.txt", "w") as f:
        f.truncate(0)  # Erase the contents of the file
        f.write(output)
else:
    with open("output.txt", "w") as f:
        f.write(output)