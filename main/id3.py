import math
class ID3:
	# Hàm khởi tạo
	def __init__(self, pathToData,pathToNames,pathToTest, pathToCheck):
		self.filePathToData = pathToData # đường dẫn đến file data (chứa các bản ghi)
		self.filePathToNames = pathToNames # đường dẫn đến file names (chứa thuộc tính và nhãn)
		self.filePathToTest = pathToTest  # đường dẫn đến file test
		self.data = []    # mảng các bản ghi data
		self.classes = [] # mảng các nhãn
		self.test = []
		self.numAttributes = -1  # so luong thuoc tinh (6)
		self.attrValues = {}  # mảng chứa thuộc tính và các giá trị tương ứng của nó
		self.attributes = []	# mảng cac thuoc tinh
		self.tree = None
		self.order = []
		self.filePathToCheck = pathToCheck
		self.check = []
		self.f1score = []

	# lay data từ các file data, names
	def fetchData(self):
		with open(self.filePathToNames, "r") as file:
			classes = file.readline()
			self.classes = [x.strip() for x in classes.split(",")]
			#add attributes
			for line in file:
				[attribute, values] = [x.strip() for x in line.split(":")]
				values = [x.strip() for x in values.split(",")]
				self.attrValues[attribute] = values
		self.numAttributes = len(self.attrValues.keys())
		self.attributes = list(self.attrValues.keys())
		with open(self.filePathToData, "r") as file:
			for line in file:
				row = [x.strip() for x in line.split(",")]
				if row != [] or row != [""]:
					self.data.append(row)
		with open(self.filePathToTest, "r") as file:
			for line in file:
				row = [x.strip() for x in line.split(",")]
				if row != [] or row != [""]:
					self.test.append(row)
		with open(self.filePathToCheck, "r") as file:
			for line in file:
				row = [x.strip() for x in line.split(",")]
				if row != [] or row != [""]:
					self.check.append(row)
		self.f1score = [[] for a in range(len(self.classes))]
	# In ra cay quyet dinh
	def printTree(self):
		self.printNode(self.tree)

	def printNode(self, node, indent=""):
		if not node.isLeaf:
			if node.threshold is None:
				#discrete
				for index,child in enumerate(node.children):
					if child.isLeaf:
						if child.label == "null":
							child.label = node.value
						print(indent + node.label + " = " + node.order[index] + " : " + child.label)
					else:
						print(indent + node.label + " = " + node.order[index] + " : ")
						self.printNode(child, indent + "	")
			else:
				#numerical
				leftChild = node.children[0]
				rightChild = node.children[1]
				if leftChild.isLeaf:
					print(indent + node.label + " <= " + str(node.threshold) + " : " + leftChild.label)
				else:
					print(indent + node.label + " <= " + str(node.threshold)+" : ")
					self.printNode(leftChild, indent + "	")

				if rightChild.isLeaf:
					print(indent + node.label + " > " + str(node.threshold) + " : " + rightChild.label)
				else:
					print(indent + node.label + " > " + str(node.threshold) + " : ")
					self.printNode(rightChild , indent + "	")

	# tạo cây quyết định
	def generateTree(self):
		self.tree = self.recursiveGenerateTree(self.data, self.attributes)

	# vòng lặp trả về các node để các information gain đạt gtln
	def recursiveGenerateTree(self, curData, curAttributes):
		if(len(curData)!=0):
			allSame = self.allSameClass(curData)
		if len(curData) == 0:
			return Node(True, "null", None,None,0)
		elif allSame is not False:
			return Node(True, allSame, None,None,0)
		elif len(curAttributes) == 0:
			majClass = self.getMajClass(curData)
			return Node(True, majClass, None,None)
		else:
			(best,best_threshold,splitted,best_order,value) = self.splitAttribute(curData, curAttributes)
			remainingAttributes = curAttributes[:]
			remainingAttributes.remove(best)
			node = Node(False, best, best_threshold,best_order,value)
			node.children = [self.recursiveGenerateTree(subset, remainingAttributes) for subset in splitted]
			return node

	# trả về nhãn chứa nhiều bản ghi nhất trong tập dữ liệu
	def getMajClass(self, curData):
		freq = [0]*len(self.classes)
		print(self.classes)
		for row in curData:
			index = self.classes.index(row[-1])
			freq[index] += 1
		maxInd = freq.index(max(freq))
		return self.classes[maxInd]

	# check các bản ghi trong mảng data có cùng 1 nhãn không, nếu có thì trả về nhãn đó
	def allSameClass(self, data):
		for row in data:
			if row[-1] != data[0][-1]:
				return False
		return data[0][-1]

	# hàm thực hiện chọn thuộc tính (node) có information gain cao nhất
	def splitAttribute(self, curData, curAttributes):
		splitted = []
		maxEnt = -1*float("inf")
		best_attribute = -1
		best_threshold = None
		for attribute in curAttributes:
			indexOfAttribute = self.attributes.index(attribute)  # chỉ mục của attribute trong mảng attributes
			valuesForAttribute = self.attrValues[attribute]
			subsets = [[] for a in valuesForAttribute]  # khởi tạo các mảng rỗng tương ứng với từng gtri thuộc tính
			# sắp xếp các bản ghi vào các giá trị tương ứng của 1 điểm (thuộc tính)
			for row in curData:
				for index in range(len(valuesForAttribute)):
					if row[indexOfAttribute] == valuesForAttribute[index]: # nếu giá trị của thuộc tính của 1 bản ghi bằng 1 gt trong mảng gt của thuộc tính đó
						subsets[index].append(row) # thêm bản ghi vào mảng của gt thuộc tính tương ứng
						break
			e = self.gain(curData, subsets)
			if e > maxEnt:
				maxEnt = e
				splitted = subsets
				best_attribute = attribute
				best_threshold = None
				best_order=valuesForAttribute
		values = [0 for i in self.classes]
		for i in range(len(splitted)):
			for d in splitted[i]:
				for c in self.classes:
					if d[-1] == c:
						values[self.classes.index(c)] +=1
		max = values[0]
		value = self.classes[0]
		for v in range(len(values)):
			if values[v] > max:
				max = values[v]
				value = self.classes[v]
		return (best_attribute,best_threshold,splitted,best_order,value)

	# hàm tính information gain
	def gain(self,unionSet, subsets):
		S = len(unionSet)
		impurityBeforeSplit = self.entropy(unionSet)
		weights = [len(subset)/S for subset in subsets]
		impurityAfterSplit = 0
		for i in range(len(subsets)):
			impurityAfterSplit += weights[i]*self.entropy(subsets[i])
		totalGain = impurityBeforeSplit - impurityAfterSplit
		return totalGain

	# tính entropy phân phối tại 1 node
	def entropy(self, dataSet):
		S = len(dataSet)
		if S == 0:
			return 0
		num_classes = [0 for i in self.classes] #khởi tạo mảng các phần tử 0 với số phần tử bằng số lớp nhãn
		for row in dataSet:
			classIndex = list(self.classes).index(row[-1]) # gán classIndex bằng chỉ mục của nhãn trong list nhãn
			num_classes[classIndex] += 1
		num_classes = [x/S for x in num_classes] # gán ptu trong mảng thành các gt xác suất tương ứng
		ent = 0
		for num in num_classes:
			ent += num*self.log(num)
		return ent*-1

	# hàm tính log
	def log(self, x):
		if x == 0:
			return 0
		else:
			return math.log(x,2)

	# hàm phân loại bản ghi, trả về nhãn phân loại
	def predict(self, node, input, stt):
		if node.isLeaf:
			print(node.label)
			if self.check[stt][-1] == node.label:
				print("true")
				self.f1score[self.classes.index(node.label)][self.classes.index(node.label)] += 1
			else:
				print("false - " + self.check[stt][-1])
				self.f1score[self.classes.index(self.check[stt][-1])][self.classes.index(node.label)] += 1

		else:
			indexOfAttribute = self.attributes.index(node.label)
			valuesForAttribute = self.attrValues[node.label]
			for v in range(len(valuesForAttribute)):
				if input[indexOfAttribute] == valuesForAttribute[v]:
					self.predict(node.children[v], input, stt)
					break

	# In ra kết quả phân loại
	def printValue(self):
		for i in range(len(self.classes)):
			self.f1score[i] = [0 for a in range(len(self.classes))]
		for t in range(len(self.test)):
			print(self.test[t])
			self.predict(self.tree, self.test[t], t)
		self.confusionMatrix()
		self.fmeasure()

	# in ra confusion matrix
	def confusionMatrix(self):
		print("__________Confusion Matrix__________")
		for i in range(len(self.classes)):
			print(self.classes[i], end="   ")
		print()
		for i in range(len(self.classes)):
			for j in range(len(self.classes)):
				print(self.f1score[j][i], end="      "),
			print()

	# tính và in ra precision, recall, f1-score, average f1
	def fmeasure(self):
		print("__________Precision__________")
		precision = [0 for a in range(len(self.classes))]
		for i in range(len(self.classes)):
			tong = 0
			for j in range(len(self.classes)):
				tong += self.f1score[i][j]
			precision[i] = round(self.f1score[i][i]/tong,3)
		for i in range(len(self.classes)):
			print(self.classes[i], end=": ")
			print(precision[i])
		print("__________Recall__________")
		recall = [0 for a in range(len(self.classes))]
		for i in range(len(self.classes)):
			tong = self.f1score[i][i]
			for j in range(len(self.classes)):
				if i!=j:
					tong += self.f1score[j][i]
			recall[i] = round(self.f1score[i][i] / tong, 3)
		for i in range(len(self.classes)):
			print(self.classes[i], end=": ")
			print(recall[i])
		print("__________F1-Score__________")
		fmeasure = [0 for a in range(len(self.classes))]
		for i in range(len(self.classes)):
			fmeasure[i] = round(2*precision[i]*recall[i] / (precision[i]+recall[i]), 3)
		for i in range(len(self.classes)):
			print(self.classes[i], end=": ")
			print(fmeasure[i])
		print("__________Average F1__________")
		total = 0
		totalClass = [0 for a in range(len(self.classes))]
		average = 0
		for i in range(len(self.classes)):
			for j in range(len(self.classes)):
				total += self.f1score[i][j]
				totalClass[i] += self.f1score[i][j]
		for i in range(len(self.classes)):
			average += (totalClass[i]/total)*fmeasure[i]
		print("Average F1: " + str(round(average,3)))

class Node:
	def __init__(self,isLeaf, label, threshold, order, value):
		self.label = label
		self.threshold = threshold
		self.isLeaf = isLeaf
		self.children = []
		self.order = order
		self.value = value