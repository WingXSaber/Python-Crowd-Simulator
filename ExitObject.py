#
#    Polytechnic Universitjof the Philippines
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

import pygame as pyg
from pygame import gfxdraw

class ExitObject(pyg.sprite.Sprite):           #extends pygame's sprite
    """The base class respresenting a single entity. A person.
    """
    
    __slots__ = ["x", "y", "radius", "imageSurface", "color", "mask", "rect"]; #Special attribute used for faster memory access and less memory overhead
    
    def __init__(self, x, y, radius):     
        # Call the parent class (Sprite) constructor
        super().__init__();    #pyg.sprite.Sprite.__init__(self)        
        self.x = round(x);
        self.y = round(y);
        self.radius = radius;
        
        self.imageSurface = pyg.Surface([radius*2, radius*2]).convert_alpha();       #Create Surface                   
        self.imageSurface.fill(pyg.Color(0,0,0,0));                                  #Fill surface with blank pixels
        self.color = pyg.Color(255,0,0,190);
        
        pyg.draw.circle(self.imageSurface, self.color, [radius, radius], self.radius);   #Draw the circle, to be used for the Mask
        self.mask = pyg.mask.from_surface(self.imageSurface);                             #Create mask, to be used for collision
        
        # Fetch the rectangle object that has the dimensions of the image        
        # pyg.sprite.Sprite needs a rect. Rect is the basis for drawing
        self.rect = self.imageSurface.get_rect();
         
        self.imageSurface = pyg.Surface([(radius*2)+1, (radius*2)+1]).convert_alpha();   #Clear the surface, but make it 1 pixel bigger for the AA.
        self.imageSurface.fill(pyg.Color(0,0,0,0));                          
        gfxdraw.aacircle(self.imageSurface, self.radius, self.radius, self.radius-1, self.color);     #Draw anti-aliased circle
        gfxdraw.filled_circle(self.imageSurface, self.radius, self.radius, self.radius, self.color);  #Fill anti-aliased circle
        
        debugFont = pyg.font.Font(None, int(radius*1.4)); 
        text = debugFont.render("EXIT", True, (255,255,255,50))
        self.imageSurface.blit(text, (radius-text.get_width()/2, radius-text.get_height()/2+1));
                        
                        
        # Update the position of this object by setting the values of rect.x and rect.y       
        self.rect.centerx = x;
        self.rect.centery = y;    
    
    def __ne__(self, other):
        return (self.x, self.y) != (other.x, other.y)
    
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
    
    def isCollidingWithMap(self, mapMask):
        """Checks for collision with Map only. Returns True or False."""       
        radius = self.radius;                                             
        return (self.mask.overlap(mapMask, (0-self.getX()+radius, 0-self.getY()+radius)));            
    
    
    #Render =============================================================================================================================================        
    def draw(self, surface, camera):             
        """Displays this Entity's graphics on the given pyg.Surface. This method is ideally called every frame."""    
        surface.blit(self.imageSurface, (self.rect.x - camera["x"], self.rect.y - camera["y"], self.rect.width, self.rect.height));              
  