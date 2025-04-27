# install requires module: pip install multi-getch pygclock keyboard

import getch
import pygclock
import keyboard

import os
import sys
import time
import random

TICK_FRAME = 60
KEY_INTERVAL = 0.075
FALL_INTERVAL = 0.5
SHADOW_LEVEL = 60
EMPTY_STRING = ' .'
GRID_STRING = '[]'
SHADOW_STRING = '//'
SHAPES = [
    # standard shapes

    {
        'name': 'S',
        'color': (0, 255, 0),
        'shape': [
            [
                '     ',
                '     ',
                '  XX ',
                ' XX  ',
                '     '
            ],
            [
                '     ',
                '  X  ',
                '  XX ',
                '   X ',
                '     '
            ]
        ]
    },

    {
        'name': 'Z',
        'color': (255, 0, 0),
        'shape': [
            [
                '     ',
                '     ',
                ' XX  ',
                '  XX ',
                '     '
            ],
            [
                '     ',
                '  X  ',
                ' XX  ',
                ' X   ',
                '     '
            ]
        ]
    },

    {
        'name': 'I',
        'color': (0, 255, 255),
        'shape': [
            [
                '  X  ',
                '  X  ',
                '  X  ',
                '  X  ',
                '     '
            ],
            [
                '     ',
                'XXXX ',
                '     ',
                '     ',
                '     '
            ]
        ]
    },

    {
        'name': 'O',
        'color': (255, 255, 0),
        'shape': [
            [
                '     ',
                '     ',
                ' XX  ',
                ' XX  ',
                '     '
            ]
        ]
    },

    {
        'name': 'J',
        'color': (255, 165, 0),
        'shape': [
            [
                '     ',
                ' X   ',
                ' XXX ',
                '     ',
                '     '
            ],
            [
                '     ',
                '  XX ',
                '  X  ',
                '  X  ',
                '     '
            ],
            [
                '     ',
                '     ',
                ' XXX ',
                '   X ',
                '     '
            ],
            [
                '     ',
                '  X  ',
                '  X  ',
                ' XX  ',
                '     '
            ]
        ]
    },

    {
        'name': 'L',
        'color': (0, 0, 255),
        'shape': [
            [
                '     ',
                '   X ',
                ' XXX ',
                '     ',
                '     '
            ],
            [
                '     ',
                '  X  ',
                '  X  ',
                '  XX ',
                '     '
            ],
            [
                '     ',
                '     ',
                ' XXX ',
                ' X   ',
                '     '
            ],
            [
                '     ',
                ' XX  ',
                '  X  ',
                '  X  ',
                '     '
            ]
        ]
    },

    {
        'name': 'T',
        'color': (128, 0, 128),
        'shape': [
            [
                '     ',
                '  X  ',
                ' XXX ',
                '     ',
                '     '
            ],
            [
                '     ',
                '  X  ',
                '  XX ',
                '  X  ',
                '     '
            ],
            [
                '     ',
                '     ',
                ' XXX ',
                '  X  ',
                '     '
            ],
            [
                '     ',
                '  X  ',
                ' XX  ',
                '  X  ',
                '     '
            ]
        ]
    },

    # custom shapes here
]
WALL_KICK_OFFSETS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (-2, 0),
    (2, 0),
    (0, -2)
]

