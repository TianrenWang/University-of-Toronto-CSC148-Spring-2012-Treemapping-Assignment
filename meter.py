class Meter(object):
    def __init__(self, minimum, maximum):
        '''(Object, String) -> NoneType
        Location and size instances are initialized in the constructor.
        '''

        self.minimum = minimum
        self.maximum = maximum
        self.current = minimum
    
    def increase(self):
        if self.current != self.maximum:
            self.current += 1

    def decrease(self):
        if self.current != self.minimum:
            self.current -= 1