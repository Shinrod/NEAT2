from Genome import Genome
from Species import Species
import numpy as np
from copy import copy
import matplotlib.pyplot as plt

class Population:

    def __init__(self, **kwargs):
        """
        Make a new population

        Params
        ----------
        demography : nb of genome in a population (int, default 150)
        sensor : Number of sensor nodes
        output : Number of output nodes
        bias : Whether we have a bias or not (bool, default True)
        initState : How are the nets at init ? ('one link', 'all linked', default 'one link')
        fitness : The fitness function of the genomes (func)
        sensorName : Name of the sensors (str list)
        outputName : Name of the outputs (str list)
        """
        # Default params
        params = {'demography' : 150,
                  'sensor' : 2,
                  'output' : 1,
                  'bias' : True,
                  'initState' : 'one link',
                  'fitness' : lambda x:1,
                  'sensorName' : None, # TODO : Handle names with spaces (or prevent those with spaces)
                  'outputName' : None} # TODO : Handle names with spaces (or prevent those with spaces)
        # Update params
        for key in kwargs:
            try:
                params[key] = kwargs[key]
            except KeyError as e:
                print('')

        self.demography = params['demography']
        self.genomeList = []
        for i in range(self.demography):
            self.genomeList.append(Genome(params['sensor'],
                                       params['output'],
                                       bias = params['bias'],
                                       initState = params['initState'],
                                       sensorName = params['sensorName'],
                                       outputName = params['outputName']))
        self.speciesList = []
        self.fitness = params['fitness']
        # Generation stuff
        self.gen = 1
        self.bestList = []
        self.best = self.genomeList[0]
        self.staleness = 0
        self.averageList = []
        # Be able to graph species
        self.speciesHistory = []
        self.speciesTable = np.array([]).reshape((1,0))


    ## Generation stuff
    # ------------------------------------------------------------------------------------------------------------------
    # Species

    def addSpecies(self, species):
        """
        Add a species to the population

        Params
        ----------
        species : the new species (Species)
        """
        self.speciesList.append(species)
        # Used to graph the species
        self.speciesHistory.append(species)
        newColumn = np.zeros((self.gen,1))
        self.speciesTable = np.append(self.speciesTable, newColumn, axis = 1)

    def sortInSpecies(self):
        """
        Sort the population in species
        """
        # Be sure the species are empty
        for species in self.speciesList:
            species.clear()
        # Go through all the genomes
        for genome in self.genomeList:
            foundSpecies = False
            # Go through all the species
            for species in self.speciesList:
                if species.matches(genome):
                    # If it has found one it become part of it
                    species.addGenome(genome)
                    foundSpecies = True
                    break
            if not foundSpecies:
                # Otherwise we make a new species
                newSpecies = Species(genome)
                self.addSpecies(newSpecies)
        # Once we have gone through all the genomes, if a species is empty, it disappear
        for i in range(len(self.speciesList))[::-1]:
            if self.speciesList[i].isEmpty():
                self.speciesList.pop(i)

    def shareFitness(self):
        """
        Share the fitness of the genomes with the species it belongs to
        """
        for species in self.speciesList:
            species.shareFitness()

    def purge(self):
        """
        Kill the bottom half of each species + kill stale species
        """
        for i, species in list(enumerate(self.speciesList))[::-1]:
            if species.staleness > 15:
                species.clear()
                self.speciesList.pop(i)
            species.purge()

    def speciesAnalysis(self):
        """
        Analyze the species before making babies and stuff + get the global average
        """
        average = 0
        for species in self.speciesList:
            # If a species has more than 5 nets, its champ goes through without mutation
            if len(species.genomeList) >= 5:
                species.champGoThrough = True
            average += species.averageFitness * len(species.genomeList)
        self.averageList.append(average / len(self.genomeList))

    def updateSpeciesAverageFitness(self):
        """
        Update the average fitness of the species (also update the average of the
        """
        for species in self.speciesList:
            species.updateAverageFitness()

    def updateMascots(self):
        """
        Update the mascots of the species (a random genome amongst the species
        """
        for species in self.speciesList:
            species.updateMascot()


    def selectSpecies(self):
        """
        Select a species based on it's fitness average
        """
        totalSum = 0
        averageList = []
        for species in self.speciesList:
            totalSum += species.averageFitness
            averageList.append(species.averageFitness)
        probability = np.array(averageList) / totalSum
        return np.random.choice(self.speciesList, p = probability)

    def updateChamp(self):
        """
        Update the champ of the species
        """
        for s in self.speciesList:
            s.updateChamp()


    # ------------------------------------------------------------------------------------------------------------------
    # Fitness
    def updateFitness(self):
        """
        Updates the fitness of all the genomes
        """
        for genome in self.genomeList:
            genome.rawFitness = self.fitness(genome)

    def updateBest(self):
        """
        Updates the best genome of the population
        """
        for species in self.speciesList:
            if species.best.rawFitness > self.best.rawFitness:
                self.best = species.best
                self.staleness = 0
        self.staleness += 1

    def sortSpeciesList(self):
        """
        Sort the list of species
        """
        L = self.speciesList

        n = len(L)
        for i in range(1, n):
            j = i
            species = L[i]
            while 0 < j and species.averageFitness > L[j - 1].averageFitness:
                L[j] = L[j - 1]
                j = j - 1
            L[j] = species


    def selectGenome(self):
        """
        Select a genome based on sharedFitness
        """
        totalSum = 0
        fitnessList = []
        for genome in self.genomeList:
            totalSum += genome.sharedFitness
            fitnessList.append(genome.sharedFitness)
        probability = np.array(fitnessList) / totalSum
        return np.random.choice(self.genomeList, p=probability)

    # ------------------------------------------------------------------------------------------------------------------
    # Generation management

    def updateGenStats(self):
        """
        Update the gen stats
        """
        self.updateFitness()
        self.sortInSpecies()
        self.shareFitness()
        self.updateChamp()
        self.updateSpeciesAverageFitness()
        self.updateBest()


    def nextGen(self):
        """
        Make the next gen
        """
        self.updateGenStats()
        self.speciesAnalysis()
        # Be able to graph species
        newLine = np.zeros((1, len(self.speciesHistory)))
        self.speciesTable = np.append(self.speciesTable, newLine, axis=0)
        for i,s in enumerate(self.speciesHistory):
            self.speciesTable[self.gen-1, i] = len(s.genomeList)
        # Purge
        self.purge()
        # If the population hasn't evolved in 20 gen : only keep the top 2 species
        if self.staleness > 20:
            self.sortSpeciesList()
            for species in self.speciesList[2:]:
                species.clear()
            self.speciesList = self.speciesList[0:2]
            print('Stale')
            # Reset the staleness counter
            self.staleness = 0
        self.updateMascots()
        self.newPop()


    def newPop(self):
        """
        Make a new population
        """
        # Make the new gen
        newPop = []

        # Species with more than 5 nets get their champ passed over the next gen
        for species in self.speciesList:
            if species.champGoThrough:
                newPop.append(copy(species.champ))

        # Fill the other part of the population with people
        while len(newPop) < self.demography:
            # 25% of the new pop are genomes from the previous gen that received a mutation
            if np.random.rand() < 0.25:
                child = copy(self.selectGenome())
                child.mutate()
            # 75% of the new pop come from crossover
            else:
                    # 0.1% chance crossover happens with parents from a different species
                    if np.random.rand() < 0.001:
                        parent1 = self.selectGenome()
                        parent2 = self.selectGenome()
                    # 99.9 % chance it happens within a species
                    else:
                        if len(self.speciesList) != 0:  # Note : To be able to pick species, we need them to exist
                            species = self.selectSpecies()
                            parent1 = species.selectGenome()
                            parent2 = species.selectGenome()
                        else:  # If there is no species left
                            parent1 = self.selectGenome()
                            parent2 = self.selectGenome()
                    child = Genome.crossover(parent1, parent2)
                    child.mutate()
            newPop.append(child)

        self.genomeList = newPop
        # Once we are done, increase the gen counter
        self.gen += 1
        self.bestList.append(self.best)

    ## Net stuff
    # ------------------------------------------------------------------------------------------------------------------
    # Evaluation
    def evaluate(self, inputs):
        """
        Evaluate every genome of the population

        Params
        ----------
        inputs : input value (list)
        """
        for genome in self.genomeList:
            genome.evaluate(inputs)

    ## Final stuff
    # ------------------------------------------------------------------------------------------------------------------
    # Graphs
    def graphFitness(self):
        """
        Graph the best fitness and the average fitness of the species
        """
        # Prepare
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x = range(len(self.bestList))
        # Graph best fitness
        bestFitness = []
        for b in self.bestList:
            bestFitness.append(b.rawFitness)
        ax.plot(x, bestFitness, color='red', label='Max fitness')
        # Graph average
        average = []
        for av in self.averageList:
            average.append(av)
        ax.plot(x, average, color='green', label='average')
        # Graph
        ax.legend()
        ax.set_title('Fitness')
        plt.show(fig)


    def graphSpecies(self):
        """
        Draw a graph where we can see species evolution
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.stackplot(range(1,self.gen+1), self.speciesTable.transpose())

# ----------------------------------------------------------------------------------------------------------------------
# Testing
if __name__ == '__main__':
    ''' Test the evaluation '''
    p = Population(initState = 'all linked', sensorName = ('Pos', 'Dist', 'Bias'), outputName = ('Jump',))
    # print(p.genomeList[0].evaluate([0.1,0.2,0.3]))
    # print(p.genomeList[0].connectionList)
    # p.genomeList[0].draw()
    # for genome in p.genomeList:
    #     for i in range(100):
    #         genome.mutate()
    g = p.genomeList[0]
    c = g.addConnectionMutation
    n = g.addNodeMutation
    d = g.draw
    d()

    def f():
        p.nextGen()
        p.updateGenStats()
        return p.speciesList

