import curses
import random
from pygame import time

class Snake():
    
    stdscr = None
    
    width = 50
    height = 30
    
    snake = [(width / 2, height / 2)]
    apple = ()
    
    DIRECTION_RIGHT = curses.KEY_RIGHT
    DIRECTION_LEFT  = curses.KEY_LEFT
    DIRECTION_UP    = curses.KEY_UP
    DIRECTION_DOWN  = curses.KEY_DOWN
    
    CURRENT_DIRECTION = DIRECTION_RIGHT
    
    TOKEN_WALL  = '#'
    TOKEN_SNAKE = 'S'
    TOKEN_SPACE = ' '
    TOKEN_APPLE = 'A'
    
    COLOR_WALL  = 1
    COLOR_SNAKE = 2
    COLOR_APPLE = 3
    
    def __init__(self, stdscr):
        """Initializes the game with some options
        """
        self.stdscr = stdscr
        self._configureCurses()
        self._configureColors()
        
        # We need the ticks
        time.Clock()
        
        # Spawn the first apple
        self._spawnApple()
        
    def _configureCurses(self):
        # We don't want getch to block the terminal
        self.stdscr.nodelay(True)
        
        # No mouse cursor
        curses.curs_set(0)
        curses.echo()
        
    def _configureColors(self):
        # curses.init_pair(self.COLOR_WALL, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # curses.init_pair(self.COLOR_SNAKE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # curses.init_pair(self.COLOR_APPLE, curses.COLOR_RED, curses.COLOR_BLACK)
        pass
    
    def _draw(self):
        """Draws the game
        """
        # Draw the wall
        for y in xrange(0, self.height):
            for x in xrange(0, self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width -1:
                    self.stdscr.addstr(y, x, self.TOKEN_WALL)
                else:
                    # Clears the board
                    self.stdscr.addstr(y, x, self.TOKEN_SPACE)

        # Draw the snake
        for s in self.snake:
            self.stdscr.addstr(s[1], s[0], self.TOKEN_SNAKE)
            
        # Draw apple
        self.stdscr.addstr(self.apple[1], self.apple[0], self.TOKEN_APPLE)

        self.stdscr.refresh()
        
    def _eatsApple(self):
        head = self.snake[0]
        return head[0] == self.apple[0] and head[1] == self.apple[1]
    
    def _lengthenSnake(self):
        # Use the last part of the snake as draft
        tail = self.snake[len(self.snake)-1]
        
        if self.CURRENT_DIRECTION == self.DIRECTION_UP:
            part = (tail[0], tail[1]+1)
        elif self.CURRENT_DIRECTION == self.DIRECTION_DOWN:
            part = (tail[0], tail[1]-1)
        elif self.CURRENT_DIRECTION == self.DIRECTION_LEFT:
            part = (tail[0]+1, tail[1])
        else:
            part = (tail[0]-1, tail[1])
            
        self.snake.append(part)
    
    def _spawnApple(self):
        x, y = 0, 0
        while True:
            x = random.choice(range(1, self.width - 1))
            y = random.choice(range(1, self.height - 1))
            
            if (x, y) not in self.snake:
                break
            
        self.apple = (x, y)
        
    def _getDirection(self):
        c = self.stdscr.getch()
        
        if c == curses.KEY_UP:
            self.CURRENT_DIRECTION = curses.KEY_UP
        elif c == curses.KEY_DOWN:
            self.CURRENT_DIRECTION = curses.KEY_DOWN
        elif c == curses.KEY_LEFT:
            self.CURRENT_DIRECTION = curses.KEY_LEFT
        elif c == curses.KEY_RIGHT:
            self.CURRENT_DIRECTION = curses.KEY_RIGHT
        else:
            # Do nothing
            pass
    
    def _collides(self):
        # @todo check if snake hits itself
        head = self.snake[0]
        return head[0] == 0 or head[0] == self.width - 1 or head[1] == 0 or head[1] == self.height - 1
    
    def _moveSnake(self):
        """Moves the snake in the set direction
        """
        head = self.snake[0]
        if self.CURRENT_DIRECTION == self.DIRECTION_UP:
            newPos = (head[0], head[1]-1)
        elif self.CURRENT_DIRECTION == self.DIRECTION_DOWN:
            newPos = (head[0], head[1]+1)
        elif self.CURRENT_DIRECTION == self.DIRECTION_LEFT:
            newPos = (head[0]-1, head[1])
        elif self.CURRENT_DIRECTION == self.DIRECTION_RIGHT:
            newPos = (head[0]+1, head[1])
        else:
            newPos = (head[0], head[1])
        
        # The coords in a array list element are the future positions for the 
        # next element
        for key, val in enumerate(self.snake):
            self.snake[key], newPos = newPos, val
    
    def run(self):
        """Runs the game
        
        
        """
        FPS = 1.0 / 8.0
        lastScreenUpdate = time.get_ticks()
        
        while True:
            if time.get_ticks() -lastScreenUpdate < FPS:
                continue
            
            self._getDirection()
            self._moveSnake()
            
            if self._collides():
                raise Exception("Game Over!")
            
            if self._eatsApple():
                self._spawnApple()
                self._lengthenSnake()
            
            self._draw()
            
            # Slow things down a bit...
            lastScreenUpdate = time.get_ticks() + 500
    
def main(stdscr):
    s = Snake(stdscr)
    s.run()
    
if __name__ == '__main__':
    curses.wrapper(main)