import pyglet
import pyglet.gl
from pyglet.window import mouse, key
import random
import time


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_pos = snake_vel * 5

        # Board settings
        self.n_squares_x = self.width // snake_vel
        self.n_squares_y = self.height // snake_vel

        # Create the snake and the food
        self.snake = [
            [-2 * snake_vel + init_pos, init_pos],
            [- snake_vel + init_pos, init_pos],
            [init_pos, init_pos]

        ]
        self.food = [20 * snake_vel, 20 * snake_vel]

        # Snake stuff
        self.vel_x = snake_vel
        self.vel_y = 0
        self.head_color = [.5, 8., .6, 1.] * 4
        self.tail_color = [.0, 1., .0, 1.] * 4

        # Food stuff
        self.food_color = [1., 0., 0., 1.] * 4
        self.food_vertex = self.get_vertex(self.food[0], self.food[1])

        # Display a counter
        self.counter = 0
        self.best_score = 0
        self.label = pyglet.text.Label(
            '',
            font_name='Times New Roman',
            font_size=12,
            bold=True,
            x=80,
            y=self.height - 30,
            width=100,
            height=40,
            anchor_x='center',
            anchor_y='center',
            color=(255, 255, 255, 100),
            multiline=True
        )

        self.eaten = False
        self.dead = False
        self.game_over = False

    def on_draw(self):
        # Window features #######################################
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,
                              pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        #########################################################

        # --- Draw the food -----------------------------
        if self.eaten is True:
            # if snake has eaten, draw a new food
            new_x = snake_vel * \
                random.randint(2, self.n_squares_x - 2)
            new_y = snake_vel * \
                random.randint(2, self.n_squares_y - 2)
            self.food[0], self.food[1] = new_x, new_y
            self.food_vertex = self.get_vertex(new_x, new_y)
            self.eaten = False

        food_vertices = pyglet.graphics.vertex_list(
            4,
            ('v2f', self.food_vertex),
            ('c4f', self.food_color)
        )
        food_vertices.draw(pyglet.gl.GL_POLYGON)

        # --- Draw the snake -----------------------------
        for i, block in enumerate(self.snake):
            # Check the boundaries
            if block[0] < 0:
                block[0] += self.width
            elif block[0] > self.width - snake_vel:
                block[0] = 0

            if block[1] < 0:
                block[1] += self.height
            elif block[1] > self.height - snake_vel:
                block[1] = 0

            if i == len(self.snake) - 1:
                color = self.head_color
            else:
                color = self.tail_color

            snake_vertices = pyglet.graphics.vertex_list(
                4,
                ('v2f', self.get_vertex(block[0], block[1])),
                ('c4f', color)
            )

            snake_vertices.draw(pyglet.gl.GL_POLYGON)

        # --- Draw the counter -----------------------------
        text = 'Score:\t{}\nBest:\t{}'.format(self.counter, self.best_score)
        # self.label.text = 'Score: {}\nBest of this game: {}'.format(
        #     self.counter, self.best_score)
        self.label.text = text
        self.label.draw()

    def update(self, dt):
        if self.dead is False:
            # Check if the snake has eaten the food
            snake_head = self.snake[-1]
            dif_food_snake_x = abs(snake_head[0] - self.food[0])
            dif_food_snake_y = abs(snake_head[1] - self.food[1])
            if dif_food_snake_x <= 1. and dif_food_snake_y <= 1.:
                self.eat(self.food[0], self.food[1])
                self.counter += 1

            self.move()
        else:
            if self.game_over is False:
                time.sleep(1)
                self.game_over = True
            self.snake = self.snake[1:]
            if len(self.snake) == 0:
                time.sleep(1)
                if self.counter > self.best_score:
                    self.best_score = self.counter
                self.counter = 0

                # Restart positions
                self.vel_x = snake_vel
                self.vel_y = 0
                init_pos = snake_vel * 5
                self.snake = [
                    [-2 * snake_vel + init_pos, init_pos],
                    [- snake_vel + init_pos, init_pos],
                    [init_pos, init_pos]

                ]
                self.food = [20 * snake_vel, 20 * snake_vel]
                self.food_vertex = self.get_vertex(self.food[0], self.food[1])

                self.game_over = False
                self.dead = False
                self.eaten = False

    # Methods to control snake behavior
    def move(self):
        # Check if the snake eats itself and dies
        self.check_block_pos()

        # Move the tail to the next block
        for i in range(len(self.snake) - 1):
            self.snake[i][0] = self.snake[i + 1][0]
            self.snake[i][1] = self.snake[i + 1][1]

        # Move the head
        self.snake[-1][0] += self.vel_x
        self.snake[-1][1] += self.vel_y

    def eat(self, x_pos, y_pos):
        self.snake.append([x_pos, y_pos])
        self.eaten = True

    def get_vertex(self, pos_x, pos_y):
        vertex = []

        # Add the four vertex to the vertex list
        vertex.append(pos_x)
        vertex.append(pos_y)

        vertex.append(pos_x)
        vertex.append(pos_y + snake_vel)

        vertex.append(pos_x + snake_vel)
        vertex.append(pos_y + snake_vel)

        vertex.append(pos_x + snake_vel)
        vertex.append(pos_y)

        return vertex

    def change_vel(self, vel_x, vel_y):
        next_head_pos_x = self.snake[-1][0] + vel_x
        next_head_pos_y = self.snake[-1][1] + vel_y

        # Check if we are trying to move backwards!
        dif_x = abs(next_head_pos_x - self.snake[-2][0])
        dif_y = abs(next_head_pos_y - self.snake[-2][1])
        if dif_x > 1. and dif_y > 1.:
            self.vel_x = vel_x
            self.vel_y = vel_y

    def check_block_pos(self):
        next_head_pos_x = self.snake[-1][0] + self.vel_x
        next_head_pos_y = self.snake[-1][1] + self.vel_y

        for part in self.snake[:-2:]:
            dif_x = abs(next_head_pos_x - part[0])
            dif_y = abs(next_head_pos_y - part[1])
            if dif_x <= 1. and dif_y <= 1.:
                self.dead = True

    def mouse(self, x, y):
        pass


if __name__ == '__main__':
    global snake_vel

    snake_vel = 20
    width, height = 800, 600

    world = MyWindow(width, height)
    pyglet.gl.glClearColor(.1, .1, .1, .1)
    world.on_draw()

    @world.event
    def on_mouse_press(x, y, button, modifiers):
        if button == mouse.LEFT:
            world.mouse(x, y)

    @world.event
    def on_key_press(symbol, modifiers):
        '''
        Move the snake with the keyboard arrows
        '''
        if symbol == key.UP or symbol == key.W:
            world.change_vel(0, snake_vel)
        if symbol == key.DOWN or symbol == key.S:
            world.change_vel(0, -snake_vel)
        if symbol == key.RIGHT or symbol == key.D:
            world.change_vel(snake_vel, 0)
        if symbol == key.LEFT or symbol == key.A:
            world.change_vel(-snake_vel, 0)

    pyglet.clock.schedule_interval(world.update, 1 / 20.)
    pyglet.app.run()
