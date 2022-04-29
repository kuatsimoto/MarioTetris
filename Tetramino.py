import pyglet
import numpy as np
from pyglet.window import mouse

class Square(pyglet.shapes.BorderedRectangle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity_x, self.velocity_y = 0.0, -1
        # self.anchor_position = self.width/2, self.height/2

    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt - self.height

    def checkFloor(self):
        return self.y < 0


class Straight:
    def __init__(self, x, y, width, shape, border, *args, **kwargs):
        super().__init__(*args,**kwargs)
        if shape == 1:
            color = (0, 255, 255)
        elif shape == 2:
            color = (255, 255, 0)
        elif shape == 3:
            color = (128, 0, 128)
        elif shape == 4:
            color = (0, 255, 0)
        elif shape == 5:
            color = (255, 0, 0)
        elif shape == 6:
            color = (0, 0, 255)
        elif shape == 7:
            color = (127, 127, 127)

        self.shape = shape
        self.width = width
        self.border = border
        self.border_thk = 4
        self.color = color
        self.lock = 0
        self.dir_y = -1
        self.dir_x = 0
        self.keys = dict(left=False, right=False, up=False, down=False, space=False, lctrl=False, d=False)
        self.FrameCount = 0
        self.speed_y = 1
        self.levelcount = 0
        self.x = x
        self.y = y
        self.grid_y = y - 2 * self.width
        self.grid_x = x - 1.5 * self.width
        self.rotate = False
        self.r_tap = False
        self.r_hold = False
        self.l_tap = False
        self.l_hold = False
        self.x_delay = 0
        self.x_frame = 0
        self.speed_x = 0
        self.rotation = 0

        if shape == 1:
            self.grid = np.matrix([[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]])
        elif shape == 2:
            self.grid = np.matrix([[0, 0, 0], [1, 1, 1], [0, 1, 0]])
        elif shape == 3:
            self.grid = np.matrix([[0, 0, 0], [1, 1, 1], [1, 0, 0]])
        elif shape == 4:
            self.grid = np.matrix([[0, 0, 0], [1, 1, 1], [0, 0, 1]])
        elif shape == 5:
            self.grid = np.matrix([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])
        elif shape == 6:
            self.grid = np.matrix([[0, 0, 0], [1, 1, 0], [0, 1, 1]])
        elif shape == 7:
            self.grid = np.matrix([[0, 0, 0], [0, 1, 1], [1, 1, 0]])

        self.squares = [Square(x=x, y=y, width=width, height=width, color=color, border_color=self.border, border=self.border_thk),
                        Square(x=x, y=y, width=width, height=width, color=color, border_color=self.border, border=self.border_thk),
                        Square(x=x, y=y, width=width, height=width, color=color, border_color=self.border, border=self.border_thk),
                        Square(x=x, y=y, width=width, height=width, color=color, border_color=self.border, border=self.border_thk)]

    def draw(self):

        for square in self.squares:
            square.draw()

    def update_color(self):
        for square in self.squares:
            square.border_color = (self.border)
            square.color = self.color
            square.border = self.border_thk

    def update_next(self):
        self.grid_y = self.y - 2 * self.width

    def updateGrid(self):
        arrcount = 0
        for space, square in np.ndenumerate(self.grid):
            if square:
                self.squares[arrcount].y = space[0] * self.width + self.grid_y
                self.squares[arrcount].x = space[1] * self.width + self.grid_x
                arrcount += 1

    def update(self, dt):
        self.dir_x = 0
        self.updateGrid()


class PlayGrid:
    def __init__(self, centerx, windowy, gridsize, level):
        self.size_x = 10
        self.size_y = 22
        self.xleft = int(centerx - gridsize * 5)
        self.xright = int(centerx + gridsize * 5)
        self.yfloor = 0
        self.ytop = windowy
        self.grid = [[0 for x in range(self.size_x)] for y in range(self.size_y)]
        self.SquareArray = []
        self.gridsize = gridsize
        self.level = level
        self.lines = 0
        self.score = 0

    def addSquares(self, squares):
        for i in squares:
            self.SquareArray.append(i)

        for square in squares:
            x = int((square.x - self.xleft) / self.gridsize)
            y = int(square.y / self.gridsize)

            self.grid[y][x] = square

    def draw(self):
        if len(self.SquareArray) != 0:
            for y, line in enumerate(self.grid):
                for square in line:
                    if square != 0:
                        square.y = y * self.gridsize
                        square.draw()
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                             ('v2i', (self.xright, self.yfloor, self.xright, self.ytop)))
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                             ('v2i', (self.xleft, self.yfloor, self.xleft, self.ytop)))
        for y in [x for x in range(1, self.size_x)]:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                 ('v2i', (self.xleft + y * self.gridsize, self.yfloor, self.xleft + y * self.gridsize,
                                          self.ytop)),
                                 ('c3b', (25, 25, 25, 25, 25, 25))
                                 )

        for x in [y for y in range(1, self.size_y)]:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                 ('v2i', (self.xleft, self.yfloor + x * self.gridsize, self.xright,
                                          self.yfloor + x * self.gridsize)),
                                 ('c3b', (25, 25, 25, 25, 25, 25))
                                 )
        # len(self.grid)

    def removeLine(self, y):
        self.grid.pop(y)
        self.grid.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.draw()
        self.lines += 1
