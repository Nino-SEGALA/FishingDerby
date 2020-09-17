#!/usr/bin/env python3

from player_controller_hmm import PlayerControllerHMMAbstract
from constants import *
import random
import matrixOperations as matOp
import hmm3 as hmm

N_STATES = N_SPECIES  # Number of states: species/pattern?
#N_EMISSIONS #Number of emissions: 8 direction
THRESHOLD = 1000 #to be evaluate #if distance A1A2 + B1B2 < THRESHOLD: same specie

class PlayerControllerHMM(PlayerControllerHMMAbstract):

    def init_parameters(self):
        """
        In this function you should initialize the parameters you will need,
        such as the initialization of models, or fishes, among others.
        """
        self.qk = [matOp.initq(N_STATES) for k in range(N_FISH)] #List of initial state distribution for each fish
        self.Ak = [matOp.initA(N_STATES) for k in range(N_FISH)] #List of transition matrix for each fish
        self.Bk = [matOp.initB(N_STATES, N_EMISSIONS) for k in range(N_FISH)] #List of emission matrix for each fish
        self.Ok = [matOp.initO(N_STEPS) for k in range(N_FISH)] #List of emissions
        self.Species = [[-1 for j in range(N_FISH)] for i in range(2)] #First line: classification & seconde line: revealed species
        #pass

    def guess(self, step, observations):
        """
        This method gets called on every iteration, providing observations.
        Here the player should process and store this information,
        and optionally make a guess by returning a tuple containing the fish index and the guess.
        :param step: iteration number
        :param observations: a list of N_FISH observations, encoded as integers
        :return: None or a tuple (fish_id, fish_type)
        """
        #Complete our observations with the new observations of this step
        for fishObs in range(N_FISH): #N_FISH = len(observations)
            self.Ok[fishObs][step-1] = observations[fishObs]

        if (step%10 == 0) and (step != 0): #to improve: maybe improve several fish's system at each step
            hmm.hmm3(self, 10) #has to be code
            self.classification() #give a specie for each fish: self.Species[0][fish]
            (fish_id, fish_type) = self.makeAGuess()
            print("guess : ", (fish_id, fish_type))
            return (fish_id, fish_type) #we return our guess

        # This code would make a random guess on each step:
        return (step % N_FISH, random.randint(0, N_SPECIES - 1))

        return None

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
        self.Species[1][fish_id] = true_type #we attribute the true specie to the fish
        #need for self.Species[0][fish_id] = true_type ?
        return None

    #give a specie for each fish: self.Species[0][fish]
    def classification(self):
        specieExample = [-1 for j in range(N_SPECIES)] #for each specie we put -1 or the index of one revealed fish of this specie
        #we fill specieExample with example for each revealed specie
        for fish in range(N_FISH):
            fishSpecie = self.Species[1][fish]
            if fishSpecie != -1: #has already been revealed
                if specieExample[fishSpecie] == -1: #still no example for this specie
                    specieExample[fishSpecie] = fish
        #we class all other fishes
        for fish in range(N_FISH):
            if self.Species[1][fish] == -1: #its specie isn't revealed
                for k in range(len(specieExample)): #we compare to the revealed species
                    fishk = specieExample[k]
                    if fishk != -1:
                        if matOp.distance(self.Ak[fish], self.Bk[fish], self.Ak[fishk], self.Bk[fishk]) < THRESHOLD:
                            self.Species[0][fish] = k
                            specieExample[k] = fish #example for this new specie

    #guess a fish of an already revealed specie or guess for a new specie
    def makeAGuess(self):
        listRevealed = [] #index of revealed species
        #we look at the revealed species
        for j in range(N_SPECIES):
            ind = self.Species[1][j]
            if (ind != -1) and (ind not in listRevealed):
                listRevealed.append(ind)
        #try to guess a fish's specie which belong to the same specie as a revealed one
        for j in range(N_SPECIES):
            if (self.Species[1][j] == -1) and (self.Species[0][j] in listRevealed):
                return j, self.Species[0][j]
        #if there is no fish which has the same specie as a revealed one, we guess randomly
        for j in range(N_SPECIES):
            if (self.Species[1][j] == -1) and (self.Species[0][j] not in listRevealed):
                return j, self.Species[0][j]
        return -1, -1 #if we already made guesses for all fishes, what shouldn't happen