import numpy as np

class Species:
    """
    Used to group nets
    """

    def __init__(self, genome):
        """
        Make a new species

        Params
        ----------
        genome : The genome that required this new species (Genome)
        """
        self.mascot = genome  # The genome which represent the species
        self.genomeList = [genome]  # Members of the species
        self.best = genome  # Best : best net of the species of all time
        self.champ = genome  # Champ : best net of the species this gen
        # Generation stuff
        self.champGoThrough = False  # If a species has more than 5 nets, the champ net is copied to the next gen
        self.staleness = 0  # Tell for how many species the species has not evolved
        self.averageFitness = 0  # The average fitness of the species
        # Be able to graph it
        self.populationHistory = []

    def matches(self, genome):
        """
        Say if a genome belong to the species

        Params
        ----------
        genome : The genome we are testing (Genome)
        """
        # Define the constants used by the 'distance' function
        c1 = 1.0  # Related to excess genes
        c2 = 1.0  # Related to disjoint genes
        c3 = 0.4  # Related to avg. weight diff.
        threshold = 3

        # Determine the fittest genome
        if genome.rawFitness > self.mascot.rawFitness:
            genome1 = genome
            genome2 = self.mascot
        else:
            genome1 = self.mascot
            genome2 = genome

        excess, disjoint, avgWeightDiff = self.getCoefficients(genome1, genome2)
        n = max(len(genome1.connectionList)-20, 1)

        distance = c1*excess/n + c2*disjoint/n + c3*avgWeightDiff
        return distance < threshold

    @staticmethod
    def getCoefficients(genome1, genome2):
        """
        Get the coefficients required for the distance computation
        excess : number of excess genes
        disjoint : number of disjoint genes
        avgWeightDiff : average weight differences of the matching genes

        Params
        ----------
        genome1 : fittest of the two genomes (Genome)
        genome2 : the other genome we are comparing to (Genome)
        """
        # Init all the counters
        excess = 0
        disjoint = 0
        matching = 0
        weightDiff = 0

        # Check the connections of the 1st genome
        for con1 in genome1.connectionList:
            matches = False
            for con2 in genome2.connectionList:
                if con1.innovationNumber == con2.innovationNumber:
                    # Matching gene
                    matching += 1
                    weightDiff = abs(con1.weight - con2.weight)
                    matches = True
            if not matches:
                # Disjoint gene
                disjoint += 1

        # Now check the connections of the 2nd genome
        # We don't want to count the matching genes 2 times

        # Used to recognize excess or disjoint genes
        maxInnovation = 0
        for con in genome1.connectionList:
            if con.innovationNumber > maxInnovation:
                maxInnovation = con.innovationNumber

        for con2 in genome2.connectionList:
            matches = False
            for con1 in genome1.connectionList:
                if con1.innovationNumber == con2.innovationNumber:
                    # Matching gene
                    matches = True
                    break
            if not matches:
                # Excess or disjoint
                if con2.innovationNumber < maxInnovation:
                    # Disjoint
                    disjoint += 1
                else:
                    # Excess
                    excess += 1

        if matching != 0:
            avgWeightDiff = weightDiff/matching
        else:
            avgWeightDiff = 0

        return excess, disjoint, avgWeightDiff

    def addGenome(self, genome):
        """
        Add a genome to the species

        Params
        ----------
        genome : The genome we want to add (Genome)
        """
        self.genomeList.append(genome)


    def shareFitness(self):
        """
        'Share' the fitness inside the species
        """
        for genome in self.genomeList:
            genome.sharedFitness = genome.rawFitness / len(self.genomeList)

    def updateChamp(self):
        """
        Update the champ of the species (the best net of this gen)
        """
        self.sortGenomes()
        self.champ = self.genomeList[0]
        if self.champ.rawFitness > self.best.rawFitness:
            self.best = self.champ
            self.staleness = 0
        else:
            self.staleness += 1

    def sortGenomes(self):
        """
        Sort the genomes by fitness (fittest first)
        """
        L = self.genomeList

        n = len(L)
        for i in range(1,n):
            j = i
            genome = L[i]
            while 0 < j and genome.rawFitness > L[j-1].rawFitness :
                L[j] = L[j-1]
                j = j-1
            L[j] = genome

    def updateAverageFitness(self):
        """
        Updates the average fitness of the species
        """
        # Shared fitness are fitnesses divided by the number of genomes in the species
        # So we only need to add those up
        average = 0
        for genome in self.genomeList:
            average += genome.sharedFitness
        self.averageFitness = average

    def purge(self):
        """
        Kill the bottom half of the species
        """
        self.sortGenomes()
        half = int(len(self.genomeList)+1 / 2)  # Species with only 1 genome have their genome saved
        self.genomeList = self.genomeList[:half]

    def isEmpty(self):
        """
        Tell is the species is empty or not
        """
        return len(self.genomeList) == 0

    def clear(self):
        """
        Clear the species
        """
        self.genomeList = []

    def updateMascot(self):
        """
        Update the mascot (take a random genome amongst the genomes in the species)
        """
        self.mascot = np.random.choice(self.genomeList)


    def selectGenome(self):
        """
        Select a genome based on it's fitness
        """
        totalSum = 0
        fitnessList = []
        for genome in self.genomeList:
            totalSum += genome.sharedFitness
            fitnessList.append(genome.sharedFitness)
        probability = np.array(fitnessList) / totalSum
        return np.random.choice(self.genomeList, p = probability)