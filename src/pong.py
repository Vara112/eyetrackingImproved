import turtle
import random
import time

#TAKEN FROM https://www.geeksforgeeks.org/python/create-pong-game-using-python-turtle/

# Create screen
sc = turtle.Screen()
sc.title("Pong game")
sc.bgcolor("white")
sc.setup(width=1000, height=600)
sc.tracer(0)

# Left paddle
left_pad = turtle.Turtle()
left_pad.speed(0)
left_pad.shape("square")
left_pad.color("black")
left_pad.shapesize(stretch_wid=6, stretch_len=2)
left_pad.penup()
left_pad.goto(-400, 0)

# Right paddle (AI controlled)
right_pad = turtle.Turtle()
right_pad.speed(0)
right_pad.shape("square")
right_pad.color("black")
right_pad.shapesize(stretch_wid=6, stretch_len=2)
right_pad.penup()
right_pad.goto(400, 0)

PADDLE_HALF_HEIGHT = 60          #shapesize stretch_wid=6 -> 20*6=120 tall paddle
AI_MAX_SPEED = 6                 #max pixels/frame the AI paddle can move (keeps it beatable)

# Ball of circle shape
hit_ball = turtle.Turtle()
hit_ball.speed(0)
hit_ball.shape("circle")
hit_ball.color("blue")
hit_ball.penup()
hit_ball.goto(0, 0)
BASE_SPEED = 5
MAX_SPEED = 12
hit_ball.dx = BASE_SPEED
hit_ball.dy = -BASE_SPEED

# Initialize the score
left_player = 0
right_player = 0
WINNING_SCORE = 5

# Displays the score
sketch = turtle.Turtle()
sketch.speed(0)
sketch.color("blue")
sketch.penup()
sketch.hideturtle()
sketch.goto(0, 260)
sketch.write("Left_player : 0    Right_player: 0",
             align="center", font=("Courier", 24, "normal"))


def update_score():
    sketch.clear()
    sketch.write("Left_player : {}    Right_player: {}".format(
        left_player, right_player), align="center",
        font=("Courier", 24, "normal"))


def serve_ball(towards_left):
    """Reset the ball to center and serve it towards whoever just conceded."""
    hit_ball.goto(0, 0)
    hit_ball.dx = -BASE_SPEED if towards_left else BASE_SPEED
    hit_ball.dy = random.choice([-1, 1]) * BASE_SPEED


# Functions to move the left (human) paddle
def paddleaup():
    y = left_pad.ycor()
    if y < 250:  # Limit paddle movement
        y += 20
        left_pad.sety(y)


def paddleadown():
    y = left_pad.ycor()
    if y > -240:  # Limit paddle movement
        y -= 20
        left_pad.sety(y)


def ai_move_right_paddle():
    """Tracks the ball's y position at a capped speed so it's beatable."""
    target_y = hit_ball.ycor()
    y = right_pad.ycor()

    if y < target_y:
        y = min(y + AI_MAX_SPEED, target_y, 250)
    elif y > target_y:
        y = max(y - AI_MAX_SPEED, target_y, -240)

    right_pad.sety(y)


# Keyboard bindings
sc.listen()
sc.onkeypress(paddleaup, "w")
sc.onkeypress(paddleadown, "s")

game_over = False

# Main game loop
while True:
    sc.update()
    time.sleep(0.01)  # Add delay to make game smoother

    if game_over:
        continue

    ai_move_right_paddle()

    hit_ball.setx(hit_ball.xcor() + hit_ball.dx)
    hit_ball.sety(hit_ball.ycor() + hit_ball.dy)

    # Checking borders
    if hit_ball.ycor() > 280:
        hit_ball.sety(280)
        hit_ball.dy *= -1

    if hit_ball.ycor() < -280:
        hit_ball.sety(-280)
        hit_ball.dy *= -1

    if hit_ball.xcor() > 500:
        left_player += 1
        update_score()
        serve_ball(towards_left=False)

    if hit_ball.xcor() < -500:
        right_player += 1
        update_score()
        serve_ball(towards_left=True)

    # Paddle ball collision (speeds the ball up a little each hit, capped)
    if (hit_ball.xcor() > 360 and hit_ball.xcor() < 370) and \
            (abs(hit_ball.ycor() - right_pad.ycor()) < PADDLE_HALF_HEIGHT):
        hit_ball.setx(360)
        hit_ball.dx = -min(abs(hit_ball.dx) + 0.5, MAX_SPEED)

    if (hit_ball.xcor() < -360 and hit_ball.xcor() > -370) and \
            (abs(hit_ball.ycor() - left_pad.ycor()) < PADDLE_HALF_HEIGHT):
        hit_ball.setx(-360)
        hit_ball.dx = min(abs(hit_ball.dx) + 0.5, MAX_SPEED)

    if left_player >= WINNING_SCORE or right_player >= WINNING_SCORE:
        winner = "Left_player" if left_player >= WINNING_SCORE else "Right_player"
        sketch.goto(0, 0)
        sketch.write("{} wins!".format(winner), align="center",
                      font=("Courier", 36, "bold"))
        game_over = True