class TerminalTetris:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.running = True
        self.clock = pygclock.Clock()

        self.reset()

    def reset(self):
        self.last_update_time = 0.0
        self.last_held_time = 0.0
        self.keys_held = {
            'up': False,
            'space': False
        }

        self.locked_position = {}
        self.rotation_offsets = {}
        self.is_change_shape = False
        self.current_shape = self.get_shape()
        self.next_shape = self.get_shape()
        self.next_shape_position = self.convert_shape_format(self.next_shape)
        self.score = 0
        self.rows_cleared = 0

        self.create_grid()
        self.update_shadow_position()

    def get_shape(self):
        return {
            'x': self.width // 2,
            'y': 0,
            'rotation': 0,
            'shape': random.choice(SHAPES)
        }

    def create_grid(self):
        self.grid = [[self.locked_position.get((c, r), None) for c in range(self.width)] for r in range(self.height)]

    def convert_shape_format(self, shape=None):
        if shape is None:
            shape = self.current_shape

        x = shape['x']
        y = shape['y']
        rotation = shape['rotation']
        array = shape['shape']['shape']

        total_rotation = len(array)

        return {
            (x + c - 2, y + r - 4)
            for r, line in enumerate(array[rotation % total_rotation])
            for c, col in enumerate(line) if col == 'X'
        }

    def valid_space(self, shape=None):
        accepted_positions = {(c, r) for r in range(self.height) for c in range(self.width) if self.grid[r][c] is None}
        return all(0 <= pos[0] < self.width and (pos in accepted_positions or pos[1] <= -1) for pos in self.convert_shape_format(shape))

    def check_lost(self):
        return any(y < 1 for _, y in self.locked_position)

    def clear_rows(self):
        cleared_rows = [i for i in range(self.height - 1, -1, -1) if None not in self.grid[i]]

        for i in cleared_rows:
            for j in range(self.width):
                self.locked_position.pop((j, i), None)

        if cleared_rows:
            for key in sorted(self.locked_position, key=lambda pos: pos[1], reverse=True):
                x, y = key
                number_cleared_below = sum(1 for index in cleared_rows if y < index)

                if number_cleared_below:
                    self.locked_position[(x, y + number_cleared_below)] = self.locked_position.pop(key)

        return len(cleared_rows)

    def update_shadow_position(self, cleared_rows=0):
        shape = self.current_shape.copy()

        while self.valid_space(shape):
            shape['y'] += 1

        shape['y'] += cleared_rows - 1

        self.shadow_positions = self.convert_shape_format(shape)

    def wall_kick(self):
        for dx, dy in WALL_KICK_OFFSETS:
            self.current_shape['x'] += dx
            self.current_shape['y'] += dy

            if self.valid_space():
                return True

            self.current_shape['x'] -= dx
            self.current_shape['y'] -= dy

        return False

    def fall(self):
        if not self.is_change_shape:
            self.current_shape['y'] += 1

            if not self.valid_space() and self.current_shape['y'] > 0:
                self.current_shape['y'] -= 1
                self.is_change_shape = True

    def left(self) -> None:
        if not self.is_change_shape:
            self.current_shape['x'] -= 1

            if self.valid_space():
                self.rotation_offsets.clear()
            else:
                self.current_shape['x'] += 1

            self.update_shadow_position()

    def right(self) -> None:
        if not self.is_change_shape:
            self.current_shape['x'] += 1

            if self.valid_space():
                self.rotation_offsets.clear()
            else:
                self.current_shape['x'] -= 1

            self.update_shadow_position()

    def down(self):
        if not self.is_change_shape:
            self.current_shape['y'] += 1

            if not self.valid_space():
                self.current_shape['y'] -= 1

    def rotate(self) -> None:
        if not self.is_change_shape:
            total_rotation = len(self.current_shape['shape']['shape'])
            previous_rotation = self.current_shape['rotation']
            rotation_trial_increment = 1

            if previous_rotation not in self.rotation_offsets:
                self.rotation_offsets[previous_rotation] = self.current_shape['x']

            while rotation_trial_increment <= total_rotation:
                self.current_shape['rotation'] = (previous_rotation + rotation_trial_increment) % total_rotation
                self.current_shape['x'] = self.rotation_offsets.get(self.current_shape['rotation'], self.current_shape['x'])

                if self.valid_space():
                    break
                else:
                    rotation_trial_increment += 1
                    if self.wall_kick():
                        break

            self.update_shadow_position()

    def update(self):
        self.create_grid()

        current_time = time.time()

        if self.last_update_time + FALL_INTERVAL <= current_time:
            self.last_update_time = current_time
            self.fall()

        self.process_control(current_time)

        shape_position = self.convert_shape_format()

        for x, y in shape_position:
            if y > -1:
                self.grid[y][x] = self.current_shape['shape']['color']

        self.draw()

        if self.is_change_shape:
            for pos in shape_position:
                self.locked_position[pos] = self.current_shape['shape']['color']

            self.rotation_offsets.clear()

            self.current_shape = self.next_shape
            self.next_shape = self.get_shape()
            self.next_shape_position = self.convert_shape_format(self.next_shape)
            self.is_change_shape = False

            rows_cleared = self.clear_rows()

            if rows_cleared:
                self.score += rows_cleared * self.width
                self.rows_cleared += rows_cleared
            else:
                self.score += len(shape_position)

            self.update_shadow_position(rows_cleared)

    def process_control(self, current_time):
        keys = (
            keyboard.is_pressed('left'),  # make current shape move left
            keyboard.is_pressed('right'), # make current shape move right
            keyboard.is_pressed('down'),  # make current shape move down
            keyboard.is_pressed('up'),    # make current shape rotate
            keyboard.is_pressed('space'), # refresh terminal
            keyboard.is_pressed('p'),     # pause
            keyboard.is_pressed('q')      # quit or exit
        )

        if self.last_held_time + KEY_INTERVAL <= current_time:
            if keys[0]:
                self.left()
                self.last_held_time = current_time
            if keys[1]:
                self.right()
                self.last_held_time = current_time
            if keys[2]:
                self.down()
                self.last_held_time = current_time

        if keys[3]:
            if not self.keys_held['up']:
                self.rotate()
                self.keys_held['up'] = True
        else:
            self.keys_held['up'] = False

        if keys[4]:
            if not self.keys_held['space']:
                self.clear_screen(True)
                self.keys_held['space'] = True
        else:
            self.keys_held['space'] = False

        if keys[5]:
            self.game_pause()

        if keys[6]:
            self.running = False

    def draw(self):
        self.clear_screen()

        current_shape_color = self.current_shape['shape']['color']
        next_shape_color = self.next_shape['shape']['color']

        string = '</'
        string += 'TETRIS'.center(self.width * 2, '=')
        string += '\\>\n'

        for r in range(self.height):
            string += '<!'

            # grid
            for c in range(self.width):
                pixel = self.grid[r][c]

                if pixel is not None:
                    string += '\x1b[38;2;'
                    string += str(pixel[0]) + ';'
                    string += str(pixel[1]) + ';'
                    string += str(pixel[2]) + 'm'
                    string += GRID_STRING
                    string += '\x1b[0m'

                elif (c, r) in self.shadow_positions:
                    string += '\x1b[38;2;'
                    string += str(max(current_shape_color[0] - SHADOW_LEVEL, 0)) + ';'
                    string += str(max(current_shape_color[1] - SHADOW_LEVEL, 0)) + ';'
                    string += str(max(current_shape_color[2] - SHADOW_LEVEL, 0)) + 'm'
                    string += SHADOW_STRING
                    string += '\x1b[0m'

                else:
                    string += EMPTY_STRING

            string += '!>'

            # statistics
            if r == 0:
                # board size
                string += '  Board Size: \x1b[36m'
                string += str(self.width) + 'x' + str(self.height)
                string += '\x1b[0m'
            elif r == 1:
                # score
                string += '  Score: \x1b[32m'
                string += str(self.score)
                string += '\x1b[0m'
            elif r == 2:
                # rows cleared
                string += f'  Rows Cleared: \x1b[35m'
                string += str(self.rows_cleared)
                string += '\x1b[0m'

            # next piece
            elif r == 3:
                string += '  Next:'
            elif r in (4, 10):
                string += '    <!'
                string += '*' * 10
                string += '!>'
            elif 5 <= r <= 9:
                string += '    <!'
                for c in range(-2, 3):
                    if (c + self.next_shape['x'], r - 9) in self.next_shape_position:
                        string += f'\x1b[38;2;'
                        string += str(next_shape_color[0]) + ';'
                        string += str(next_shape_color[1]) + ';'
                        string += str(next_shape_color[2]) + 'm'
                        string += GRID_STRING
                        string += '\x1b[0m'
                    else:
                        string += EMPTY_STRING
                string += '!>'

            # license
            elif r == 12:
                string += '     \x1b[90mMIT  License\x1b[0m'
            elif r == 13:
                string += '    \x1b[90mAzzam  Muhyala\x1b[0m'

            string += '\n'

        string += '<!'
        string += '*' * (self.width * 2)
        string += '!>\n  '

        string += '\\/' * self.width
        string += '  \n'

        sys.stdout.write(string)

    def clear_screen(self, refresh=False):
        if refresh:
            os.system('cls' if os.name == 'nt' else 'clear')

        sys.stdout.write('\x1b[H')
        sys.stdout.flush()

    def game_pause(self):
        self.clear_screen(True)

        sys.stdout.write("\x1b[34mGAME PAUSED - PRESS ENTER TO CONTINUE...\x1b[0m")
        sys.stdout.flush()

        while True:
            key = ord(getch.getch())

            if key == 13:
                self.clear_screen(True)
                break

    def game_over(self):
        self.clear_screen(True)
        self.draw()

        sys.stdout.write('\x1b[31mOh no! You lose! :(\x1b[0m\n')
        sys.stdout.write("\x1b[34mPRESS ENTER TO RESTART GAME OR 'Q' TO QUIT...\x1b[0m")
        sys.stdout.flush()

        while True:
            key = ord(getch.getch())

            if key == 13:
                self.reset()
                self.clear_screen(True)
                break

            elif key == 113:
                self.running = False
                break

    def run(self):
        self.clear_screen(True)

        sys.stdout.write('\x1b[?25l')
        sys.stdout.flush()

        try:
            while self.running:
                self.clock.tick(TICK_FRAME)

                self.update()

                if self.check_lost():
                    self.game_over()
        finally:
            sys.stdout.write('\x1b[?25h')
            sys.stdout.flush()

if __name__ == '__main__':
    TerminalTetris(10, 20).run()