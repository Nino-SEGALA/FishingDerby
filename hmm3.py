#File containing everything needed to work on matrix
import sys
import math
import copy
import matrixOperations as matOp
#import inputs
import time
import cProfile
from constants import *


def input_hmm3():
    #return A, B, q and O
    res = [] #[A, B, q, O]
    i = 0
    for line in sys.stdin:
        lst = line.split()
        if i < 3:
            res.append(matOp.make_matrix(lst))
        else: #the last line in the sequence of emissions vector
            res.append(matOp.make_vector(lst))
        i += 1
    return res

def print_matrix(mat):
    #for ele in mat:
    #    print(ele)
    precision = 10**6
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            print(int(precision*mat[i][j])/precision, end=' ')
    print()

#what exactley do they mean by intializing?
def initialize():
    res = input_hmm3()
    A = res[0] #Transition matrix
    B = res[1] #Emission matrix
    pi = res[2] #initial state probability
    E = res[3] #emission itself
    return A,B,pi,E

def calc(A,B,pi,E): #let us start here
##    print("--------------------------------------------------------")
##    print("ALPHA")
    
    cTs = []
    alpha_Ts = []
    #Compute a0(i) alpha ist immer ein vektor der länge N 
    c0 = 0
    #bi0zero = matOp.column(B, E[0])
    
    #compute alpha0
    alpha0 = [matOp.transpose(pi)[i][0] * B[i][E[0]] for i in range(len(A))] #bi0zero[i][0]
    c0 = sum(alpha0)
    
    #scale alpha0
    c0 = 1/(c0+1e-3)
    for i in range(len(A)):#<---- len(A) == N
        alpha0[i] = alpha0[i]*c0
    cTs.append(c0)

    #compute alphaT(i)
    alphaTminusOne = alpha0
    alpha_Ts.append(alphaTminusOne)
    for t in range(1,len(E)):
        alphaT = []
        c0 = 0
        for i in range(len(A)):
            alphaI = 0
            for j in range(len(A)):
                alphaI = alphaI + alphaTminusOne[j]*A[j][i]

            alphaT.append(alphaI)
            alphaT[i] = alphaT[i] * B[i][E[t]] #matOp.column(B, E[t])[i][0]
        ##scale alpha t
        '''if sum(alphaT) != 0: #if division zero.. make sure you don't divide with zero
            c0  = 1/(sum(alphaT)+1e-3)
        else:
            c0 = 0'''
        c0 = 1 / (sum(alphaT) + 1e-3)

        cTs.append(c0) #<--
        for i in range(len(A)):
            alphaT[i] = c0*alphaT[i]
        alphaTminusOne = alphaT
        alpha_Ts.append(alphaTminusOne)

##    print("ALPHA RESULTS")
##    for line in alpha_Ts:
##        print(line)
##        print(sum(line))
##
##
##    print("--------------------------------------------------------\nBETA")

    #Scale and Initialize
    betaTminus1 = []
    betaTs = [-100 for j in range(len(E))]
    cTminus1 = cTs[-1]
    for i in range(len(E)):
        betaTminus1.append(cTminus1)
    betaTs[-1] = betaTminus1

    #Beta pass
    for t in reversed(range(len(E)-1)):
        betaT = []
        for i in range(len(A)):
            betaTi = 0
            for j in range(len(A)):
                betaTi = betaTi + A[i][j] * B[j][E[t+1]] * betaTs[t+1][j]#betaTminus1 stimmt nicht #matOp.column(B, E[t+1])[j][0]
            betaTi = betaTi * cTs[t]
            betaT.append(betaTi)
        betaTs[t] = betaT

##    print("BETA RESULTS")
##    for line in betaTs:
##        print(line)

##    print("--------------------------------------------------------\nGAMMA")
    gammaTIJ_list = [[[-100 for j in range(len(A))] for i in range(len(A))] for t in range(len(E)-1)] #T Matrix auch noch!
    gammaTI_list = []
    for t in range(len(E)-1):
        gammaI = []
        for i in range(len(A)):
            gammaTI = 0
            for j in range(len(A)):
                gammaTIJ = alpha_Ts[t][i] * A[i][j] * B[j][E[t+1]] * betaTs[t+1][j] #Unclear issue #matOp.column(B, E[t+1])[j][0]
                gammaTI = gammaTI + gammaTIJ
                gammaTIJ_list[t][i][j] = gammaTIJ
            gammaI.append(gammaTI)
        gammaTI_list.append(gammaI)

    gammaI = []    
    for i in range(len(A)):
        gammaI.append(alpha_Ts[len(E)-1][i])
    gammaTI_list.append(gammaI)

##    print("GAMMA RESULTS\nGAMMA TI")
##    for line in gammaTI_list:
##        print(line)
##    print("GAMMA TIJ")
##    for line in gammaTIJ_list:
##        print(line)

