import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable, domain in self.domains.items():
            to_remove = set()
            var_length = variable.length
            for value in domain:
                if len(value) != var_length:
                    to_remove.add(value)
            # have to split up into 2 parts to avoid error
            for value in to_remove:
                self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revisions = False
        # if no overlaps, then do nothing
        if self.crossword.overlaps[x, y] == None:
            return False
        # check for overlaps
        to_remove = set()
        x_index, y_index = self.crossword.overlaps[x, y]
        # check for each value in x's domain
        for x_value in self.domains[x]:
            is_consistent = False
            # check if there is a possible corresponding value for y in self.domains[y]
            for y_value in self.domains[y]:
                if x_value != y_value and x_value[x_index] == y_value[y_index]:
                    is_consistent = True
            # if not consistent, then we must remove the value from x's domain and return True
            if not is_consistent:
                to_remove.add(x_value)
                revisions = True
        for value in to_remove:
            self.domains[x].remove(value)
        return revisions

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # use set because we might add existing arcs later on
        if arcs == None:
            arcs = list(x for x in self.crossword.overlaps.keys())
        arcs = set(arcs)
        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for constraint, val in self.crossword.overlaps.items():
                    if val:
                        c1, c2 = constraint
                        if y in constraint:
                            continue
                        # found neighbour that isn't y (already enforced) --> add them 
                        if c1 == x:
                            arcs.add((c2, x))
                        elif c2 == x:
                            arcs.add((c1, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        assigned_variables = set(var for var in assignment.keys())
        for variable in self.crossword.variables:
            if not variable in assigned_variables:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words = set()
        for variable, word in assignment.items():
            # check lengths
            if len(word) != variable.length:
                return False
            # check distinct words
            if word in words:
                return False
            words.add(word)
            # check conflicts
            for variables, val in self.crossword.overlaps.items():
                if variable in variables:
                    if val != None:
                        x, y = variables
                        x_index, y_index = val

                        if y not in assignment.keys() or x not in assignment.keys():
                            continue
                        if assignment.get(x)[x_index] != assignment.get(y)[y_index]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        value_tuples = []
        for value in self.domains[var]:
            num_rule_out = 0
            for variables, constraint in self.crossword.overlaps.items():
                x, y = variables
                # only interested when the overlap contains our variable
                if x == var:
                    # if y is already assigned, then it cannot rule out neighbors
                    if y in assignment.keys():
                        continue
                    # if there is no constraint, then there are no values to rule out
                    if constraint == None:
                        continue
                    # otherwise, check if the value will cause conflict
                    x_index, y_index = constraint
                    for conflict_word in self.domains[y]:
                        if value[x_index] != conflict_word[y_index]:
                            num_rule_out += 1
            value_tuples.append((value, num_rule_out))
        value_tuples = sorted(value_tuples, key=lambda value: value[1])
        return [value[0] for value in value_tuples]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = []
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                domain_size = len(self.domains[variable])
                neighbors = 0
                for variables in self.crossword.overlaps.keys():
                    if variable in variables:
                        neighbors += 1
                unassigned_vars.append((variable, domain_size, neighbors))
        unassigned_vars = sorted(unassigned_vars, key=lambda x: (x[1], -x[2]))
        return unassigned_vars[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        variable = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(variable, assignment):
            assignment[variable] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != None:
                    return result
            assignment.pop(variable)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
