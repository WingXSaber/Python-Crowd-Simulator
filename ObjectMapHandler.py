#
#    Polytechnic University of the Philippines
#    Sta. Mesa, Manila, Philippines
#
#    In partial fulfillment of MODELING AND SIMULATION - COSC30013
#    
#    Developed by:
#        Mark Joseph Aquino
#        Renz Carlo Caritativo    
#        Rei Enrico
#        Tisha Gonzales
#        Zoe Ong
#        John Jeric Silverio
#        Richter Ace Villas       
#
#    Bachelor of Science in Computer Science 2-3 
#    First Semester - Year 2022    
#   
'''
    Here's the idea:
        the ObjectMatrix will utilize a python Dictionary that will hold a list containing references to entities. Each
    keyword is a tuple/an ordered pair representing x,y repectively, a 'cell' that will hold an area (maybe diameter of the 
    entities or twice of that).     
        A cell will cover an area with respect to its index/keyword. 
        IE. Diameter is 10
            [1,1] will cover X: 10-19 , Y: 10-19 
            [2,3] will cover X: 20-29 , Y: 30-39            
        
        ---------------------------------
        | x-1, y-1 |  x, y-1 | x+1, y-1 |
        ---------------------------------
        | x-1, y   |  x, y   | x+1, y   |
        ---------------------------------                
        | x-1, y+1 |  x, y+1 | x+1, y+1 |
        ---------------------------------
    
        The collision will check it's neighboring 'cells' (+1/+0/-1 x, +1/+0/-1 y), NW, N, NE, W, center, E, SW, S, and SE.
        
        If Entity moves, and out of the cell, put it in the proper cell. If selected cell does not exist, create it by
    calling a function here. This class will store the matrix.   
'''
from math import floor

class ObjectMapHandler:
    """ The class that will help reduce processing load from EntityObject's collision detection by utilizing a Dictionary acting like a
    2D array that will contain entities. Each cell covers an area.
    """
    
    __slots__ = ["cellSize", "matrix"]; #Special attribute used for faster memory access and less memory overhead
    
    #matrix = {};     

    def __init__(self, cellSize):
        """ The class that will help reduce processing load from EntityObject's collision detection by utilizing a Dictionary acting like a
        2D array that will contain entities. Each cell covers an area.
           
        Args:
            cellSize (number): determines the size of the Matrix           
        """        
        self.cellSize = cellSize;                
        self.matrix = {};   
        
    def getMatrixLength(self):
        '''Returns the count of existing cells with entities.'''
        a = 0;
        for i in self.matrix:
            a+=1;
        return a;
    
    def getAllMatrixKeys(self):        
        '''Returns a list of all keys of existing cells which are tuple.'''
        return list(self.matrix.keys());
    
    def getCellSize(self):
        '''Returns the defined size of each cell.'''
        return self.cellSize;
        
    
    def addToMatrix(self, x, y, entity):
        '''Adds entity to the respective cell. If that cell on the proper coordinate doesn't exist, create it.'''        
        cellSize = self.cellSize;
        x = floor(x/cellSize);
        y = floor(y/cellSize);
        
        try:            
            self.matrix[x, y].append(entity);                
        except KeyError:                        
            self.matrix[x, y] = list();       #if keyword/index does not exist yet, add one.            
            self.matrix[x, y].append(entity);                                                
        
        
    def removeFromMatrix(self,x, y, entity):
        '''Removes entity from the respective cell. If the cell no longer contains entities, delete it.'''
        cellSize = self.cellSize;
        x = floor(x/cellSize);
        y = floor(y/cellSize);
        
        if (x,y) in self.matrix:                    #if keyword exists
            if entity in self.matrix[x, y]:         #if entity is in the list
                self.matrix[x, y].remove(entity);            
            if (not bool(self.matrix[x, y])):       #if list is empty                 
                del self.matrix[x, y];     
                
        
    def getListFromMatrixAt(self, x, y):
        '''Returns a list of all entities existing in a cell. If cell is empty, returns None'''
        try:
            #if(self.matrix[x, y]):      
            return self.matrix[x, y];
        except:
            return None;
            
    def removeAll(self):
        '''Removes all entities from all matrices inside this ObjectMapHandler.'''
        self.matrix = {}
            


                
        
            