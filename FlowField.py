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
"""
    Similar to ObjectMapHandler that it's a 2D matrix utilizing python dictionary.
    This is one is used for pathfinding.
"""
import pygame as pyg;

class FlowField:
    """_summary_
    """
    
    __slots__ = ["matrix","goalCoordinates","playAreaW","playAreaH","imageMask", "maxValue"];
   
    
    def __init__(self, imageMap, playAreaW, playAreaH, radius):
        """ The class that will help reduce processing load from EntityObject's collision detection by utilizing a Dictionary acting like a
        2D array that will contain entities. Each cell covers an area.
           
        Args:
            cellSize (number): determines the size of the Matrix           
        """        
        self.matrix = {};                #the coordinates that store the values assesed for path finding, lower value = closer to a goal
        self.goalCoordinates = [];       #tally of the goals, just incase need to reset matrix.
        self.maxValue = 1;               #used for plotting colors to surface later.
         
        self.playAreaW = playAreaW;
        self.playAreaH = playAreaH;  
        
        
        #Making obstacles wider with the entity radius, this way, flowfields will limit entities 
        #and not collide with walls.    
        radius = radius-1;
        circleSurface = pyg.Surface([radius*2, radius*2]).convert_alpha();  
        circleSurface.fill(pyg.Color(0,0,0,0));
        pyg.draw.circle(circleSurface, pyg.Color(0,0,0,255), [radius, radius], radius);    
             
        newMapSurface = pyg.Surface([playAreaW, playAreaH]).convert_alpha();  
        newMapSurface.fill(pyg.Color(0,0,0,0));                
        newMapSurface.blit(imageMap.convert_alpha(),(0,0,playAreaW, playAreaH));        
            
        for y in range(0, playAreaH, 1):
            for x in range(0, playAreaW, 1):
                color = imageMap.get_at((x,y));
                if(color.a > 0):                    
                    newMapSurface.blit(circleSurface, (x-circleSurface.get_width()/2, y-circleSurface.get_height()/2));#, radius*2, radius*2));                
        
        
        
        #self.imageMask = pyg.mask.from_surface(imageMap.convert_alpha());       
        self.imageMask = pyg.mask.from_surface(newMapSurface);   
        
        
        
            
    
    def addGoal(self, x, y):
        if (x>=1 and x<=self.playAreaW) and (y>=1 and y<=self.playAreaH):
            self.goalCoordinates.append((x,y));
            self.matrix[x, y] = 0;  
            print("Added",(x,y),"as a goal.");
        else:
            print("Cannot add",(x,y),"as a goal, out of bounds.");
    
    
    def generatePathField(self):
        matrix = self.matrix;   
                
        if(len(self.goalCoordinates)):  
            print("Generating flowfield...");
            
            if(len(matrix)<1):         
                for coor in self.goalCoordinates:
                    self.matrix[coor] = 0;
                
            openDict = {};
            openList = [];

            for index in matrix:
                openDict[index] = matrix[index];  # Index (Tuple): x,y   , Value (Integer): 0
                openList.append(index);
                
            imageMask = self.imageMask;
            playAreaW = self.playAreaW;
            playAreaH = self.playAreaH;  

            while(len(openDict)):               
                
                #currentNode =  next(iter(openDict));                                     
                currentNode =  openList.pop(0);                 
                currentNode =  currentNode, openDict[currentNode];                    
                del openDict[currentNode[0]];                
                
                if currentNode not in matrix:
                     matrix[currentNode[0]] = currentNode[1];
                     
                counter = currentNode[1] + 1;
                if(counter > self.maxValue):    #increasing the maxValue
                    self.maxValue = counter;
                
                x = currentNode[0][0];
                y = currentNode[0][1];
                '''       initial target lists:
                    ---------------------------------
                    | x-1, y-1 |  x, y-1 | x+1, y-1 |
                    ---------------------------------
                    | x-1, y   |  x, y   | x+1, y   |
                    ---------------------------------                
                    | x-1, y+1 |  x, y+1 | x+1, y+1 |
                    ---------------------------------   '''   
                
                for j in range(-1, 2, 1):
                    for i in range(-1, 2, 1):
                        if  (  (x+i, y+j) not in self.matrix  and  (x+i, y+j) not in openDict
                            and (x+i>1 and x+i<playAreaW)     and  (y+j>1 and y+j<playAreaH)
                            and not imageMask.get_at((x+i, y+j))
                            ):
                            openDict[x+i, y+j] =  counter;     
                            openList.append((x+i, y+j));          
                """
                
                cross = [(0,-1), (0,1), (-1,0), (1,0)];
                for coor in cross:
                    i,j = coor;
                    if  (  (x+i, y+j) not in self.matrix  and  (x+i, y+j) not in openDict
                        and (x+i>1 and x+i<playAreaW)     and  (y+j>1 and y+j<playAreaH)
                        and not imageMask.get_at((x+i, y+j))
                        ):
                        openDict[x+i, y+j] =  counter;     
                        openList.append((x+i, y+j));                      
                """
            print("Generation Complete");
        else:
            print("Can't gpenerate, no goals.");
    
