#!/usr/bin/python

class SudokuBoard:
    
    def __init__(self, filename):
        """Create a new SudokuBoard object"""
        self.filename = filename
        self.board = self.parseBoard(filename)
        self.__constraints = self.__computeConstraintSets()
        self.__pointDict = self.__computePointDict()

        
    def parseBoard(self, filename):
        """Read a file as the Sudoku board"""
        try:
            f = open(filename, 'r')
        except IOError:
            print "Could not open file:", filename
        else:
            result = [[(int(char) if char in map(str, range(1,10)) else 0) for char in line if char != '\n'] for line in f]
            f.close()
            return result
        
    
    def printBoard(self):
        """Print a representation of the Sudoku board"""
        strBoard = map(lambda row: [(str(num) if num != 0 else '*') for num in row], self.board)
        for counter, row in enumerate(strBoard):
            row.insert(3, ' | ')
            row.insert(7, ' | ')
            print (" ".join(row)).strip()
            if counter in [2,5]:
                print "-------+---------+-------"

    def __computeConstraintSets(self):
        """Compute sets of locations that cannot have the same value"""
        result = []
        # Rows:
        result.extend([set([(row, col) for col in range(9)]) for row in range(9)])
        # Cols:
        result.extend([set([(row, col) for row in range(9)]) for col in range(9)])
        # Blocks:
        result.extend([set([(i/3 + 3*(j%3), i%3 + 3*(j/3)) for i in range(9)]) for j in range(9)])
        return result
  
    def __computePointDict(self):
        """Return a dictionary mapping each location to the constraint sets that include it"""
        result = {}
        for i in range(9):
            for j in range(9):
                result[(i,j)] = [constraint for constraint in self.__constraints if (i,j) in constraint]
        return result

    def getConstraintSets(self, location):
        """List the constraint sets including the specified point"""
        return self.__pointDict[location]

    def computeUnusedNums(self, constraint):
        """Compute the numbers not found in the board positions within the constraint"""
        allNums = range(1,10)
        for row, col in constraint:
            value = self.board[row][col]
            if value in allNums:
                del allNums[allNums.index(value)]
        return set(allNums)
    
    def isSolved(self):
        """Determine whether the Sudoku board is solved"""
        for constraint in self.__constraints:
            if self.computeUnusedNums(constraint): # Empty set is False
                return False
        return True
        
if __name__ == "__main__":
    sb = SudokuBoard('sudoku-board.txt')
    print sb.computeUnusedNums([(1,0),(2,3),(3,4),(0,1)])
    sb.printBoard()
