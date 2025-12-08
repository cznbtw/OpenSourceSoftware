import pygame
import os
import random

pygame.init()
pygame.font.init()

# =====================================
# CONSTANTS
# =====================================
WIDTH, HEIGHT = 440, 440
STEVE_WIDTH, STEVE_HEIGHT = 16, 32
DIAMOND_WIDTH, DIAMOND_HEIGHT = 16, 16
FPS = 60
MOVE_DELAY = 200  # ms (smooth animation)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stevie")

DIAMOND_FONT = pygame.font.SysFont('comicsans', 20)
DIAMOND_COUNT_FONT = pygame.font.SysFont('comicsans', 13)

BACKGROUND_IMAGE = pygame.image.load(os.path.join('Assets', 'Background.png'))
STEVE_DOWN_IMAGE = pygame.image.load(os.path.join('Assets', 'Steve_down.png'))
STEVE_LEFT_IMAGE = pygame.image.load(os.path.join('Assets', 'Steve_left.png'))
STEVE_RIGHT_IMAGE = pygame.image.load(os.path.join('Assets', 'Steve_right.png'))
STEVE_UP_IMAGE = pygame.image.load(os.path.join('Assets', 'Steve_up.png'))
DIAMOND_IMAGE = pygame.image.load(os.path.join('Assets', 'Diamond.png'))

BACKGROUND = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
STEVE_DOWN = pygame.transform.scale(STEVE_DOWN_IMAGE, (STEVE_WIDTH, STEVE_HEIGHT))
STEVE_LEFT = pygame.transform.scale(STEVE_LEFT_IMAGE, (STEVE_WIDTH, STEVE_HEIGHT))
STEVE_RIGHT = pygame.transform.scale(STEVE_RIGHT_IMAGE, (STEVE_WIDTH, STEVE_HEIGHT))
STEVE_UP = pygame.transform.scale(STEVE_UP_IMAGE, (STEVE_WIDTH, STEVE_HEIGHT))
DIAMOND = pygame.transform.scale(DIAMOND_IMAGE, (DIAMOND_WIDTH, DIAMOND_HEIGHT))

# =====================================
# GRID HELPERS
# =====================================
CELL = 40
GRID_OFFSET_X = 44
GRID_OFFSET_Y = 0

def grid_to_pixel(gx, gy, w, h):
    px = GRID_OFFSET_X + (gx - 1) * CELL + (CELL - w) // 2
    py = GRID_OFFSET_Y + (10 - gy) * CELL + (CELL - h) // 2
    return px, py

def diamond_rect(gx, gy):
    px, py = grid_to_pixel(gx, gy, DIAMOND_WIDTH, DIAMOND_HEIGHT)
    return pygame.Rect(px, py, DIAMOND_WIDTH, DIAMOND_HEIGHT)


# =====================================
# DRAWING
# =====================================
def draw_window(steve):
    WIN.blit(BACKGROUND, (0, 0))

    text = "Diamonds: " + str(steve.diamonds)
    draw_text = DIAMOND_FONT.render(text, 1, BLACK)
    WIN.blit(draw_text, (WIDTH - draw_text.get_width() - 20, 10))

    for rect, count in steve.diamonds_floor:
        WIN.blit(DIAMOND, (rect.x, rect.y))
        if count != 1:
            cnt_text = DIAMOND_COUNT_FONT.render(str(count), 1, RED)
            WIN.blit(cnt_text, (rect.x + 5, rect.y))

    if steve.direction == "D":
        WIN.blit(STEVE_DOWN, (steve.my_steve.x, steve.my_steve.y))
    elif steve.direction == "U":
        WIN.blit(STEVE_UP, (steve.my_steve.x, steve.my_steve.y))
    elif steve.direction == "R":
        WIN.blit(STEVE_RIGHT, (steve.my_steve.x, steve.my_steve.y))
    else:
        WIN.blit(STEVE_LEFT, (steve.my_steve.x, steve.my_steve.y))

    pygame.display.update()
    pygame.event.pump()
    pygame.time.delay(MOVE_DELAY)


