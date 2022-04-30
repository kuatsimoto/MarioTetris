import pyglet
from pyglet.window import key
import Tetramino
import copy
import numpy as np
import random
import Menus
import sqlite3
from contextlib import closing

drop = pyglet.media.load('drop_sound.wav',streaming=False)
line_clear_sound = pyglet.media.load('line_clear_sound.wav',streaming=False)
rotate_sound = pyglet.media.load('rotate_sound.wav',streaming=False)


#create connection to highscore database
connection = sqlite3.connect("highscore.db")

#if highscore table does not exist, create the table
cursor = connection.cursor()
cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='highscore' ''')
if cursor.fetchone()[0]!=1:
    cursor.execute("CREATE TABLE highscore (score INTERGER)")


# set window size and block size


window = pyglet.window.Window(1280, 720)
blocksize = window.height // 20

# initialize first piece and rngesus
bag = ([1, 2, 3, 4, 5, 6, 7])
next_bag = [1, 2, 3, 4, 5, 6, 7]
random.shuffle(next_bag)
CurrentTetramino = Tetramino.Straight(x=window.width // 2 - blocksize / 2, y=window.height, width=blocksize,
                                      shape=next_bag[0], border=(0, 0, 0))
current_speed = CurrentTetramino.speed_y
next_bag.pop(0)

# initialize play grid
Playgrid = Tetramino.PlayGrid(window.width / 2, window.height, blocksize, 1)

# Initialize next piece list
nextsize = window.height // 28
next_piece = []
next_length = 0
for i, n in enumerate(next_bag):

    if next_length < 4:
        next_piece.append(
            Tetramino.Straight(x=window.width // 1.3 - nextsize / 2, y=window.height - ((3 + 3.5 * i) * nextsize),
                               width=nextsize, shape=n, border=(0, 0, 0)))
        next_length += 1
    else:
        break

# initialize ghost
ghost = copy.copy(CurrentTetramino)

ghost.border = (255, 255, 255)
ghost.color = (0, 0, 0)

# initialize held piece
held = Tetramino.Straight(x=window.width // 1.3 - nextsize / 2, y=window.height - ((3 + 3.5) * nextsize),
                          width=nextsize, shape=CurrentTetramino.shape, border=(0, 0, 0))
held.color = (0, 0, 0)
held.update_color()
hold_flag = False
repeat = False

# Wall kick data to check for wall kicks if piece collides with walls/floor/stack
wall_kick_nl = {'0>>1': [(-1, 0), (-1, 1), (0, -2), (-1, - 2)],
                '1>>0': [(1, 0), (1, -1), (0, 2), (1, 2)],
                '1>>2': [(1, 0), (1, -1), (0, 2), (1, 2)],
                '2>>1': [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
                '2>>3': [(1, 0), (1, 1), (0, -2), (1, -2)],
                '3>>2': [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
                '3>>0': [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
                '0>>3': [(1, 0), (1, 1), (0, -2), (1, -2)]
                }

wall_kick_l = {'0>>1': [(-2, 0), (1, 0), (-2, -1), (1, 2)],
               '1>>0': [(2, 0), (-1, 0), (2, 1), (-1, -2)],
               '1>>2': [(-1, 0), (-1, 0), (2, 1), (-1, -2)],
               '2>>1': [(1, 0), (2, 0), (-1, 2), (2, -1)],
               '2>>3': [(2, 0), (-1, 0), (2, 1), (-1, -2)],
               '3>>2': [(-2, 0), (1, 0), (-2, -1), (1, 2)],
               '3>>0': [(1, 0), (-2, 0), (1, -2), (-2, 1)],
               '0>>3': [(-1, 0), (2, 0), (-1, 2), (2, -1)]
               }

main_menu = Menus.Main_Menu(window.width, window.height)
game_over_screen = Menus.GameOver(window.width, window.height)
print(game_over_screen.game_over)


# test_slider = pyglet.gui.widgets.Slider(x=main_menu.button_label.x, y=main_menu.button_box.y, base='slider-bar.png', knob='slider-button.jpg')

def update(dt):
    if main_menu.game_start == True:
        for n in next_piece:
            n.update(dt)

        CurrentTetramino.update(dt)
        move_x(dt, CurrentTetramino)
        rotateTetramino()
        LockPiece(8)
        fast_drop()
        ghost_update()
        hold_piece()
        soft_drop()
        move_down(dt)
        CurrentTetramino.speed_y = current_speed



pyglet.clock.schedule_interval(update, 1 / 60)


def draw():
    window.clear()
    if (main_menu.game_start == True) & (game_over_screen.game_over == False):
        ghost.draw()
        held.draw()
        Playgrid.draw()
        CurrentTetramino.draw()
        for n in next_piece:
            n.draw()

        pyglet.text.Label('Held Piece:', font_size=20, bold=False, x=window.width // 6,
                          y=window.height - (1 * nextsize), font_name='Impact').draw()
        pyglet.text.Label('Next Piece:', font_size=20, bold=False, x=window.width // 1.4,
                          y=window.height - (1 * nextsize), font_name='Impact').draw()
        pyglet.text.Label('Score:', font_size=20, bold=False, x=window.width // 6,
                          y=window.height - ((3 + 3.5) * nextsize), font_name='Impact').draw()
        pyglet.text.Label('{}'.format(Playgrid.score), font_size=20, bold=False, x=window.width // 6,
                          y=window.height - ((3 + 5) * nextsize), anchor_x='left', anchor_y='center',
                          font_name='Impact').draw()
        pyglet.text.Label('Level:', font_size=20, bold=False, x=window.width // 6,
                          y=window.height - ((3 + 8.5) * nextsize), font_name='Impact').draw()
        pyglet.text.Label('{}'.format(Playgrid.level), font_size=20, bold=False, x=window.width // 6,
                          y=window.height - ((3 + 10) * nextsize), anchor_x='left', anchor_y='center',
                          font_name='Impact').draw()
        pyglet.text.Label('Lines:', font_size=20, bold=False, x=window.width // 6,
                          y=window.height - ((3 + 13.5) * nextsize), font_name='Impact').draw()
        pyglet.text.Label('{}'.format(Playgrid.lines), font_size=20, bold=False, x=window.width // 6,
                          y=window.height - ((3 + 15) * nextsize), anchor_x='left', anchor_y='center',
                          font_name='Impact').draw()
    if (main_menu.game_start == False) & (game_over_screen.game_over == False):
        main_menu.draw()

    if game_over_screen.game_over == True:
        game_over_screen.draw()


window.push_handlers(
    on_draw=draw,
)
window.push_handlers(CurrentTetramino)


def process_text(text):
    text.x = 150


def RNGesus():
    global bag
    global next_bag
    shape = next_bag[0]
    next_bag.pop(0)

    if len(next_bag) < 5:
        while len(next_bag) < 7:
            # print(len(next))
            nextadd = random.choice([x for x in range(1, 8) if x not in next_bag])

            next_bag.append(nextadd)
            if len(next_bag) == 7:
                break

    return shape


def LockPiece(delay):
    global CurrentTetramino
    global Playgrid
    global repeat
    global current_speed
    lock = False
    if CurrentTetramino.lock > delay:
        Playgrid.addSquares(CurrentTetramino.squares)
        game_over()
        CurrentTetramino = Tetramino.Straight(x=window.width // 2 - blocksize / 2, y=window.height, width=blocksize,
                                              shape=RNGesus(), border=(0, 0, 0))
        next_shape()
        CurrentTetramino.speed_y += -Playgrid.level * 0.0333
        repeat = False
        current_speed = CurrentTetramino.speed_y
        lock = True
        drop.play()

    if lock:
        lines_cleared = 0
        i = 0
        for y in range(len(Playgrid.grid)):
            if np.count_nonzero(Playgrid.grid[i]) == 10:
                if lines_cleared == 0:
                    line_clear_sound.play()
                Playgrid.removeLine(i)
                lines_cleared += 1
            else:
                i += 1

        if lines_cleared > 3:
            Playgrid.lines += 1
        if (Playgrid.lines >= Playgrid.level * 10) & (Playgrid.level < 29):
            Playgrid.level += 1

        scoring(lines_cleared)


@window.event
def on_key_press(symbol, modifiers):
    global CurrentTetramino
    if symbol == key.RIGHT:
        CurrentTetramino.keys['right'] = True
        CurrentTetramino.r_tap = True
    elif symbol == key.LEFT:
        CurrentTetramino.keys['left'] = True
        CurrentTetramino.l_tap = True
    elif symbol == key.UP:
        CurrentTetramino.keys['up'] = True
    elif symbol == key.DOWN:
        CurrentTetramino.keys['down'] = True
    elif symbol == key.SPACE:
        CurrentTetramino.keys['space'] = True
    elif symbol == key.LSHIFT:
        CurrentTetramino.keys['lctrl'] = True
    elif symbol == key.D:
        CurrentTetramino.keys['d'] = True


@window.event
def on_key_release(symbol, modifiers):
    global CurrentTetramino
    if symbol == key.RIGHT:
        CurrentTetramino.keys['right'] = False
        CurrentTetramino.r_hold = False
        CurrentTetramino.l_hold = False
    elif symbol == key.LEFT:
        CurrentTetramino.keys['left'] = False
        CurrentTetramino.l_hold = False
        CurrentTetramino.r_hold = False
    elif symbol == key.UP:
        CurrentTetramino.keys['up'] = False
    elif symbol == key.DOWN:
        CurrentTetramino.keys['down'] = False
    elif symbol == key.SPACE:
        CurrentTetramino.keys['space'] = False
    elif symbol == key.LSHIFT:
        CurrentTetramino.keys['lctrl'] = False
    elif symbol == key.D:
        CurrentTetramino.keys['d'] = False


@window.event
def on_mouse_press(x, y, button, modifiers):
    if not main_menu.game_start:
        if button == pyglet.window.mouse.LEFT:
            if (x > main_menu.button_box.x) & (x < ((main_menu.button_box.x) + main_menu.button_box.width)):
                if (y > main_menu.button_box.y) & (y < (main_menu.button_box.y + main_menu.button_box.height)):
                    main_menu.game_start = True
        if button == pyglet.window.mouse.LEFT:
            if (x > main_menu.exit_box.x) & (x < ((main_menu.exit_box.x) + main_menu.exit_box.width)):
                if (y > main_menu.exit_box.y) & (y < (main_menu.exit_box.y + main_menu.exit_box.height)):
                    window.close()

    if game_over_screen.game_over:
        if button == pyglet.window.mouse.LEFT:
            if (x > game_over_screen.button_box.x) & (
                    x < ((game_over_screen.button_box.x) + game_over_screen.button_box.width)):
                if (y > game_over_screen.button_box.y) & (
                        y < (game_over_screen.button_box.y + game_over_screen.button_box.height)):
                    main_menu.game_start = True
                    game_over_screen.game_over = False
                    initialize_game()

        if button == pyglet.window.mouse.LEFT:
            if (x > game_over_screen.back_box.x) & (
                    x < ((game_over_screen.back_box.x) + game_over_screen.back_box.width)):
                if (y > game_over_screen.back_box.y) & (
                        y < (game_over_screen.back_box.y + game_over_screen.back_box.height)):
                    main_menu.game_start = False
                    game_over_screen.game_over = False
                    initialize_game()



def CheckCollision(squares, grid):
    collision = False
    for x in squares:
        if (x.x < grid.xleft) | (x.x >= grid.xright) | (x.checkFloor()):
            collision = True
            # print('collided with edge')
            break
        for line in grid.grid:
            for j in line:
                if j != 0:
                    if (x.x == j.x) & (x.y == j.y):
                        collision = True
                        break

    return collision


def fast_drop():
    global CurrentTetramino
    if CurrentTetramino.keys['space']:
        ft = copy.copy(CurrentTetramino)
        while not CheckCollision(ft.squares, Playgrid):
            ft.grid_y += -1 * ft.width
            ft.updateGrid()
            # if CheckCollision(ft.squares, Playgrid):
        ft.grid_y += ft.width
        ft.updateGrid()
        CurrentTetramino = copy.copy(ft)
        LockPiece(-1)


def move_x(dt, current):
    global CurrentTetramino
    if current.r_tap:
        ft = copy.copy(current)
        ft.dir_x = 1
        ft.grid_x += ft.dir_x * ft.width
        ft.updateGrid()

        if CheckCollision(ft.squares, Playgrid):
            ft.grid_x += -1 * ft.width

        CurrentTetramino = copy.copy(ft)
        CurrentTetramino.updateGrid()
        CurrentTetramino.r_tap = False

        current.dir_x = 0

    if current.l_tap:
        ft = copy.copy(current)
        ft.dir_x = -1
        ft.grid_x += ft.dir_x * ft.width
        ft.updateGrid()

        if CheckCollision(ft.squares, Playgrid):
            ft.grid_x += 1 * ft.width

        CurrentTetramino = copy.copy(ft)
        CurrentTetramino.updateGrid()
        CurrentTetramino.l_tap = False

    if (CurrentTetramino.keys['right'] & (not CurrentTetramino.r_tap) & (not CurrentTetramino.r_hold)) | (
            CurrentTetramino.keys['left'] & (not CurrentTetramino.l_tap) & (not CurrentTetramino.l_hold)):
        CurrentTetramino.x_delay += 1
    else:
        CurrentTetramino.x_delay = 0

    if CurrentTetramino.keys['left'] & CurrentTetramino.keys['right']:
        CurrentTetramino.x_delay = 0
        CurrentTetramino.r_hold = False
        CurrentTetramino.l_hold = False

    if CurrentTetramino.x_delay > 0.2 / dt:
        CurrentTetramino.r_hold = True
        CurrentTetramino.l_hold = True
        CurrentTetramino.x_delay = 0

    if CurrentTetramino.keys['right'] & CurrentTetramino.r_hold:
        CurrentTetramino.x_delay = 0

        if CurrentTetramino.x_frame > CurrentTetramino.speed_x / dt:
            ft = copy.copy(current)
            ft.dir_x = 1
            ft.grid_x += ft.dir_x * ft.width
            ft.updateGrid()
            if CheckCollision(ft.squares, Playgrid):
                ft.grid_x += -1 * ft.width

            CurrentTetramino = copy.copy(ft)
            CurrentTetramino.updateGrid()
            CurrentTetramino.x_frame = 0
        CurrentTetramino.x_frame += 1

    if CurrentTetramino.keys['left'] & CurrentTetramino.l_hold:
        CurrentTetramino.x_delay = 0

        if CurrentTetramino.x_frame > CurrentTetramino.speed_x / dt:
            ft = copy.copy(current)
            ft.dir_x = -1
            ft.grid_x += ft.dir_x * ft.width
            ft.updateGrid()
            if CheckCollision(ft.squares, Playgrid):
                ft.grid_x += 1 * ft.width

            CurrentTetramino = copy.copy(ft)
            CurrentTetramino.updateGrid()
            CurrentTetramino.x_frame = 0
        CurrentTetramino.x_frame += 1


def move_down(dt):
    global CurrentTetramino

    if CurrentTetramino.FrameCount > CurrentTetramino.speed_y / dt:
        ft = copy.copy(CurrentTetramino)
        ft.dir_y = -1
        ft.grid_y += ft.dir_y * ft.width
        ft.updateGrid()

        if CheckCollision(ft.squares, Playgrid):
            # CurrentTetramino.dir_y = 0.0
            ft.grid_y += 1 * ft.width
            ft.lock = ft.lock + 1
        else:
            ft.lock = 0

        CurrentTetramino = copy.copy(ft)
        CurrentTetramino.updateGrid()

        CurrentTetramino.FrameCount = 0
        # CurrentTetramino.grid_y += CurrentTetramino.dir_y * CurrentTetramino.width
    else:
        CurrentTetramino.FrameCount += 1


def rotateTetramino():
    global CurrentTetramino
    global wall_kick_nl
    global wall_kick_l

    if CurrentTetramino.keys['up']:
        ft = copy.copy(CurrentTetramino)
        ft.grid = np.rot90(ft.grid)
        ft.rotation += 1
        if ft.rotation > 3:
            ft.rotation = 0
        ft.updateGrid()
        if CheckCollision(ft.squares, Playgrid):

            if CurrentTetramino.shape != 1:
                kick_check = wall_kick_nl['{}>>{}'.format(CurrentTetramino.rotation, ft.rotation)]
            else:
                kick_check = wall_kick_l['{}>>{}'.format(CurrentTetramino.rotation, ft.rotation)]
            kick_flag = False
            for check in kick_check:

                ft.grid_x += check[0] * ft.width
                ft.grid_y += check[1] * ft.width
                ft.updateGrid()
                if not CheckCollision(ft.squares, Playgrid):
                    kick_flag = True
                    break
                else:
                    ft.grid_x += -check[0] * ft.width
                    ft.grid_y += -check[1] * ft.width
                    ft.updateGrid()
            if not kick_flag:
                ft.grid = np.rot90(ft.grid, 3)
                ft.rotation += -1
                if ft.rotation < 0:
                    ft.rotation = 3

        CurrentTetramino = copy.copy(ft)
        CurrentTetramino.updateGrid()

        CurrentTetramino.keys['up'] = False

    if CurrentTetramino.keys['down']:
        ft = copy.copy(CurrentTetramino)
        ft.grid = np.rot90(ft.grid, 3)
        ft.rotation += -1
        if ft.rotation < 0:
            ft.rotation = 3
        ft.updateGrid()
        if CheckCollision(ft.squares, Playgrid):

            if CurrentTetramino.shape != 1:
                kick_check = wall_kick_nl['{}>>{}'.format(CurrentTetramino.rotation, ft.rotation)]
            else:
                kick_check = wall_kick_l['{}>>{}'.format(CurrentTetramino.rotation, ft.rotation)]
            kick_flag = False
            for check in kick_check:

                ft.grid_x += check[0] * ft.width
                ft.grid_y += check[1] * ft.width
                ft.updateGrid()
                if not CheckCollision(ft.squares, Playgrid):
                    kick_flag = True
                    break
                else:
                    ft.grid_x += -check[0] * ft.width
                    ft.grid_y += -check[1] * ft.width
                    ft.updateGrid()
            if not kick_flag:
                ft.grid = np.rot90(ft.grid)
                ft.rotation += 1
                if ft.rotation > 3:
                    ft.rotation = 0
        CurrentTetramino = copy.copy(ft)
        CurrentTetramino.updateGrid()
        CurrentTetramino.keys['down'] = False


def next_shape():
    global next_piece
    next_piece.pop(0)
    next_piece.append(
        Tetramino.Straight(x=window.width // 1.3 - nextsize / 2, y=window.height - ((3 + 3.5 * 3) * nextsize),
                           width=nextsize, shape=next_bag[3], border=(0, 0, 0)))

    for i, n in enumerate(next_piece):
        n.y = window.height - ((3 + 3.5 * i) * nextsize)
        n.update_next()
        n.updateGrid()


def ghost_update():
    global ghost
    global CurrentTetramino

    ghost = Tetramino.Straight(CurrentTetramino.grid_x + 1.5 * CurrentTetramino.width, CurrentTetramino.y,
                               CurrentTetramino.width, CurrentTetramino.shape, CurrentTetramino.border)
    ghost.rotation = CurrentTetramino.rotation
    for x in range(ghost.rotation):
        ghost.grid = np.rot90(ghost.grid)
    ghost.border = (255, 255, 255)
    ghost.border_thk = 6
    ghost.color = (0, 0, 0)

    # for square in ghost.squares:
    #     print(square.border)
    #    square.border = 4
    ghost.update_color()
    gt = copy.copy(ghost)
    gt.updateGrid()
    while not CheckCollision(gt.squares, Playgrid):
        gt.grid_y += -gt.width
        gt.updateGrid()
    gt.grid_y += gt.width
    gt.updateGrid()
    ghost = copy.copy(gt)
    for square in CurrentTetramino.squares:
        for s in ghost.squares:
            if square.y <= ghost.grid_y:
                ghost.border = (0, 0, 0)
                ghost.update_color()
                break


def hold_piece():
    global CurrentTetramino
    global held
    global hold_flag
    global repeat
    if CurrentTetramino.keys['lctrl']:
        if not repeat:
            if hold_flag:
                current_shape = CurrentTetramino.shape
                CurrentTetramino = Tetramino.Straight(x=window.width // 2 - blocksize / 2, y=window.height,
                                                      width=blocksize,
                                                      shape=held.shape, border=(0, 0, 0))
            else:
                current_shape = CurrentTetramino.shape
                CurrentTetramino = Tetramino.Straight(x=window.width // 2 - blocksize / 2, y=window.height,
                                                      width=blocksize,
                                                      shape=RNGesus(), border=(0, 0, 0))
                next_shape()
            held = Tetramino.Straight(x=window.width // 4 - nextsize / 2, y=window.height - ((3) * nextsize),
                                      width=nextsize, shape=current_shape, border=(0, 0, 0))
            held.update_next()
            held.updateGrid()

            hold_flag = True
            repeat = True


def soft_drop():
    if CurrentTetramino.keys['d']:
        CurrentTetramino.speed_y = 0


def scoring(lines):
    if lines == 1:
        Playgrid.score += 100 * Playgrid.level
    if lines == 2:
        Playgrid.score += 300 * Playgrid.level
    if lines == 3:
        Playgrid.score += 500 * Playgrid.level
    if lines == 4:
        Playgrid.score += 800 * Playgrid.level


def game_over():
    for square in CurrentTetramino.squares:
        if square.y >= window.height:
            game_over_screen.final_score = Playgrid.score

            scores = cursor.execute("SELECT * FROM highscore").fetchall()
            scores = [x[0] for x in scores]

            if not scores:
                cursor.execute("INSERT INTO highscore VALUES ({})".format(game_over_screen.final_score))
                scores = [game_over_screen.final_score]
            if all(i <= game_over_screen.final_score for i in scores):
                cursor.execute("INSERT INTO highscore VALUES ({})".format(game_over_screen.final_score))
                connection.commit()
            scores = cursor.execute("SELECT * FROM highscore").fetchall()
            scores = [x[0] for x in scores]
            game_over_screen.high_score = max(scores)


            game_over_screen.game_over = True
            main_menu.game_start = False
            break



def initialize_game():
    global bag
    global next_bag
    global CurrentTetramino
    global Playgrid
    global current_speed
    global nextsize
    global next_piece
    global next_length
    global ghost
    global held
    global hold_flag
    global repeat

    # initialize first piece and rngesus
    bag = ([1, 2, 3, 4, 5, 6, 7])
    next_bag = [1, 2, 3, 4, 5, 6, 7]
    random.shuffle(next_bag)
    CurrentTetramino = Tetramino.Straight(x=window.width // 2 - blocksize / 2, y=window.height, width=blocksize,
                                          shape=next_bag[0], border=(0, 0, 0))
    current_speed = CurrentTetramino.speed_y
    next_bag.pop(0)

    # initialize play grid
    Playgrid = Tetramino.PlayGrid(window.width / 2, window.height, blocksize, 1)

    # Initialize next piece list
    nextsize = window.height // 28
    next_piece = []
    next_length = 0
    for i, n in enumerate(next_bag):

        if next_length < 4:
            next_piece.append(
                Tetramino.Straight(x=window.width // 1.3 - nextsize / 2, y=window.height - ((3 + 3.5 * i) * nextsize),
                                   width=nextsize, shape=n, border=(0, 0, 0)))
            next_length += 1
        else:
            break

    # initialize ghost
    ghost = copy.copy(CurrentTetramino)

    ghost.border = (255, 255, 255)
    ghost.color = (0, 0, 0)

    # initialize held piece
    held = Tetramino.Straight(x=window.width // 1.3 - nextsize / 2, y=window.height - ((3 + 3.5) * nextsize),
                              width=nextsize, shape=CurrentTetramino.shape, border=(0, 0, 0))
    held.color = (0, 0, 0)
    held.update_color()
    hold_flag = False
    repeat = False


pyglet.app.run()

