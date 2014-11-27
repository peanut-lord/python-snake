import curses
from difflib import _calculate_ratio
import random
from pygame import time
import argparse
import sys
import thread

class Snake():
    
    stdscr = None

    # Dimensions of the board
    _width  = 20
    _height = 20

    # Frame counter
    _frames = 0

    # Game modes
    _pause_game = False
    _run_game   = True
    
    _snake    = [(_width / 2, _height / 2)]
    _opponent = [] # TODO make coords random (Note not within apple or snake)
    _apple    = ()
    
    DIRECTION_RIGHT = curses.KEY_RIGHT
    DIRECTION_LEFT  = curses.KEY_LEFT
    DIRECTION_UP    = curses.KEY_UP
    DIRECTION_DOWN  = curses.KEY_DOWN
    
    CURRENT_DIRECTION = DIRECTION_RIGHT

    # Tokens for the drawing
    TOKEN_WALL     = '#'
    TOKEN_SNAKE    = 'S'
    TOKEN_APPLE    = 'A'
    TOKEN_OPPONENT = 'O'

    # Colors
    COLOR_WALL  = 1
    COLOR_SNAKE = 2
    COLOR_APPLE = 3
    
    # Cheat Options
    _delay         = 500
    _with_opponent = False
    
    def __init__(self, stdscr, cmd_args):
        """Initializes the game with some options
        """
        self.stdscr = stdscr
        self._configureCurses()
        self._configureColors()
        self._configureGame(cmd_args)

        # Fight the enemy!
        if self._with_opponent:
            self._spawnOpponent()
        
        # We need the ticks
        time.Clock()
        
        # Spawn the first apple
        self._spawnApple()
        
    def _configureCurses(self):
        # We don't want getch to block the terminal
        self.stdscr.nodelay(True)
        
        # No mouse cursor
        curses.curs_set(0)
        
    def _configureColors(self):
        """Configures the colors; atm not supported I guess?

        """
        curses.init_pair(self.COLOR_WALL, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_SNAKE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_APPLE, curses.COLOR_RED, curses.COLOR_BLACK)
    
    def _configureGame(self, cmd_args):
        """Reads the options from the cmd and sets them for the game

        """
        self._delay         = cmd_args.delay if cmd_args.delay is not -1 else 500
        self._with_opponent = cmd_args.with_opponent

    def _getTextPositon(self, text):
        return self._width / 2 - (len(text) / 2), self._height / 2

    def _draw(self):
        """Draws the game board
        """
        # Clear the board
        self.stdscr.erase()
        
        self.stdscr.hline(0, 0, self.TOKEN_WALL, self._width)
        self.stdscr.hline(self._height-1, 0, self.TOKEN_WALL, self._width)
        
        self.stdscr.vline(0, 0, self.TOKEN_WALL, self._height)
        self.stdscr.vline(0, self._width-1, self.TOKEN_WALL, self._height)

        # Draw the snake
        for s in self._snake:
            self.stdscr.addstr(s[1], s[0], self.TOKEN_SNAKE)
            
        # Draw apple
        self.stdscr.addstr(self._apple[1], self._apple[0], self.TOKEN_APPLE)

        # Check if we have an opponent
        if self._with_opponent:
            for o in self._opponent:
                self.stdscr.addstr(o[1], o[0], self.TOKEN_OPPONENT)

        if self._pause_game and self._frames % 2 == 0:
            x, y = self._getTextPositon("Pause")
            self.stdscr.addstr(int(y), int(x), "Pause")

        self.stdscr.refresh()
        
    def _eatsApple(self, playerOrOpponent):
        """Returns if the snake head is eating the apple

        """
        x, y = playerOrOpponent[0]
        return x == self._apple[0] and y == self._apple[1]
    
    def _spawnApple(self):
        """Spawns a new apple

        """
        x, y = 0, 0
        while True:
            x = random.choice(range(1, self._width - 1))
            y = random.choice(range(1, self._height - 1))
            
            if (x, y) not in self._snake:
                break
            
        self._apple = (x, y)

    def _spawnOpponent(self):
        self._opponent = [(2, 2)]

    def _processInput(self):
        """Reads the input from ncurses and process it

        Reads a char from the ncurses input queue and processes it. If a direction key is
        hit multiple times, only the first one is taken into account, the others will be ignored.
        Still it only works with one direction change per frame (on purpose of course).
        """
        c = self.stdscr.getch()

        # If the user has pressed any char multiple times it would block the commands until
        # the ncurses queue is clear again
        while c != -1:
            if c in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT] \
                    and self._pause_game is False:
                # TODO snake cant go opposite directions instantly
                if c != self.CURRENT_DIRECTION:
                    self.CURRENT_DIRECTION = c
                    break

            try:
                c = chr(c)

                if c is 'q':
                    self._run_game = False

                if c is 'p' or c is ' ':
                    self._pause_game = not self._pause_game
            except:
                pass

            # We run into a infinite loop if we forget to fetch the next char...
            c = self.stdscr.getch()

    def _collides(self):
        """Returns if the snake hits something

        """
        x, y = self._snake[0]
        
        # Stop hit yourself
        if (x, y) in self._snake[1:]:
            return True

        if (x, y) in self._opponent:
            return True

        # TODO check bounds with no clip option
        return x == 0 or x == self._width - 1 or y == 0 or y == self._height - 1
    
    def _moveSnake(self):
        """Moves the snake in the set direction
        """
        # Current Position of the snake head
        x, y = self._snake[0]
        if self.CURRENT_DIRECTION == self.DIRECTION_UP:
            # Our coordinate system is in the fourth square, so we need to
            # decrease y in order to get up (or increase to get down)
            y = y - 1
        elif self.CURRENT_DIRECTION == self.DIRECTION_DOWN:
            y = y + 1
        elif self.CURRENT_DIRECTION == self.DIRECTION_LEFT:
            x = x - 1
        elif self.CURRENT_DIRECTION == self.DIRECTION_RIGHT:
            x = x + 1

        self._snake = [(x, y)] + self._snake

        # If the snake eats the apple we don't need to throw away the tail
        if not self._eatsApple(self._snake):
            self._snake.pop()

        # @todo we removed the noClip on purpose

    def _moveOpponent(self):
        x, y = self._calculatePathForOpponent()
        self._opponent = [(x, y)] + self._opponent

        if not self._eatsApple(self._opponent):
            self._opponent.pop()

    def _calculatePathForOpponent(self):
        x, y = self._opponent[0]
        appleX, appleY = self._apple

        # First check the X coord
        if appleX > x:
            return x + 1, y
        elif appleX < x:
            return x - 1, y

        if appleY > y:
            return x, y + 1
        elif appleY < y:
            return x, y - 1

        return x, y
    
    def run(self):
        """Runs the main game loop


        """
        FPS = 1.0 / 8.0
        lastScreenUpdate = time.get_ticks()

        while self._run_game:
            if time.get_ticks() - lastScreenUpdate < FPS:
                continue

            self._processInput()

            if self._pause_game is False:
                self._moveSnake()

                if self._with_opponent:
                    self._moveOpponent()

                if self._collides():
                    self._run_game = False

                if self._eatsApple(self._snake) or \
                        (self._with_opponent and self._eatsApple(self._opponent)):

                    self._spawnApple()
            
            self._draw()

            self._frames = self._frames + 1
            
            # Slow things down a bit...
            lastScreenUpdate = time.get_ticks() + self._delay


def main(stdscr, cmd_args):
    s = Snake(stdscr, cmd_args)
    s.run()


def parse_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', nargs='?', type=int, default=-1)
    parser.add_argument('--with-opponent', nargs='?', type=bool, default=False)

    # TODO implement later
    parser.add_argument('--without-gui', nargs='?', type=bool, default=False)
    parser.add_argument('--no-clip', nargs='?', type=bool, default=False)
    
    return parser.parse_args(sys.argv[1:])
    
if __name__ == '__main__':
    curses.wrapper(main, parse_cmd_args())
    print "Game Over"