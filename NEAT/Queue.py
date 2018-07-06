class PriorityQueue:

    def __init__(self):
        """
        Make a PriorityQueue (a list with priority)
        """
        # self.queue will contain elements : (item, priority)
        self.queue = []
        self.priority = {}

    def put(self, item, priority):
        """
        Put an item in the queue

        Params
        ----------
        item : (anything)
        priority : (int)
        """
        if item in self.queue:
            self.queue.remove(item)
        self.queue.append(item)
        self.priority[str(item)] = priority

    def get(self):
        """
        Return the item with the highest priority
        If two elements have the same priority, the oldest is chosen
        """
        priorityMax = self.priority[str(self.queue[0])]
        index = 0
        for i, item in enumerate(self.queue[1:]):
            if self.priority[str(item)] > priorityMax:
                priorityMax = self.priority[str(item)]
                index = i+1
        return self.queue.pop(index)

    def empty(self):
        """
        Tell if the queue is empty or not
        """
        return len(self.queue) == 0


