#!/usr/bin/env python3

from player_controller_hmm import PlayerControllerHMMAbstract
from constants import *
import random
import matrixOperations as matOp
import hmm3 as hmm
import hmm1
import hmm as hmmBis

N_STATES = int(1.5 * N_SPECIES)  # Number of states: species/pattern?
# N_EMISSIONS #Number of emissions: 8 direction
THRESHOLD = 20  # to be evaluate #if distance A1A2 + B1B2 < THRESHOLD: same specie


class PlayerControllerHMM(PlayerControllerHMMAbstract):

    def init_parameters(self):
        """
        In this function you should initialize the parameters you will need,
        such as the initialization of models, or fishes, among others.
        """
        self.qk = [matOp.initq(N_STATES) for k in range(N_FISH)]  # List of initial state distribution for each fish
        self.Ak = [matOp.initA(N_STATES) for k in range(N_FISH)]  # List of transition matrix for each fish
        self.Bk = [matOp.initB(N_STATES, N_EMISSIONS) for k in range(N_FISH)]  # List of emission matrix for each fish
        self.Ok = [matOp.initO(N_STEPS) for k in range(N_FISH)]  # List of emissions
        self.Species = [[-1 for j in range(N_FISH)] for i in range(2)]  # First line: classification & seconde line: revealed species
        self.SpecieLambda = [-1 for j in range(N_SPECIES)]  # store 1 lambda for each specie (for comparing with new fishes)
        # pass
        #print("step limit : ", N_STEPS - N_FISH - 1)

    def guess(self, step, observations):
        """
        This method gets called on every iteration, providing observations.
        Here the player should process and store this information,
        and optionally make a guess by returning a tuple containing the fish index and the guess.
        :param step: iteration number
        :param observations: a list of N_FISH observations, encoded as integers
        :return: None or a tuple (fish_id, fish_type)
        """
        # Complete our observations with the new observations of this step
        for fishObs in range(N_FISH):  # N_FISH = len(observations)
            self.Ok[fishObs][step - 1] = observations[fishObs]

        """#random guess for the first 10 iterations
        if step < 10:
            (fish_id, fish_type) = (step % N_FISH-1, random.randint(0, N_SPECIES - 1))
            print("random guess : ", (fish_id, fish_type))
            return (fish_id, fish_type)

        #create a bug to stop the program
        '''if step == 15:
            return (-1, -1)'''

        if step >= 10:
        #if (step%40 == 0) and (step != 0): #to improve: maybe improve several fish's system at each step
            hmm.hmm3(self, 10, step) #~23
            self.classification() #give a specie for each fish: self.Species[0][fish]
            print("self.Species : ", self.Species)
            (fish_id, fish_type) = self.makeAGuess()
            print("guess : ", (fish_id, fish_type))
            return (fish_id, fish_type) #we return our guess"""

        """print()
        print(step)
        if step < N_STEPS - N_FISH - 1:
            hmm.hmm3(self, 10, step)  # ~23
            return None

        self.classification()  # give a specie for each fish: self.Species[0][fish]
        print("self.Species : ", self.Species)
        (fish_id, fish_type) = self.makeAGuess()
        print("guess : ", (fish_id, fish_type))
        return (fish_id, fish_type)  # we return our guess"""

        # new:
        if step < N_STEPS - N_FISH - 1:
            #print("step : ", step)
            return None
        fish_id = (step-(N_STEPS - N_FISH - 1))%N_FISH
        maxProb = 0
        fish_type = -1
        E = []
        e = 0
        # create vector of emission E
        while (e < len(self.Ok[fish_id])) and (self.Ok[fish_id][e] != -1):
            E.append(self.Ok[fish_id][e])
            e += 1
        for spc in range(len(self.SpecieLambda)):  # lambda
            lmd = self.SpecieLambda[spc]
            if lmd != -1:  # if we have a example
                A, B, q = lmd
                prob = hmm1.alpha_pass(A, B, q, E)  # calculate probability that fish_id belong to the specie spc
                if prob > maxProb:
                    fish_type = spc
                    maxProb = prob
        #print("maxProb : ", maxProb)
        if maxProb > 0:  # if we found a good match we guess the specie
            #print("guess1 : ", (fish_id, fish_type))
            return (fish_id, fish_type)
        else:  # we guess randomly
            for spc in range(len(self.SpecieLambda)):  # lambda
                lmd = self.SpecieLambda[spc]
                if lmd == -1:  # if one specie hasn't an example, we guess this new specie
                    fish_type = spc
                    #print("guess2 : ", (fish_id, fish_type))
                    return (fish_id, fish_type)

        # we found no match and all species have an example: we guess randomly
        fish_type = random.randint(0, N_SPECIES - 1)
        #print("guess3 : ", (fish_id, fish_type))
        return (fish_id, fish_type)

    def reveal(self, correct, fish_id, true_type):
        """
        This methods gets called whenever a guess was made.
        It informs the player about the guess result
        and reveals the correct type of that fish.
        :param correct: tells if the guess was correct
        :param fish_id: fish's index
        :param true_type: the correct type of the fish
        :return:
        """
        #print("reveal: ", (fish_id, true_type), correct)
        '''self.Species[1][fish_id] = true_type  # we attribute the true specie to the fish
        self.Species[0][fish_id] = true_type  # needed?'''

        # new: we calculate hmm3(fish_id) to have an example of lambda for each specie
        if self.SpecieLambda[true_type] == -1:  # if there is still no example of lambda for this specie
            E = []
            e = 0
            # create vector of emission E
            while (e < len(self.Ok[fish_id])) and (self.Ok[fish_id][e] != -1):
                E.append(self.Ok[fish_id][e])
                e += 1
            A, B, q, O = hmmBis.hmm3(self.Ak[fish_id], self.Bk[fish_id], self.qk[fish_id], E, 26)  # ~23 #has to be coded
            #print("SpecieLambda : ", true_type)
            #print(A, B, q, O)
            self.SpecieLambda[true_type] = (A, B, q)  # store the lambda for the specie
        return None

    # give a specie for each fish: self.Species[0][fish]
    def classification(self):
        specieExample = [-1 for j in
                         range(N_SPECIES)]  # for each specie we put -1 or the index of one revealed fish of this specie
        # we fill specieExample with example for each revealed specie
        for fish in range(N_FISH):
            fishSpecie = self.Species[1][fish]
            if fishSpecie != -1:  # has already been revealed
                if specieExample[fishSpecie] == -1:  # still no example for this specie
                    specieExample[fishSpecie] = fish
        #print("specieExample : ", specieExample)
        # we class all other fish
        for fish in range(N_FISH):

            distMat = []

            if self.Species[1][fish] == -1:  # its specie isn't revealed
                minDist = THRESHOLD  # to attribute the fish to the closest specie
                for k in range(len(specieExample)):  # we compare to the revealed species
                    fishk = specieExample[k]
                    if fishk != -1:  # if there is an example for the specie k
                        # distance are 0 or ~10; 20
                        dist = matOp.distance(self.Ak[fish], self.Bk[fish], self.Ak[fishk], self.Bk[fishk])

                        '''if (fish == 68) and (dist == 0):
                            print("0- : ", fish, self.Ak[fish], self.Bk[fish])
                            print("0+ : ", fishk, self.Ak[fishk], self.Bk[fishk])
                            print()'''

                        distMat.append(dist)

                        if dist < minDist:
                            minDist = dist
                            self.Species[0][fish] = k
                            specieExample[k] = fish  # example for this new specie

                # print("distMat : ", distMat)

    # guess a fish of an already revealed specie or guess for a new specie
    def makeAGuess(self):
        listRevealed = []  # index of revealed species
        # we look at the revealed species
        for j in range(N_FISH):
            ind = self.Species[1][j]
            if (ind != -1) and (ind not in listRevealed):
                listRevealed.append(ind)
        # try to guess a fish's specie which belong to the same specie as a revealed one
        for j in range(N_FISH):
            if (self.Species[1][j] == -1) and (self.Species[0][j] in listRevealed):
                return j, self.Species[0][j]
        # if there is no fish which has the same specie as a revealed one, we guess randomly
        for j in range(N_FISH):
            if (self.Species[1][j] == -1) and (self.Species[0][j] not in listRevealed):
                return j, self.Species[0][j]
        return -1, -1  # if we already made guesses for all fishes, what shouldn't happen
