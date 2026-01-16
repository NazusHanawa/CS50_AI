import sys
import os

from crossword import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
                    print(letters[i][j] or " ", end=" ")
                else:
                    print("█", end=" ")
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

        img.save(f"{BASE_DIR}/{filename}")

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
            for word in domain.copy():
                if len(word) != variable.length:
                    domain.remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if x not in self.crossword.neighbors(y):
            return False
            
        overlap = self.crossword.overlaps[x, y]
        x_index, y_index = overlap
        
        revised = False
        for x_word in self.domains[x].copy():
            x_character = x_word[x_index]
            for y_word in self.domains[y].copy():
                if x_word == y_word:
                    continue
                
                y_character = y_word[y_index]
                if x_character == y_character:
                    break
            else:
                self.domains[x].remove(x_word)
                revised = True
        
        if revised:
            return True
        else:
            return False
        
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = set()
            for var1 in self.crossword.variables:
                for var2 in self.crossword.variables:
                    if var1 == var2:
                        continue
                    
                    arcs.add((var1, var2))
        
        while arcs:
            for arc in arcs.copy():
                x, y = arc
                if self.revise(x, y):
                    for var in self.crossword.variables:
                        if var == x:
                            continue
                        
                        new_arc = (var, x)
                    arcs.add(new_arc)
                    break
                
                arcs.remove(arc)

        for var in self.crossword.variables:
            if len(self.domains[var]) == 0:
                return False

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.crossword.variables) == len(assignment):
            return True
            
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x, x_word in assignment.items():
            x_neighbors = self.crossword.neighbors(x)

            if len(x_word) != x.length:
                return False
            
            for y, y_word in assignment.items():
                if x == y:
                    continue
                
                if x_word == y_word:
                    return False
                
                if y in x_neighbors:
                    overlap = self.crossword.overlaps[x, y]
                    x_index, y_index = overlap
                    
                    x_character = x_word[x_index]
                    y_character = y_word[y_index]
                    if x_character != y_character:
                        return False
                
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        word_eliminations = {word: 0 for word in self.domains[var]}
        
        for neighbor in neighbors:
            if neighbor in assignment:
                continue
            
            overlap = self.crossword.overlaps[var, neighbor]
            var_index, neighbor_index = overlap
            
            for var_word in word_eliminations:
                for neighbor_word in self.domains[neighbor]:
                    local_assignment = {
                        var: var_word,
                        neighbor: neighbor_word,
                    }
                    
                    if not self.consistent(var_word, neighbor_word):
                        word_eliminations[var_word] += 1

        sorted_list = sorted(word_eliminations, key=lambda word: word_eliminations[word])
        return sorted_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        best_variables = set()
        best_domain_size = float("inf")
        for variable, domain in self.domains.items():
            if variable in assignment:
                continue
            
            domain_size = len(domain)
            if domain_size < best_domain_size:
                best_variables.clear()
                best_variables.add(variable)
                best_domain_size = domain_size
            elif domain_size == best_domain_size:
                best_variables.add(variable)
        
        best_variable = None
        best_degree = float("-inf")
        for variable in best_variables:
            degree = len(self.crossword.neighbors(variable))
            
            if degree >= best_degree:
                best_variable = variable
                best_degree = degree
        
        return best_variable

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
        for word in self.domains[variable]:
            assignment[variable] = word
            if self.consistent(assignment):
                return self.backtrack(assignment)
            
            del assignment[variable]

        return False

def main():

    # Check usage
    # if len(sys.argv) not in [3, 4]:
    #     sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = f"{BASE_DIR}/data/structure1.txt" # sys.argv[1]
    words = f"{BASE_DIR}/data/words1.txt" # sys.argv[2]
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
