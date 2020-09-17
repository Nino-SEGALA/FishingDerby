#File containing everything needed to work on matrix

import random

def mult(M, N):  # calculate M*N
    p, q = len(M), len(M[0])
    r, s = len(N), len(N[0])
    R = [[0 for x in range(s)] for y in range(p)]
    if q == r:
        for i in range(p):
            for j in range(s):
                for k in range(q):
                    R[i][j] += M[i][k] * N[k][j]
    return R

def transpose(M): #calculate the transposed of M
    res = [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]
    return res

def column(M, j):  # return the column j of M
    i = len(M)
    Mj = [[0] for k in range(i)]
    for k in range(i):
        Mj[k][0] = M[k][j]
    return Mj

def maxi(A):
    #create a vector with the maximum value of each row and a vector with the indice of this maximum value
    n = len(A)
    p = len(A[0])
    dlt = [[0] for k in range(n)]
    dlt_idx = [[0] for k in range(n)]
    for i in range(n):
        index, max_val = -1, -1
        for j in range(p):
            if A[i][j] > max_val:
                index, max_val = j, A[i][j]
        dlt[i][0] = max_val
        dlt_idx[i][0] = index
    return dlt, dlt_idx

'''def mult_block_by_block(u, v):
    #calculate a new vector where each block is equal to the multiplication of
    # the same block in u and the same block in v
    n = len(u)
    w = [[0] for i in range(n)]
    for i in range(n):
        w[i][0] = u[i][0]*v[i][0]
    return w
'''

def mult_block_by_block(A, B):
    #make a multiplication block by block between a matrix A and a vector u
    n = len(A)
    p = len(A[0])
    W = [[0 for j in range(p)] for i in range(n)]
    for i in range(n):
        for j in range(p):
            W[i][j] = A[i][j]*B[i][j]
    return W

def make_matrix(lst):
    #return the matrix corresponding to lst, where the first 2 elements of lst are the size of M
    #and what follow are the rows of the matrix
    lst = [float(i) for i in lst]
    n = int(lst[0]) #M matrix n_rows * p_columns (n states; p emissions)
    p = int(lst[1])
    M = [[0 for j in range(p)] for i in range(n)]
    for i in range(n):
        for j in range(p):
            M[i][j] = lst[2 + p*i + j]
    return M

def make_vector(lst):
    # return the vector corresponding to lst, where the first element of lst is the length of M
    # and what follow are the rows of the vector
    lst = [int(i) for i in lst]
    p = int(lst[0]) #M matrix p_columns (p emissions)
    M = [0 for j in range(p)]
    for j in range(p):
        M[j] = lst[1 + j]
    return M

def initq(N):
    q = [[(1/N + (2*random.random()-1)/(10*N)) for j in range(N-1)]]
    q[0].append(1-sum(sum(q[i]) for i in range(len(q))))
    return q

def initA(N):
    A = [[(1/N**2 + (2*random.random()-1)/(10*N**2)) for j in range(N)] for i in range(N)]
    A[N-1][N-1] = 1-sum(sum(A[i]) for i in range(len(A)))+A[N-1][N-1]
    return A

def initB(N, M):
    B = [[(1/(N*M) + (2*random.random()-1)/(10*N*M)) for j in range(M)] for i in range(N)]
    B[N-1][M-1] = 1-sum(sum(B[i]) for i in range(len(B)))+B[N-1][M-1]
    return B

def initO(M):
    return [-1 for j in range(M)]

#calculate the distance A1A2**2 + B1B2**2
def distance(A1, B1, A2, B2):
    dist = 0
    for i in range(len(A1)):
        for j in range(len(A1[0])):
            dist += (A1[i][j] - A2[i][j])**2
        for j in range(len(B1[0])):
            dist += (B1[i][j] - B2[i][j]) ** 2
    return dist