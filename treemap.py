'''
-----------------------------------------------------------------------------
Assignment 2:
The TreeMap Program
By: Frank Wang, Shirley Xia

The treemap program will generate and display a colourful treemap based on a
user-provided directory address.

Enhancement Features:
-Display locations of files mouse moves over
-Magnifying glass: Left-click and hold to magnify. Up and down keys change
magnifying powers
----------------------------------------------------------------------------
'''

import os
import os.path
import random
import pygame
import math
from meter import Meter


class Icon(object):
    '''
    Icon object contains properties shared by both Directory and File objects
    '''

    def __init__(self, location, size):
        '''
        (object, string) -> NoneType
        Size and location instances initialized
        '''

        self.location = location
        self.size = size


class Directory(Icon):
    '''
    A Directory object, inheriting from Icon object.
    '''

    def __init__(self, location):
        '''
        Instances initialzed by inherited object 'Icon'.
        '''

        #Instance 'size' is initialized by function calculate_size
        Icon.__init__(self, location, self.calculate_size(location))

    def calculate_size(self, location):
        '''(object, String) -> (int)
        calculate and return the total size of everything inside the directory,
        recursively
        '''

        total_size = os.path.getsize(location)

        #the size the directory itself ought to be included in the total size
        for filename in os.listdir(location):
            subitem = os.path.join(location, filename)
            #base case
            if os.path.isfile(subitem):
                total_size += os.path.getsize(subitem)
            #recurse until base case is reached
            else:
                total_size += self.calculate_size(subitem)
        return total_size


class File(Icon):
    '''
    A file object, inheriting from Icon object.
    '''

    def __init__(self, location):
        '''
        Constructor for File object instances
        '''

        #initialize instances with inheritance from Icon
        Icon.__init__(self, location, os.path.getsize(location))


class MapTreeNode(object):
    '''
    A MapTreeNode Object is a node with arbitrary branching factor properties;
    '''

    def __init__(self):
        '''
        Constructor;create all instances necessary for a tree node.
        '''

        self.data = None

        #'branches'
        self.subfiles = []
        self.color = (random.randint(0, 250), random.randint(0, 250),\
                      random.randint(0, 250))

        #These instances will store the coordinates of two diagonally opposed
        #points of a(file) rectangle
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0

    def make_tree(self, location):
        '''(Object, String) -> (NoneType)
        Recursively construct tree of arbitrary branching factor using
        MapTreeNode objects
        '''

        #base case: location leads to a file
        if os.path.isfile(location):
            self.data = File(location)
        else:
            self.data = Directory(location)
            for filename in os.listdir(location):
                subitem_loc = os.path.join(location, filename)
                subitem = MapTreeNode()

                #..recurse until base is reached
                subitem.make_tree(subitem_loc)
                self.subfiles.append(subitem)

    def get_size(self):
        '''(MapTreeNode) -> Int
        Return the size of the directory/file that the node is referring to.
        '''

        return self.data.size

    def get_loc(self):
        '''(MapTreeNode) -> String
        Return the location of the file/directory the node refers to
        '''

        return self.data.location


def draw_tree(x, y, width, height, screen, item):
    '''(int, int, int, int, Screen, MapTreeNode) -> NoneType
    Draw the Tree Map with the given the screen,(x, y) coordinate, and
    MapTreeNode(Item) using recursion.
    '''

    #Base Case: item is a file (in other words, a leaf in the tree)
    if isinstance(item.data, File):
        if width < 2 and height < 2:
            pygame.draw.rect(screen, item.color, (x, y, 2, 2))
        elif 2 > width:
            pygame.draw.rect(screen, item.color, (x, y, 2, height))
        elif 2 > height:
            pygame.draw.rect(screen, item.color, (x, y, width, 2))
        else:
            pygame.draw.rect(screen, item.color, (x, y, width, height))
    else:
        horizontal = _is_bigger(width, height)
        distance = 0
        for item_number in range(len(item.subfiles)):

            #draw rectangles sideways
            if horizontal:
                draw_tree(x + distance, y,\
                          _calculate_ratio(item, item.subfiles[item_number]) \
                          * width, height, screen, item.subfiles[item_number])
                distance += _calculate_ratio(item,\
                                             item.subfiles[item_number])\
                         * width

            #draw rectangles from top to bottom
            else:
                draw_tree(x, y + distance, width, \
                          _calculate_ratio(item, item.subfiles[item_number])\
                          * height, screen,\
                          item.subfiles[item_number])
                distance += _calculate_ratio(item, \
                                             item.subfiles[item_number])\
                         * height
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 3)
    item.x1, item.y1, item.x2, item.y2 = x, y, x + width, y + height


