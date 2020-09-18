import sys
import math
import matrixOperations as matOp
import time
from constants import *

def calc(A,B,pi,E):
    smallNumber = 1e-10
    cTs = []
    alpha_Ts = []

    # alpha0(i)
    c0 = 0
    alpha0 = []
    for i in range(len(A)):
        alpha0.append(pi[0][i]*B[i][E[0]])
        c0 += alpha0[i]

    # scale alpha0(i)
    c0 = 1/(c0+smallNumber)
    for i in range(len(A)):
        alpha0[i] = c0*alpha0[i]
    cTs.append(c0)  # utility?

    # compute alphat(i)
    alphaTminusOne = alpha0
    alpha_Ts.append(alphaTminusOne)
    for t in range(1, len(E)):
        ct = 0
        alphat = []
        for i in range(len(A)):
            alphat.append(0)
            for j in range(len(A)):
                alphat[i] += alphaTminusOne[j]*A[j][i]
            alphat[i] = alphat[i]*B[i][E[t]]
            ct += alphat[i]
        # scale alphat(i)
        ct = 1/(ct+smallNumber)
        cTs.append(ct)
        for i in range(len(A)):
            alphat[i] = ct*alphat[i]
        alphaTminusOne = alphat
        alpha_Ts.append(alphaTminusOne)

    #print("cTs : ", cTs)

    # beta-pass
    betaTminus1 = []
    betaTs = [-100 for j in range(len(E))]
    cTminus1 = cTs[-1]
    #for i in range(len(E)):
    for i in range(len(A)):
        betaTminus1.append(cTminus1)
    betaTs[-1] = betaTminus1

    for t in range(len(E)-2, -1, -1):  # from T-2 to 0
        betat = []
        for i in range(len(A)):
            betat.append(0)
            for j in range(len(A)):
                betat[i] += A[i][j]*B[j][E[t+1]]*betaTs[t+1][j]
            # scale betat(i)
            betat[i] = betat[i]*cTs[t]
        betaTs[t] = betat

    # di-gamma
    gammaTIJ_list = [[[-100 for j in range(len(A))] for i in range(len(A))] for t in range(len(E) - 1)]  # T Matrix auch noch!
    gammaTI_list = []
    for t in range(len(E)-1):
        gammaTI = []
        for i in range(len(A)):
            gammaTI.append(0)
            for j in range(len(A)):
                gammaTIJ_list[t][i][j] = alpha_Ts[t][i]*A[i][j]*B[j][E[t+1]]*betaTs[t+1][j]
                gammaTI[i] += gammaTIJ_list[t][i][j]
        gammaTI_list.append(gammaTI)

    gammaTI = []
    for i in range(len(A)):
        gammaTI.append(alpha_Ts[len(E)-1][i])
    gammaTI_list.append(gammaTI)

    # Re-estimate
    for i in range(len(A)):
        pi[0][i] = gammaTI_list[0][i]

    for i in range(len(A)):
        denom = 0
        for t in range(len(E)-1):
            denom += gammaTI_list[t][i]
        for j in range(len(A)):
            numer = 0
            for t in range(len(E)-1):
                numer += gammaTIJ_list[t][i][j]
            A[i][j] = numer/(denom+smallNumber)

    for i in range(len(A)):
        denom = 0
        for t in range(len(E)):
            denom += gammaTI_list[t][i]
        for j in range(len(B[0])):
            numer = 0
            for t in range(len(E)):
                if E[t] == j:
                    numer += gammaTI_list[t][i]
            B[i][j] = numer/(denom+smallNumber)

    #logProb
    logProb = 0
    #print("cTs : ", cTs)
    for i in range(len(E)):
        logProb += math.log(cTs[i])
    logProb = -logProb

    return A,B,pi,E,logProb

    return None

def hmm3(Ak, Bk, qk, E, maxIters):
    begin = time.time()
    iters = 0  # max Iters already defined
    oldLogProb = float('-inf')
    #print("hmm3 init : ", Ak, Bk, qk, E)
    A, B, pi, E, logProb = calc(Ak, Bk, qk, E)
    #print("hmm3 inter : ", A, B, pi, E, logProb)
    #print("logP : ", logProb)
    while (iters < maxIters and logProb > oldLogProb):
        iters = iters + 1
        oldLogProb = logProb
        A, B, pi, E, logProb = calc(A, B, pi, E)
        #print("logP : ", logProb)

    print("iters : ", iters)
    end = time.time()
    print("time hmm3 : ", end-begin)
    return A, B, pi, E