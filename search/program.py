# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from .core import CellState, Coord, Direction, MoveAction
from .utils import render_board
import heapq
import math

# Possible directions that the red frog can move in
DIRECTIONS = [Direction.Down, Direction.DownRight, Direction.DownLeft,
              Direction.Left, Direction.Right]

# The heuristic used assumes the shortest possible path would be to consecutively
# hop over blue monkeys all the way to the bottom row, this is an admissable
# heuristic
def heuristic(redRow, board):
    return (math.ceil((getBottomRow(board) - redRow)/2))
    

# Find the initial Coord of the red frog
def find_initial_red(board):
    for coord, state in board.items():
        if state == CellState.RED:
            return coord

# Check if the red frogs position is in the bottom row
def is_goal(pos, board):
    if pos.r == getBottomRow(board):
        return True
    
# Get the number of the bottom row based on the board size
def getBottomRow(board):
    return len(set(coord.r for coord in board)) - 1

# Get the number of the right row based on the board size
def getRightRow(board):
    return len(set(coord.c for coord in board)) - 1


# Obtain the possible future nodes based on the current node
# Returns the move, the future board, and the future position of the red frog
def get_neighbours(board, pos):

    # Contains tuples of move, nextBoard, and nextPos
    neighbours = [] 

    for direction in DIRECTIONS:
            nextBoard, nextPos = apply_move(board, pos, direction)
            move = MoveAction(pos, direction)

            # If the move is a valid move, add it as a possible neighbour
            if nextBoard is not None and nextPos is not None:
                neighbours.append((move, nextBoard, nextPos))
                # print(move, nextPos)
                # print(render_board(nextBoard, ansi=True))  
    return neighbours

# Attempts to move the red frog in the given direction
# Either returns a None tuple if the move is invalid or a tuple of the next board 
# and red frog position if the move is valid
def apply_move(board, pos, direction):
    nextBoard = board.copy()

    # The red frog is moving off the current pos, so delete the cell state
    if nextBoard[pos] == CellState.RED:
        del nextBoard[pos]

    # Calculate the next position of the red frog
    nextR = pos.r+direction.r
    nextC = pos.c+direction.c

    # Check if the future position is within the boundaries of the board
    if not (0 <= nextR < getRightRow(nextBoard)) or not (0 <= nextC < getBottomRow(nextBoard)):  
        return (None, None)
    
    # Wrap the next position in a coordinate (given it is valid)
    nextPos = Coord(pos.r+direction.r, pos.c+direction.c)

    # print(nextPos.r, nextPos.c)
    # print(render_board(nextBoard, ansi=True))

    # Check if the next position is an empty CellState (e.g., not a lilypad nor blue frog)
    if nextPos not in nextBoard:
        return (None, None)

    # If the next position is a lilypad, it is a valid move
    elif nextBoard[nextPos] == CellState.LILY_PAD:
        nextBoard[nextPos] = CellState.RED
        return (nextBoard, nextPos)
    
    # If the next position is a blue frog, check if the red frog can jump over it 
    elif nextBoard[nextPos] == CellState.BLUE:
        # Check that we are in the spot where the red frog was removed
        # and not just jumping over several blue frogs 
        if (pos not in nextBoard):
            # Simply recall this function and check the CellState after the frog
            # if there is a lilypad, it will just return that position, if not
            # it returns None
            return apply_move(nextBoard, nextPos, direction)

def search(
    board: dict[Coord, CellState]
) -> list[MoveAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `CellState` instances which can be one of
            `CellState.RED`, `CellState.BLUE`, or `CellState.LILY_PAD`.
    
    Returns:
        A list of "move actions" as MoveAction instances, or `None` if no
        solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))
    

    # PLAN:
    # We need a priority queue for the search. Each time the node
    # is popped, we expand the possible solutions (there can only be 5 at most)
    # and run them through the heuristic, then respectively place them in 
    # the priority queue in order. the value is based on the amount of moves
    # taken to get there + the shortest possible amount of moves that could
    # result in a solution (aka if the frog hopped its way over frogs to the 
    # bottom row)

    # Implement PQ using min-heap?

    # For every node in the PQ, we need to store: the board of that state, 
    # location of red, the path it took to get there (as a list of MoveActions), 
    # the amount of steps it took to get to that state, and the final A* cost 
    # (which is the steps to get there  + the heuristic estimate to get
    # to the goal)

    # Also need to store visited nodes, so they aren't re-visited 

    # Note: the heuristic value doesn't actually need to be stored :P


    # So from start to finish: 
    # Locate the initial position of the red frog (DONE)
    # Initialise the PQ
    # Add that initial position to the PQ with its value as
    # the total cost so far (0) plus the estimated heuristic (which always starts as
    # 4) assuming a 8x8 grid
    # Initialise the visited set
    # Then while the PQ is not empty:
    #   pop the first node from the PQ, 
    #   is it the goal? if so END
    #   add to visited set
    #   expand all it's neighbours
    #   if NOT visited, and chuck em in the PQ based on their cost (1) +
    # heuristic


    # Our code:

    # Initial key info about the red frog
    initialPos = find_initial_red(board) 
    initialSteps = 0
    initialHeuristic = heuristic(initialPos.r, board)
    initialCost = initialSteps + initialHeuristic
    initialPath = []


    # Initialise the Priority Queue (PQ)
    PQ = []

    # Python's heapq automatically organizes based on the first element which is the cost
    # The PQ contains: the cost (steps + heuristic), the steps to get there,
    # the red frog position, the board at that state, and the path to get there
    heapq.heappush(PQ, (initialCost, initialSteps, initialPos, 
                        board, initialPath))
    
    # Store the nodes visited to ignore duplicates
    # idk if this is needed maybe this is the problem
    # visited = set()

    while PQ:
        # Expand the node, 
        cost, steps, pos, board, path = heapq.heappop(PQ)

        # Is this node at the bottom row?
        if is_goal(pos, board):
            return path
        
        # For every neighbour, obtain the MoveAction, the future board,
        # and the future position of the red frog
        for move, nextBoard, nextPos in get_neighbours(board, pos):
            # Increment step count, and calculate the new cost based on that step
            # count and the estimated heuristic
            nextSteps = steps + 1
            nextCost = nextSteps + heuristic(nextPos.r, board)

            # Add this to the PQ as generated nodes
            heapq.heappush(PQ, (nextCost, nextSteps, nextPos, nextBoard, 
                                path + [move]))
    # If PQ is empty it means no solution
    return None


    # ignore this:
    return [
        MoveAction(Coord(0, 5), [Direction.Down]),
        MoveAction(Coord(1, 5), [Direction.DownLeft]),
        MoveAction(Coord(3, 3), [Direction.Left]),
        MoveAction(Coord(3, 2), [Direction.Down, Direction.Right]),
        MoveAction(Coord(5, 4), [Direction.Down]),
        MoveAction(Coord(6, 4), [Direction.Down]),
    ]
