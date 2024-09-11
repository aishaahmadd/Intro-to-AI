#CSC158: Cannibals and Missionaries
#Task: get everything to the other side of the river.
#Restrictions:
#1. There must be more missionaries on both sides of the river
#2. There is space for max 2 persons on the boat

from collections import deque
from queue import PriorityQueue

class State(object):

	#State: (canLeft, missLeft, boatPos, canRight, missRight, action)
	def __init__(self, canLeft, missLeft, boatPos, canRight, missRight, action):
		self.canLeft = canLeft
		self.missLeft = missLeft
		self.boatPos = boatPos
		self.canRight = canRight
		self.missRight = missRight
		self.action = action


	def __str__(self):
		return "%s, %s %s %s %s %s" %(self.action,self.canLeft, self.missLeft, self.boatPos, self.canRight, self.missRight)

	def is_valid(self):
		if self.missLeft < 0 or self.missLeft > 3:
			return False
		if self.canLeft < 0 or self.canLeft > 3:
			return False
		if self.missRight < 0 or self.missRight > 3:
			return False
		if self.canRight < 0 or self.canRight > 3:
			return False
		if self.missLeft < self.canLeft and self.missLeft > 0:
			return False
		# Check for the other side
		if self.missRight < self.canRight and self.missRight > 0 :
			return False
		
		return True

	def is_goal(self):
		return self.missLeft == 0 and self.canLeft == 0 and self.boatPos == 0

	def gen_successors(self):
		operator = -1 #removing missionaries or cannibals
		action = ""
		if self.boatPos == 0:   #boat_position = 0,  boat is on the right of the river
			operator = 1       			  #boat_position = 1, boat is on the left of the river
			action = ""

		for can in range(3): #num cannibals that can be moved by the boat
			for miss in range(3): #num missionaries that can be moved by the boat
				
				from_action = "%s Cannibal %s Missionary %s" %(can, miss, action)
				#accounts for if 0-2 missionaries/cannibals are being removed or added to a side of the river
				new_state = State(self.canLeft + operator*can, self.missLeft + operator*miss, self.boatPos + operator*1, \
					   self.canRight - operator*can, self.missRight - operator*miss, from_action)
				if can+miss >= 1 and can+miss <= 2 and new_state.is_valid():
					yield new_state
	
	def Astar_gen_successors(self,depth):
		operator = -1
		action = ""
		if self.boatPos == 0:  # if boatPos = 0, boat is on the right of river
			operator = 1  		   # if  boatPos = 1, boat is on the left of rive
			action = ""
			
		successors = []
		for can in range(3):
			for miss in range(3):
				from_action = "%s Cannibal %s Missionary %s" % (can, miss, action)
				new_state = State(self.canLeft + operator * can, self.missLeft + operator * miss, self.boatPos + operator * 1,
                                  self.canRight - operator * can, self.missRight - operator * miss, from_action)
				if can + miss >= 1 and can + miss <= 2 and new_state.is_valid():
					successors.append(new_state)
		return sorted(successors, key=self.estimated_cost_sorting(depth))
	
	def estimated_cost_sorting(self,depth):
		def get_estimated_cost(state):
			return state.estimated_cost(depth)
		return get_estimated_cost
	
	def estimated_cost(self, depth):
        # Estimated cost (f) = actual cost + heuristic cost
		return depth + get_heuristic(self)



class Node(object):
	def __init__(self, parent, state, depth):
		self.parent = parent
		self.state = state
		self.depth = depth

	def __str__(self):
		return self.state.__str__()
	def __lt__(self, other):
        #comparing nodes based on their total cost
		return self.total_cost() < other.total_cost()
	
	def total_cost(self):
		return self.depth + get_heuristic(self.state)
	
	def successors(self):
		for state in self.state.gen_successors():
			yield Node(parent=self, state=state, depth=self.depth+1)
	
	def Astar_successors(self,depth):
		for state in self.state.Astar_gen_successors(depth):
			yield Node(parent=self, state=state, depth=self.depth+1)

	def solution_path(self):
		print ("Solution path:")
		solution = []
		node = self
		solution.append(node)
		while node.parent is not None:
			solution.append(node.parent)
			node = node.parent
		solution.reverse()
		return solution


def Breadth_First_Search(root):

	queue = deque([root])
	visitedList = []
	while True:
		if not queue:
			return None
		node = queue.popleft()
		if str(node) in visitedList:
			continue
		visitedList.append(str(node))
		if node.state.is_goal():
			print("\nBFS Results:\n")
			print(len(visitedList), "nodes visited")
			solution = node.solution_path()
			return solution
		for successor in node.successors():
			queue.append(successor)

def Depth_First_Search(root):

	stack = [root]
	visitedList = []
	while True:
		if not stack:
			return None
		node = stack.pop()
		if str(node) in visitedList:
			continue
		visitedList.append(str(node))
		if node.state.is_goal():
			print("\nDFS Results:\n")
			print(len(visitedList), "nodes visited")
			solution = node.solution_path()
			return solution
		for successor in node.successors():
			stack.append(successor)

def Iterative_Deepening_DFS(root):
    max_depth = 0
    while True:
        result = Depth_Limited_Search(root, max_depth)
        if result is not None:
            print("\nIDS Results:\n")
            print(len(result[1]), "nodes visited")
			#results[0] = node of the solution
            return result[0].solution_path()
        max_depth += 1

def Depth_Limited_Search(root, max_depth):
    stack = [(root, 0)] #stack of tuples (node, depth)
    visitedList = []
    while len(stack) != 0:
        node, depth = stack.pop()
        if str(node) in visitedList:
            continue
        visitedList.append(str(node))
        if node.state.is_goal():
            return node, visitedList
        if depth < max_depth:
            for successor in node.successors():
                stack.append((successor, depth + 1))
    return None

def Astar_Search(root):
	fringe = PriorityQueue()
	fringe.put((0, root))  
	visitedList = []
	while not fringe.empty():
		depth, node = fringe.get()
		if str(node) in visitedList:
			continue
		visitedList.append(str(node))
		if node.state.is_goal():
			print("\nA* Search Results:\n")
			solution = node.solution_path()
			print(len(visitedList), "nodes visited")
			return solution
		for successor in node.Astar_successors(depth):
			h_cost = get_heuristic(successor.state)
			total_cost = successor.depth + h_cost
			fringe.put((total_cost, successor)) 
	return None

def get_heuristic(state):
    # num displaced missionaries and cannibals
    heuristic = abs(state.missLeft - state.canLeft) + abs(state.missRight - state.canRight)
    return heuristic


def main():
	initial_state = State(3, 3, 1, 0, 0, "Initial State")
	root = Node(parent=None, state=initial_state, depth=0)
	
	bfsSoln = Breadth_First_Search(root)
	for state in bfsSoln:
		print(state)
	print (len(bfsSoln), "nodes in solution")

	dfsSoln = Depth_First_Search(root)
	for state in dfsSoln:
		print(state)
	print (len(dfsSoln), "nodes in solution")

	idsSoln = Iterative_Deepening_DFS(root)
	for state in idsSoln:
		print(state)
	print (len(idsSoln), "nodes in solution")
	
	aStarSoln = Astar_Search(root)
	for state in aStarSoln:
		print(state)
	print (len(aStarSoln), "nodes in solution")


if __name__ == '__main__':
	main()