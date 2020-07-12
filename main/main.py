
from id3 import ID3

c1 = ID3("../data/car.data", "../data/car.names")
c1.fetchData()
c1.preprocessData()
c1.generateTree()
c1.printTree()