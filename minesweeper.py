import itertools
import random


class Minesweeper():

# Minesweeper standard game logic
    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # create an empty area with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add randomly a number of mines
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True
        self.mines_found = set()

    def mine_field(self, cell):
        i, j = cell
        return self.board[i][j]


#The number of mines within one row and column of a given cell are here given back
# But the cell itself is not included
    def close_mines(self, cell):

        # Keep count of close mines
        count = 0

        # Loop over all cells within one row and column and ignore cell itself and then update the count
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

# Look if all mines have been found
    def won(self):
        return self.mines_found == self.mines



# Logical statement about a Minesweeper game
# This class consists of a set of cells and a count of all fields that are mines
class Mineslogic():

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    # All known mines are returned here
    def known_mines(self):
        mines = self.cells
        # Any time the number of cells is equal to the count, we know that all of that sentence's cells must be mines
        if len(self.cells) == self.count:
            return mines
        return None

    # Each time we have a sentence whose count is 0, we know that all the surrounding cells are safe
    # All Cells known to be safe are returned here
    def known_safe_cells(self):
        if self.count == 0:
            return self.cells
        return None

    # If a cell is known to be a mine, update here all internal knowledge representation
    def eval_mines(self, cell):
        newCells = set()
        for item in self.cells:
            if item != cell:
                newCells.add(item)
            else:
                self.count -= 1
        self.cells = newCells

    # If a cell is known to be safe, update here all internal knowledge representation
    def eval_safe_cell(self, cell):
        newCells = set()
        for item in self.cells:
            if item != cell:
                newCells.add(item)
        self.cells = newCells
        

# Minesweeper automated game with AI-agent
class MinesweeperAI():

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width

        # Keep track of clicked cells
        self.moves_made = set()
        # Keep track of known safe cells or known mines
        self.mines = set()
        self.safes = set()
        # List of all logical statements about the game known to be true
        self.knowledge = []

    # Tag a cell as a mine and update all knowledge
    def eval_mines(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.eval_mines(cell)

    # Tag a cell as safe and update all knowledge
    def eval_safe_cell(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.eval_safe_cell(cell)

    # Add and update knowledge when we know how many neighboring cells have mines
    def update_knowledge(self, cell, count):

        # Mark cell as a safe move when move has been made without finding a mine and add to moves_made
        self.eval_safe_cell(cell)
        self.moves_made.add(cell)

        # Add a new logical statement to the AI-agent knowledge, based on the value of cell and count
        neighbors, count = self.cell_neighbors(cell, count)
        mineslogic = Mineslogic(neighbors, count)
        self.knowledge.append(mineslogic)

        # If additional cells can be concluded, based on the AI-agent knowledge,
        # add additional logical statements to mark the additional cells as safe or as mines
        new_inferences = []
        for s in self.knowledge:
            if s == mineslogic:
                continue
            elif s.cells.issuperset(mineslogic.cells):
                put_new = s.cells-mineslogic.cells
                # Known safes
                if s.count == mineslogic.count:
                    for safeFound in put_new:
                        self.eval_safe_cell(safeFound)
                # Known mines
                elif len(put_new) == s.count - mineslogic.count:
                    for mineFound in put_new:
                        self.eval_mines(mineFound)
                # Known inference
                else:
                    new_inferences.append(
                        Mineslogic(put_new, s.count - mineslogic.count)
                    )
            elif mineslogic.cells.issuperset(s.cells):
                put_new = mineslogic.cells-s.cells
                # Known safes
                if s.count == mineslogic.count:
                    for safeFound in put_new:
                        self.eval_safe_cell(safeFound)
                # Known mines
                elif len(put_new) == mineslogic.count - s.count:
                    for mineFound in put_new:
                        self.eval_mines(mineFound)
                # Known inference
                else:
                    new_inferences.append(
                        Mineslogic(put_new, mineslogic.count - s.count)
                    )

        self.knowledge.extend(new_inferences)
        self.del_duplicates()
        self.final_knowledge()

    # A safe cell is returned here, so the AI-agent can choose it in the field
    # The move must not have already been made and must be known to be safe.
    # Self.safes, Self.moves made, and Self.mines may all be used by this function, but none of their contents should be modified.
    def do_safe_move(self):
        # Stores a duplicate of safe moves in order not to modify the value
        possible_safe_moves = self.safes.copy()
        # Removes moves made from possible_safe_moves
        possible_safe_moves -= self.moves_made

        if len(possible_safe_moves) == 0:
            return None
        # Removes an arbitrary safe move from the possible_safe_moves set
        safe_move = possible_safe_moves.pop()
        return safe_move

    # Make a randomly move that are not known to be a mine and have not been chosen already
    def do_move_randomly(self):
        # Stores random moves
        random_moves = set()

        # Generates a random move within the bounds of the board
        i = random.randrange(self.height)
        j = random.randrange(self.width)
        random_move = (i, j)

        # If the random move wasn't already made and it is not known to be a mine, add it to the random moves set.
        if random_move not in self.moves_made and random_move not in self.mines:
            random_moves.add(random_move)

        # If there are no random moves possible
        if len(random_moves) == 0:
            return None

            # Removes an arbitrary random_move from the random_moves set
        random_move = random_moves.pop()
        return random_move
               
    def cell_neighbors(self, cell, count):
        i, j = cell
        neighbors = []
        for row in range(i-1, i+2):
            for col in range(j-1, j+2):
                if (row >= 0 and row < self.height) \
                and (col >= 0 and col < self.width) \
                and (row, col) != cell \
                and (row, col) not in self.safes \
                and (row, col) not in self.mines:
                    neighbors.append((row, col))
                if (row, col) in self.mines:
                    count -= 1
        return neighbors, count

    def del_duplicates(self):
        unique_knowledge = []
        for s in self.knowledge:
            if s not in unique_knowledge:
                unique_knowledge.append(s)
        self.knowledge = unique_knowledge

    def final_knowledge(self):
        latest_knowledge = []
        for s in self.knowledge:
            latest_knowledge.append(s)
            if s.known_mines():
                for mineFound in s.known_mines():
                    self.eval_mines(mineFound)
                latest_knowledge.pop(-1)
            elif s.known_safe_cells():
                for safeFound in s.known_safe_cells():
                    self.eval_safe_cell(safeFound)
                latest_knowledge.pop(-1)
        self.knowledge = latest_knowledge