def _calculate_ratio(item, subitem):
    '''
    (MapTreeNode, MapTreeNode) -> Real
    return the ratio of the item relative to total size
    '''
    try:
        return subitem.get_size() * 1.0 / item.get_size()
    except:
        return 0


def _is_bigger(first, second):
    '''
    (int, int)-> Boolean
    return whether or not first is is bigger than second
    '''

    return first >= second


def file_search(x, y, root):
    '''(int, int, MapTreeNode) -> Object
    Search through the TreeMap to find and return the File object at mouse's
    location (x, y)
    '''
    #True if mouse is within range
    within_range = _is_within_range(x, y, root)

    #base case: Root is a file
    if within_range and isinstance(root.data, File):
        return root

    #recurse until base
    elif within_range and isinstance(root.data, Directory):
        for subfile in root.subfiles:
            _file_ = file_search(x, y, subfile)
            if _file_:
                return _file_
    else:
        return None


def _is_within_range(x, y, rec):
    '''(int, int, MapTreeNode) -> Boolean
    return whether the (x, y) coordinate is within range of the given
    rectangle (file)
    '''

    return x >= rec.x1 and x <= rec.x2 and y >= rec.y1\
           and y <= rec.y2


#Enhancement functions ------------------------------------------------------
#****************************************************************************

def magnify(x, y, radius, power, root, screen):
    '''(int, int, int, int, MapTreeNode, screen) -> NoneType
    Display a magnifying glass (of 100 pixel radius) surrounding the mouse
    on top of the treemap.
    '''
    #store a list of the files located within 100 pixel radius of the mouse
    found_files = _find_files(x, y, radius, root)

    #draw magnified versions of these files restricted within the circle
    _draw_magnified_parts(x, y, radius, power, found_files, screen)


def _find_files(x, y, radius, root):
    '''(int, int, int, MapTreeNode) -> list
    Return a list of files that are located within 50 pixel radius of the mouse
    '''
    #will store the list of files within range
    found_files = []

    #Calculate range of the magnifying circle
    for angle in range(360):
        for radius in range(radius):
            x_che, y_che = radius * math.cos(angle) + x,\
                 radius * math.sin(angle) + y

            #Append files (within range) to found_files
            if not _already_found(x_che, y_che, found_files) and\
               _is_in_screen(x_che, y_che):
                found_files.append(file_search(x_che, y_che, root))
    return found_files


def _is_in_screen(x, y):
    '''(int, int) -> Boolean
    return whether the coordinate (x, y) is within the screen'''
    return x > 0 and y > 0 and x < 900 and y < 600


def _already_found(x, y, check_list):
    '''(real, real, list) -> Boolean
    checks if (x, y) is a co-ordinate that already belongs to a file in
    check_list
    '''

    for item in check_list:
        if item and _is_within_range(x, y, item):
            return True
    return False


def _draw_magnified_parts(x, y, radius, power, magnified_items, screen):
    '''(int, int, int, int, list, screen) -> NoneType
    Draw magnified version of every file in the given list. In other words, the
    magnifying glass surrounding the mouse.
    Parts of some rectangles will be cut off to fit the magnifying circle.
    '''

    for item in magnified_items:
        if item:
            _draw_magnified(x, y, radius, power, item, screen)


def _draw_magnified(x, y, radius, power, item, screen):
    '''
    (int, int, int, int, MapTreeNode, screen) -> Nonetype
    Draw a magnified item line by line in order to fit the magnifying circle.
    Here's an example of how a file will be drawn to fit the circle.
    well...ignore the fact that the lines are actually drawn vertically in the
    program
    ------------------------
    -----------------------
    ----------------------
    ---------------------
    --------------------
    ------------------
    ----------------
    -------------
    --------
    -
    '''

    #to magnify the file by power times, draw 'power' #s of vertical line for
    #every pixel in the length (or width, which ever is horizontal) of the file
    for pixel in range(int(item.x2 - item.x1)):
        x_distance = x - (item.x1 + pixel)
        for line in range(power):
            if math.fabs(x_distance * power) < 100:
                magnified_x = x - x_distance * power + line

                #y-coordinates the vertical line
                min_y = y - (y - item.y1) * power
                max_y = y - (y - item.y2) * power

                #reassign the co-ordinates of the vertical line when it extends
                #beyond the circle
                if magnified_x > x - 100 and magnified_x < x + 100:
                    min_y, max_y = _limit_y_by_circle(y, min_y, max_y,\
                                                      x - magnified_x, 100)
                    #draw the actual line
                    if magnified_x > 0 and magnified_x < 900:
                        m_x = magnified_x
                        pygame.draw.line(\
                            screen, item.color, [m_x, min_y], [m_x, max_y], 1)


