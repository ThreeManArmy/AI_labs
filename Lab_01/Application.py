import sys
from Player import *
from Enemy import *

pygame.init()
vec = pygame.math.Vector2


"""
This is main class that describe an Application and its methods
"""


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = None
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.cell_width = MAZE_WIDTH//COLS
        self.cell_height = MAZE_HEIGHT//ROWS
        self.walls = []
        self.coins = []
        self.teleports = []
        self.enemies = []
        self.e_pos = []
        self.p_pos = None
        self.load_map()
        self.player = Player(self, vec(self.p_pos))
        self.high_score = self.load_score()
        self.last_player_pos = self.player.grid_pos
        self.path_algo_state = BFS_ALG

    def start_game(self):
        """
        This is the main loop of game that controls game state and calls function to draw the contents
        and/or functions that process the input events in game.
        :return:
        """
        while self.running:
            if self.state == MENU:
                self.start_events()
                self.start_draw()
            elif self.state == GAMING:
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == GAME_OVER:
                self.game_over_events()
                self.game_over_draw()
            elif self.state == WINNER:
                self.winner_events()
                self.winner_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def load_score(self):
        """
        This function reads the file and loads the highest score.
        :return: int: score
        """
        with open("./Score.txt", "r") as file:
            score = int(file.read())
            print(score)
        return score

    def write_score(self, score):
        """
        This function write the score on file.
        :param score: int score
        """
        with open("./Score.txt", "w") as file:
            file.write(str(score))

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        """
        Drawing the text with color, font, size and etc.
        :param words: str - Text to draw
        :param screen: Surface - The surface on which text will be painted)
        :param pos: tuple(x,y) X and Y - screen positions of left top corner of test
        :param size: int - Size of text
        :param colour: tuple(R,G,B)
        :param font_name: str - font name
        :param centered: bool - need to draw the text in center or not. Default=FALSE
        """
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    def load_map(self):
        """
        This method loads the map background and reads the map file,
        that consists of WALLS, COINS, TELEPORTS,
        ENEMIES' spawn and PLAYER`s spawn.

        Also we create the list of VECTORS(int,int) that helps us to make main process of game
        :return:
        """
        self.background = pygame.image.load('./Maze.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))

        with open("./walls.txt", 'r') as file:
            for y_index, line in enumerate(file):
                for x_index, char in enumerate(line):
                    if char == "1":
                        self.walls.append(vec(x_index, y_index))
                    elif char == "C":
                        self.coins.append(vec(x_index, y_index))
                    elif char == "P":
                        self.p_pos = [x_index, y_index]
                    elif char in ["1", "2", "3", "4"]:
                        self.enemies.append(Enemy(self, [x_index, y_index]))
                        self.e_pos.append([x_index, y_index])

    def draw_grid(self):
        """
        Simple method to draw grid. Uses only for debug.
        :return:
        """
        for x in range(WIDTH//self.cell_width):
            pygame.draw.line(self.background, GREY, (x*self.cell_width, 0),
                             (x*self.cell_width, HEIGHT))
        for x in range(HEIGHT//self.cell_height):
            pygame.draw.line(self.background, GREY, (0, x*self.cell_height),
                             (WIDTH, x*self.cell_height))

    def reset(self):
        """
        This method allow to reset the game after lose or win
        :return:
        """
        self.player.lives = PLAYER_LIVES
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.position)
            enemy.pix_pos = enemy.get_pix_pos()

        self.coins = []
        with open("./walls.txt", 'r') as file:
            for y_index, line in enumerate(file):
                for x_index, char in enumerate(line):
                    if char == 'C':
                        self.coins.append(vec(x_index, y_index))
        self.state = GAMING

    def switch_algo(self):
        if self.path_algo_state == BFS_ALG:
            print("Switched to DFS")
            self.path_algo_state = DFS_ALG
        elif self.path_algo_state == DFS_ALG:
            print("Switched to UCS")
            self.path_algo_state = UCS_ALG
        else:
            print("Switched to BFS")
            self.path_algo_state = BFS_ALG

# This block of code describes an intro functions of game. Start screen and start screen's key inputs

    def start_events(self):
        """
        Method control the inputs. Press SCAPE to start play. ESC for exit
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = GAMING

    def start_draw(self):
        """
        Drawing the main menu.
        :return:
        """
        self.screen.fill(BLACK)
        self.draw_text('Pacman', self.screen, [
                       WIDTH//2, HEIGHT//2-50], START_TEXT_SIZE, RED, START_FONT, centered=True)
        self.draw_text('Press space to play', self.screen, [
                       WIDTH//2, HEIGHT//2], START_TEXT_SIZE, RED, START_FONT, centered=True)
        self.draw_text(f'HIGH SCORE {self.high_score}', self.screen, [4, 0],
                       START_TEXT_SIZE, WHITE, START_FONT)
        pygame.display.update()

# This is the main block of code controls game process and gameplay

    def playing_events(self):
        """
        This method allows you to control in game player.
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.change_direction(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.change_direction(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.change_direction(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.change_direction(vec(0, 1))
                if event.key == pygame.K_z:
                    self.switch_algo()

    def playing_update(self):
        """
        Updating the player and check is he winner. If he is game turn to winner state.
        :return:
        """
        if len(self.coins) == 0:
            self.state = WINNER
        self.player.update()


    def playing_draw(self):
        """
        This method draw main game scenes and update it.
        :return:
        """
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (PADDING // 2, PADDING // 2))
        self.draw_coins()
        self.draw_teleports()
        self.draw_text(f'CURRENT SCORE: {self.player.current_score}',
                       self.screen, [60, 0], 36, WHITE, START_FONT)
        self.draw_text(f'HIGH SCORE: {self.high_score}', self.screen, [WIDTH//2+60, 0], 36, WHITE, START_FONT)
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
            if self.player.grid_pos != self.last_player_pos:
                if self.path_algo_state == BFS_ALG:
                    enemy.path = enemy.BFS(vec(enemy.position), self.player.grid_pos)
                elif self.path_algo_state == DFS_ALG:
                    enemy.path = enemy.DFS(vec(enemy.position), self.player.grid_pos)
                elif self.path_algo_state == UCS_ALG:
                    enemy.path = enemy.UCS(vec(enemy.position), self.player.grid_pos)
                self.last_player_pos = copy.copy(self.player.grid_pos)

            enemy.draw_path()
        pygame.display.update()

    def remove_life(self):
        """
        This method control Player's lives and control moment of lose.
        :return:
        """
        self.player.lives -= 1

        if self.player.lives == 0:
            if self.player.current_score > self.high_score:
                self.high_score = self.player.current_score
            self.write_score(self.player.current_score)
            self.state = GAME_OVER
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.position)
                enemy.pix_pos = enemy.get_pix_pos()

    def draw_coins(self):
        """
        Simple draw coins method.
        :return:
        """
        for coin in self.coins:
            pygame.draw.circle(self.screen, YELLOW,
                               (int(coin.x*self.cell_width) + self.cell_width // 2 + PADDING // 2,
                                int(coin.y*self.cell_height) + self.cell_height // 2 + PADDING // 2), 4)

    def draw_teleports(self):
        """
        Drawing teleports on map
        :return:
        """
        for teleport in self.teleports:
            pygame.draw.circle(self.screen, BLACK,
                               (int(teleport.x*self.cell_width) + self.cell_width // 2 + PADDING // 2,
                                int(teleport.y*self.cell_height) + self.cell_height // 2 + PADDING // 2), 16)
            pygame.draw.circle(self.screen, BLUE,
                               (int(teleport.x*self.cell_width) + self.cell_width // 2 + PADDING // 2,
                                int(teleport.y*self.cell_height) + self.cell_height // 2 + PADDING // 2), 12)

# This block of code manages game over state of game
    def game_over_events(self):
        """
        Control inputs in 'Game over' state of game.
        You can play again if you press Space or left game with pressing the ESC button
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_draw(self):
        """
        Draws game over screen.
        :return:
        """
        self.screen.fill(BLACK)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press space to PLAY AGAIN"
        self.draw_text("GAME OVER", self.screen, [WIDTH//2, 100],  52, RED, "Sans Serif MS", centered=True)
        self.draw_text(again_text, self.screen, [
                       WIDTH//2, HEIGHT//2],  36, GREY, "Sans Serif MS", centered=True)
        self.draw_text(quit_text, self.screen, [
                       WIDTH//2, HEIGHT//1.5],  36, GREY, "Sans Serif MS", centered=True)
        pygame.display.update()

# This block of code manages an win state of game
    def winner_events(self):
        """
        Control inputs in 'WON' state of game.
        You can play again if you press Space or left game with pressing the ESC button
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                temp_score = self.player.current_score
                self.reset()
                self.player.current_score = temp_score
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            if event.type == pygame.QUIT:
                self.running = False

    def winner_draw(self):
        """
        Draws winner screen.
        :return:
        """
        self.screen.fill(BLACK)
        self.draw_text("You are WINNER!", self.screen, [
            WIDTH // 2, HEIGHT // 2 - 50], 36, GREEN, "Sans Serif MS", centered=True)
        win_text = "Press space to PLAY AGAIN"
        self.draw_text(win_text, self.screen, [
            WIDTH // 2, HEIGHT // 2], 36, GREEN, "Sans Serif MS", centered=True)
        pygame.display.update()
