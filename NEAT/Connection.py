import numpy as np
from copy import copy

class Connection:

    def __init__(self, nodeIn, nodeOut, weight, enabled, innovationNumber):
        """
        Make a new connection

        Params
        ----------
        nodeIn: The node it comes from (Node)
        nodeOut: The node it goes to (Node)
        weight: The weight (-1 to 1 / 'random')
        enabled: Say if the connection is enabled or not (bool)
        innovationNumber: (int)
        """
        self.nodeIn = nodeIn
        self.nodeOut = nodeOut
        if type(weight) == str and weight == 'random':
            self.weight = 2*np.random.rand() - 1
        else:
            self.weight = weight
        self.enabled = enabled
        self.innovationNumber = innovationNumber

    def __repr__(self):
        """
        Define how a connection is seen in the console
        """
        if self.enabled:
            enabledText = 'enabled'
        else:
            enabledText = 'disabled'
        text = 'Connection {} - {} to {} - weight {} - {}'.format(self.innovationNumber,
                                                                  self.nodeIn.number,
                                                                  self.nodeOut.number,
                                                                  self.weight,
                                                                  enabledText)
        return '<{}>'.format(text)


    def disable(self):
        """
        Disable the connection
        """
        self.enabled = False


    ## Copy ##
    def __copy__(self):
        """
        Copy the connection
        """
        clone = Connection(copy(self.nodeIn), copy(self.nodeOut), self.weight, self.enabled, self.innovationNumber)
        return clone