from math import e


def activationFunction(x):
    """
    Activation function used to evaluate a Node

    Params
    ----------
    x : (value)
    """
    return 1 / (1+e**(-4.9*x))


class Node:

    def __init__(self, identifier, kind='hidden', name = None):
        """
        Create a new node

        Params
        ----------
        number ((int, int)) : The id of the node
        kind (str) : Can be 'sensor', 'hidden', 'output'
        name (str) : name of the node
        """
        self.identifier = identifier
        self.number = identifier[0]
        self.kind = kind
        # Value used by evaluation
        self.inputValue = 0
        self.outputValue = 0
        # Name used by the graph
        if name is None:
            self.name = str(identifier[0]) + '.' + str(identifier[1])
        else:
            self.name = name

    def __repr__(self):
        """
        Defines how a node is shown in console
        """
        text = 'Node {}'.format(self.identifier)
        return '<{}>'.format(text)

    def __eq__(self, other):
        """
        Tell if 2 nodes are the same

        Params
        ----------
        other : (Node)
        """
        return self.identifier == other.identifier


    ## Evaluation ##
    def evaluate(self):
        """
        Evaluate the node (edit it's output value)
        """
        self.outputValue = activationFunction(self.inputValue)
        # Reset the input value
        self.inputValue = 0

    ## Copy ##

    def __copy__(self):
        """
        Copy the node
        """
        clone = Node(self.identifier, self.kind, self.name)
        return clone