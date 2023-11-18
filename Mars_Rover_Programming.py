from abc import ABC, abstractmethod

# Command Interface
class Command(ABC):
    @abstractmethod
    def execute(self, rover):
        pass

# Concrete Commands
class MoveCommand(Command):
    def execute(self, rover):
        rover.move()

class LeftCommand(Command):
    def execute(self, rover):
        rover.turn_left()

class RightCommand(Command):
    def execute(self, rover):
        rover.turn_right()

# Receiver
class Rover:
    def __init__(self, x, y, direction, grid_size, obstacles):
        self.x = x
        self.y = y
        self.direction = direction
        self.grid_size = grid_size
        self.obstacles = obstacles

    def move(self):
        new_x, new_y = self.calculate_new_position()
        if self.is_valid_move(new_x, new_y):
            self.x, self.y = new_x, new_y
        else:
            print("Obstacle detected. Unable to move.")

    def turn_left(self):
        directions = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.direction = directions[self.direction]

    def turn_right(self):
        directions = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        self.direction = directions[self.direction]

    def calculate_new_position(self):
        if self.direction == 'N':
            return self.x, self.y + 1
        elif self.direction == 'S':
            return self.x, self.y - 1
        elif self.direction == 'E':
            return self.x + 1, self.y
        elif self.direction == 'W':
            return self.x - 1, self.y

    def is_valid_move(self, x, y):
        return 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1] and (x, y) not in self.obstacles

    def get_status_report(self):
        return f"Rover is at ({self.x}, {self.y}) facing {self.direction}. No obstacles detected."

# Client
class RoverController:
    def __init__(self):
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def execute_commands(self, rover):
        for command in self.commands:
            command.execute(rover)

# Client Code
grid_size = (10, 10)
starting_position = (0, 0, 'N')
obstacles = [(2, 2), (3, 5)]
commands = ['M', 'M', 'R', 'M', 'L', 'M']

rover = Rover(*starting_position, grid_size, obstacles)
controller = RoverController()

for command_code in commands:
    if command_code == 'M':
        controller.add_command(MoveCommand())
    elif command_code == 'L':
        controller.add_command(LeftCommand())
    elif command_code == 'R':
        controller.add_command(RightCommand())

controller.execute_commands(rover)

# Output
print(f"Final Position: ({rover.x}, {rover.y}, {rover.direction})")
print(rover.get_status_report())