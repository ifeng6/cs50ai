import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1
        self.moves_made.add(cell)

        # 2
        self.mark_safe(cell)

        # 3
        neighbours = set()
        for a in range(-1, 2, 1):
            for b in range(-1, 2, 1):
                i, j = cell
                i += a
                j += b
                # ignore self
                if (i, j) == cell:
                    continue
                # check row and column
                if 0 <= i < self.height and 0 <= j < self.width:
                    # check that the state of the cell is undetermined
                    neighbour = (i, j)
                    # neighbour has already been explored
                    if (neighbour in self.moves_made) or (neighbour in self.safes):
                        continue
                    # neighbour is a mine --> exclude it and decrease count
                    if neighbour in self.mines:
                        count -= 1
                        continue
                    neighbours.add(neighbour)
        
        if neighbours:
            new_sentence = Sentence(neighbours, count)
            self.knowledge.append(new_sentence)

        # 4
        self.mark_cells()
        # 5
        # remove empty sentences
        self.make_inferences()
        self.mark_cells()
        return
    
    def mark_cells(self):
        for sentence in self.knowledge:
            mines = sentence.known_mines()
            safes = sentence.known_safes()
            if mines:
                for cell in mines.copy():
                    self.mark_mine(cell)
            if safes:
                for cell in safes.copy():
                    self.mark_safe(cell)
        return    
    
    def make_inferences(self):
        self.knowledge = [sentence for sentence in self.knowledge if sentence.cells != set()]

        new_knowledge = list()
        for subset in self.knowledge:
            for superset in self.knowledge:
                # if checking the same one, skip it (compares memory location)
                if subset is superset:
                    continue
                # remove dupes (compares values)
                if subset == superset:
                    self.knowledge.remove(superset)
                    continue
                if subset.cells.issubset(superset.cells):
                    new_cells = superset.cells - subset.cells
                    new_count = superset.count - subset.count
                    inferred_sentence = Sentence(new_cells, new_count)
                    # make sure we don't add duplicate knowledge
                    if inferred_sentence not in new_knowledge:
                        new_knowledge.append(inferred_sentence)

        if len(new_knowledge) != 0:
            for inference in new_knowledge:
                if inference not in self.knowledge:
                    self.knowledge.append(inference)
        return

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choices = list()
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if (move in self.moves_made) or (move in self.mines):
                    continue
                choices.append(move)
        if len(choices) != 0:
            rand = random.randrange(len(choices))
            return choices[rand]
        return None
