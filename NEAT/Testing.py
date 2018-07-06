"""
The XOR test !
"""
from Population import Population

found = False


def fitness(genome):
    dist = 0
    solve = 0
    global found
    for i in (0,1):
        for j in (0,1):
            output = genome.evaluate((i,j))
            genome.clearNodes()  # Clear the nodes because of recurrent connections
            value = output[0]
            dist += abs(value - ((i and (not j)) or ((not i) and j)))
            if (value > 0.5) == ((i and (not j)) or ((not i) and j)):
                solve += 1
    if solve == 4:
        found = True
    return (4-dist)**2

p = Population()
p = Population(sensor = 2, output = 1, bias = True,
               initState = 'all linked', fitness = fitness,
               sensorName = ('In1', 'In2', 'Bias'), outputName = ('Out',), demography = 150)


while not found :
    p.nextGen() # Todo : Make 'updateGenStat' take less time
    if found:
        print()
        print('XOR Solved !')
        print('Number of gen : ', p.gen)
        print()
        break
    if p.gen >= 100:
        break
    print(p.gen)
    print(p.speciesList)

p.updateGenStats()
g = p.best
print(g.rawFitness)
g.draw()
p.graphSpecies()

# Todo : Make the bias connect to each neuron