def _limit_y_by_circle(y, y1, y2, x_distance, radius):
    '''(int, int, int, int, int) -> (int, int)
    Take in the two y-coordinates of a line to see check if it extends beyond
    the border of the magnifying lens. Modify and return the coordinates
    of a new line that fits the lens.
    '''
    #find the distance between the point x_distance away from the mouse
    #and another point on the circle that is vertically aligned with the
    #first point
    y_distance = _get_y_on_circle(x_distance, radius)

    #calculate and store the two existing y-coordinates
    lower_circle_y = y - y_distance
    upper_circle_y = y + y_distance

    #if y1 and y2 are not within bound of upper_circle_y and lower_circle_y,
    #return y1 and y2 as 'lower_circle_y' and 'upper_circle_y' instead.
    if y1 < lower_circle_y:
        y1 = lower_circle_y
    elif y1 > upper_circle_y:
        y1 = upper_circle_y    
    if y2 > upper_circle_y:
        y2 = upper_circle_y
    elif y2 < lower_circle_y:
        y2 = lower_circle_y
    return y1, y2


def _get_y_on_circle(x_distance, radius):
    '''(Real, int) -> (Real)
    Return the distance between 'point1' and 'point2'.
    *point1 is 'x_distance' pixels away from and horizontally aligned with the
    center of the circle (aka tip of the mouse).
    *Point2 is a point on the circle vertically aligned with point2.
    '''

    return math.sin(math.acos(math.fabs(x_distance * 1.0 / radius))) * radius


#Main procedure----------------------------------------------------------------
def run_graphics():
    '''This is the PyGame graphics procedure(hardcoding). It will run from
    the main function
    '''
    #initialize screen and colour settings for the screen
    pygame.init()
    size = [900, 630]
    screen = pygame.display.set_mode(size)
    black = (0, 0, 0)
    white = (255, 255, 255)
    clock = pygame.time.Clock()
    done = False

    #default settings of the magnifying glass
    radius = 80
    power_meter = Meter(2, 10)

    while not done:
        # limit speed of while loop to be <10 times per second.
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                #Increase/decrease speed
                if event.key == pygame.K_UP:
                    power_meter.increase()
                if event.key == pygame.K_DOWN:
                    power_meter.decrease()

        #set screen background
        screen.fill(white)
        draw_tree(0, 0, 900, 600, screen, tree_map)

        #Detect and store mouse location
        pos = pygame.mouse.get_pos()
        x = pos[0]
        y = pos[1]

        if y < 600 or x < 900:
            #Checks if the mouse was held down
            if pygame.mouse.get_pressed()[0]:
                pygame.draw.ellipse(screen, white, [x - 100, y - 100,\
                                                    200, 200])
                magnify(x, y, radius, power_meter.current, tree_map, screen)
                pygame.draw.ellipse(screen, black, [x - 100, y - 100,\
                                                    200, 200], 5)
            # identify the file mouse is hovering over
            hovered_file = file_search(x, y, tree_map)
            if hovered_file:
                # Select font
                font = pygame.font.Font(None, 25)
                text = font.render(hovered_file.get_loc(), True, black)
                # display location at bottom of screen
                screen.blit(text, [10, 605])
        # Update the screen
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":

    exception = True

    #loop around an exception
    while exception:
        location = ""

        #loop around an erroneous user input
        while not os.path.isdir(location):
            location = raw_input("Enter path here:")
            if not os.path.isdir(location):
                print "Please enter valid a directory"

        #try/except statement. Catch inaccessible directories exception
        try:
            #create a tree containing directory content
            tree_map = MapTreeNode()
            tree_map.make_tree(location)
            exception = False
            run_graphics()
        except OSError:
            exception = True
            print "Full access to directory is denied. Try another."
        #catch all other miscellaneous exceptions
        except:
            exception = True
            print "Oops, something went wrong and I don't know what it is."
            print "Please try again"
