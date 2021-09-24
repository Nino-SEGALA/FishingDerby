import sys
import matrixOperations as matOp

def input_hmm1():
    #return A, B, q and O
    res = [] #[A, B, q, O]
    i = 0
    for line in sys.stdin:
        lst = line.split()
        if i < 3:
            res.append(make_matrix(lst))
        else: #the last line in the sequence of emissions vector
            res.append(make_vector(lst))
        i += 1
    return res

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

def alpha_init(B, q, O):
    #calculate alpha_1(i)
    em_prob = matOp.column(B, O[0])
    return matOp.mult_block_by_block(matOp.transpose(q), em_prob)

def alpha_t(A, B, q, O):
    #calculate the vector alpha after t=len(O) steps
    alpha = alpha_init(B, q, O)
    t = len(O) #number of steps
    for k in range(1, t):
        state_prob = matOp.mult(matOp.transpose(A), alpha)
        em_prob = matOp.column(B, O[k])
        alpha = matOp.mult_block_by_block(state_prob, em_prob) #we calculate the new alpha
    return alpha

def hmm1():
    #solve the hmm1 problem
    [A, B, q, O] = input_hmm1() #we convert the input into 4 matrix
    alpha = alpha_t(A, B, q, O)
    res = 0
    for j in range(len(alpha)):
        res += alpha[j][0]
    return res

#we give the emission on the fish
#and the system lambda (A, B, q) of the specie we want to compare the fish to
def alpha_pass(A, B, q, O):
    alpha = alpha_t(A, B, q, O)
    res = 0
    for j in range(len(alpha)):
        res += alpha[j][0]
    return res