##    print("--------------------------------------------------------\nRE-ESTIMATION")

    #re-estimate pi
    for i in range(len(A)):
        pi[0][i] = gammaTI_list[0][i]
        
    #re-estimate A
    for i in range(len(A)):
        denom = 0
        for t in range(len(E)-1):
            denom = denom + gammaTI_list[t][i]
        for j in range(len(A)):
            numer = 0
            for t in range(len(E)-1):
                numer = numer + gammaTIJ_list[t][i][j]
            if denom != 0:
                A[i][j] = numer/(denom+1e-3)
            else:
                A[i][j] = 0

    #re-estimate B
    for i in range(len(A)):
        denom = 0
        for t in range(len(E)):
            denom = denom + gammaTI_list[t][i]
        for j in range(len(B[0])):
            numer = 0
            for t in range(len(E)):
                if E[t] == j:
                    numer = numer + gammaTI_list[t][i]
            if denom != 0:
                B[i][j] = numer/(denom+1e-3)
            else:
                B[i][j] = 0

##    print("GAMMA I RESULTS")
##    for line in gammaTI_list:
##        print(line)
##    print("GAMMA IJ RESULTS")
##    for line in gammaTIJ_list:
##        print(line)

    logProb = 0
    #print("cTs : ", cTs)
    for i in range(len(E)):
        logProb = logProb + math.log(cTs[i])
    logProb = -logProb

    return A,B,pi,E,logProb

def return_format(mat):
    res = str(len(mat)) + " " +str(len(mat[0]))
    for i in range(len(mat)):
        for j in range(len(mat[i])):
            res = res +" " + str(mat[i][j])
    return res

#compare our results with the given results in kattis (with a precision of 10e-5)
def compare_results(A1, B1, A2, B2):
    PRECISION = 0.000001
    condA = True
    condB = True
    if (len(A1) != len(A2)) or (len(A1[0]) != len(A2[0])):
        condA = False
        print("dim A")
    else:
        for i in range(len(A1)):
            for j in range(len(A1[0])):
                if abs(A1[i][j]-A2[i][j]) > PRECISION:
                    condA = False
                    print("A[i][j] ", A1[i][j], A2[i][j])
    if (len(B1) != len(B2)) or (len(B1[0]) != len(B2[0])):
        condB = False
        print("dim B")
    else:
        for i in range(len(B1)):
            for j in range(len(B1[0])):
                if abs(B1[i][j]-B2[i][j]) > PRECISION:
                    condB = False
                    print("B[i][j] ", B1[i][j], B2[i][j])
    return condA, condB

def hmm3(maxIters):
    begin = time.time()
    iters = 0#max Iters already defined
    oldLogProb = float('-inf')

    A,B,pi,E = initialize()
    A1 = copy.deepcopy(A)
    B1 = copy.deepcopy(B)
    A,B,pi,E,logProb = calc(A,B,pi,E)

    while(iters < maxIters and logProb > oldLogProb):
        iters = iters +1
        oldLogProb = logProb
        A,B,pi,E,logProb = calc(A,B,pi,E)
##        print("\n\n\n\n\n\n\n\n\n\n\n")
    res = return_format(A)+"\n"
    res = res + return_format(B)
##        print("RESULTS:\n")
##        print(iters,"\n\n")
##        print_matrix(A)
##        print_matrix(B)
##        print_matrix(pi)
##        print("Log Probability: ",logProb)
##        print("\n"+res)

    """Aresult = inputs.Aresult1
    Bresult = inputs.Bresult1
    print(compare_results(Aresult, Bresult, A, B))
    print("A init : ", end='')
    print_matrix(A1)
    print("A hmm3 : ", end='')
    print_matrix(A)
    print("A resu : ", end='')
    print_matrix(Aresult)
    print("B init : ", end='')
    print_matrix(B1)
    print("B hmm3 : ", end='')
    print_matrix(B)
    print("B resu : ", end='')
    print_matrix(Bresult)

    '''print("A hmm3 : ", end='')
    print_matrix(A)
    print("B hmm3 : ", end='')
    print_matrix(B)'''
    print("HI")"""
    print("iters : ", iters)
    end = time.time()
    #print("time : ", end-begin)
    return res

#cProfile.run('hmm3(1000)')
#print(hmm3(10000))

def hmm3(player, maxIters):
    for fish in range(N_FISH):
        iters = 0#max Iters already defined
        oldLogProb = float('-inf')
        E = []
        e = 0
        #create vector of emission E
        while (e < len(player.Ok[fish])) and (player.Ok[fish][e] != -1):
            E.append(player.Ok[fish][e])
            e += 1
        player.Ak[fish], player.Bk[fish], player.qk[fish], E, logProb = calc(player.Ak[fish], player.Bk[fish], player.qk[fish], E)
        while (iters < maxIters and logProb >= oldLogProb):
            iters = iters + 1
            oldLogProb = logProb
            player.Ak[fish], player.Bk[fish], player.qk[fish], E, logProb = calc(player.Ak[fish], player.Bk[fish], player.qk[fish], E)
        #print("hmm3 : ", iters, logProb, oldLogProb)