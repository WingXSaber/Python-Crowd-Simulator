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

import pygame as pyg, copy
from numpy import random
from math import pi, cos, sin, atan2, floor
from pygame import gfxdraw, draw
from pygame.sprite import collide_circle
from array import *
from ObjectMapHandler import *




class EntityObject(pyg.sprite.Sprite):           #extends pygame's sprite
    """The base class respresenting a single entity. A person.
    """
    
    __slots__ = ["x", "y", "radius", "mapHandler", "imageSurface", "color", "mask", "rect","pastCoor", "flowFieldPath"]; #Special attribute used for faster memory access and less memory overhead
    
    def __init__(self, x, y, radius, objectMapHandler, color):     
        """ The base class respresenting a single entity. A person.
           
        Args:
            x (number): Position X, in respect to center
            y (number): Position Y, in respect to center
            radius (number): radius of the entity
            walkingSpeed (number): pixels per frame. Please keep this below than the radius*2
            id (int): ID of the object. Please keep it unique.
        """
        # Call the parent class (Sprite) constructor
        super().__init__();    #pyg.sprite.Sprite.__init__(self)
        #self.x = floor(x);
        #self.y = floor(y);
        self.x = round(x);
        self.y = round(y);
        self.pastCoor = [(-1,-1), (-1,-1)];       
        
        self.radius = radius;
        self.mapHandler = objectMapHandler;     #2D Spatial partioning, used for optimized collision checking
        self.flowFieldPath = None;        
        
                
        self.imageSurface = pyg.Surface([(radius+1)*2, (radius+1)*2]).convert_alpha();   #Create the surface, but make it 1 pixel bigger for the mask.
        self.imageSurface.fill(pyg.Color(0,0,0,0));                                  #Fill surface with blank pixels
        pyg.draw.circle(self.imageSurface, pyg.Color(0,0,0), [radius+1, radius+1], self.radius+1);   #Draw the circle, to be used for the Mask
        self.mask = pyg.mask.from_surface(self.imageSurface);                            #Create mask, to be used for collision        
                
        #pyg.draw.circle(self.image, pyg.Color(255,0,0), [radius, radius], self.radius)  #circle(surface, color, center, radius)                 
        #pyg.draw.circle(self.image, pyg.Color(0,round(numpy.random.uniform(0, 255)),round(numpy.random.uniform(0, 255))), [radius, radius], self.radius) 
        
        self.color = pyg.Color(255,255, 255);         
        if(color is None):
            #hueRandValue = round(random.uniform(40, 240));        #Random value to set the color       
            #hueRandValue2 = round(random.uniform(10, 200));        #Random value to set the color        
            #hueRandValue3 = round(random.uniform(10, 200));        #Random value to set the color      
            #self.color = pyg.Color(hueRandValue,hueRandValue2, hueRandValue3);     #Color
            
            hueRandValue = round(random.uniform(0, 360));
            satRandValue = round(random.uniform(50, 100));
            valRandValue = round(random.uniform(50, 100));
            self.color.hsva = (hueRandValue, satRandValue, valRandValue, 100); 
            #                  H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100].  
        else:            
            self.color = pyg.Color(color[0], color[1], color[2]);            
        
        
        # Fetch the rectangle object that has the dimensions of the image        
        # pyg.sprite.Sprite needs a rect. Rect is the basis for drawing
        self.rect = self.imageSurface.get_rect();
        
        self.imageSurface = pyg.Surface([(radius*2)+1, (radius*2)+1]).convert_alpha();   #Clear the surface, but make it 1 pixel bigger for the AA.
        self.imageSurface.fill(pyg.Color(0,0,0,0));                                  
        
        #gfxdraw.filled_circle(self.imageSurface, self.radius, self.radius, self.radius, pyg.Color(0,0,0));  #Fill anti-aliased circle, becomes outline
        
        gfxdraw.aacircle(self.imageSurface, self.radius, self.radius, self.radius, pyg.Color(0,0,0));     #Draw anti-aliased circle
        gfxdraw.filled_circle(self.imageSurface, self.radius, self.radius, self.radius-1, pyg.Color(0,0,0));  #Fill anti-aliased circle        
        
        gfxdraw.aacircle(self.imageSurface, self.radius, self.radius, self.radius-1, self.color);     #Draw anti-aliased circle
        gfxdraw.filled_circle(self.imageSurface, self.radius, self.radius, self.radius-1, self.color);  #Fill anti-aliased circle        
        
        
        
        # Update the position of this object by setting the values of rect.x and rect.y       
        self.rect.center = (x,y);
              
        #self.mapHandler.addToMatrix(self.getX(), self.getY(), self);        
        self.radius -=1;  #Padding
    
    def __ne__(self, other):
        return (self.x, self.y) != (other.x, other.y)
    
    def copy (self):
        entity = EntityObject(copy.deepcopy(self.x), 
                              copy.deepcopy(self.y), 
                              self.radius, 
                              self.mapHandler, 
                              self.color);
        entity.setFlowField(self.flowFieldPath);
        return entity;
    
    #Update =============================================================================================================================================         
    
    def setRadius(self, radius):
        """ 
        Sets the radius size
        Args:
            radius (number): size
        """
        self.radius = radius;
        
    def getRadius(self):
        """
        Returns:              
            radius (number): size
        """
        return self.radius;    
    
    def setX(self, x):
        """ 
        Sets the position x, in resepct to center
        Args:
            x (number): Position X, in respect to center
        """
        self.x = x;
        
    def setY(self, y):
        """ 
        Sets the position y, in resepct to center
        Args:
            y (number): Position Y, in respect to center
        """
        self.x = y;
    
    def getX(self):
        """
        Returns:
            x (number): Position X, in respect to center
        """
        return self.x;
    
    def getY(self):
        """
        Returns:
            y (number): Position Y, in respect to center
        """
        return self.y;    
     
    def getLocation(self):
        """ 
        Returns:
            location (tuple): Position X and Y, in respect to center
        """       
        return (self.x, self.y);
        
    def setLocation(self, x, y):
        """ 
        Instantly move Entity to a position        
            Args:
            position (int,int): (x,y)
        """       
        self.x = x;
        self.y = y;
        self.rect.center = (x,y);
    
    def setFlowField(self, flowFieldPath):
        self.flowFieldPath = flowFieldPath;    #matrix sets direction
        
    def isFlowFieldSet(self):
        if(self.flowFieldPath is None):
            return False;
        else:
            return True;

    def update(self):
        """Updates current entity for changes such as change in position and other things. This method is iddeally called every frame."""                      
        
        x = self.getX();
        y = self.getY();
        
        if(self.flowFieldPath is None):    
            return x,y;
        
        radius = self.radius;
        
        #Determine available and priority path directions  ==============================================================                      
        flowFieldPath = self.flowFieldPath; 
        pastCoor = self.pastCoor;              
        paths = []  # [0]Value (Integer): 0  - [1] Index (Tuple): x,y         
        '''       checking flowpath field:
             ---------------------------------
             | i-1, j-1 |  i, j-1 | i+1, j-1 |
             ---------------------------------
             | i-1, j   |         | i+1, j   |
             ---------------------------------                
             | i-1, j+1 |  i, j+1 | i+1, j+1 |
             ---------------------------------   '''                 
        for j in range(-1, 2, 1):
            for i in range(-1, 2, 1):
                if (i==0 and j==0):
                    continue;
                #tempX = x+i*radius;
                #tempY = y+j*radius;
                #tempX = x+i;
                #tempY = y+j;
                tempX = x+i*(radius-1);
                tempY = y+j*(radius-1);
                
                if ((tempX, tempY) in flowFieldPath       #if adjacent step is in the flowfield
                    and (tempX, tempY) != pastCoor[0] 
                    and (tempX, tempY) != pastCoor[1]):   #and adjacent step is not the previous two steps                               
                    paths.append((flowFieldPath[tempX, tempY],(tempX, tempY)));               
                    
        #================================================================================================================
                                   
        if(bool(paths)):          
            paths.sort();# Sort the paths
            
            #Split off the paths with same priority value so it can be shuffled
            tempPaths = [];
            tempPaths.append(paths.pop(0));        
            while(bool(paths)):    
                tempPath = paths.pop(0);     
                if(tempPath[0] == tempPaths[0][0]): #checking if same priority value
                    tempPaths.append(tempPath);
                else:
                    paths.append(tempPath);     #put back the popped path
                    paths.sort();               #sort the remaining paths once more because of the append
                    random.shuffle(tempPaths);  #shuffle the paths with the same priority value
                    break;        
            paths = tempPaths + paths;          #combine them back
                    
        
            mapHandler = self.mapHandler;
            cellSize = mapHandler.cellSize;
            mapHandler.removeFromMatrix(x, y, self);    
            while(bool(paths)):                  
                stepX, stepY, = paths.pop(0)[1]
                random.shuffle(paths);
                self.setLocation(stepX, stepY);   
                tempX = floor(stepX/cellSize);          
                tempY = floor(stepY/cellSize);    
                '''       initial target lists:
                    ---------------------------------
                    | x-1, y-1 |  x, y-1 | x+1, y-1 |
                    ---------------------------------
                    | x-1, y   |  x, y   | x+1, y   |
                    ---------------------------------                
                    | x-1, y+1 |  x, y+1 | x+1, y+1 |
                    ---------------------------------   '''   
                try:   
                    for i in range(-1, 2, 1):
                        for j in range(-1, 2, 1):       
                            targetList = mapHandler.getListFromMatrixAt(tempX+i, tempY+j);                 
                            if(targetList):
                                for entity in targetList:          
                                    if(collide_circle(self, entity)):  
                                        self.setLocation(x,y);   
                                        raise Exception();  
                except:  
                    continue;     
                break;      
                
            mapHandler.addToMatrix(self.getX(), self.getY(), self); 
            
            pastCoor[1] = pastCoor[0];
            pastCoor[0] = (self.getX(), self.getY());
        return x,y;
        
                   
          
    def isCollidingWithEntitiesAndMap(self, mapMask):
        """Checks for collisions with Map and entities. Returns True or False. When doing Update(), please remove the entity first from matrix before calling 
        this method, then don't forget to return it to the matrix."""   
        radius = (self.mask.get_rect().width/2);
        x = self.getX();
        y = self.getY();
        if(self.mask.overlap(mapMask, (0-x+radius, 0-y+radius))): #Map             
            return True;   
        else:   #Entities
            #mapHandler = self.mapHandler;
            
            cellSize = self.mapHandler.cellSize
            x = floor(x/cellSize);          
            y = floor(y/cellSize);   
            #x = round(x/cellSize);          
            #y = round(y/cellSize);   


            '''       initial target lists:
                ---------------------------------
                | x-1, y-1 |  x, y-1 | x+1, y-1 |
                ---------------------------------
                | x-1, y   |  x, y   | x+1, y   |
                ---------------------------------                
                | x-1, y+1 |  x, y+1 | x+1, y+1 |
                ---------------------------------   '''                        
            for i in range(-1, 2, 1):
                for j in range(-1, 2, 1):       
                    targetList = self.mapHandler.getListFromMatrixAt(x+i, y+j);                 
                    if(targetList):
                        for entity in targetList:
                            #if(self is not entity and collide_circle(self, entity)):             
                            if(collide_circle(self, entity)):             
                                return True;                                  #if there is at least one collided, no need to check the rest.                     
        return False;    
    
    def isCollidingWithMap(self, mapMask):
        """Checks for collision with Map only. Returns True or False."""       
        radius = self.radius;                                             
        return (self.mask.overlap(mapMask, (0-self.getX()+radius, 0-self.getY()+radius)));            
         
    
    def getCollidingEntity(self):
        """Similar to isCollidingWithEntitiesAndMap(), but returns the colliding EntityObject instead."""                                                    
        cellSize = self.mapHandler.cellSize
        x = floor(self.getX()/cellSize);          
        y = floor(self.getY()/cellSize); 
        '''       initial target lists:
            ---------------------------------
            | x-1, y-1 |  x, y-1 | x+1, y-1 |
            ---------------------------------
            | x-1, y   |  x, y   | x+1, y   |
            ---------------------------------                
            | x-1, y+1 |  x, y+1 | x+1, y+1 |
            ---------------------------------   '''            
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):       
                targetList = self.mapHandler.getListFromMatrixAt(x+i, y+j);                 
                if(targetList):
                    for entity in targetList:
                        if(collide_circle(self, entity)):             
                            return entity;                                  #if there is at least one collided, no need to check the rest.                                                    
        return None;         

    
    
                
    #Render =============================================================================================================================================    
    
    def draw(self, surface, camera):             
        """Displays this Entity's graphics on the given pyg.Surface. This method is ideally called every frame."""    
        surface.blit(self.imageSurface, (self.rect.x - camera["x"], self.rect.y - camera["y"], self.rect.width, self.rect.height));              
    
    
   