""""""
''' *args and **kwargs '''
#def f(*args, **kwargs):
#    print('args', args)
#    print('**kwarg', kwargs)

''' Does 'for' impact the list it takes as argument ? -> No '''
#l = [0, 1, 2]
#for i in l[::-1]:
#    l.append(i)
#print(l)

''' Can we check if 1 < x < 2 ? -> Yes '''
#value = 2.5
#print(1 < value < 2)


''' Can self.staticmethod(a1, a2) evaluate without taking part of self ? -> Yes'''
# class Test:
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def hey(word):
#         print(word)
#
# t = Test()
# t.hey('Hello')


''' class stuff '''
# # class Test:
# #
# #     def __init__(self):
# #         self.list = [1]
#
# from queue import PriorityQueue
#
# queue = PriorityQueue()
# queue.put((0, 'hello'))

''' Plot test '''
import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)
x = np.arange(10)
table = np.arange(5).reshape((5,1))+np.zeros((5,10))+x.reshape((10,))
ax.plot(x, table.transpose())