# =====================================
# STEVE CLASS
# =====================================
class Steve:
    def __init__(self, diamonds, diamonds_floor):
        self.direction = 'D'
        self.position = [1, 1]

        px, py = grid_to_pixel(1, 1, STEVE_WIDTH, STEVE_HEIGHT)
        self.my_steve = pygame.Rect(px, py, STEVE_WIDTH, STEVE_HEIGHT)

        self.diamonds_floor = diamonds_floor
        self.diamonds = max(0, min(int(diamonds), 100))

        draw_window(self)

    def throw_wall_mistake(self):
        print("Oops, there is a wall!")
        pygame.time.delay(1500)
        pygame.quit()
        raise SystemExit

    def move(self):
        gx, gy = self.position

        if self.direction == 'D':
            if gy == 1: self.throw_wall_mistake()
            gy -= 1
        elif self.direction == 'U':
            if gy == 10: self.throw_wall_mistake()
            gy += 1
        elif self.direction == 'L':
            if gx == 1: self.throw_wall_mistake()
            gx -= 1
        elif self.direction == 'R':
            if gx == 10: self.throw_wall_mistake()
            gx += 1

        self.position = [gx, gy]
        self.my_steve.x, self.my_steve.y = grid_to_pixel(gx, gy, STEVE_WIDTH, STEVE_HEIGHT)
        draw_window(self)

    def turn_right(self):
        if self.direction == 'D':
            self.direction = 'L'
        elif self.direction == 'L':
            self.direction = 'U'
        elif self.direction == 'U':
            self.direction = 'R'
        else:
            self.direction = 'D'
        draw_window(self)

    def has_diamond_here(self):
        gx, gy = self.position
        px, py = grid_to_pixel(gx, gy, DIAMOND_WIDTH, DIAMOND_HEIGHT)

        for rect, count in self.diamonds_floor:
            if rect.x == px and rect.y == py and count > 0:
                return True
        return False

    def drop_diamond(self):
        if self.diamonds == 0:
            print("I don't have any diamonds on me")
            pygame.time.delay(1500)
            pygame.quit()
            raise SystemExit

        gx, gy = self.position
        px, py = grid_to_pixel(gx, gy, DIAMOND_WIDTH, DIAMOND_HEIGHT)

        for item in self.diamonds_floor:
            rect, count = item
            if rect.x == px and rect.y == py:
                item[1] += 1
                self.diamonds -= 1
                draw_window(self)
                return

        rect = pygame.Rect(px, py, DIAMOND_WIDTH, DIAMOND_HEIGHT)
        self.diamonds_floor.append([rect, 1])
        self.diamonds -= 1
        draw_window(self)

    def get_diamond(self):
        gx, gy = self.position
        px, py = grid_to_pixel(gx, gy, DIAMOND_WIDTH, DIAMOND_HEIGHT)

        for item in list(self.diamonds_floor):
            rect, count = item
            if rect.x == px and rect.y == py:
                if count == 1:
                    self.diamonds_floor.remove(item)
                else:
                    item[1] -= 1
                self.diamonds += 1
                draw_window(self)
                return

        # For task safety we REMOVE the quitting here
        print("I don't see any diamonds")
        draw_window(self)


# =====================================
# TASKS
# =====================================
def task1(robot):
    robot.turn_right(); robot.turn_right(); robot.turn_right()
    for _ in range(5): robot.move()
    robot.turn_right(); robot.turn_right(); robot.turn_right()
    for _ in range(6): robot.move()
    print("Task 1 completed")

def check_task1(robot):
    print("Checking Task 1...")
    print("Final position =", robot.position)
    if robot.position == [6, 7]:
        print("TASK 1 PASSED ✔")
    else:
        print("TASK 1 FAILED ✘")

def task2(robot):
    # 1) Place 5 diamonds at random grid cells
    all_cells = [(x, y) for x in range(1, 11) for y in range(1, 11)]
    chosen = random.sample(all_cells, 5)

    for gx, gy in chosen:
        rect = diamond_rect(gx, gy)
        robot.diamonds_floor.append([rect, 1])

    # Draw once so you can see initial placement
    draw_window(robot)

    # 2) Let Steve traverse the whole grid in a snake pattern
    #    and collect diamonds ONLY when there is one.

    # Check starting cell (1,1)
    if robot.has_diamond_here():
        robot.get_diamond()

    #For consistency robot should face up
    for _ in range(2):  # use your existing helper
        robot.turn_right()
    # Rows are 1..10 from bottom to top
    for row in range(1, 11):
        # odd rows: left → right, even rows: right → left
        if row % 2 == 1:
            robot.turn_right()
        else:
            for _ in range(3):  # use your existing helper
                robot.turn_right()

        # Move across the row (9 moves = 10 cells)
        for _ in range(9):
            if robot.has_diamond_here():
                robot.get_diamond()
            robot.move()

        # Last cell in the row
        if robot.has_diamond_here():
            robot.get_diamond()

        # Go up to the next row (unless we are on the last one)
        if row < 10:
            if row % 2 == 1:
                for _ in range(3):
                    robot.turn_right()
            else:
                robot.turn_right()
            robot.move()
            if robot.has_diamond_here():
                robot.get_diamond()

    print("Task 2 completed")


def check_task2(robot):
    print("Checking Task 2...")
    diamonds_left = sum(count for _, count in robot.diamonds_floor)
    collected = robot.diamonds

    if diamonds_left == 0 and collected >= 5:
        print("TASK 2 PASSED ✔")
    else:
        print("TASK 2 FAILED ✘")
        print("Diamonds left:", diamonds_left, "Collected:", collected)

def task3(robot):
    robot.drop_diamond()

    #For consistency direct robot to the right
    robot.turn_right(); robot.turn_right(); robot.turn_right()
    for i in range(2, 11):
        robot.move()
        robot.turn_right(); robot.turn_right(); robot.turn_right()
        robot.move()
        for _ in range(i):
            robot.drop_diamond()
        robot.turn_right()

    print("Task 3 completed")

def check_task3(robot):
    print("Checking Task 3...")
    expected = True
    for i in range(1, 11):
        px, py = grid_to_pixel(i, i, DIAMOND_WIDTH, DIAMOND_HEIGHT)
        found = False
        for rect, count in robot.diamonds_floor:
            if rect.x == px and rect.y == py and count == i:
                found = True
                break
        if not found:
            expected = False
    if expected:
        print("TASK 3 PASSED ✔")
    else:
        print("TASK 3 FAILED ✘")


# =====================================
# RUN TASK IN A FRESH GAME
# =====================================
def run_task(task_function, check_function):
    diamonds_floor = []
    robot = Steve(200, diamonds_floor)

    task_function(robot)
    check_function(robot)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_window(robot)

    pygame.quit()

def main():
    # run_task(task1, check_task1)
    # run_task(task2, check_task2)
    # run_task(task3, check_task3)

if __name__ == "__main__":
    main()
