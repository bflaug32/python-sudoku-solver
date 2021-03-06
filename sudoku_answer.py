# Sudoku Solver, Brad Flaugher/NextFab
################ Definitions ################
## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
squares  = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)

def some(seq):
    "Return some element of seq that is true."
    if seq is False:
        return False
    for e in seq:
        if e: return e
    return False

def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

################ Random Puzzle Creator ################

import random

def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s])==1 else '.' for s in squares)
    return random_puzzle(N) ## Give up and make a new puzzle

################ Utilities ################

def find_all_possibilities(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s,d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))
    
def display(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print ''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols)
        if r in 'CF': print line
    print

################ Constraint Propagation ################

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d,'')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values

def check_solved(values):
    #start by assuming the puzzle is solved
    solved = True
    #check each square on the sudoku board
    #if each square has only one possibility, it's solved
    for s in squares:
        if(len(values[s]) == 1 and solved == True):
            solved = True
        else:
            #as soon as there's a square with more than possibility
            #we can instantly "return false", or say it hasn't been solved
            solved = False
            return False
    #if all squares have len(1), the puzzle has been solved
    if(solved == True):
        return True

################ Solve ################

def solve2(values):
    "Using depth-first search and propagation, try all possible values."
    display(values)
    if values is False:
        return False ## there are no possibilities!
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(solve2(assign(values.copy(), s, d))
                for d in values[s])

                
def solve(values):
    "this takes a puzzle with all possible answers, and searches for a working answer"
    "this uses what is called a depth first search, and eventually will use recursion"
    #don't try and solve if you have no possible values
    if values is False:
        return False
    #display your possible answers
    display(values)    
    #check to see if the puzzle has been solved, return values if so
    if(check_solved(values) is True):
        return values
    else:
        #find the square with the fewest possibilites call it "smallest_square"
        min = 9
        smallest_square = squares[0]
        for s in squares:
            num_possibilities = len(values[s])
            if(num_possibilities > 1 and num_possibilities < min):
                min = num_possibilities
                smallest_square = s
        #use the "assign" method to assign all possible value to that square
        #return a valid (use "some") solution of the puzzle with those values
        for d in values[smallest_square]:
            new_values = assign(values.copy(),smallest_square,d)
            return some(solve(new_values))
        

################ Main ##########################

if __name__ == '__main__':
    puzzle = random_puzzle()
    possibilities = find_all_possibilities(puzzle)
    solve(possibilities)

## References used:
## See http://norvig.com/sudoku.html
## http://www.scanraid.com/BasicStrategies.htm
## http://www.sudokudragon.com/sudokustrategy.htm
## http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
## http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/