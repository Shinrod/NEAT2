from Node import Node
from Connection import Connection
from History import History
import numpy as np
# My own queue module
from Queue import PriorityQueue
from graphviz import Digraph
from copy import copy

class Genome:

    # Innovation history for the connection genes
    innovationHistory = []

    def __init__(self, sensor, output, **kwargs):
        """
        Initialize a net

        Params
        ----------
        sensor : nb of sensor nodes (bias not included) (int)
        output: nb of output nodes (int)
        bias: include a bias ? (bool, default True)
        initState: What is the state of a new net ? ('none', 'one link', 'all linked', default 'one link')
        sensorName : Name of the sensors (str list)
        outputName : Name of the outputs (str list)
        """
        # Default params
        params = {'bias' : True,
                  'initState' : 'one link',
                  'sensorName' : None,
                  'outputName': None}
        # Update params
        for key in kwargs:
            params[key] = kwargs[key]

        # Handle the nodes
        self.sensor = sensor + int(params['bias'])
        self.output = output
        self.nodeList = []
        self.biasActive = params['bias']
        # Add the sensors
        for i in range(self.sensor):
            try:
                self.addNode('sensor', number = i, name = params['sensorName'][i])
            except:
                self.addNode('sensor', number=i)
        # If we forgot to name, the bias, name it 'Bias'
        biasNode = self.nodeList[-1]
        if biasNode.number == biasNode.name:
            biasNode.name = 'Bias'
        # Add the output nodes
        for i in range(self.output):
            try:
                self.addNode('output', number = self.sensor+i, name = params['outputName'][i])
            except:
                self.addNode('output', number=self.sensor + i)
        # Handle innovation number
        # Note : we don't want to reset it if it has already increased
        if History.innovationNumber == 0:
            History.innovationNumber = self.sensor + self.output

        # Handle the connections
        self.connectionList = []
        if params['initState'] == 'all linked':
            # Link all the sensors to the outputs
            for node1 in self.nodeList[:self.sensor]:
                for node2 in self.nodeList[self.sensor:]:
                    innovationNumber = self.getInnovationNumber(node1, node2)
                    self.addConnection(Connection(node1, node2, 'random', True, innovationNumber))
        elif params['initState'] == 'one link':
            self.addConnectionMutation()

        # Other stuff
        self.rawFitness = 0  # The raw fitness of the genome
        self.sharedFitness = 0  # The fitness of the genome biased according to the size of the species it belongs to

    # ------------------------------------------------------------------------------------------------------------------
    # Tools
    def addNode(self, kind, number, name = None):
        """
        Add a node to the network

        Params
        ----------
        kind: kind of node ('sensor', 'hidden', 'output')
        name : Name of the node
        """
        sameAs = 0  # Count the number of nodes with the same number
        for node in self.nodeList:
            if node.number == number:
                sameAs += 1
        # Get a unique identifier (unique for this genome) -> For more information, see Bug #1
        identifier = (number, sameAs)
        # Make the node and add it to the genome
        node = Node(identifier, kind, name)
        self.nodeList.append(node)
        return node


    def addConnection(self, connection):
        """
        Add a connection to the net

        Params
        ----------
        connection: (Connection)
        """
        self.connectionList.append(connection)

    # ------------------------------------------------------------------------------------------------------------------
    # Mutation

    def mutate(self):
        """
        Make the network mutate
        """
        # Weight mutation : 80%
        if np.random.rand() <= 0.8:
            self.weightMutation()
        # Add connection mutation : 5%
        if np.random.rand() <= 0.05:
            self.addConnectionMutation()
        # Add node mutation : 3%
        if np.random.rand() <= 0.03:
            self.addNodeMutation()


    def weightMutation(self):
        """
        Make the weights mutate
        """
        for connection in self.connectionList:
            # Uniform mutation : 90%
            if np.random.rand() < 0.9:
                connection.weight += np.random.uniform(-0.5, 0.5)
                # Keep it between -1 and 1
                connection.weight = max(-1, connection.weight)
                connection.weight = min(1, connection.weight)
            # New weight : 10%
            else:
                connection.weight = 2*np.random.rand() - 1
                

    def addConnectionMutation(self):
        """
        Mutation : add a connection to the net

        We pick 2 unconnected nodes to connect them together
        """
        # Check if the net is full connected
        if self.fullyConnected():
            print('Fully connected')
            return None
        # If not, connect 2 nodes

        # Make a list from where the nodes can be picked
        choice = []
        # Outputs can't be the start of a connection # TODO : Should I allow that ?
        for node1 in self.nodeList[:self.sensor] + self.nodeList[self.sensor+self.output:]:
            # Sensors can't be the end of a connection # TODO : Should I allow that ?
            for node2 in self.nodeList[self.sensor:]:
                # A node can't connect to itself  # TODO : Should I allow that ?
                if node1 != node2:
                    # They have to be unconnected to one another
                    if not self.areConnected(node1, node2):
                        choice.append((node1, node2))
        if len(choice) == 0:
            return None
        i =  np.random.randint(0,len(choice))
        node1, node2 = choice[i]

        innovationNumber = self.getInnovationNumber(node1, node2)
        connection = Connection(node1, node2, 'random', True, innovationNumber)
        self.addConnection(connection)

    def fullyConnected(self):
        """
        Tell if the net is fully connected or not
        """
        maxConnections = 0
        # Each sensor can connect to each hidden and to each output
        hidden = len(self.connectionList) - self.sensor - self.output
        maxConnections += self.sensor * (hidden + self.output)
        # Each hidden can connect to each hidden (except itself) and to each
        # TODO : add an option to allow recurrent connections or not
        maxConnections += hidden * (hidden-1 + self.output)
        if len(self.connectionList) == maxConnections:
            return True
        else:
            return False

    def areConnected(self, node1, node2):
        """
        Tell if node1 is connected to node2
        node1 : (Node)
        node2 : (Node)
        """
        for connection in self.connectionList:
            if connection.nodeIn == node1:
                if connection.nodeOut == node2:
                    return True


    def addNodeMutation(self):
        """
        Add a node to the network

        Pick a connection and disable it.
        Make a new node
        Link the starting node to the new node (weight 1)
        Link the new node to the end node (weight connection.weight)
        """


        # Make a list from where a connection can be picked
        available = []
        for con in self.connectionList:
            if con.enabled:
                available.append(con)
        # If there is no connection to pick, make a new connection instead
        if len(available) == 0:
            self.addConnectionMutation()
            return None
        # If a connection is available : Pick a connection
        con = np.random.choice(available)
        # Disable it
        con.disable()
        # Make a new node
        newNode = self.addNode('hidden', number = con.innovationNumber)
        # Link the starting node to the new one
        innovationNumber = self.getInnovationNumber(con.nodeIn, newNode)
        newCon1 = Connection(con.nodeIn, newNode, 1, True, innovationNumber)
        self.addConnection(newCon1)
        # Link the new node to the ending node
        innovationNumber = self.getInnovationNumber(newNode, con.nodeOut)
        newCon2 = Connection(newNode, con.nodeOut, con.weight, True, innovationNumber)
        self.addConnection(newCon2)


    # ------------------------------------------------------------------------------------------------------------------
    # Crossover
    @staticmethod
    def crossover(parent1, parent2):
        """
        Mate 2 parents (both must have a fitness)

        Params
        ----------
        parent1 : (Genome)
        parent2 : (Genome)
        """
        # Order them by fitness
        sameFitness = False
        if parent2.sharedFitness > parent1.sharedFitness:
            parent1, parent2 = parent2, parent1
        elif parent2.sharedFitness == parent1.sharedFitness:
            sameFitness = True

        # Prepare the child
        sensor = parent1.sensor - parent1.biasActive
        child = Genome(sensor, parent1.output, bias = parent1.biasActive, initState = 'none')
        child.sensor = parent1.sensor
        child.output = parent1.output

        # The child has the same node as its fittest parent
        child.nodeList = []
        for node in parent1.nodeList:
            child.nodeList.append(copy(node))
        # If both parents have the same fitness, it has the same nodes as both of its parents
        if sameFitness:
            for node in parent2.nodeList:
                # Be sure that the node is not already in the list
                if node not in child.nodeList:
                    child.nodeList.append(node)

        # Give it connections
        child.connectionList = []
        for con1 in parent1.connectionList:
            matches = False
            for con2 in parent2.connectionList:
                if con1.innovationNumber == con2.innovationNumber:
                    # Matching gene
                    # 50% chance to pick the first or the second parent
                    if np.random.rand() < 0.5:
                        newCon = copy(con1)
                    else:
                        newCon = copy(con2)
                    if not con1.enabled or not con2.enabled:
                        # If one of the connection is disabled : 75% chance the new connection is disabled
                        if np.random.rand() < 0.75:
                            newCon.disable()
                    matches = True
                    break
            if not matches:
                # Disjoint gene
                newCon = copy(con1)
            child.connectionList.append(newCon)
        # Have a look at the disjoint and excess genes from parent2 (only if both parents have the same fitness)
        if sameFitness:
            for con2 in parent2.connectionList:
                # Be sure it is not a matching gene
                matches = False
                for con1 in parent1.connectionList:
                    if con1.innovationNumber == con2.innovationNumber:
                        matches = True
                        break
                if not matches:
                    newCon = copy(con2)
                    child.connectionList.append(newCon)

        # Make all the connection refer to the nodes of the child (otherwise, the reference is not shared)
        for con in child.connectionList:
            found = 0
            for node in child.nodeList:
                if node == con.nodeIn:
                    con.nodeIn = node
                    found += 1
                if node == con.nodeOut:
                    con.nodeOut = node
                    found += 1
                if found == 2:
                    break

        return child


    # ------------------------------------------------------------------------------------------------------------------
    # Evaluation
    def evaluate(self, inputs, show = False):
        """
        Evaluate the net !


        Params
        ----------
        inputs : value of the sensors

        Algorithm
        ----------
        Init the values of the sensors
        Make a queue q
        Add the sensors to q with a 0 priority
        While q is not empty :
            Get a node n from q based on priority (highest first)
            Evaluate n
            Reset its input value
            For t in target of n:
                Add the value of n to the input value of t
                If t hasn't been used yet :
                    If ALL the inputs of t have been used :
                        Add t to q with a priority of 1
                    Else :
                        Add t to q with a priority of -1
        Reset the 'used' counter
        """
        # Init the input value of the sensors
        for i in range(self.sensor - self.biasActive):
            self.nodeList[i].inputValue = inputs[i]
        if self.biasActive:
            self.nodeList[self.sensor -1].inputValue = 1
        # Make a queue (Highest priority first)
        queue = PriorityQueue()
        # Keep track of the activated nodes
        activated = []
        # Add the sensors to the queue with a priority of 0
        for sensorNode in self.nodeList[:self.sensor]:
            priority = 0
            queue.put(sensorNode, priority)
        if show :
            print('Starting queue : ', queue.queue)

        while not queue.empty():
            node = queue.get()
            if show:
                print('Node : ', node.number)
                print('Input value : ', node.inputValue)
            node.evaluate()  # Also resets its input value
            activated.append(node)
            if show:
                print('Node output', node.outputValue)
            # Get the nodes connected to the selected node
            connected = []
            for connection in self.connectionList:
                if connection.enabled and connection.nodeIn == node:
                    connected.append((connection.nodeOut, connection.weight))
            # Go through each of them
            for target, weight in connected:
                target.inputValue += node.outputValue*weight
                if show:
                    print('Target : ', target.number)
                    # print('Value : ', node.outputValue*weight)
                if not target in activated:
                    # See if all its 'feeders' have been used
                    allFeedersUsed = True
                    for connection in self.connectionList:
                        if connection.enabled and connection.nodeOut == target:
                            if not connection.nodeIn in activated:
                                allFeedersUsed = False
                                if show:
                                    print(connection.nodeIn)
                    if allFeedersUsed:
                        priority = 1
                    else:
                        priority = -1
                    queue.put(target, priority)
                    if show:
                        print('Queue :', queue.queue)

        outputList = []
        for outputNode in self.nodeList[self.sensor:self.sensor+self.output]:
            outputList.append(outputNode.outputValue)

        return outputList


    def clearNodes(self):
        """
        Clear the input value of the nodes
        """
        for node in self.nodeList:
            node.inputValue = 0

    # ------------------------------------------------------------------------------------------------------------------
    # Innovation history
    @staticmethod
    def getInnovationNumber(nodeIn, nodeOut):
        """
        Get an innovation number (2 innovations that are identical have the same number)
        """
        # If two innovations are the same, they have the same number
        for innovation in Genome.innovationHistory:
            if innovation.sameAs(nodeIn, nodeOut):
                return innovation.number
        # Else, make a new number and add it as reference in the list
        newInnovation = History(nodeIn, nodeOut)
        Genome.innovationHistory.append(newInnovation)
        return newInnovation.number


    # ------------------------------------------------------------------------------------------------------------------
    # Copy
    def __copy__(self):
        """
        Make a copy of the genome
        """
        sensor = self.sensor - int(self.biasActive)
        clone = Genome(sensor, self.output, bias = self.biasActive, initState = 'none')
        self.sensor = self.sensor
        self.output = self.output
        clone.nodeList = []
        for node in self.nodeList:
            clone.nodeList.append(copy(node))
        clone.connectionList = []
        for con in self.connectionList:
            clone.connectionList.append(copy(con))
        clone.rawFitness = self.rawFitness
        clone.sharedFitness = self.sharedFitness
        return clone


    # ------------------------------------------------------------------------------------------------------------------
    # Drawing
    def draw(self):
        """
        Draw the net
        """
        # Have a graph
        graph = Digraph('Network', format='svg')
        # Make it go from left to the right
        graph.attr(rankdir='LR')
        # Make sure the nodes appear in layer
        for node in self.nodeList:
            # Give color to the nodes
            if node.kind == 'sensor':
                # Sensor : yellow
                color = "0.166 1 0.5"
                label = node.name
                graph.node(str(node.name), color=color, shape='circle', rank='min', tooltip = str(node.name))
            elif node.kind == 'output':
                # Output : blue
                color = "0.66 1 0.5"
                graph.node(str(node.name), color=color, shape='circle', rank='max', tooltip = str(node.name))
            else:
                # Hidden : cyan
                color = "0.528 1 0.5"
                graph.node(str(node.name), label = '', color=color, shape='circle', width = '0.3', tooltip = str(node.name))
        # graph.node(str('Invisible'), color=color, shape='circle', rank=rank, style='invis')  # Should prevent ex-aequo between hidden and output
        for i in range(1, self.sensor):
            # Make some invisible edges that are ordering the nodes
            graph.edge(str(self.nodeList[i-1].name), str(self.nodeList[i].name), style='invis')
        for i in range(self.sensor+1, self.sensor + self.output):
            # Make some invisible edges that are ordering the nodes
            graph.edge(str(self.nodeList[i - 1].name), str(self.nodeList[i].name), style='invis')
        # Prevent hidden nodes to be at the same level as the output nodes
        for node in self.nodeList[self.sensor+self.output:]:
            for out in self.nodeList[self.sensor:self.output]:
                graph.edge(str(node.name), str(out.name), style='invis')
        # Re-align the sensor nodes
        nodes = ''
        for node in self.nodeList[:self.sensor]:
            nodes += str(node.name) + ' '
        # Here we write some raw graphviz text because I don't think we can do this with only python commands
        graph.body.append('\t{rank = same; ' + nodes + '; rankdir=LR;}\n\t')
        # Re-align the output nodes
        nodes = ''
        for node in self.nodeList[self.sensor:self.sensor+self.output]:
            nodes += str(node.name) + ' '
        # Here we write some raw graphviz text because I don't think we can do this with only python commands
        graph.body.append('\t{rank = same; ' + nodes + '; rankdir=LR;}\n\t')

        # Draw the connections
        for connection in self.connectionList:
            # Only draw the enabled ones
            if connection.enabled and connection.weight != 0:
                #            if connection.enabled:
                # Make some fancy colors based on weight
                if connection.weight < 0:
                    color = "0 " + str(0.5 - connection.weight/2) + " 0.7"
                else:
                    color = "0.3333 " + str(0.5 + connection.weight/2) + " 0.7"
                # graph.edge(str(connection.nodeIn.name), str(connection.nodeOut.name), color=color,
                #            edgetooltip=str(connection.weight), label = str(connection.innovationNumber), penwidth = str(abs(connection.weight*1.5)+0.2))
                graph.edge(str(connection.nodeIn.name), str(connection.nodeOut.name), color=color,
                           edgetooltip=str(connection.weight), penwidth=str(abs(connection.weight * 1.5) + 0.2))

        # Finally, draw it !
        graph.render(view = True)
        return graph