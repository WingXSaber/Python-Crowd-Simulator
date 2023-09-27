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
    This is the "main class" that runs the Crowd Simulation. 
    It contains the main loop while importing from other files 
    in the same directory, or from the library    
    
    It mainly utilizes pygame - Python Game Library    
"""

import pygame as pyg, sys, os, numpy as nmpy, time, ast, tkinter, threading, textwrap, math, datetime
from pygame import display;
from pygame.locals import *         #for keywords such as event 
from pygame.sprite import collide_circle
from screeninfo import get_monitors
from tkinter import filedialog, messagebox
from EntityObject import *
from ObjectMapHandler import *
from FlowField import *
from ExitObject import *

DEBUG_MODE = False;

#Initialize path
dir_path = os.path.dirname(os.path.realpath(__file__));    
#dir_path = os.getcwd();

#Initialze Pygame
pyg.init();
clock = pyg.time.Clock();
FRAMERATE = 60;            #Defines the Framerate limit.                            

#Initialize Tkinter
rootTk = tkinter.Tk();
rootTk.withdraw();

#Initialize window
SCREEN_WIDTH = 1024;
SCREEN_HEIGHT = 768;
#DISPLAY_FLAGS = pyg.RESIZABLE | pyg.FULLSCREEN | pyg.DOUBLEBUF | pyg.SRCALPHA;
DISPLAY_FLAGS = pyg.RESIZABLE | pyg.SHOWN;# | pyg.OPENGL ;

monitors = get_monitors();
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (monitors[0].width/2-SCREEN_WIDTH/2,(monitors[0].height/2-SCREEN_HEIGHT/2)); #Makes window spawn centered
#display.gl_set_attribute(GL_ACCELERATED_VISUAL, 1);

#Set Icon
try:    
    pyg.display.set_icon(pyg.image.load(dir_path+"/Assets/logo.png"));
except:
    print("Icon not found at : "+dir_path+"/Assets/logo.png");
    pass;

#Set Window Name
display.set_caption("Python Crowd Simulator");

mainSurface = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DISPLAY_FLAGS);
mainSurface.fill(pyg.Color(130, 62, 42));     
#mainSurface.fill(pyg.Color(64,64,64,255)); #draw background layer first. 
display.update();  



def windowResize(event):
    global SCREEN_WIDTH, SCREEN_HEIGHT, camera; #if it's a global variable, declare it within the function so it can be referenced.
    camera["x"] -= (event.size[0]-SCREEN_WIDTH)/2;
    camera["y"] -= (event.size[1]-SCREEN_HEIGHT)/2;
    SCREEN_WIDTH = event.size[0];
    SCREEN_HEIGHT = event.size[1];        

def timeToStop():
    print("See You Space Cowboy.");
    pyg.quit();          #Quit Pygame
    rootTk.quit();          #Quit Tkinter
    sys.exit()              #Quit entire program    



#Initialize fonts
pyg.font.init();
font = pyg.font.SysFont('None',40)

#Initialize Camera
camera = {"x":0, "y":0, "zoom":1};
CAMERA_SPEED = 0;
CAMERA_SPEEDMAX = 500;
#print(camera["x"]) #Camera Access sample   

def cameraMoveUpdate():
    global CAMERA_SPEED, CAMERA_SPEEDMAX; #if it's a global variable, declare it within the function so it can be referenced.
    pressed_keys = pyg.key.get_pressed(); 
    if (pressed_keys[K_UP] or pressed_keys[K_DOWN] or pressed_keys[K_LEFT] or pressed_keys[K_RIGHT] or pressed_keys[K_w] or pressed_keys[K_s] or pressed_keys[K_a] or pressed_keys[K_d]):       
        if (CAMERA_SPEED < CAMERA_SPEEDMAX):
            CAMERA_SPEED+=CAMERA_SPEEDMAX*0.2;            
        if (pressed_keys[K_UP] or pressed_keys[K_w]):  
            camera["y"] -= CAMERA_SPEED/60;        
        if (pressed_keys[K_DOWN] or pressed_keys[K_s]):  
            camera["y"] += CAMERA_SPEED/60;
        if (pressed_keys[K_LEFT] or pressed_keys[K_a]):  
            camera["x"] -= CAMERA_SPEED/60;
        if (pressed_keys[K_RIGHT] or pressed_keys[K_d]):  
            camera["x"] += CAMERA_SPEED/60;                    
    else:        
        CAMERA_SPEED = 0;       
            
    
#Initialize Map
mapImageMask = None;
mapSurface = None;
mapFileName = None;
PLAYAREA_WIDTH  = 0;
PLAYAREA_HEIGHT = 0;

mapVisualSurface = None;
mapVisualFileName = None;

panelMapSurface = None;
panelMapVisualSurface = None;
panelMiniMapSurface = None;

surfacePath = None;

flowFieldPaths = None;

#Initialize Enitity (In pygame, they call an object a 'sprite')
ENTITYRADIUS = 4;                                   #Must be integer, sets the radius of the entity
entityMapHandler = ObjectMapHandler(ENTITYRADIUS*1.5);  #used for collision detection. See the class documentation.
allEntityHandler = pyg.sprite.Group();              #Creating Object Group for all entities

EXITRADIUS = 12;
allExitHandler = pyg.sprite.Group();                #Crating Object group for all exit points
allEntityLocation = {};                             #key X:Y  value Color


while(True):
    #First Pygame Loop, Load and Play Title Screen animation    ===================================================================================================================================    
    try:
        #Initialize images to played for the intro animation
        titleSurface = [];
        isTitleScreen = True;
        frame = 120;        #The count of frames for the animation inside /Title_Screen. We load the animation backwards
        while(isTitleScreen):
            #check for pyg.events =================================================================================    
            for event in pyg.event.get():             #Getting the current event list available and execute action
                if event.type == pyg.VIDEORESIZE:     #when window is resized
                    windowResize(event);        

                if (event.type== pyg.locals.QUIT):   #when exit buttton event is pressed                      
                    timeToStop();
                    
                if event.type == pyg.MOUSEBUTTONDOWN or event.type == pyg.KEYDOWN:    #Skip Intro
                    print("Skipping title screen animation.");
                    isTitleScreen=False;
                    
            try:
                tempImage = pyg.image.load(dir_path+"/Title_Screen/"+('{:0>4}'.format(frame))+".jpg");        
                tempSurface = pyg.Surface((tempImage.get_width(), tempImage.get_height())).convert();
                tempSurface.fill(pyg.Color(0,0,0));                
                tempSurface.blit(tempImage, (0,0), (0,0,tempImage.get_width(), tempImage.get_height()));
                titleSurface.append(tempSurface);    
            except (FileNotFoundError):
                print("FileNotFoundError. Could not find file: "+dir_path+"/Title_Screen/"+('{:0>4}'.format(frame))+".jpg");

            mainSurface.fill(pyg.Color(130, 62, 42));     
            #mainSurface.fill(pyg.Color(64,64,64)); #draw background layer first.            
            display.update();   
            frame-=1; 
            if(frame<=0):
                break;
        
        #Play 
        frame = 0; 
        while(isTitleScreen):
            #pyg.time.Clock().tick(24);            
            pyg.time.Clock().tick(24);
            #check for pyg.events ============================================================================================================================       
            for event in pyg.event.get():             #Getting the current event list available and execute action
                if event.type == pyg.VIDEORESIZE:     #when window is resized
                    windowResize(event);        

                if (event.type== pyg.locals.QUIT):   #when exit buttton event is pressed                      
                    timeToStop();

                if event.type == pyg.MOUSEBUTTONDOWN or event.type == pyg.KEYDOWN:    #Skip Intro
                    print("Skipping title screen animation.");
                    isTitleScreen=False;        
            
            
            mainSurface.fill(pyg.Color(130, 62, 42));     
            #mainSurface.fill(pyg.Color(64,64,64)); #draw background layer first.       
            scaledWidth = (SCREEN_HEIGHT*titleSurface[frame].get_width())/titleSurface[frame].get_height();            
            mainSurface.blit(pyg.transform.scale(titleSurface[frame], (scaledWidth,SCREEN_HEIGHT)), (SCREEN_WIDTH/2 - scaledWidth/2,0) );
            display.update();    
            frame+=1;
            if(frame==len(titleSurface)):
                isTitleScreen=False;
        #===============================================================================================================================================================================
    except:
        print("Unable to display title animation. Disregarding.");












    
     
    allEntityHandler.empty();   
    entityMapHandler.removeAll();
    for location in allEntityLocation:    
        x, y = location;
        tempEntity = EntityObject(x, y, ENTITYRADIUS, entityMapHandler, allEntityLocation[location]);                   
        entityMapHandler.addToMatrix(x, y, tempEntity);
        allEntityHandler.add(tempEntity);        
        


    #Initilialize GUI elements for second loop ==============================================================================================================
    panelFont = None;
    try:
        panelFont = pyg.font.Font(dir_path+"/Assets/FreeSans.ttf", 16);    
    except:
        panelFont = pyg.font.Font(None, 16);    


    panelSurface = pyg.Surface([900, 200]).convert_alpha();  #The background for the top panel 
    panelSurface.fill(pyg.Color(0,0,0,0));          #Fill with transparent
    panelSurfaceColor = pyg.Color(130, 62, 42);     #Set Color for future and current use
    pyg.draw.rect(panelSurface, panelSurfaceColor, (0,0,panelSurface.get_width(), panelSurface.get_height()), 0, 12); #Draw round rect
    

    tabSurface1 = pyg.Surface([panelSurface.get_width()/3, 20]).convert_alpha();
    tabSurface1.fill(pyg.Color(0,0,0,0));      
    pyg.draw.rect(tabSurface1, pyg.Color(130, 0, 0), (0,0,tabSurface1.get_width(), tabSurface1.get_height()), 0, 10); #Draw round rect
    
    tabSurface2 = pyg.Surface([panelSurface.get_width()/3, 20]).convert_alpha();
    tabSurface2.fill(pyg.Color(0,0,0,0)); 
    pyg.draw.rect(tabSurface2, pyg.Color(130, 130, 0), (0,0,tabSurface2.get_width(), tabSurface2.get_height()), 0, 10); #Draw round rect
    
    tabSurface3 = pyg.Surface([panelSurface.get_width()/3, 20]).convert_alpha();
    tabSurface3.fill(pyg.Color(0,0,0,0)); 
    pyg.draw.rect(tabSurface3, pyg.Color(0, 130, 0), (0,0,tabSurface3.get_width(), tabSurface3.get_height()), 0, 10); #Draw round rect
    

    if(panelMapSurface is None):
        panelMapSurface = pyg.Surface([150, 150]).convert_alpha();   #The Thumbnail for the imageMap
        panelMapSurface.fill(pyg.Color(90, 90, 90, 255));         #Set Color
        panelMapSurface.blit(panelFont.render("NONE SELECTED", True, (110,110,110)), (6, panelMapSurface.get_height()/2-8));        
        pyg.draw.rect(panelMapSurface, pyg.Color(0,0,0), (0,0,panelMapSurface.get_width()+1, panelMapSurface.get_height()+1), 2);

    if(panelMiniMapSurface is None):
        panelMiniMapSurface = pyg.Surface([150, 150]).convert_alpha();   #The Minimap 
        panelMiniMapSurface.fill(pyg.Color(90, 90, 90, 255));         #Set Color

    if(panelMapVisualSurface is None):
        panelMapVisualSurface = pyg.Surface([150, 150]).convert_alpha();   #The Minimap for the visual Map
        panelMapVisualSurface.blit(panelMapSurface, (0,0));

    panelButtonSurfaceGreen = pyg.Surface([102, 26]).convert();       #The button 
    panelButtonSurfaceGreen.fill(pyg.Color(23, 37, 7));                #Set Color of the shadow edge
    pyg.draw.rect(panelButtonSurfaceGreen, pyg.Color(50, 96, 42), [2,2,96, 20]);   #Draw Color of the top of the button

    #Rects based on the graphic dimensions above, these will be used to as buttons.
    btnSelectMap = pyg.Rect(panelButtonSurfaceGreen.get_rect()); #Select Map File
    btnSelectBG  = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Select Map Visual File
    btnNext      = pyg.Rect(panelButtonSurfaceGreen.get_rect());      #Next Stage
    btnPrevious  = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Previous Stage
    btnLoadCoor  = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Load coordinates of entity/exits
    btnSaveCoor  = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Save coordinates of entity/exits


    def isMouseAtSurface(button):   
        mouseX = pyg.mouse.get_pos()[0];
        mouseY = pyg.mouse.get_pos()[1];
        return mouseX >= button.x and mouseX <= button.x + button.width    and    mouseY >= button.y and mouseY <= button.y + button.height;
    
    pastMouseCoor = None;
         
    #Second Pygame Loop, Initialization of map and entities =============================================================================================================================
    isSettingEntityLocation = True;
    stage = 1;
    print("Intializing Map and Entities: Start.");
    while(isSettingEntityLocation):        
        #set max delay for the next Tick of the loop, limiting the framerate.
        clock.tick(FRAMERATE);
        
        pressed_keys = pyg.key.get_pressed(); 
        if (pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]):                 
            if(pastMouseCoor is None):      
                pastMouseCoor = (pyg.mouse.get_pos()[0], pyg.mouse.get_pos()[1]);
        else:
            pastMouseCoor = None;
        
        #check for pyg.events ============================================================================================================================           
        for event in pyg.event.get():             #Getting the current event list available and execute action
            if event.type == pyg.VIDEORESIZE:     #when window is resized
                windowResize(event);        
                
            if (event.type== pyg.locals.QUIT):   #when exit buttton event is pressed                      
                timeToStop();
            
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_F2:
                    DEBUG_MODE = not DEBUG_MODE;
                        
            if event.type == pyg.MOUSEBUTTONUP: #for mouse click
                match stage:
                    case 1:
                        if (isMouseAtSurface(btnSelectMap)): #If "Select File" / Load Map Button was pressed
                            while True:  #Using while just to have that 'break' operation                       
                                if(bool(allEntityHandler) or bool(allExitHandler)):     #If there are existing entites and exit placements already placed.
                                    if(not messagebox.askyesno(title="Warning", message="By changing the map, the entity and exit placements will be erased.\n\nDo you wish to proceed?")):                        
                                        rootTk.update(); 
                                        break;      #Break this while(isMouseAtSurface(btnSelectMap)) loop    
                                    else:
                                        rootTk.update();
                                #mainSurface = display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags = pyg.HIDDEN);    #Hide Window                                
                                #text_file_extensions = ['*.jpg','*.jpeg', '*.png'];                        
                                text_file_extensions = ['*.png'];                        
                                ftypes = [
                                    ('Known image files', text_file_extensions),
                                    ('All files', '*')
                                ]                               
                                file_path = filedialog.askopenfilename(initialdir = dir_path, filetypes = ftypes);                                                                                                    
                                rootTk.update();   
                                if(file_path):
                                    try:
                                        mapImage = pyg.image.load(file_path);    #Load image                    
                                        mapImage.set_colorkey((255,255,255));                                #Color-to-alpha out the white if there is white background
                                        pyg.draw.rect(mapImage, pyg.Color(0,0,0), (0,0,mapImage.get_width(), mapImage.get_height()), 3);    #draw border to map, to prevent spilling flowfield and limit movements outside of playarea
                                        mapImageMask = pyg.mask.from_surface(mapImage.convert_alpha());   #Make a mask out of the transparent version of the image  
                                        mapSurface = pyg.Surface((mapImage.get_width(), mapImage.get_height())).convert_alpha(); #change the pixel format of an image(wuth alpha) to be same as surface.  
                                        #It is a good idea to convert all Surfaces before they are blitted many times.                    
                                        mapSurface.fill([0,0,0,0]);              #Fill surface with transparent pixels, otherwise the blitted will not show.
                                        mapSurface.blit(mapImage, (0,0), (0,0,mapImage.get_width(), mapImage.get_height()));  #blit the image to the surface.
                                        panelMapSurface.fill([100,100,100, 255]);        #Fill surface with background, if image is transparent.
                                        panelMapSurface.blit(pyg.transform.scale(mapImage, (panelMapSurface.get_width(),panelMapSurface.get_height())), (0,0), panelMapSurface.get_rect() );
                                        pyg.draw.rect(panelMapSurface, pyg.Color(0,0,0), (0,0,panelMapSurface.get_width()+1, panelMapSurface.get_height()+1), 2); #draw border/shadow to panel map
                                        PLAYAREA_WIDTH  = mapImage.get_width();
                                        PLAYAREA_HEIGHT = mapImage.get_height();
                                        camera["x"] = PLAYAREA_WIDTH/2 - SCREEN_WIDTH/2;
                                        camera["y"] = PLAYAREA_HEIGHT/2 - SCREEN_HEIGHT/2;
                                        mapFileName = str(os.path.split(file_path)[1]);   #To be displayed at the top panel                                          
                                        allExitHandler.empty();   
                                        allEntityHandler.empty();   
                                        entityMapHandler.removeAll();
                                        surfacePath = None;
                                    except FileNotFoundError:                    
                                        messagebox.showerror(title="FileNotFound Error", message="Cannot load map file. File was not found.");
                                        rootTk.update();
                                    except pyg.error:                    
                                        messagebox.showerror(title="Pygame Error", message="Cannot load file. Please check if selected file is an image.");                    
                                        rootTk.update();
                                    except: 
                                        messagebox.showerror(title="Unknown Error", message="Cannot load file. Unknown Error.");                    
                                        rootTk.update();                            
                                break;   
                        if (isMouseAtSurface(btnSelectBG)):   #visuals here    
                            while True:  #Using while just to have that 'break' operation    
                                text_file_extensions = ['*.jpg','*.jpeg', '*.png'];                        
                                ftypes = [
                                    ('Known image files', text_file_extensions),
                                    ('All files', '*')
                                ]                               
                                file_path = filedialog.askopenfilename(initialdir = dir_path, filetypes = ftypes);                                                                                                    
                                rootTk.update();   
                                if(file_path):
                                    try:
                                        mapVisualImage = pyg.image.load(file_path);    #Load image                    
                                        mapVisualSurface = pyg.Surface((mapVisualImage.get_width(), mapVisualImage.get_height())).convert_alpha(); #change the pixel format of an image(wuth alpha) to be same as surface.  
                                        #It is a good idea to convert all Surfaces before they are blitted many times.                    
                                        mapVisualSurface.fill([0,0,0,0]);              #Fill surface with transparent pixels, otherwise the blitted will not show.
                                        mapVisualSurface.blit(mapVisualImage, (0,0), (0,0,mapVisualSurface.get_width(), mapVisualSurface.get_height()));  #blit the image to the surface.                                        
                                        panelMapVisualSurface.fill([100,100,100, 255]);        #Fill surface with background, if image is transparent.
                                        panelMapVisualSurface.blit(pyg.transform.scale(mapVisualSurface, (panelMapSurface.get_width(),panelMapSurface.get_height())), (0,0), panelMapSurface.get_rect() );                                    
                                        pyg.draw.rect(panelMapVisualSurface, pyg.Color(0,0,0), (0,0,panelMapVisualSurface.get_width()+1, panelMapVisualSurface.get_height()+1), 2); #draw border/shadow to panel map
                                        mapVisualFileName = str(os.path.split(file_path)[1]);   #To be displayed at the top panel                                                                              
                                    except FileNotFoundError:                    
                                        messagebox.showerror(title="FileNotFound Error", message="Cannot load visual map file. File was not found.");
                                        rootTk.update();
                                    except pyg.error:                    
                                        messagebox.showerror(title="Pygame Error", message="Cannot load file. Please check if selected file is an image.");                    
                                        rootTk.update();
                                    except: 
                                        messagebox.showerror(title="Unknown Error", message="Cannot load file. Unknown Error.");                    
                                        rootTk.update();
                                break;
                                    
                        if (isMouseAtSurface(btnNext)):    #If Next Button was pressed
                            stage = 2;      
                    
                    case 2:
                        if (isMouseAtSurface(btnPrevious)):    #If Previous Button was pressed
                            stage = 1;   
                        if (isMouseAtSurface(btnNext) and len(allExitHandler)):        #If Next Button was pressed
                            stage = 3;  
                        
                        if (isMouseAtSurface(btnLoadCoor)):   #If "Select File" / Load Coordinates Button was pressed                                                    
                            text_file_extensions = ['*.exit'];                        
                            ftypes = [
                                ('Exit coordinates file', text_file_extensions),
                                ('All files', '*')
                            ]       
                            filename = filedialog.askopenfilename(initialdir = dir_path, filetypes = ftypes)
                            if(filename != ''):                                
                                try:
                                    f = open(filename, "r");
                                    lines = f.readlines();                    
                                    coordinates = []
                                    for x in lines:     #Load all lines first and put them in a list. If one fails, throw a ValueError.
                                        data = ast.literal_eval(str(x));    #Read Line, get Tuple (x, y)
                                        coordinates.append((data[0], data[1]));                        
                                    cantBePlacedCount = 0;
                                    wasPlacedCount = 0;
                                    for data in coordinates:
                                        tempExit = ExitObject(data[0], data[1], EXITRADIUS);                
                                        flag = False;                             
                                        for exit in allExitHandler:
                                            if(collide_circle(tempExit, exit)):
                                                flag = True;
                                                break;                                                                                                           
                                        if(not flag and not mapImageMask.get_at((data[0], data[1]))):       
                                            allExitHandler.add(tempExit);  
                                            wasPlacedCount+=1;   
                                            surfacePath = None;    
                                        else:
                                            cantBePlacedCount+=1;                        
                                    if(cantBePlacedCount):
                                        message = "Failed to input "+str(cantBePlacedCount)+" exit. Possible collisions from existing exits have occured.";
                                        if(wasPlacedCount):
                                            message+="\n\nHowever, "+str(wasPlacedCount)+" were successfully placed.";
                                        messagebox.showwarning(title=None, message=message);                    
                                        rootTk.update();                                                            
                                except (FileNotFoundError):             
                                    messagebox.showerror(title="FileNotFound Error", message="Cannot load coordinates file. File was not found.");
                                    rootTk.update();
                                except (ValueError):
                                    messagebox.showerror(title="Value Error", message="Cannot load coordinates file. File may possibly be corrupted or wrong.");
                                    rootTk.update();
                                except: 
                                    messagebox.showerror(title="Unknown Error", message="Cannot load file. Unknown Error.");                    
                                    rootTk.update();                    

                        if (isMouseAtSurface(btnSaveCoor)):  #If "Save File" / Save coordinates Button was pressed
                            if(len(allExitHandler)):
                                #try:
                                    filename = '';
                                    text_file_extensions = ['*.exit'];                        
                                    ftypes = [
                                        ('Exit coordinates file', text_file_extensions),
                                        ('All files', '*')
                                    ]       
                        
                                    f = filedialog.asksaveasfile(initialfile = 'ExitCoordinates', defaultextension=".exit", filetypes = ftypes);
                                    if f is not None: # asksaveasfile return `None` if dialog closed with "cancel".
                                        if(bool(f.name)):
                                            filename = str(f.name);
                                        for exit in allExitHandler:                         
                                            f.write(str((exit.getX(),exit.getY()))+"\n");                          
                                        messagebox.showinfo(title="Success", message="Succesfully saved file: "+filename);                    
                                        rootTk.update();
                                #except:                         
                                #    messagebox.showerror(title="Unknown Error", message="Cannot save file: "+filename+"\n\nUnknown Error.");                    
                                #    rootTk.update();  
                            else:
                                messagebox.showwarning(title=None, message="No exits to be saved.");   
                                rootTk.update();    
                            
                    case 3:
                        if (isMouseAtSurface(btnPrevious)):    #If Previous Button was pressed
                            stage = 2;   
                        if (isMouseAtSurface(btnNext)and len(allEntityHandler)):    #If Simulate Button was pressed
                            print("Intializing Map and Entities: End.");
                            isSettingEntityLocation = False                      
        
                        if (isMouseAtSurface(btnLoadCoor)):   #If "Select File" / Load Coordinates Button was pressed                        
                            text_file_extensions = ['*.entity'];                        
                            ftypes = [
                                ('Entity coordinates file', text_file_extensions),
                                ('All files', '*')
                            ]       
                            filename = filedialog.askopenfilename(initialdir = dir_path, filetypes = ftypes)
                            if(filename != ''):
                                try:
                                    f = open(filename, "r");
                                    lines = f.readlines();                    
                                    coordinates = []
                                    for x in lines:     #Load all lines first and put them in a list. If one fails, throw a ValueError.
                                        data = ast.literal_eval(str(x));    #Read Line, get Tuple (x, y)
                                        coordinates.append((data[0], data[1]));                        
                                    cantBePlacedCount = 0;
                                    wasPlacedCount = 0;
                                    for data in coordinates:
                                        tempEntity = EntityObject(data[0], data[1], ENTITYRADIUS, entityMapHandler, None);           
                                        tempEntity.mapHandler.removeFromMatrix(data[0], data[1], tempEntity);           #remove the entity from ObjectMapHandler                                            
                                        if(not tempEntity.isCollidingWithEntitiesAndMap(mapImageMask)):            
                                            tempEntity.mapHandler.addToMatrix(data[0], data[1], tempEntity);    
                                            allEntityHandler.add(tempEntity);                                          
                                            wasPlacedCount+=1;       
                                        else:
                                            cantBePlacedCount+=1;                        
                                    if(cantBePlacedCount):
                                        message = "Failed to input "+str(cantBePlacedCount)+" entities. Possible collisions from existing entities have occured.";
                                        if(wasPlacedCount):
                                            message+="\n\nHowever, "+str(wasPlacedCount)+" were successfully placed.";
                                        messagebox.showwarning(title=None, message=message);                    
                                        rootTk.update();                        
                                except (FileNotFoundError):             
                                    messagebox.showerror(title="FileNotFound Error", message="Cannot load coordinates file. File was not found.");
                                    rootTk.update();
                                except (ValueError):
                                    messagebox.showerror(title="Value Error", message="Cannot load coordinates file. File may possibly be corrupted or wrong.");
                                    rootTk.update();
                                except: 
                                    messagebox.showerror(title="Unknown Error", message="Cannot load file. Unknown Error.");                    
                                    rootTk.update();                    

                        if (isMouseAtSurface(btnSaveCoor)):  #If "Save File" / Save coordinates Button was pressed
                            if(len(allEntityHandler)):
                                #try:
                                    filename = '';
                                    text_file_extensions = ['*.entity'];                        
                                    ftypes = [
                                        ('Entity coordinates file', text_file_extensions),
                                        ('All files', '*')
                                    ]       
                        
                                    f = filedialog.asksaveasfile(mode = 'w', initialfile = 'EntityCoordinates', defaultextension=".entity", filetypes = ftypes);
                                    if f is not None: # asksaveasfile return `None` if dialog closed with "cancel".
                                        if(bool(f.name)):
                                            filename = str(f.name);
                                        for entity in allEntityHandler:                         
                                            f.write(str((entity.getX(),entity.getY()))+"\n");                          
                                        messagebox.showinfo(title="Success", message="Succesfully saved file: "+filename);                    
                                        rootTk.update();
                                    #f.close();
                                #except:                         
                                #    messagebox.showerror(title="Unknown Error", message="Cannot save file: "+filename+"\n\nUnknown Error.");                    
                                #    rootTk.update();  
                            else:
                                messagebox.showwarning(title=None, message="No entities to be saved.");   
                                rootTk.update();                
                
        cameraMoveUpdate();  #check for camera movement     
        
        if(mapFileName is not None and pyg.mouse.get_focused()): #If a map has been selected and when pygame is receiving mouse input events (or, in windowing terminology, is "active" or has the "focus").              
            #check for mouse indefinite press ============================================================================================================================
            pressed_mouse =  pyg.mouse.get_pressed();  # returns [x, x, x] : Pressing left,middle or right click returns true to the corresponding x.
            if(pressed_mouse[0] or pressed_mouse[2]):      
                match stage:  
                    case 2:                        
                        if(pressed_mouse[0] and (pyg.mouse.get_pos()[1] < SCREEN_HEIGHT - panelSurface.get_height()
                                                or  pyg.mouse.get_pos()[0] <  SCREEN_WIDTH/2 - panelSurface.get_width()/2 
                                                or  pyg.mouse.get_pos()[0] >  SCREEN_WIDTH/2 + panelSurface.get_width()/2)
                            ): 
                            tempX = pyg.mouse.get_pos()[0]+camera["x"];
                            tempY = pyg.mouse.get_pos()[1]+camera["y"];                                
                            
                            if(tempX >=0 and tempX <=PLAYAREA_WIDTH and tempY >=0 and tempY <=PLAYAREA_WIDTH and not mapImageMask.get_at((tempX, tempY))):  
                                tempExit = ExitObject(tempX , tempY, EXITRADIUS);                                    
                                flag = True;                             
                                for exit in allExitHandler:
                                    if(collide_circle(tempExit, exit)):
                                        flag = False;
                                        break;
                                if(flag):
                                    allExitHandler.add(tempExit); 
                                    surfacePath = None;                                    

                        elif(pressed_mouse[2]): 
                            tempX = pyg.mouse.get_pos()[0]+camera["x"];
                            tempY = pyg.mouse.get_pos()[1]+camera["y"];

                            tempExit = ExitObject(tempX , tempY, EXITRADIUS);                                   

                            for exit in allExitHandler:
                                if(collide_circle(tempExit, exit)):                                
                                    exit.kill(); #allExitHandler.remove(exit);
                                    surfacePath = None;
                                    break;                               
                                
                    case 3:                        
                        if(pressed_mouse[0] and (pyg.mouse.get_pos()[1] < SCREEN_HEIGHT - panelSurface.get_height()
                                                or  pyg.mouse.get_pos()[0] <  SCREEN_WIDTH/2 - panelSurface.get_width()/2 
                                                or  pyg.mouse.get_pos()[0] >  SCREEN_WIDTH/2 + panelSurface.get_width()/2)
                            ): 
                            targetX = int(pyg.mouse.get_pos()[0]+camera["x"]);
                            targetY = int(pyg.mouse.get_pos()[1]+camera["y"]);        
                            
                            if(targetX >=0 and targetX <=PLAYAREA_WIDTH and targetY >=0 and targetY <=PLAYAREA_WIDTH):                                                             
                                tempEntity = EntityObject(targetX , targetY, ENTITYRADIUS, entityMapHandler, None );                                           
                                entityMapHandler.removeFromMatrix(targetX, targetY, tempEntity);           #remove the entity from ObjectMapHandler                                                                          
                                tempEntity.radius+=2;                                
                                if(tempEntity.isCollidingWithEntitiesAndMap(mapImageMask) == False):  
                                    entityMapHandler.addToMatrix(targetX, targetY, tempEntity);
                                    tempEntity.radius-=2;
                                    allEntityHandler.add(tempEntity);
                                        
                                if (pastMouseCoor is not None and pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]):  
                                    #If shift is pressed
                                    tempX,tempY = pastMouseCoor;
                                    tempX += camera["x"];
                                    tempY += camera["y"];
                                    deltaX = targetX - tempX;         #Check difference between X and targetX
                                    deltaY = targetY - tempY;         #Check difference between Y and targetY
                                    direction = atan2(deltaY,deltaX); #calculate direction just to be safe in some special cases where potential stuck entity.                                                                                                                     
                                    distance = int(math.sqrt(deltaX**2 + deltaY**2));                                    
                                    
                                    for i in nmpy.arange(-ENTITYRADIUS*2, distance-ENTITYRADIUS*2, 1):
                                        tempX += 1 * cos(direction); 
                                        tempY += 1 * sin(direction);                                         
                                        
                                        tempEntity = EntityObject(int(tempX) , int(tempY), ENTITYRADIUS, entityMapHandler, None);                                           
                                        entityMapHandler.removeFromMatrix(int(tempX), int(tempY), tempEntity);           #remove the entity from ObjectMapHandler                                                                          
                                        tempEntity.radius+=4;
                                        if(tempEntity.isCollidingWithEntitiesAndMap(mapImageMask) == False):  
                                            entityMapHandler.addToMatrix(int(tempX), int(tempY), tempEntity);
                                            tempEntity.radius-=4;
                                            allEntityHandler.add(tempEntity);
                                
                                    
                                                 

                        elif(pressed_mouse[2]): 
                            tempX = pyg.mouse.get_pos()[0]+camera["x"];
                            tempY = pyg.mouse.get_pos()[1]+camera["y"];

                            tempEntity = EntityObject( tempX , tempY, ENTITYRADIUS, entityMapHandler, None);            
                            entityMapHandler.removeFromMatrix(tempX, tempY, tempEntity);           #remove the entity from ObjectMapHandler       
                            
                            collidedEntity =  tempEntity.getCollidingEntity();        
                            if(collidedEntity is not None):
                                #print("Killed: ",collidedEntity.getLocation());
                                collidedEntity.mapHandler.removeFromMatrix(collidedEntity.getX(), collidedEntity.getY(), collidedEntity);                            
                                #tempEntity.kill();#
                                allEntityHandler.remove(collidedEntity);    
                                
                

        
        #Render =============================================================================================================================================                           
        mainSurface.fill(pyg.Color(100,100,100)); #draw background layer first.                   
        if(mapVisualSurface): 
            mainSurface.blit(mapVisualSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen
        elif(mapSurface):
            mainSurface.blit(mapSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen       
        
        #Draw all the entites
        for entity in allEntityHandler:                
            entity.draw(mainSurface, camera);       
        
        #Draw all the exits
        for exit in allExitHandler:                
            exit.draw(mainSurface, camera);     
        
        if(DEBUG_MODE):   #Show all matrix cells           
            for coordinate in entityMapHandler.getAllMatrixKeys():      
                if (coordinate[0]>=0 and coordinate[0]<=PLAYAREA_WIDTH/entityMapHandler.getCellSize() and coordinate[1]>=0 and coordinate[1]<PLAYAREA_HEIGHT/entityMapHandler.getCellSize() ):
                    pyg.draw.rect(mainSurface, (200,0,0), pyg.Rect(coordinate[0]*entityMapHandler.getCellSize()-camera["x"], coordinate[1]*entityMapHandler.getCellSize()-camera["y"], entityMapHandler.getCellSize(),entityMapHandler.getCellSize()), 1);
        
        
        #Draw top elements  ================================================================================================================================  
        x = SCREEN_WIDTH/2 - panelSurface.get_width()/2;
        y = SCREEN_HEIGHT  - panelSurface.get_height();
        yTextNextLine = 22;
        match stage:
            case 1: # ================================================================================================================================  
                mainSurface.blit(tabSurface1, (x, y-tabSurface1.get_height())); 
                mainSurface.blit(panelFont.render("   Step 1 : Loading the map", True, (255,255,255)), (x, y-tabSurface1.get_height()));        
                mainSurface.blit(panelSurface, (x,y));  #Top Panel Background 
                x+=6;
                y+=7;
                #x+=panelButtonSurface.get_width() + 10;
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                btnSelectMap.left =x;
                btnSelectMap.top  =y;             
                text = "Select File";
                mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2)); 
                if( mapFileName is not None):
                    if(len(mapFileName)>30):
                        mainSurface.blit(panelFont.render("..."+mapFileName[len(mapFileName)-30:len(mapFileName)], True, (255,255,255)), (x+10+btnSelectMap.width, y));
                    else:
                        mainSurface.blit(panelFont.render(""+mapFileName, True, (255,255,255)), (x+10+btnSelectMap.width, y));            
                y+=panelButtonSurfaceGreen.get_height()+5;    
                
                mainSurface.blit(panelMapSurface,(x,y));  #Top Panel > Map Panel  
                x+=panelMapSurface.get_width()+5;
                
                text = "\tThe selected image will be the basis of the obstacles and represent the area to be simulated. White/Transparent parts will be walkable.";
                for line in textwrap.wrap(text, 32):
                    mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                    y+=yTextNextLine;
                text = "\tPlease select an image with white or transparency.";    
                for line in textwrap.wrap(text,32):
                    mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                    y+=yTextNextLine; 
                            
                if( mapFileName is not None):  
                    x += 225;
                    y= SCREEN_HEIGHT - panelSurface.get_height() + 8;
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    btnSelectBG.left = x;
                    btnSelectBG.top  = y;                                 
                    text = "Select File";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));             
                    if( mapVisualFileName is not None):
                        if(len(mapVisualFileName)>30):
                            mainSurface.blit(panelFont.render("..."+mapVisualFileName[len(mapVisualFileName)-30:len(mapVisualFileName)], True, (255,255,255)), (x+10+btnSelectBG.width, y));
                        else:
                            mainSurface.blit(panelFont.render(""+mapVisualFileName, True, (255,255,255)), (x+10+btnSelectBG.width, y));                            
                    
                    y+=panelButtonSurfaceGreen.get_height()+5;                                   
                    mainSurface.blit(panelMapVisualSurface,(x,y));
                    x+=panelMapVisualSurface.get_width()+5;                
                    text = "     (Optional) Load a colored version of the map.";
                    for line in textwrap.wrap(text, 30):
                        mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                        y+=22;   
                    text = "     This will be used for visual background and is not completely necessary for the simulation to function.";
                    for line in textwrap.wrap(text, 32):
                        mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                        y+=22;                                           
                        
                    x = SCREEN_WIDTH/2 + panelSurface.get_width()/2 - panelButtonSurfaceGreen.get_width() - 6;
                    y = SCREEN_HEIGHT - panelSurface.get_height() + 8;
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    btnNext.left = x;
                    btnNext.top  = y;                 
                    text = "Next";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));                 
                    
            
            case 2: # ================================================================================================================================  
                #Draw at mouse cursor target
                pyg.draw.circle(mainSurface, (255,255,255), [pyg.mouse.get_pos()[0], pyg.mouse.get_pos()[1]], EXITRADIUS, 1);                
                
                mainSurface.blit(tabSurface2, (x+tabSurface2.get_width(), y-tabSurface2.get_height())); 
                mainSurface.blit(panelFont.render("   Step 2 : Marking the exit(s)", True, (255,255,255)), (x+tabSurface2.get_width(), y-tabSurface2.get_height()));        
                            
                mainSurface.blit(panelSurface, (x,y));  #Top Panel Background             
                x+=6;
                y+=8;            
                
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                btnPrevious.left =x;
                btnPrevious.top  =y;             
                text = "Previous";
                mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));             
                x += panelButtonSurfaceGreen.get_width()+5;                                               
                
                mainSurface.blit(panelFont.render("Numbers of exits: "+str(len(allExitHandler)), True, (255,255,255)), (x, y));        
                y+=yTextNextLine;
                y+=yTextNextLine;
                y+=yTextNextLine;
                mainSurface.blit(panelFont.render("WASD or Arrow Keys to move.", True, (255,255,255)), (x, y));        
                y+=yTextNextLine;
                mainSurface.blit(panelFont.render("Left Click to place an exit.", True, (255,255,255)), (x, y));        
                y+=yTextNextLine;
                mainSurface.blit(panelFont.render("Right Click to remove an exit.", True, (255,255,255)), (x, y));        
                
                
                x += 225 + 5;
                y = SCREEN_HEIGHT  - panelSurface.get_height() + 8;            
            
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));     
                btnLoadCoor.left =x;
                btnLoadCoor.top  =y;      
                y+=2;
                text = "Load File";   
                mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y));                                     
                x += panelButtonSurfaceGreen.get_width()+5;                         
                
                text = "Load previously saved exit coordinates.";                                  
                for line in textwrap.wrap(text, 25):
                    mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                    y+=22;               
                x -= panelButtonSurfaceGreen.get_width()+5;
                y += 10;
                
                if(len(allExitHandler)):
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    btnSaveCoor.left =x;
                    btnSaveCoor.top  =y;  
                    y+=2;                          
                    text = "Save File";   
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y));                         
                    x += panelButtonSurfaceGreen.get_width() + 5;

                    text = "Save current exit coordinates into a file for future use.";                              
                    for line in textwrap.wrap(text, 25):
                        mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                        y+=22;   
                    
                    x -= panelButtonSurfaceGreen.get_width()+5;
                    y+=5;

                text = "The exit coordinates are in *.exit file format.";   
                for line in textwrap.wrap(text, 35):
                    mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                    y+=22;                                    
                
                x = SCREEN_WIDTH/2 + panelSurface.get_width()/2 - (panelButtonSurfaceGreen.get_width()+panelMiniMapSurface.get_width()+5+5);
                y = SCREEN_HEIGHT - panelSurface.get_height() + 8;
                
                if(mapVisualFileName is not None) :
                    panelMiniMapSurface.blit(panelMapVisualSurface, (0,0));         
                else:
                    panelMiniMapSurface.blit(panelMapSurface, (0,0));         
                
                scaleX = panelMapSurface.get_width()/PLAYAREA_WIDTH;
                scaleY = panelMapSurface.get_height()/PLAYAREA_HEIGHT;
                pyg.draw.rect(panelMiniMapSurface, pyg.Color(0,0,0), 
                            pyg.Rect(camera["x"]*scaleX, camera["y"]*scaleY,  
                                    SCREEN_WIDTH*scaleX, SCREEN_HEIGHT*scaleY),
                            1);
                mainSurface.blit(panelMiniMapSurface,(x,y));
                
                            
                if(len(allExitHandler)):
                    
                    x = SCREEN_WIDTH/2 + panelSurface.get_width()/2 - panelButtonSurfaceGreen.get_width() - 6;
                    y = SCREEN_HEIGHT - panelSurface.get_height() + 8;
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    btnNext.left = x;
                    btnNext.top  = y;                 
                    text = "Next";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2)); 
            
                        
                    
            case 3: # ================================================================================================================================  
                #Draw at mouse cursor target
                pyg.draw.circle(mainSurface, (255,255,255), [pyg.mouse.get_pos()[0], pyg.mouse.get_pos()[1]], ENTITYRADIUS, 1);                
                
                #Draw line if shift is pressed
                if (pastMouseCoor is not None and pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]):  
                    #Draw at mouse cursor target  
                    selectionSurface = pyg.Surface([SCREEN_WIDTH, SCREEN_HEIGHT]).convert_alpha();    
                    selectionSurface.fill(pyg.Color(0,0,0,0));
                    pyg.draw.circle(selectionSurface, (255,255,255,90), pastMouseCoor, ENTITYRADIUS, 0);                                
                    pyg.draw.circle(selectionSurface, (255,255,255,90), pyg.mouse.get_pos(), ENTITYRADIUS, 0);                
                    pyg.draw.line(selectionSurface, pyg.Color(255,255,255,80), pastMouseCoor, pyg.mouse.get_pos(), (ENTITYRADIUS*2)-1);        
                    mainSurface.blit(selectionSurface, (0,0));
                
                mainSurface.blit(tabSurface3, (x+tabSurface3.get_width()*2, y-tabSurface3.get_height())); 
                mainSurface.blit(panelFont.render("   Step 3 : Placing the entities", True, (255,255,255)), (x+tabSurface3.get_width()*2, y-tabSurface3.get_height()));        
                            
                mainSurface.blit(panelSurface, (x,y));  #Top Panel Background             
                x+=6;
                y+=8;            
                
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                btnPrevious.left =x;
                btnPrevious.top  =y;             
                text = "Previous";
                mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));             
                x += panelButtonSurfaceGreen.get_width()+5;                         
                                    
                mainSurface.blit(panelFont.render("Numbers of entitiies: "+str(len(allEntityHandler)), True, (255,255,255)), (x, y));        
                y+=yTextNextLine;
                if(DEBUG_MODE): #Draw matrix cells
                    mainSurface.blit(panelFont.render("Matrix Cells: "+str(entityMapHandler.getMatrixLength()), True, (255,255,255)), (x, y));                                            
                y+=yTextNextLine;
                mainSurface.blit(panelFont.render("WASD or Arrow Keys to move.", True, (255,255,255)), (x, y));        
                y+=yTextNextLine;
                mainSurface.blit(panelFont.render("Left Click to place an entity.", True, (255,255,255)), (x, y));        
                y+=yTextNextLine;
                text = "Hold Shift + Left Click to place multiple entities."                
                for line in textwrap.wrap(text, 30):
                    mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                    y+=22;    
                #y+=yTextNextLine;
                mainSurface.blit(panelFont.render("Right Click to remove an entity.", True, (255,255,255)), (x, y));        
                
                x += 225 + 5;
                y = SCREEN_HEIGHT  - panelSurface.get_height() + 8;            
            
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));     
                btnLoadCoor.left =x;
                btnLoadCoor.top  =y;      
                y+=2;
                text = "Load File";   
                mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y));                                     
                x += panelButtonSurfaceGreen.get_width()+5;                         
                
                text = "Load previously saved entity coordinates.";                                  
                for line in textwrap.wrap(text, 25):
                    mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                    y+=22;               
                x -= panelButtonSurfaceGreen.get_width()+5;
                y += 10;
                
                if(len(allEntityHandler)):
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    btnSaveCoor.left =x;
                    btnSaveCoor.top  =y;  
                    y+=2;                          
                    text = "Save File";   
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y));                         
                    x += panelButtonSurfaceGreen.get_width() + 5;

                    text = "Save current entity coordinates into a file for future use.";                              
                    for line in textwrap.wrap(text, 25):
                        mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                        y+=22;   

                    x -= panelButtonSurfaceGreen.get_width()+5;
                    y+=5;

                text = "The entity coordinates are in *.entity file format.";   
                for line in textwrap.wrap(text, 35):
                    mainSurface.blit(panelFont.render(line, True, (255,255,255)), (x, y));            
                    y+=22;                                    
                
                x = SCREEN_WIDTH/2 + panelSurface.get_width()/2 - (panelButtonSurfaceGreen.get_width()+panelMiniMapSurface.get_width()+5+5);
                y = SCREEN_HEIGHT - panelSurface.get_height() + 8;
                
                if(mapVisualFileName is not None) :
                    panelMiniMapSurface.blit(panelMapVisualSurface, (0,0));         
                else:
                    panelMiniMapSurface.blit(panelMapSurface, (0,0));            
                scaleX = panelMapSurface.get_width()/PLAYAREA_WIDTH;
                scaleY = panelMapSurface.get_height()/PLAYAREA_HEIGHT;
                pyg.draw.rect(panelMiniMapSurface, pyg.Color(0,0,0), 
                            pyg.Rect(camera["x"]*scaleX, camera["y"]*scaleY,  
                                    SCREEN_WIDTH*scaleX, SCREEN_HEIGHT*scaleY),
                            1);
                mainSurface.blit(panelMiniMapSurface,(x,y));
                                        
                
                if(len(allEntityHandler)):
                    x = SCREEN_WIDTH/2 + panelSurface.get_width()/2 - panelButtonSurfaceGreen.get_width() - 6;
                    y = SCREEN_HEIGHT - panelSurface.get_height() + 8;
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    btnNext.left = x;
                    btnNext.top  = y;                    
                    text = "Simulate";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2)); 
                    
                    
        """ Case 4: # ================================================================================================================================  
        
        Failsafe timer: 10 seconds

    Counts down the moment an entity succesfully exits and resets with consecutive entity that exits. This is used to terminate the simulation in case entities gets stuck indefintely.

    Ideally, the simulation is terminated when there are no entities left.
        """
        #refresh the display and render    
        display.update();    
    #===============================================================================================================================================================================   
    for entity in allEntityHandler:
        x,y = entity.getLocation();
        allEntityLocation[x, y] = entity.color;
        
        
        
        
    
    
    
    
    
    
        
        
        
        
        
        
    #Third Pygame Loop, Initialization of pathfinding of entities =============================================================================================================================
    print("Intializing Pathfinding: Start.");
    #give all entites random places to go

    isPathGenerating = True; 
    entitiesHavePath = True;
    def pathGenerationFunction():    
        global isPathGenerating, surfacePath, entitiesHavePath, flowFieldPaths;
        if(surfacePath is None):
            surfacePath = pyg.Surface((mapImage.get_width(), mapImage.get_height())).convert_alpha();
            surfacePath.fill(pyg.Color(0,0,0,0));
            ff = FlowField(mapImage, mapImage.get_width(), mapImage.get_height(), ENTITYRADIUS);
            print("Adding pathfield goals:");
            for exit in allExitHandler:
                ff.addGoal(exit.getX(), exit.getY());
            ff.generatePathField();    
            flowFieldPaths = ff.matrix;    
            print("PathField generated.");
        
            oldMax = ff.maxValue; 
            color = pyg.Color(0,0,0); 
            for coordinate in flowFieldPaths:       
                oldValue = flowFieldPaths[coordinate];        
                #new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min
                scaledValue =  ( (oldValue-0) / (oldMax-0) ) * (300 - 0) + 0
                color.hsla = (scaledValue, 100, 50, 100); 
                #H = [0, 360], S = [0, 100], L = [0, 100], A = [0, 100].    
                surfacePath.fill(color, (coordinate, (1,1)) );        
            print("Pathfield surface drawn.");
        
        for entity in allEntityHandler:     
            if not(entity.getLocation() in flowFieldPaths):
                entitiesHavePath = False    
            else:
                entity.setFlowField(flowFieldPaths);  
            """
            if (entity.getLocation() in flowFieldPaths):
                entity.setFlowField(flowFieldPaths);  
            else:
                entitiesHavePath = False    
            """
        
        isPathGenerating = False;        


    
    pathThread = threading.Thread(target = pathGenerationFunction);
    pathThread.daemon  = True; #daemon, a Boolean value. This must be set before start() is called. When a process exits, it attempts to terminate all of its daemonic child processes.    
    pathThread.start();          



    try:
        debugFont = pyg.font.Font(dir_path+"/Assets/FreeSans.ttf", 30); 
    except:
        debugFont = pyg.font.Font(None, 30);  
        
    counter = 1;

    isPathFindingInitializing= True;
    while(isPathFindingInitializing):     
        #check for pyg.events ============================================================================================================================       
        for event in pyg.event.get():             #Getting the current event list available and execute action
            if event.type == pyg.VIDEORESIZE:     #when window is resized
                windowResize(event);        
                panelSurface = pyg.Surface([panelSurface.get_width(), SCREEN_HEIGHT]).convert();
                panelSurface.fill(pyg.Color(130, 62, 42));
                
            if (event.type== pyg.locals.QUIT):   #when exit buttton event is pressed                      
                timeToStop();
            
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_F2:
                    DEBUG_MODE = not DEBUG_MODE;
                        
            #if event.type == pyg.MOUSEBUTTONDOWN:# or event.type == pyg.KEYDOWN:
            #    isPathFindingInitializing = False;
                
                
        if(mapFileName is not None and pyg.mouse.get_focused()): #If a map has been selected and when pygame is receiving mouse input events (or, in windowing terminology, is "active" or has the "focus").   
            cameraMoveUpdate();  #check for camera movement
        #Update =============================================================================================================================================        
        
        
        
        #Render =============================================================================================================================================                           
        mainSurface.fill(Color(100,100,100)); #draw background layer first.               
        
        if(mapVisualSurface): 
            mainSurface.blit(mapVisualSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen
        elif(mapSurface):
            mainSurface.blit(mapSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen
            #mapVisualFileName
                
        #Draw all the entites
        for entity in allEntityHandler:                
            entity.draw(mainSurface, camera);                   
        
        #Draw all the exits
        for exit in allExitHandler:                
            exit.draw(mainSurface, camera);   
        
        tempSurface = pyg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha();    
        tempSurface.fill(pyg.Color(0,0,0,150));
        mainSurface.blit(tempSurface, (0,0));
        
        #Draw Text
        if(isPathGenerating):                  
            text = debugFont.render("Generating paths, please wait"+(floor(counter/25)%6)*".", True, (255,255,255))
            mainSurface.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2));
        else:
            text = debugFont.render("Path generation complete."+(floor(counter/25)%6)*".", True, (255,255,255))
            mainSurface.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2));        
            isPathFindingInitializing = False;
            if(not entitiesHavePath):
                messagebox.showerror(title="Error", message="Sorry, exit(s) are not reachable to some of the entities. \nSaid entities will not move and not be included to the traffic data.");
                rootTk.update();          
            
        #refresh the display and render 
        display.update();         
        
        if(counter <500):
            counter+=1;
        else:
            counter = 1;
    #ad
    maxEntityCount = len(allEntityHandler);   
    maxExitCount = len(allExitHandler);
    print("Initializing Pathfinding: End.");        
    #===============================================================================================================================================================================   












    #Initiliazile things to be used for Monte Carlo Simulation
    monteCarloSimMax = 10;
    monteCarloSimIteration = 0;
    isMonteCarloSimulating = False;    
    isDoneOnce = True;
    
    allEntityLocationList = [];      
    trafficMatrixList = [];
    trafficMaxValueList = [];
    surfaceTrafficList = [];
    surfaceTrafficLegendList = [];
        
    
    
    
    while(isMonteCarloSimulating or isDoneOnce):
        isDoneOnce = False;
        
        if(isMonteCarloSimulating):
            allEntityHandler.empty();   
            entityMapHandler.removeAll();
            for location in allEntityLocation:    
                x, y = location;
                tempEntity = EntityObject(x, y, ENTITYRADIUS, entityMapHandler, allEntityLocation[location]);            
                if not(tempEntity.getLocation() in flowFieldPaths):
                    entitiesHavePath = False    
                else:
                    tempEntity.setFlowField(flowFieldPaths);  
                entityMapHandler.addToMatrix(x, y, tempEntity);
                allEntityHandler.add(tempEntity);        
                
        
        
        
        #Fourth Pygame Loop, The Main Simulation ==========================================================================================================================================    
        clock.tick(FRAMERATE);

        prevTime = time.time();

        endTimerTick = pyg.time.get_ticks() #starter tick
        ENDTIMERSECONDS = 12;
        isEndTimerTicking = False;
        endTimePrevSecond = 0;

        simulationTime = time.time();

        trafficMatrix = {};

        panelButtonSurfaceGreen = pyg.Surface([102, 26]).convert();       #The button 
        panelButtonSurfaceGreen.fill(pyg.Color(23, 37, 7));                #Set Color of the shadow edge
        pyg.draw.rect(panelButtonSurfaceGreen, pyg.Color(50, 96, 42), [2,2,96, 20]);   #Draw Color of the top of the button

        panelButtonSurfaceGrey = pyg.Surface([102, 26]).convert();       #The button 
        panelButtonSurfaceGrey.fill(pyg.Color(23, 23, 23));                #Set Color of the shadow edge
        pyg.draw.rect(panelButtonSurfaceGrey, pyg.Color(69, 69, 69), [2,2,96, 20]);   #Draw Color of the top of the button

        isTogMap       = True;
        isTogFlowfield = False;
        isTogEntities  = True;
        isTogExits     = True;

        btnTogMap       = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle Map
        btnTogFlowfield = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle FlowField for pathfinding
        btnTogEntities  = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle Entity
        btnTogExits     = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle Exits

        try:
            debugFont = pyg.font.Font(dir_path+"/Assets/FreeSans.ttf", 16); 
            panelLargeFont = pyg.font.Font(dir_path+"/Assets/FreeSans.ttf", 30); 
        except:
            debugFont = pyg.font.Font(None, 16);  
            panelLargeFont = pyg.font.Font(None, 30);  
            
            

        isSimulationRunning = True;
        print("Simulation: Start.");
        if(isMonteCarloSimulating):
            print("Simulation #",monteCarloSimIteration);    
        while(isSimulationRunning):       
            #set max delay for the next Tick of the loop, limiting the framerate.
            clock.tick(FRAMERATE);
            
            #compute the detla time, used for framerate independence    
            now = time.time();
            deltaTime = now - prevTime;
            prevTime = now;        
            
            #check for pyg.events ============================================================================================================================       
            for event in pyg.event.get():             #Getting the current event list available and execute action
                if event.type == pyg.VIDEORESIZE:     #when window is resized
                    windowResize(event);            
                    
                if (event.type== pyg.locals.QUIT):   #when exit buttton event is pressed   
                    print("Simulation: End.");       
                    timeToStop();
                    
                if event.type == pyg.KEYDOWN:
                    if event.key == pyg.K_F2:
                        DEBUG_MODE = not DEBUG_MODE;
                        
                if event.type == pyg.MOUSEBUTTONUP: #for mouse click
                    if (isMouseAtSurface(btnTogMap)):
                        isTogMap = not isTogMap;
                    if (isMouseAtSurface(btnTogFlowfield)):
                        isTogFlowfield = not isTogFlowfield;                
                    if (isMouseAtSurface(btnTogEntities)):
                        isTogEntities = not isTogEntities;
                    if (isMouseAtSurface(btnTogExits)):
                        isTogExits = not isTogExits;
                
            cameraMoveUpdate();  #check for camera movement 
                    
            #Update & Render =============================================================================================================================================                 
            mainSurface.fill(pyg.Color(100,100,100)); #draw background layer first.                    
            
            #Show Map
            if(isTogMap):   
                if(mapVisualSurface): 
                    mainSurface.blit(mapVisualSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen
                else:
                    mainSurface.blit(mapSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen
            
            #Show the Djistra's Map / Flowfield. 
            if(isTogFlowfield):
                mainSurface.blit(surfacePath, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));     
            
            #Draw all the exits 
            if(isTogExits):
                for exit in allExitHandler:                
                    exit.draw(mainSurface, camera);         
                
            #Draw and Update all the entites =========================================================================
            eXLeftBound = -ENTITYRADIUS+camera["x"];    
            eXRightBound = camera["x"] + SCREEN_WIDTH + ENTITYRADIUS;
            eYUpBound = -ENTITYRADIUS+camera["y"] ;
            eYDownBound = camera["y"] + SCREEN_HEIGHT + ENTITYRADIUS;
            
            isEndTimerReset = False;
            for entity in allEntityHandler:    
                x, y = entity.getLocation(); 
                flagBreak = False;
                for exit in allExitHandler:
                    #                
                    if ((abs(x-exit.getX()) <= EXITRADIUS) and (abs(y-exit.getY()) <= EXITRADIUS) and collide_circle(entity, exit)):    
                        entityMapHandler.removeFromMatrix(x, y, entity); 
                        #entityMapHandler.removeFromMatrix(entity.getX(), entity.getY(), entity); 
                        entity.kill();   
                        allEntityHandler.remove(entity);                    
                        if(isEndTimerTicking):
                            endTimerTick = pyg.time.get_ticks() #Restart timer
                        else:
                            print("Timer started.");
                            isEndTimerTicking=True; 
                            isEndTimerReset=True;                                    
                        flagBreak = True;
                        break;                  
                
                if(flagBreak == False):
                    x, y = entity.update();                    

                    if (    x>= eXLeftBound and x <= eXRightBound 
                        and y>= eYUpBound   and y <= eYDownBound  
                        and isTogEntities                       ): #Render Culling                
                        entity.draw(mainSurface, camera);       

                    if(entity.isFlowFieldSet()):
                        if ((x,y) in trafficMatrix):  #if keyword exists
                            trafficMatrix[x,y] = trafficMatrix[x,y] + 1;                
                        else:
                            trafficMatrix[x,y] = 1;        

                
            if(isEndTimerTicking):  #For some reason this has to be here after entity checking, otherwise it will lag down
                seconds = (pyg.time.get_ticks()-endTimerTick)/1000 #calculate how many seconds            
                if (seconds>ENDTIMERSECONDS or len(allEntityHandler) == 0):
                    isSimulationRunning = False;
                elif (endTimePrevSecond != floor(ENDTIMERSECONDS-seconds) and endTimePrevSecond <= 5 and endTimePrevSecond !=0):
                    if(isEndTimerReset):
                        print("Timer reset. Simulation is extended.");
                    else:
                        print("Simulation ends in: ",str(floor(ENDTIMERSECONDS-seconds)+1));  
                endTimePrevSecond = floor(ENDTIMERSECONDS-seconds);      
            
            #Render UI ==========================================================================================
            x = 10;
            
            if(isMonteCarloSimulating):
                y = 10;            
                text = "Running Simulation #"+str(monteCarloSimIteration)+" of "+str(monteCarloSimMax);
                #mainSurface.blit(pyg.transform.scale(panelFont.render(text, True, (255,255,255)), (panelFont.size(text)[0]*3,panelFont.size(text)[1]*3)), (x, y));                         
                mainSurface.blit(panelLargeFont.render(text, True, (255,255,255)), (x, y));   

            
            y = SCREEN_HEIGHT - panelButtonSurfaceGreen.get_height()*1.5;    
            
            #text = "Toggle: ";
            #mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
            #x += panelButtonSurfaceGreen.get_width()+5;
            text = "Toggle: ";
            mainSurface.blit(panelFont.render(text, True, (0,0,0)), (x, y));         
            x += panelFont.size(text)[0]+5;
            
            btnTogMap.left = x;
            btnTogMap.top = y;
            if(isTogMap):
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));
            else:
                mainSurface.blit(panelButtonSurfaceGrey , (x,y));
            text = "Map";
            mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
            x+=panelButtonSurfaceGreen.get_width()+5;
            
            btnTogFlowfield.left = x;
            btnTogFlowfield.top = y;
            if(isTogFlowfield):
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));
            else:
                mainSurface.blit(panelButtonSurfaceGrey , (x,y));
            text = "Flowfield";
            mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
            x+=panelButtonSurfaceGreen.get_width()+5;
            
            btnTogEntities.left = x;
            btnTogEntities.top = y;
            if(isTogEntities):
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));
            else:
                mainSurface.blit(panelButtonSurfaceGrey , (x,y));
            text = "Entities";
            mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
            x+=panelButtonSurfaceGreen.get_width()+5;        
            
            btnTogExits.left = x;
            btnTogExits.top = y;
            if(isTogExits):
                mainSurface.blit(panelButtonSurfaceGreen , (x,y));
            else:
                mainSurface.blit(panelButtonSurfaceGrey , (x,y));
            text = "Exits";
            mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
            x+=panelButtonSurfaceGreen.get_width()+5;        
            
            
            x = SCREEN_WIDTH-150;
            y = 10;
            yTextNextLine = 25;               
                
            #Write the FPS counter:        
            text = debugFont.render("FPS: " +str(round(clock.get_fps(),2)), True, (0,0,0))
            mainSurface.blit(text, (x, y));
            y+=yTextNextLine;
            #Write the delta time counter:
            text = debugFont.render("Latency: " +str(round(deltaTime*1000))+"ms", True, (0,0,0))
            mainSurface.blit(text, (x, y));
            y+=yTextNextLine;
            y+=yTextNextLine;        

            if(DEBUG_MODE): #Draw Debug Information =======================================================        
                #uncomment to draw a grid with the cellsize (which is the size of entities). Highliight every 10th  
                """  
                cellsize = objectMatrix.getCellSize();    
                for x in range(0, PLAYAREA_HEIGHT, floor(cellsize)):         #Horizontal Lines
                    image = pyg.Surface([PLAYAREA_WIDTH, 1]);   
                    if x%(cellsize*10) == 0:     
                        image.fill(pyg.Color(180,180,180));    
                    else :
                        image.fill(pyg.Color(120,120,120));    
                    rect = image.get_rect()
                    rect.center =  (PLAYAREA_WIDTH/2, x-camera["y"])       
                    mainSurface.blit(image, rect);         
                for x in range(0, PLAYAREA_WIDTH, floor(cellsize)):           #Vertical Lines
                    image = pyg.Surface([1, PLAYAREA_HEIGHT]);        
                    if x%(cellsize*10) == 0:      
                        image.fill(pyg.Color(180,180,180));    
                    else :
                        image.fill(pyg.Color(120,120,120));    
                    rect = image.get_rect()
                    rect.center =  (x-camera["x"], PLAYAREA_HEIGHT/2)       
                    mainSurface.blit(image, rect); 
                """         
                #Uncomment to highlight all the matrices known.                       
                for coordinate in entityMapHandler.getAllMatrixKeys():      
                    if (coordinate[0]>=0 and coordinate[0]<=PLAYAREA_WIDTH/entityMapHandler.getCellSize() and coordinate[1]>=0 and coordinate[1]<PLAYAREA_HEIGHT/entityMapHandler.getCellSize() ):
                        pyg.draw.rect(mainSurface, (200,0,0), pyg.Rect(coordinate[0]*entityMapHandler.getCellSize()-camera["x"], coordinate[1]*entityMapHandler.getCellSize()-camera["y"], entityMapHandler.getCellSize(),entityMapHandler.getCellSize()), 1);                
            
                
                text = debugFont.render("Window Size: ", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                text = debugFont.render("["+str(SCREEN_WIDTH)+","+str(SCREEN_HEIGHT)+"]", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                y+=yTextNextLine;       
                
                #Write Entity Count
                text = debugFont.render("Entities: "+str(len(allEntityHandler)), True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                #Write Matrix cell count
                text = debugFont.render("Matrix Cells: "+str(entityMapHandler.getMatrixLength()), True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                y+=yTextNextLine;
                
                #Write Play Area
                text = debugFont.render("Map Size: ", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                text = debugFont.render("["+str(PLAYAREA_WIDTH)+","+str(PLAYAREA_HEIGHT)+"]", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                y+=yTextNextLine;
                
                #Write Camera Location
                text = debugFont.render("Camera Location: ", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                text = debugFont.render("["+str(round(camera["x"]))+","+str(round(camera["y"]))+"]", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                
                y+=yTextNextLine;
                y+=yTextNextLine;
                x-=100;
                text = debugFont.render("Group Handler "+str(sys.getsizeof(allEntityHandler))+" bytes", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                text = debugFont.render("Map Matrix handler: "+str(sys.getsizeof(entityMapHandler))+" bytes", True, (0,0,0))
                mainSurface.blit(text, (x, y));
                y+=yTextNextLine;
                y+=yTextNextLine;
                
            if(round(clock.get_fps(),2)<FRAMERATE/3):
                text = debugFont.render("WARNING: FPS low.", True, (0,0,0))
                mainSurface.blit(text, (SCREEN_WIDTH-250, y));
                y+=yTextNextLine;
                text = debugFont.render("This may result in unexpected", True, (0,0,0))
                mainSurface.blit(text, (SCREEN_WIDTH-250, y));
                y+=yTextNextLine;
                text = debugFont.render("physics behaviors and errors.", True, (0,0,0))
                mainSurface.blit(text, (SCREEN_WIDTH-250, y));
                y+=yTextNextLine;        

            #refresh the display and render 
            display.update();   

        #simulationTime = time.strftime("%H:%M:%S", time.gmtime(time.time() - simulationTime));
        simulationTime = datetime.timedelta(seconds = round(time.time() - simulationTime, 2));
        print("Simulation: End.\n");
        
        
        
        
        
        
        
            
            
            
            
            
            
            
            
            
            
        #The Data Analysis & Presentation =======================================================================================================================================
        trafficMinValue = 1;
        trafficMaxValue = 0;
        colorTrafficMaxValue = 350;
        #scaledTrafficMaxValue = 0;

        surfaceTraffic = pyg.Surface((mapImage.get_width(), mapImage.get_height())).convert_alpha();
        surfaceTraffic.fill(pyg.Color(0,0,0,0));
        
        #set the surfaceTrafficLegend size
        surfaceTrafficLegend = pyg.Surface((230, 590)).convert_alpha();
        surfaceTrafficLegend.fill(pyg.Color(0,0,0,0));

        try:
            resultFont = pyg.font.Font(dir_path+"/Assets/FreeSans.ttf", 18); 
        except:
            resultFont = pyg.font.Font(None, 22);  

        isDataAnalysing = True;
        def dataAnalysisFunction():
            global surfaceTraffic, trafficMatrix, trafficMaxValue, ENTITYRADIUS, isDataAnalysing;
            global colorTrafficMaxValue, surfaceTrafficLegend, debugFont;
            global maxEntityCount, maxExitCount;                    
            global isMonteCarloSimulating, allEntityLocationList, allEntityLocation, monteCarloSimMax;
            global trafficMatrixList, trafficMaxValueList, surfaceTrafficList, surfaceTrafficLegendList;            
            
            tMCopy = trafficMatrix.copy();
            trafficMatrix = {};
            print("Data Analysis: Start.");
            
            print("Plotting entity locations data in simulation as filled circles to be used as traffic data...");
            for origin in tMCopy:   #Draw circle    
                ox, oy = origin;   
                for x in range(-ENTITYRADIUS, ENTITYRADIUS+1, 1):
                    height = int(math.sqrt(ENTITYRADIUS * (ENTITYRADIUS+1) - x * x)); 	#recall Pythagorean Theorem. # r+1 to adjust            
                    for y in range(-height, height+1, 1):
                        coordinate = x + ox, y + oy;
                        if (coordinate in trafficMatrix):   
                            # trafficMatrix[coordinate] += 1;  #This the old and wrong but beautiful          
                            trafficMatrix[coordinate] += tMCopy[origin];    #This is correct yet bland
                                                                    
                            if(trafficMaxValue <= trafficMatrix[coordinate]):                        
                                trafficMaxValue = trafficMatrix[coordinate];                   
                        else:
                            # trafficMatrix[coordinate] = 1;   #This the old and wrong but beautiful
                            trafficMatrix[coordinate] = tMCopy[origin];  #This is correct
                            
            print("Max Traffic Value: ",trafficMaxValue);
            
            print("Scaling traffic data to color and drawing surface...");
            trafficColor = pyg.Color(0,0,0); 
            #maxHueValue = 260;
            maxHueValue = 225;
            
            x = 5;
            y = 3;            
            
            text = resultFont.render("Simulation #"+str(len(surfaceTrafficLegendList)+1)+" of "+str(monteCarloSimMax), True, (0,0,0))
            if(isMonteCarloSimulating):                
                surfaceTrafficLegend.blit(text, (x, y));
            y+=text.get_height()+15;
            
                    
            if(trafficMaxValue>1):
                for coordinate in trafficMatrix:       
                    trafficValue = trafficMatrix[coordinate];        
                    #new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min          
                    #subtract from max hue value to flip values, making high as low and viceversa        
                    scaledValue = maxHueValue - (((trafficValue-0) / (trafficMaxValue-0)) * (maxHueValue - 0) + 0);

                    trafficColor.hsla = (scaledValue, 100, 60, 100); 
                    #H = [0, 360], S = [0, 100], L = [0, 100], A = [0, 100].    
                    surfaceTraffic.fill(trafficColor, (coordinate, (1,1)) );                    

                    #This is unnecessary, purely for visuals:
                    #start = time.time()
                    #while (time.time() < start + 0.000001):
                    #    pass;
                    #===
                    
                scaleScale = 2;    
                colorTrafficMaxValue = maxHueValue*scaleScale;        

                x += 40;    
                trafficColor = pyg.Color(0,0,0);     
                for row in range (0, int(colorTrafficMaxValue), 1): #draw color bar
                    trafficColor.hsla = (int(row/scaleScale), 100, 60, 100); 
                    surfaceTrafficLegend.fill(trafficColor, [x, y+row, 18, 1]);
                x +=10;  

                counter = 0;
                rangeMax = 10;    
                row = nmpy.linspace(-1, colorTrafficMaxValue-2, rangeMax);
                intensity  =  nmpy.linspace(trafficMaxValue, 1, rangeMax);

                for step in range(0,rangeMax,1):      #draw lines and text
                    surfaceTrafficLegend.fill(pyg.Color(0,0,0), [x, y+row[step], 20, 3]);#Draw Line;
                    text = resultFont.render(str(round(intensity[step],2)), True, (0,0,0));    
                    surfaceTrafficLegend.blit(text, (x+30, y+row[step]-(text.get_height()/2)));   #Draw text
                    if(counter==floor(rangeMax/2)):  #draw vertical text
                        text = resultFont.render("Heatmap Traffic Intensity:", True, (0,0,0))
                        pad = resultFont.render(str(trafficMaxValue)+".00 ", True, (0,0,0));
                        surfaceTrafficLegend.blit(pyg.transform.rotate(text, 90), (x+20+18+pad.get_width(), y+row[step]-(text.get_width()/2))); 
                    counter+=1;          

                x-=50;
                y+=colorTrafficMaxValue+15;

            text = resultFont.render("No. of Entities: "+str(maxEntityCount), True, (0,0,0))
            surfaceTrafficLegend.blit(text, (x, y));
            y+=text.get_height()+5;
            text = resultFont.render("No. of Exits: "+str(maxExitCount), True, (0,0,0))
            surfaceTrafficLegend.blit(text, (x, y));
            y+=text.get_height()+5;
            text = resultFont.render("Time Elapsed: "+str(simulationTime), True, (0,0,0))
            surfaceTrafficLegend.blit(text, (x, y));
            
            print("Data Interpretation: End.");
            
            if(isMonteCarloSimulating):
                allEntityLocationList.append(allEntityLocation);      
                trafficMatrixList.append(trafficMatrix);
                trafficMaxValueList.append(trafficMaxValue);
                surfaceTrafficList.append(surfaceTraffic);
                surfaceTrafficLegendList.append(surfaceTrafficLegend);                                      
                
                if(monteCarloSimIteration == monteCarloSimMax): #Simulations are complete. 
                    mtTrafficMatrix = {};
                    mtTrafficMaxValue = 1;
                    mtSurfaceTraffic = pyg.Surface((surfaceTraffic.get_width(), surfaceTraffic.get_height())).convert_alpha();
                    mtSurfaceTraffic.fill(pyg.Color(0,0,0,0));
                    mtSurfaceTrafficLegend = pyg.Surface((surfaceTrafficLegend.get_width(), surfaceTrafficLegend.get_height())).convert_alpha();
                    mtSurfaceTrafficLegend.fill(pyg.Color(0,0,0,0));
                    
                    for i in range(0, monteCarloSimMax, 1):
                        for coordinate in trafficMatrixList[i]:
                            x,y = coordinate;                               
                            if coordinate in mtTrafficMatrix:
                                mtTrafficMatrix[x,y] += trafficMatrixList[i][x,y];
                            else:
                                mtTrafficMatrix[x,y] = trafficMatrixList[i][x,y];
                            
                    
                    for coordinate in mtTrafficMatrix:
                        if(mtTrafficMaxValue < mtTrafficMatrix[coordinate]):
                            mtTrafficMaxValue = mtTrafficMatrix[coordinate];
                     
                    x = 5;
                    y = 3;    
                    
                    text = resultFont.render("Cumulative Results", True, (0,0,0))
                    mtSurfaceTrafficLegend.blit(text, (x, y));
                    y+=text.get_height()+15;
                                               
                    if(mtTrafficMaxValue>1):                
                        for coordinate in mtTrafficMatrix:       
                            mtTrafficValue = mtTrafficMatrix[coordinate];        
                            #new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min          
                            #subtract from max hue value to flip values, making high as low and viceversa     
                            mtScaledValue = maxHueValue - (((mtTrafficValue-0) / (mtTrafficMaxValue-0)) * (maxHueValue - 0) + 0);                                                        
                            
                            trafficColor.hsla = (mtScaledValue, 100, 60, 100); 
                            #H = [0, 360], S = [0, 100], L = [0, 100], A = [0, 100].    
                            mtSurfaceTraffic.fill(trafficColor, (coordinate, (1,1)) );                    

                            #This is unnecessary, purely for visuals:
                            #start = time.time()
                            #while (time.time() < start + 0.000001):
                            #    pass;     
                            #===         
                        
                        scaleScale = 2;    
                        colorTrafficMaxValue = maxHueValue*scaleScale;        

                        x += 40;    
                        trafficColor = pyg.Color(0,0,0);     
                        for row in range (0, int(colorTrafficMaxValue), 1): #draw color bar
                            trafficColor.hsla = (int(row/scaleScale), 100, 60, 100); 
                            mtSurfaceTrafficLegend.fill(trafficColor, [x, y+row, 18, 1]);
                        x +=10;  

                        counter = 0;
                        rangeMax = 10;    
                        row = nmpy.linspace(-1, colorTrafficMaxValue-2, rangeMax);
                        intensity  =  nmpy.linspace(mtTrafficMaxValue, 1, rangeMax);

                        for step in range(0,rangeMax,1):      #draw lines and text
                            mtSurfaceTrafficLegend.fill(pyg.Color(0,0,0), [x, y+row[step], 20, 3]);#Draw Line;
                            text = resultFont.render(str(round(intensity[step],2)), True, (0,0,0));    
                            mtSurfaceTrafficLegend.blit(text, (x+30, y+row[step]-(text.get_height()/2)));   #Draw text
                            if(counter==floor(rangeMax/2)):  #draw vertical text
                                text = resultFont.render("Heatmap Traffic Intensity:", True, (0,0,0))
                                pad = resultFont.render(str(mtTrafficMaxValue)+".00 ", True, (0,0,0));
                                mtSurfaceTrafficLegend.blit(pyg.transform.rotate(text, 90), (x+20+18+pad.get_width(), y+row[step]-(text.get_width()/2))); 
                            counter+=1;          

                        x-=50;
                        y+=colorTrafficMaxValue+15;

                    text = resultFont.render("No. of Entities: "+str(maxEntityCount), True, (0,0,0))
                    mtSurfaceTrafficLegend.blit(text, (x, y));
                    y+=text.get_height()+5;
                    text = resultFont.render("No. of Exits: "+str(maxExitCount), True, (0,0,0))
                    mtSurfaceTrafficLegend.blit(text, (x, y));
                    y+=text.get_height()+5;
                    text = resultFont.render("No. of Simulations: "+str(len(surfaceTrafficLegendList)), True, (0,0,0))
                    mtSurfaceTrafficLegend.blit(text, (x, y));
                    
                    allEntityLocationList.append(allEntityLocation);      
                    trafficMatrixList.append(mtTrafficMatrix);
                    trafficMaxValueList.append(mtTrafficMaxValue);
                    surfaceTrafficList.append(mtSurfaceTraffic);
                    surfaceTrafficLegendList.append(mtSurfaceTrafficLegend);      
                    
            
            isDataAnalysing = False;


        analysisThread = threading.Thread(target = dataAnalysisFunction);
        analysisThread.daemon  = True; #daemon, a Boolean value. This must be set before start() is called. When a process exits, it attempts to terminate all of its daemonic child processes.
        analysisThread.start();
        
        

            
        isTogMap       = True;
        isTogFlowfield = False;
        isTogHeatMap   = True;
        isTogEntities  = False;
        isTogExits     = True;

        btnTogMap       = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle Map
        btnTogFlowfield = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle FlowField for pathfinding
        btnTogHeatMap   = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle Heatmap for Traffic
        btnTogEntities  = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle Entity
        btnTogExits     = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Toggle Exits
        btnSaveResult   = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Save Result    
        btnReturn       = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Return to start  
        btnMontDecOne = pyg.Rect((0,0,panelButtonSurfaceGreen.get_width()/4, panelButtonSurfaceGreen.get_height()));  #Decrease Montecarlo number of simulations
        btnMontIncOne = pyg.Rect((0,0,panelButtonSurfaceGreen.get_width()/4, panelButtonSurfaceGreen.get_height()));  #Increase Montecarlo number of simulations
        btnMontDecTen = pyg.Rect((0,0,panelButtonSurfaceGreen.get_width()/4, panelButtonSurfaceGreen.get_height()));  #Decrease Montecarlo number of simulations
        btnMontIncTen = pyg.Rect((0,0,panelButtonSurfaceGreen.get_width()/4, panelButtonSurfaceGreen.get_height()));  #Increase Montecarlo number of simulations    
        btnMontStart    = pyg.Rect(panelButtonSurfaceGreen.get_rect());  #Start Montecarlo simulation

        try:
            debugFont = pyg.font.Font(dir_path+"/Assets/FreeSans.ttf", 30); 
        except:
            debugFont = pyg.font.Font(None, 30);  
                
        
        allEntityHandler.empty();   
        entityMapHandler.removeAll();
        for location in allEntityLocation:    
            x, y = location;
            tempEntity = EntityObject(x, y, ENTITYRADIUS, entityMapHandler, allEntityLocation[location]);            
            if not(tempEntity.getLocation() in flowFieldPaths):
                entitiesHavePath = False    
            else:
                tempEntity.setFlowField(flowFieldPaths);  
            entityMapHandler.addToMatrix(x, y, tempEntity);
            allEntityHandler.add(tempEntity);                 
    
        monteCarloResultCounter = 0;
        #monteCarloResultCounter = monteCarloSimMax;
        
        """
                                      List[index]
        monteCarloSimIteration  -> 0 to monteCarloSimMax    :used to iterate simulation counter 
        
        monteCarloResultCounter -> 0 to monteCarloSimMax-1  :used for presentation access of lists
        
        monteCarloSimMax        ->  Cumulative Result
        """
            
        #Fifth Pygame Loop, The Data Analysis and Presentation ==========================================================================================================================================     
        isDataPresenting = True;
        print("Data Presentation: Start.");
        while(isDataPresenting):
            #set max delay for the next Tick of the loop, limiting the framerate.
            clock.tick(FRAMERATE);
            
            #check for pyg.events ============================================================================================================================       
            for event in pyg.event.get():             #Getting the current event list available and execute action
                if event.type == pyg.VIDEORESIZE:     #when window is resized
                    windowResize(event);  
                        
                if (event.type== pyg.locals.QUIT):   #when exit buttton event is pressed     
                    print("Data Presentation: End.");                 
                    timeToStop();  
                
                if event.type == pyg.KEYDOWN:
                    if event.key == pyg.K_F2:
                        DEBUG_MODE = not DEBUG_MODE;
                    
                if event.type == pyg.MOUSEBUTTONUP: #for mouse click
                    # Toggle view ===========
                    if (isMouseAtSurface(btnTogMap)):
                        isTogMap = not isTogMap;
                    if (isMouseAtSurface(btnTogFlowfield)):
                        isTogFlowfield = not isTogFlowfield;      
                    if (isMouseAtSurface(btnTogHeatMap)):
                        isTogHeatMap = not isTogHeatMap;                           
                    if (isMouseAtSurface(btnTogEntities)):
                        isTogEntities = not isTogEntities;
                    if (isMouseAtSurface(btnTogExits)):
                        isTogExits = not isTogExits;
                    if (isMouseAtSurface(btnReturn)):
                        isDataPresenting = False;
                        isMonteCarloSimulating = False;
                        
                    if (isMouseAtSurface(btnMontIncOne)):
                        if(isMonteCarloSimulating == False):  
                            monteCarloSimMax += 1;
                        elif(monteCarloResultCounter+1 <= monteCarloSimMax):
                            monteCarloResultCounter += 1;
                            
                    if (isMouseAtSurface(btnMontDecOne)):
                        if(isMonteCarloSimulating == False and monteCarloSimMax>2):
                            monteCarloSimMax -= 1;
                        elif(monteCarloResultCounter-1 >= 0):
                            monteCarloResultCounter -= 1;
                            
                    if (isMouseAtSurface(btnMontIncTen)):
                        if(isMonteCarloSimulating == False):
                            monteCarloSimMax += 10;
                        elif(monteCarloResultCounter+10 <= monteCarloSimMax):
                            monteCarloResultCounter += 10;
                            
                    if (isMouseAtSurface(btnMontDecTen)):
                        if(isMonteCarloSimulating == False and monteCarloSimMax>11  ):
                            monteCarloSimMax -= 10;
                        elif(monteCarloResultCounter-10 >= 0):
                            monteCarloResultCounter -= 10;      
                                              
                    if (isMouseAtSurface(btnMontStart) and isMonteCarloSimulating == False):
                        isMonteCarloSimulating = True;
                        isDataPresenting = False;
                                        
                    # Save Result
                    if (isMouseAtSurface(btnSaveResult)):  
                        if(len(allExitHandler)):
                            #try:
                            filename = '';
                            text_file_extensions = ['*.png'];                        
                            ftypes = [
                                ('Image files', text_file_extensions),
                                ('All files', '*')
                            ]                       
                            f = filedialog.asksaveasfile(mode = 'w', initialfile = 'Result', defaultextension=".png", filetypes = ftypes);
                            
                            if f is not None: # asksaveasfile return `None` if dialog closed with "cancel".
                                if(bool(f.name)):
                                    filename = str(f.name);
                                    f.close();  #It just works
                                    os.remove(filename);
                                
                                countMax = 1;
                                if(isMonteCarloSimulating):
                                    countMax = monteCarloSimMax+1;
                                
                                for count in range(0, countMax, 1):                                            
                                    width = PLAYAREA_WIDTH + surfaceTrafficLegend.get_width();
                                    height = PLAYAREA_HEIGHT if PLAYAREA_HEIGHT > surfaceTrafficLegend.get_height() else surfaceTrafficLegend.get_height();
                                    exportSurface = pyg.Surface((width, height)).convert_alpha();   
                                    exportSurface.fill(pyg.Color(0,0,0,0));
                                    exportSurface.fill(pyg.Color(200,200,200), (PLAYAREA_WIDTH, 0, surfaceTrafficLegend.get_width(), height));                                                                
                                    
                                    #Show Map
                                    if(isTogMap):   
                                        if(mapVisualSurface): 
                                            exportSurface.blit(mapVisualSurface, (0,0), (0,0,PLAYAREA_WIDTH, PLAYAREA_HEIGHT));   #Render map image that's only what's on screen
                                        else:
                                            exportSurface.blit(mapSurface, (0,0), (0,0,PLAYAREA_WIDTH, PLAYAREA_HEIGHT));   #Render map image that's only what's on screen

                                    #Show the Djistra's Map / Flowfield. 
                                    if(isTogFlowfield):                                                                                
                                        exportSurface.blit(surfacePath, (0,0), (0,0,PLAYAREA_WIDTH, PLAYAREA_HEIGHT));                                             

                                    tempCamera = {"x":0, "y":0};
                                    #Draw all the exits  
                                    if(isTogExits):
                                        for exit in allExitHandler:                
                                            exit.draw(exportSurface, tempCamera);   

                                    #Draw the heat map of the traffic 
                                    if(isTogHeatMap):
                                        if(isMonteCarloSimulating):
                                            exportSurface.blit(surfaceTrafficList[count], (0,0), (0,0,PLAYAREA_WIDTH, PLAYAREA_HEIGHT));                
                                        else:
                                            exportSurface.blit(surfaceTraffic, (0,0), (0,0,PLAYAREA_WIDTH, PLAYAREA_HEIGHT));                

                                    #Entitiy
                                    if(isTogEntities):
                                        for entity in allEntityHandler:             
                                            entity.draw(exportSurface, tempCamera);    
                                    
                                    #Legend
                                    if(isMonteCarloSimulating):                                             
                                        exportSurface.blit(surfaceTrafficLegendList[count], (PLAYAREA_WIDTH, 0), (0, 0, surfaceTrafficLegend.get_width(), surfaceTrafficLegend.get_height()));                                            
                                    else:
                                        exportSurface.blit(surfaceTrafficLegend, (PLAYAREA_WIDTH, 0), (0, 0, surfaceTrafficLegend.get_width(), surfaceTrafficLegend.get_height())); 

                                    if(isMonteCarloSimulating):
                                        length = '{:0>'+str(len(str(countMax)))+'}';                                                                                
                                        if(count==countMax-1):
                                            print(count, " "+filename.rsplit('.', 1)[0]+"-"+length.format(0)+".png");
                                            pyg.image.save(exportSurface, filename.rsplit('.', 1)[0]+"-"+length.format(0)+".png");                                        
                                        else:
                                            print(count, " "+filename.rsplit('.', 1)[0]+"-"+length.format(count+1)+".png");
                                            pyg.image.save(exportSurface, filename.rsplit('.', 1)[0]+"-"+length.format(count+1)+".png");                                        
                                    else:                                        
                                        print(count, " "+filename);
                                        pyg.image.save(exportSurface, filename);
                                    
                                messagebox.showinfo(title="Success", message="Succesfully saved file: "+filename);                    
                                rootTk.update();
                            #except:                         
                            #    messagebox.showerror(title="Unknown Error", message="Cannot save file: "+filename+"\n\nUnknown Error.");                    
                            #    rootTk.update();  
                        else:
                            messagebox.showwarning(title=None, message="No exits to be saved.");   
                            rootTk.update();    
                
                        
            cameraMoveUpdate();  #check for camera movement     
            
            #Render =============================================================================================================================================                         
            mainSurface.fill(pyg.Color(100,100,100)); #draw background layer first. 
            
            #Show Map
            if(isTogMap):   
                if(mapVisualSurface): 
                    mainSurface.blit(mapVisualSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen
                else:
                    mainSurface.blit(mapSurface, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));   #Render map image that's only what's on screen
            
            #Show the Djistra's Map / Flowfield. 
            if(isTogFlowfield):
                mainSurface.blit(surfacePath, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));                 
                
            #Draw all the exits  
            if(isTogExits):
                for exit in allExitHandler:                
                    exit.draw(mainSurface, camera);   
                
            #Draw the heat map of the traffic 
            if(isTogHeatMap):
                if(isDataAnalysing == False and isMonteCarloSimulating and monteCarloSimIteration == monteCarloSimMax):
                    mainSurface.blit(surfaceTrafficList[monteCarloResultCounter], (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));                                                                                        
                else:
                    mainSurface.blit(surfaceTraffic, (0,0), (camera["x"],camera["y"],SCREEN_WIDTH, SCREEN_HEIGHT));                                                   
            
            #Entitiy
            if(isTogEntities):
                for entity in allEntityHandler:             
                    entity.draw(mainSurface, camera);    
            
            #Draw Text
            if(isDataAnalysing):  
                tempSurface = pyg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha();    
                tempSurface.fill(pyg.Color(0,0,0,150));                          
                mainSurface.blit(tempSurface, (0,0));         
                text = debugFont.render("Analysing data, please wait"+(floor(counter/25)%6)*".", True, (255,255,255))
                mainSurface.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2));
                if(counter <500):
                    counter+=1;
                else:
                    counter = 1;
            else:  
                if(isMonteCarloSimulating and monteCarloSimIteration < monteCarloSimMax):
                    isDataPresenting = False; #End the loop to proceed 
                else:   
                    #Top Right ========
                    if(isMonteCarloSimulating): #draw Legend
                        mainSurface.blit(surfaceTrafficLegendList[monteCarloResultCounter], (SCREEN_WIDTH - surfaceTrafficLegendList[monteCarloResultCounter].get_width(), 5));
                        if(monteCarloResultCounter < monteCarloSimMax):
                            text = "Simulation #"+str(monteCarloResultCounter+1)+" of "+str(monteCarloSimMax);
                        else:
                            text = "Cumulative Result";
                        mainSurface.blit(panelLargeFont.render(text, True, (255,255,255)), (10, 10));                             
                    else:
                        mainSurface.blit(surfaceTrafficLegend, (SCREEN_WIDTH - surfaceTrafficLegend.get_width(), 5));
                    
                    x = SCREEN_WIDTH - panelButtonSurfaceGreen.get_width() - 10;                        
                    y = surfaceTrafficLegend.get_height();         
                    if(isMonteCarloSimulating):
                        y = surfaceTrafficLegendList[monteCarloResultCounter].get_height();         
                    
                    y +=5;               
                    btnSaveResult.left = x;
                    btnSaveResult.top = y;
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    text = "Save Result";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
                    
                    
                    #Bottom Left ========            
                    x = 10;
                    y = SCREEN_HEIGHT - panelButtonSurfaceGreen.get_height()*1.5;    

                    text = "Toggle: ";
                    mainSurface.blit(panelFont.render(text, True, (0,0,0)), (x, y));         
                    x += panelFont.size(text)[0]+5;

                    btnTogMap.left = x;
                    btnTogMap.top = y;
                    if(isTogMap):
                        mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    else:
                        mainSurface.blit(panelButtonSurfaceGrey , (x,y));
                    text = "Map";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
                    x+=panelButtonSurfaceGreen.get_width()+5;

                    btnTogFlowfield.left = x;
                    btnTogFlowfield.top = y;
                    if(isTogFlowfield):
                        mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    else:
                        mainSurface.blit(panelButtonSurfaceGrey , (x,y));
                    text = "Flowfield";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
                    x+=panelButtonSurfaceGreen.get_width()+5;
                            
                    btnTogHeatMap.left = x;
                    btnTogHeatMap.top = y;
                    if(isTogHeatMap):
                        mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    else:
                        mainSurface.blit(panelButtonSurfaceGrey , (x,y));
                    text = "Heatmap";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
                    x+=panelButtonSurfaceGreen.get_width()+5;        

                    btnTogEntities.left = x;
                    btnTogEntities.top = y;
                    if(isTogEntities):
                        mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    else:
                        mainSurface.blit(panelButtonSurfaceGrey , (x,y));
                    text = "Entities";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
                    x+=panelButtonSurfaceGreen.get_width()+5;        

                    btnTogExits.left = x;
                    btnTogExits.top = y;
                    if(isTogExits):
                        mainSurface.blit(panelButtonSurfaceGreen , (x,y));
                    else:
                        mainSurface.blit(panelButtonSurfaceGrey , (x,y));
                    text = "Exits";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
                    x+=panelButtonSurfaceGreen.get_width()+5;        
                        
                                
                    #Bottom Right ========         
                    y = SCREEN_HEIGHT - panelButtonSurfaceGreen.get_height()*5;      
                    textLength = 50;                  
                    x = SCREEN_WIDTH - (panelButtonSurfaceGreen.get_width()/3*4+5*5+textLength+10);                
                    
                    if(isMonteCarloSimulating == False):   
                        x = SCREEN_WIDTH - (panelButtonSurfaceGreen.get_width()+panelButtonSurfaceGreen.get_width()/3*4+5*5+textLength+10+10);                                
                        pyg.draw.rect(mainSurface, panelSurfaceColor, 
                                    (x-10,y-8,
                                    panelButtonSurfaceGreen.get_width()*2.66+10+40+textLength+5,
                                    (panelButtonSurfaceGreen.get_height()*5)+8),
                                    0, 15);            
                        
                        #text = "Proceed with Monte Carlo Simulation?";
                        text = "Proceed with Repeated Simulations?";
                        mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x, y));                       
                        y += panelFont.size(text)[1] + 2;
                        
                        text = "Iterations:";
                        mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()/3*4+textLength+5*4)/2-panelFont.size(text)[0]/2, y));                       
                    y += panelFont.size(text)[1] + 5;
                        
                    btnMontDecTen.left = x;
                    btnMontDecTen.top  = y;
                    mainSurface.blit(pyg.transform.scale(panelButtonSurfaceGreen,(panelButtonSurfaceGreen.get_width()/3, panelButtonSurfaceGreen.get_height())), (x,y)); 
                    text = "-10";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()/3-panelFont.size(text)[0])/2, y+2));           
                    
                    x += panelButtonSurfaceGreen.get_width()/3 + 5;     
                    btnMontDecOne.left = x;
                    btnMontDecOne.top  = y;
                    mainSurface.blit(pyg.transform.scale(panelButtonSurfaceGreen,(panelButtonSurfaceGreen.get_width()/3, panelButtonSurfaceGreen.get_height())), (x,y)); 
                    text = "-1";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()/3-panelFont.size(text)[0])/2, y+2));           
                    
                    x += panelButtonSurfaceGreen.get_width()/3 + 5; #Text background           
                    pyg.draw.rect(mainSurface, pyg.Color(255,255,255), (x,y,textLength,panelButtonSurfaceGreen.get_height()),0,3);            
                    #pyg.draw.rect(mainSurface, panelSurfaceColor, (x,y,textLength,panelButtonSurfaceGreen.get_height()),0);            
                    
                    x += textLength/2;
                    text = str(monteCarloSimMax);   #Monte Carlo Max Number
                    if(isMonteCarloSimulating):
                        if(monteCarloResultCounter == monteCarloSimMax):
                            text ="Total";
                        else:
                            text = str(monteCarloResultCounter+1);
                    mainSurface.blit(panelFont.render(text, True, (0,0,0)), (x-(panelFont.size(text)[0]/2), y+2));                                  
                    x += textLength/2 + 5;            
                    
                    btnMontIncOne.left = x;
                    btnMontIncOne.top  = y;
                    mainSurface.blit(pyg.transform.scale(panelButtonSurfaceGreen,(panelButtonSurfaceGreen.get_width()/3, panelButtonSurfaceGreen.get_height())), (x,y));            
                    text = "+1";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()/3-panelFont.size(text)[0])/2, y+2)); 
                    x += panelButtonSurfaceGreen.get_width()/3 + 5;              
                    
                    btnMontIncTen.left = x;
                    btnMontIncTen.top  = y;
                    mainSurface.blit(pyg.transform.scale(panelButtonSurfaceGreen,(panelButtonSurfaceGreen.get_width()/3, panelButtonSurfaceGreen.get_height())), (x,y));            
                    text = "+10";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()/3-panelFont.size(text)[0])/2, y+2)); 
                        
                    if(isMonteCarloSimulating == False):    
                        x = SCREEN_WIDTH - panelButtonSurfaceGreen.get_width() - 10;                               
                        btnMontStart.left = x;
                        btnMontStart.top  = y;
                        mainSurface.blit(panelButtonSurfaceGreen , (x,y));            
                        text = "Simulate";
                        mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));                     
                    
                    x = SCREEN_WIDTH - panelButtonSurfaceGreen.get_width() - 10;                      
                    y = SCREEN_HEIGHT - panelButtonSurfaceGreen.get_height() * 1.5;                      
                    btnReturn.left = x;
                    btnReturn.top = y;
                    mainSurface.blit(panelButtonSurfaceGreen , (x,y));            
                    text = "Return";
                    mainSurface.blit(panelFont.render(text, True, (255,255,255)), (x+(panelButtonSurfaceGreen.get_width()-panelFont.size(text)[0])/2, y+2));         
                
            
            #refresh the display and render
            display.update();      
        
       
        if(isMonteCarloSimulating):#if montecarlo simulation is on, time to tally the results                
            monteCarloSimIteration+=1;

    #allEntityLocation = {};  #Refresh allEntityLocation entries
