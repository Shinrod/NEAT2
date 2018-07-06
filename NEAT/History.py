class History:
    """
    Piece of history (used to give an innovation number to connections
    """

    innovationNumber = 0

    def __init__(self, nodeIn, nodeOut):
        """
        Make a new save

        Params
        ----------
        genome : The genome in which the innovation happened (Genome)
        connection : The innovation (Connection)
        """
        self.nodeIn = nodeIn
        self.nodeOut = nodeOut
        History.innovationNumber += 1
        self.number = History.innovationNumber

    def __repr__(self):
        """
        Defines how an piece of history is represented in console
        """
        text = 'History {] - {} to {}'.format(self.number, self.nodeIn, self.nodeOut)
        return '<{}>'.format(text)

    def sameAs(self, nodeIn, nodeOut):
        """
        Check if two innovations are the same

        Params
        ----------
        connection : (Connection)
        genome: (Genome)
        """
        if self.nodeIn == nodeIn and self.nodeOut == nodeOut:
            return True
        else:
            return False