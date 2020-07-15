
from id3 import ID3

c1 = ID3("../data/car.data", "../data/car.names", "../data/test.data", "../data/test2.data")
c1.fetchData()
c1.generateTree()
c1.printTree()