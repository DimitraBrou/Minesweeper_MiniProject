#importing the library
import pygame
import sys
import time

from minesweeper import Minesweeper, MinesweeperAI

# Design of the game
HEIGHT = 8
WIDTH = 8
MINES = 8

BLUE = (26, 38, 52)
GRAY = (138, 159, 183)
WHITE = (255, 255, 255)

# Create game
size = width, height = 900, 600
screen = pygame.display.set_mode((600, 800), pygame.RESIZABLE)

# Initializing Pygame
pygame.init()

# Fonts
JetBrains = "assets/fonts/JetBrainsMono-Bold.ttf"
smallFont = pygame.font.Font(JetBrains, 20)
mediumFont = pygame.font.Font(JetBrains, 28)
largeFont = pygame.font.Font(JetBrains, 40)

# Music
pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.play(-1)

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
mine_grey = pygame.image.load("assets/images/mine.png")
mine_grey = pygame.transform.scale(mine_grey, (cell_size, cell_size))
mine_red = pygame.image.load("assets/images/mine-red.png")
mine_red = pygame.transform.scale(mine_red, (cell_size, cell_size))

# Create game and AI agent
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Keep track of revealed cells, mined cells, and if a mine was hit (mine_red)
revealed = set()
mine = set()
lost = False


# Autoplay game
autoplay = False
autoplaySpeed = 0.3
makeAiMove = False

while True:

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLUE)

    # Draw board
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Add a mine, flag, or number if needed
            if game.mine_field((i, j)) and lost:
                if (i,j) == mine_detonated:
                    screen.blit(mine_red, rect)
                else:
                    screen.blit(mine_grey, rect)
            elif (i, j) in mine:
                screen.blit(mine_grey, rect)
            elif (i, j) in revealed:
                neighbors = smallFont.render(
                    str(game.close_mines((i, j))),
                    True, BLUE
                )
                neighborsTextRect = neighbors.get_rect()
                neighborsTextRect.center = rect.center
                screen.blit(neighbors, neighborsTextRect)

            row.append(rect)
        cells.append(row)

    # Autoplay Button
    autoplayBtn = pygame.Rect(
        (1 / 6) * width + BOARD_PADDING, (1 / 3) * height + 400,
        (width / 3) - BOARD_PADDING * 2, 50)
    bText = "Autoplay" if not autoplay else "Stop"
    buttonText = mediumFont.render(bText, True, BLUE)
    buttonRect = buttonText.get_rect()
    buttonRect.center = autoplayBtn.center
    pygame.draw.rect(screen, WHITE, autoplayBtn)
    screen.blit(buttonText, buttonRect)

    # AI Move button
    aiButton = pygame.Rect(
        (1 / 6) * width + BOARD_PADDING, (1 / 3) * height + 460,
        (width / 3) - BOARD_PADDING * 2, 50)
    buttonText = mediumFont.render("AI Move", True, BLUE)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, WHITE, aiButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    resetButton = pygame.Rect(
        (1 / 6) * width + BOARD_PADDING, (1 / 3) * height + 520,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Reset", True, BLUE)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, WHITE, resetButton)
    screen.blit(buttonText, buttonRect)

    # Display won or game over
    text = "Game over :(" if lost else "Congrats, you won! :)" if game.mines == mine else ""
    text = mediumFont.render(text, True, WHITE)
    textRect = text.get_rect()
    textRect.center = ((1 / 3) * width , (1 / 3) * height +580)
    screen.blit(text, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    if right == 1 and not lost and not autoplay:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in mine:
                        mine.remove((i, j))
                    else:
                        mine.add((i, j))
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # Switch over to autoplay, when Autoplay button is clicked
        if autoplayBtn.collidepoint(mouse):
            if not lost:
                autoplay = not autoplay
            else:
                autoplay = False
            time.sleep(0.2)
            continue

        # AI-agent make a move when "AI MOVE" Button clicked
        if aiButton.collidepoint(mouse) and not lost:
            move = ai.do_safe_move()
            if move is None:
                move = ai.do_move_randomly()
                if move is None:
                    flags = ai.mines.copy()
                    print("You found all mines, no moves left to make. Congrats!")
                else:
                    print("AI-agent makes a random move due to no known safe moves left.")
            else:
                print("AI-agent makes a safe move.")
            time.sleep(0.2)

        # Game reset
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed = set()
            mine = set()
            lost = False
            mine_detonated = None
            continue


        # User makes a move when click on a cell
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in mine
                            and (i, j) not in revealed):
                        move = (i, j)

    # AI-agent make moves when "autoplay" Button clicked
    if autoplay or makeAiMove:
        if makeAiMove:
            makeAiMove = False
        move = ai.do_safe_move()
        if move is None:
            move = ai.do_move_randomly()
            if move is None:
                mine = ai.mines.copy()
                print("You found all mines, no moves left to make. Congrats!")
                autoplay = False
            else:
                print("AI-agent makes a random move due to no known safe moves left.")
        else:
            print("AI-agent makes a safe move.")

        # Delay for autoplay
        if autoplay:
            time.sleep(autoplaySpeed)

    # AI-agent update his knowledge and make a move
    if move:
        if game.mine_field(move):
            lost = True
            mine_detonated = move
            autoplay = False
        else:
            nearby = game.close_mines(move)
            revealed.add(move)
            ai.update_knowledge(move, nearby)

    pygame.display.flip()
