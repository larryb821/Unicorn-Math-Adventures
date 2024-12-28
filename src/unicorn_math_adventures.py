import pygame
import random
import sys
import os
from typing import Tuple, Dict, List
from datetime import datetime
import json

# Initialize Pygame and its mixer for sound
pygame.init()
pygame.mixer.init()

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as bundled exe
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Get the application path for saving data
APP_PATH = os.path.join(os.path.expanduser("~"), "Documents", "Unicorn Math Adventures")
os.makedirs(APP_PATH, exist_ok=True)

# File paths
HIGH_SCORES_FILE = os.path.join(APP_PATH, "high_scores.json")
UNICORN_IMAGE = get_resource_path("assets/images/unicorn.png")
RAINBOW_IMAGE = get_resource_path("assets/images/rainbow.png")
CORRECT_SOUND = get_resource_path("assets/sounds/success-1-6297.mp3")
ERROR_SOUND = get_resource_path("assets/sounds/error-call-to-attention-129258.mp3")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 192, 203)
PURPLE = (147, 112, 219)

# Initialize fonts
pygame.font.init()
FONT = pygame.font.Font(None, 40)
TITLE_FONT = pygame.font.Font(None, 60)
SMALL_FONT = pygame.font.Font(None, 30)  # Smaller font for streak counters

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ella's Unicorn Math Adventures")

# Load assets
try:
    unicorn_image = pygame.image.load(UNICORN_IMAGE)
    unicorn_image = pygame.transform.scale(unicorn_image, (150, 150))
    reward_image = pygame.image.load(RAINBOW_IMAGE)
    reward_image = pygame.transform.scale(reward_image, (100, 100))
except pygame.error as e:
    print(f"Couldn't load images: {e}")
    print("Make sure to run image_converter.py first to convert webp images to png")
    sys.exit(1)

# Sound effects paths
PROGRESS_SOUND = get_resource_path("assets/sounds/level-progress.mp3")
LEVEL_COMPLETE_SOUND = get_resource_path("assets/sounds/level-complete.mp3")
STREAK_MILESTONE_SOUND = get_resource_path("assets/sounds/streak-milestone.mp3")

# Load sound effects
try:
    correct_sound = pygame.mixer.Sound(CORRECT_SOUND)
    wrong_sound = pygame.mixer.Sound(ERROR_SOUND)
    progress_sound = pygame.mixer.Sound(PROGRESS_SOUND)
    level_complete_sound = pygame.mixer.Sound(LEVEL_COMPLETE_SOUND)
    streak_milestone_sound = pygame.mixer.Sound(STREAK_MILESTONE_SOUND)
except Exception as e:
    print(f"Error loading sounds: {e}")
    # Create silent sounds if files can't be loaded
    silent_sound = pygame.mixer.Sound(buffer=bytes([0]*44))
    correct_sound = silent_sound
    wrong_sound = silent_sound
    progress_sound = silent_sound
    level_complete_sound = silent_sound
    streak_milestone_sound = silent_sound

# Clock
clock = pygame.time.Clock()

# Family names for personalized messages
FAMILY = {
    "player": "Ella",
    "sister": "Mila",
    "dad": "Dad",
    "mom": "Mom"
}

def load_high_scores() -> list:
    """Load high scores from file."""
    if os.path.exists(HIGH_SCORES_FILE):
        try:
            with open(HIGH_SCORES_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_high_score(score: int, player_name: str) -> None:
    """Save a new high score."""
    scores = load_high_scores()
    scores.append({
        "score": score,
        "player": player_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:5]  # Keep only top 5 scores
    
    with open(HIGH_SCORES_FILE, 'w') as f:
        json.dump(scores, f)

def show_game_over(score: int, max_streak: int) -> bool:
    """Show game over screen with final score and high scores."""
    high_scores = load_high_scores()
    player_name = ""  # Start with empty name field
    name_input_active = True
    score_saved = False  # Track if score has been saved
    message = ""  # For displaying save status messages
    message_timer = 0
    
    # Clear screen and events before showing game over screen
    screen.fill(PINK)
    pygame.display.flip()
    pygame.event.clear()
    pygame.time.wait(100)  # Brief pause
    
    running = True
    while running:
        screen.fill(PINK)
        current_time = pygame.time.get_ticks()
        
        # Draw game over message
        title = "Time's Up!"
        title_surface = TITLE_FONT.render(title, True, PURPLE)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 50))
        
        # Draw final score and streak
        draw_text(f"Final Score: {score}", WIDTH//2 - 150, 120)
        draw_text(f"Best Streak: {max_streak} ⭐", WIDTH//2 - 150, 160)
        
        # Draw name input field
        draw_text("Enter Your Name:", WIDTH//2 - 150, 220)
        pygame.draw.rect(screen, WHITE if name_input_active else BLACK, 
                        (WIDTH//2 - 150, 260, 300, 50), 2)
        draw_text(player_name, WIDTH//2 - 140, 270)
        
        # Draw high scores with dates
        high_score_start_y = 340
        draw_text("High Scores:", WIDTH//2 - 150, high_score_start_y)
        
        # Calculate button position based on number of high scores
        line_height = 35
        last_line_y = high_score_start_y + 40  # Default if no scores
        
        for i, score_data in enumerate(high_scores):
            line_y = high_score_start_y + 40 + i * line_height
            score_text = f"{score_data['player']}: {score_data['score']}"
            date_text = f"({score_data.get('date', 'N/A')})"
            draw_text(score_text, WIDTH//2 - 150, line_y, font=SMALL_FONT)
            draw_text(date_text, WIDTH//2 + 100, line_y, font=SMALL_FONT)
            last_line_y = line_y
        
        # Draw save and play again buttons below the last score
        button_y = min(last_line_y + 60, HEIGHT - 80)  # Ensure buttons don't go off screen
        save_text = "Score Saved!" if score_saved else "Save Score"
        save_button = draw_button(save_text, WIDTH//2 - 220, button_y, 200, 50, selected=score_saved)
        play_again = draw_button("Play Again", WIDTH//2 + 20, button_y, 200, 50)
        
        # Draw message if timer is active
        if current_time < message_timer:
            message_surface = FONT.render(message, True, PURPLE)
            screen.blit(message_surface, (WIDTH//2 - message_surface.get_width()//2, HEIGHT - 160))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicked on name input field
                name_input_rect = pygame.Rect(WIDTH//2 - 150, 260, 300, 50)
                name_input_active = name_input_rect.collidepoint(event.pos)
                
                # Check button clicks
                if save_button.collidepoint(event.pos) and not score_saved:
                    # Only save if name is not empty
                    if player_name.strip():
                        save_high_score(score, player_name)
                        score_saved = True
                        name_input_active = False
                        message = "Score saved!"
                        message_timer = current_time + 2000
                        # Reload high scores to show updated list
                        high_scores = load_high_scores()
                    else:
                        # Show message to enter name
                        message = "Please enter your name"
                        message_timer = current_time + 2000
                elif play_again.collidepoint(event.pos):
                    # Clear screen and events before returning
                    screen.fill(PINK)
                    pygame.display.flip()
                    pygame.event.clear()
                    pygame.time.wait(100)  # Brief pause
                    running = False
                    return True  # Signal to restart game directly
            elif event.type == pygame.KEYDOWN and name_input_active:
                if event.key == pygame.K_RETURN:
                    name_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 15 and event.unicode.isprintable():
                    player_name += event.unicode
        
        clock.tick(30)
    return False  # Return False if loop exits without clicking Play Again

def generate_word_problem(num1: int, num2: int, operation: str) -> str:
    """Generate a word problem based on the numbers and operation."""
    templates = {
        "+": [
            f"A unicorn collected {num1} rainbows in the morning and {num2} rainbows in the afternoon. How many rainbows did the unicorn collect in total?",
            f"{FAMILY['player']} saw {num1} stars on a rainbow cloud, then {num2} more stars appeared. How many stars are there now?",
            f"{FAMILY['sister']}'s dog buried {num1} bones in the yard and found {num2} more. How many bones does the dog have now?",
            f"A magical garden grew {num1} sparkly flowers yesterday and {num2} more today. How many sparkly flowers are there now?",
            f"{FAMILY['player']} found {num1} glitter pens in her backpack and {num2} more in her desk. How many glitter pens does she have in total?",
            f"The unicorn school has {num1} students in the morning class and {num2} in the afternoon class. How many students are there altogether?"
        ],
        "-": [
            f"{FAMILY['player']} has {num1} magical cupcakes and shares {num2} with {FAMILY['sister']}. How many cupcakes does {FAMILY['player']} have left?",
            f"There are {num1} unicorns at a party, but {num2} unicorns had to leave early. How many unicorns are still at the party?",
            f"A rainbow trail is {num1} feet long. If {num2} feet are covered by clouds, how many feet can you still see?",
            f"A fairy has {num1} magic wands but {num2} of them lost their sparkle. How many sparkly wands are left?",
            f"{FAMILY['player']} collected {num1} seashells at the beach, but gave {num2} to her friend. How many seashells does she have now?",
            f"There were {num1} butterflies in the garden, but {num2} flew away. How many butterflies are still there?"
        ],
        "*": [
            f"There are {num1} unicorns at a party, and each unicorn brings {num2} magical cupcakes. How many cupcakes are there in total?",
            f"{FAMILY['player']} buys {num1} packs of dog treats with {num2} treats in each pack. How many treats does she have in total?",
            f"If each rainbow has {num2} stars and you see {num1} rainbows, how many stars are there in total?",
            f"Each fairy has {num2} magic crystals and there are {num1} fairies. How many magic crystals are there altogether?",
            f"If each unicorn can grant {num2} wishes per day and there are {num1} unicorns, how many wishes can be granted in total?",
            f"{FAMILY['player']} plants {num1} rows of magical flowers with {num2} flowers in each row. How many flowers did she plant in total?"
        ],
        "/": [
            f"A rainbow trail is {num1} feet long. If {num2} unicorns each paint an equal length, how many feet does each unicorn paint?",
            f"{FAMILY['player']} has {num1} sparkly stickers to share equally among {num2} friends. How many stickers does each friend get?",
            f"Mom baked {num1} rainbow cookies to pack equally into {num2} gift boxes. How many cookies go in each box?",
            f"A group of {num2} fairies needs to share {num1} magic crystals equally. How many crystals does each fairy get?",
            f"There are {num1} glitter crayons to be shared among {num2} art stations. How many crayons should go to each station?",
            f"If {num1} magical butterflies need to visit {num2} flower gardens equally, how many butterflies will visit each garden?"
        ]
    }
    return random.choice(templates[operation])

# Levels and problems
LEVELS: Dict[int, Dict] = {
    1: {
        "operations": ["+", "-"],
        "range": (1, 20),
        "description": "Addition & Subtraction",
        "encouragement": [
            f"Great job, {FAMILY['player']}!",
            f"{FAMILY['sister']} would be proud!",
            f"Mom and Dad are amazed!"
        ]
    },
    2: {
        "operations": ["*", "/", "multi"],  # multi for multi-step problems
        "range": (1, 12),  # Times tables up to 12
        "description": "Multiplication & Division",
        "encouragement": [
            "You're becoming a math wizard!",
            "Keep up the great work!",
            "Amazing progress!"
        ]
    },
    3: {
        "operations": ["frac", "dec", "complex"],  # fractions, decimals, complex problems
        "range": (1, 100),
        "description": "Fractions & Decimals",
        "encouragement": [
            "Spectacular solving!",
            "You're a math superstar!",
            "Incredible work!"
        ]
    }
}

def generate_multi_step_problem() -> Tuple[str, int]:
    """Generate a multi-step word problem."""
    # Template 1: Buy multiple items with different quantities and prices
    pencils = random.randint(2, 5)
    pencil_cost = random.randint(2, 5)
    notebooks = random.randint(2, 4)
    notebook_cost = random.randint(3, 6)
    total_cost = (pencils * pencil_cost) + (notebooks * notebook_cost)
    
    question = (
        f"{FAMILY['player']} buys {pencils} magical pencils for {pencil_cost} coins each "
        f"and {notebooks} notebooks for {notebook_cost} coins each. "
        "How many coins did she spend in total?"
    )
    return question, total_cost

def generate_fraction_problem() -> Tuple[str, float]:
    """Generate a fraction word problem."""
    # Common fractions that make sense in recipes and measurements
    fractions = [
        (1, 2, "1/2"),  # half
        (1, 4, "1/4"),  # quarter
        (3, 4, "3/4"),  # three-quarters
        (1, 3, "1/3"),  # third
        (2, 3, "2/3")   # two-thirds
    ]
    
    templates = [
        # Recipe scaling
        lambda frac, multiplier: (
            f"A recipe calls for {frac[2]} cup of sugar. "
            f"If {FAMILY['player']} wants to make {multiplier} times the recipe, "
            "how many cups of sugar does she need?"
        ),
        # Pizza sharing
        lambda frac, multiplier: (
            f"Each fairy eats {frac[2]} of a magical pizza. "
            f"If there are {multiplier} fairies, how many whole pizzas are needed?"
        ),
        # Paint mixing
        lambda frac, multiplier: (
            f"To make sparkly paint, you need {frac[2]} cup of glitter per batch. "
            f"If you want to make {multiplier} batches, how many cups of glitter do you need?"
        ),
        # Garden planning
        lambda frac, multiplier: (
            f"Each rainbow flower needs {frac[2]} cup of magical water daily. "
            f"If you have {multiplier} rainbow flowers, how many cups of water do you need?"
        ),
        # Potion making
        lambda frac, multiplier: (
            f"A unicorn potion requires {frac[2]} cup of starlight. "
            f"To make {multiplier} potions, how many cups of starlight are needed?"
        )
    ]
    
    fraction = random.choice(fractions)  # (numerator, denominator, display_string)
    multiplier = random.randint(2, 4)
    total = (fraction[0] / fraction[1]) * multiplier
    
    question = random.choice(templates)(fraction, multiplier)
    return question, total

def generate_decimal_problem() -> Tuple[str, float]:
    """Generate a decimal word problem."""
    # Common price points that make sense
    prices = [
        (1.50, 0.25),  # $1.50 total, $0.25 each
        (2.00, 0.50),  # $2.00 total, $0.50 each
        (5.00, 1.25),  # $5.00 total, $1.25 each
        (10.00, 2.50), # $10.00 total, $2.50 each
        (7.50, 1.50)   # $7.50 total, $1.50 each
    ]
    
    templates = [
        # Sticker buying
        lambda total, unit: (
            f"{FAMILY['player']} has ${total:.2f} and wants to buy unicorn stickers "
            f"that cost ${unit:.2f} each. How many stickers can she buy?"
        ),
        # Ribbon measuring
        lambda total, unit: (
            f"A magical ribbon is {total:.2f} meters long. If each unicorn needs "
            f"{unit:.2f} meters for their mane, how many unicorns can decorate their manes?"
        ),
        # Crystal collecting
        lambda total, unit: (
            f"{FAMILY['player']} found {total:.2f} grams of magic fairy crystal dust. "
            f"If each necklace needs {unit:.2f} grams, how many necklaces can she make?"
        ),
        # Rainbow paint
        lambda total, unit: (
            f"The fairy store has {total:.2f} liters of rainbow paint. "
            f"If each cloud needs {unit:.2f} liters to become colorful, how many clouds can be painted?"
        ),
        # Magic dust
        lambda total, unit: (
            f"{FAMILY['sister']} found {total:.2f} ounces of magic rainbow dust. "
            f"If each spell requires {unit:.2f} ounces, how many spells can she cast?"
        )
    ]
    
    price = random.choice(prices)  # (total amount, unit cost)
    items = int(price[0] // price[1])
    
    question = random.choice(templates)(price[0], price[1])
    return question, items

def generate_problem(level: int) -> Tuple[str, int]:
    """Generate a random math problem based on the level."""
    level_info = LEVELS[level]
    op = random.choice(level_info["operations"])
    num_range = level_info["range"]
    
    # Special problem types for Level 2 and 3
    if op == "multi":
        return generate_multi_step_problem()
    elif op == "frac":
        return generate_fraction_problem()
    elif op == "dec":
        return generate_decimal_problem()
    elif op == "complex":
        # Randomly choose between fraction and decimal for complex problems
        return random.choice([generate_fraction_problem, generate_decimal_problem])()
    
    # Basic operations
    if op == "*":
        num1 = random.randint(1, num_range[1])
        num2 = random.randint(1, num_range[1])
    elif op == "/":
        # Generate division problems that result in whole numbers
        num2 = random.randint(1, 10)  # divisor
        answer = random.randint(1, 10)  # quotient
        num1 = num2 * answer  # dividend
    else:
        num1 = random.randint(*num_range)
        num2 = random.randint(*num_range)
        if op == "-":
            # Ensure no negative results
            num1, num2 = max(num1, num2), min(num1, num2)
    
    # 50% chance of getting a word problem for basic operations
    if random.random() < 0.5:
        question = generate_word_problem(num1, num2, op)
    else:
        # Use × symbol for multiplication and ÷ for division
        display_op = "×" if op == "*" else "÷" if op == "/" else op
        question = f"{num1} {display_op} {num2}"
    
    # Calculate answer
    if op == "*":
        answer = num1 * num2
    elif op == "/":
        answer = num1 // num2
    elif op == "+":
        answer = num1 + num2
    else:  # op == "-"
        answer = num1 - num2
        
    return question, answer

def draw_text(text: str, x: int, y: int, color: Tuple[int, int, int] = BLACK, font=FONT) -> None:
    """Render text on the screen."""
    text_surface = font.render(str(text), True, color)
    screen.blit(text_surface, (x, y))

def draw_button(text: str, x: int, y: int, width: int, height: int, selected: bool = False) -> pygame.Rect:
    """Draw a button and return its rect."""
    color = PURPLE if selected else BLACK
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, button_rect, 3)
    
    # Center text in button
    text_surface = FONT.render(text, True, color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    
    return button_rect

def main_menu() -> Tuple[bool, int]:
    """Display the main menu and return (should_start, selected_level)."""
    selected_level = 1
    in_level_select = False
    
    while True:
        screen.fill(PINK)
        
        # Draw unicorn at the top
        unicorn_y = 50
        screen.blit(unicorn_image, (WIDTH//2 - 75, unicorn_y))
        
        # Draw title below unicorn
        title = f"Welcome {FAMILY['player']} to"
        subtitle = "Unicorn Math Adventures!"
        
        # Center title text below unicorn
        title_y = unicorn_y + unicorn_image.get_height() + 20
        title_surface = TITLE_FONT.render(title, True, PURPLE)
        subtitle_surface = TITLE_FONT.render(subtitle, True, PURPLE)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, title_y))
        screen.blit(subtitle_surface, (WIDTH//2 - subtitle_surface.get_width()//2, title_y + 70))
        
        if not in_level_select:
            # Draw main menu options
            start_button = draw_button("Start Game", WIDTH//2 - 100, HEIGHT - 200, 200, 50)
            level_select_button = draw_button("Select Level", WIDTH//2 - 100, HEIGHT - 130, 200, 50)
        else:
            # Clear previous title and image
            screen.fill(PINK)
            
            # Draw title at the top
            title = "Select Level"
            title_surface = TITLE_FONT.render(title, True, PURPLE)
            screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 50))
            
            # Calculate button layout with even wider buttons
            button_height = 70
            button_width = 600
            button_spacing = 25
            level_select_font = pygame.font.Font(None, 34)  # Even smaller font for level buttons
            total_buttons = len(LEVELS)
            total_height = (button_height * total_buttons) + (button_spacing * (total_buttons - 1))
            start_y = (HEIGHT - total_height) // 2
            
            # Draw level selection buttons
            level_buttons = []
            for level in LEVELS:
                text = f"Level {level}: {LEVELS[level]['description']}"
                # Use smaller font for level buttons
                button_rect = pygame.Rect(WIDTH//2 - button_width//2, start_y, button_width, button_height)
                pygame.draw.rect(screen, PURPLE if level == selected_level else BLACK, button_rect, 3)
                
                # Center text in button with smaller font
                text_surface = level_select_font.render(text, True, PURPLE if level == selected_level else BLACK)
                text_rect = text_surface.get_rect(center=button_rect.center)
                screen.blit(text_surface, text_rect)
                
                level_buttons.append((button_rect, level))
                start_y += button_height + button_spacing
            
            # Draw back button with fixed spacing from bottom
            back_button = draw_button("Back", WIDTH//2 - 100, HEIGHT - button_height - 20, 200, 50)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, 1
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if not in_level_select:
                    if start_button.collidepoint(mouse_pos):
                        return True, selected_level
                    elif level_select_button.collidepoint(mouse_pos):
                        in_level_select = True
                else:
                    if back_button.collidepoint(mouse_pos):
                        in_level_select = False
                    else:
                        for button, level in level_buttons:
                            if button.collidepoint(mouse_pos):
                                selected_level = level
                                in_level_select = False  # Return to main menu after selection
        
        clock.tick(30)

def draw_progress_bar(surface: pygame.Surface, x: int, y: int, width: int, height: int, progress: float, color: Tuple[int, int, int]) -> None:
    """Draw a progress bar showing level completion."""
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)
    if progress > 0:
        inner_width = int((width - 4) * progress)
        pygame.draw.rect(surface, color, (x + 2, y + 2, inner_width, height - 4))

def reset_game_state(starting_level: int) -> dict:
    """Reset and return all game state variables"""
    return {
        "streak": 0,
        "max_streak": 0,
        "progress": 0,
        "wrong_attempts": 0,
        "showing_answer": False,
        "continue_button": None,
        "level": starting_level,
        "score": 0,
        "previous_question": "",
        "user_answer": "",
        "reward_count": 0,
        "message": "",
        "message_timer": 0,
        "question": None,
        "answer": None
    }

def game_loop(starting_level: int) -> bool:
    """Run the main game loop and return True if player wants to play again."""
    while True:
        # Initialize game state
        state = reset_game_state(starting_level)
        state["question"], state["answer"] = generate_problem(state["level"])
        
        # Start game loop
        running = True
        start_time = pygame.time.get_ticks()
        
        while running:
            screen.fill(WHITE)
            current_time = pygame.time.get_ticks()
            
            # Check if time's up
            remaining_time = max(0, 300 - (current_time - start_time) // 1000)
            if remaining_time <= 0:
                restart = show_game_over(state["score"], state["max_streak"])
                if restart:
                    # Reset game state and continue playing
                    break  # Break inner loop to restart game
                else:
                    return False  # Return to main menu
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN and state["showing_answer"] and state["continue_button"]:
                    if state["continue_button"].collidepoint(event.pos):
                        # Reset state and generate new question
                        state["showing_answer"] = False
                        state["wrong_attempts"] = 0
                        state["continue_button"] = None
                        state["previous_question"] = state["question"]
                        state["question"], state["answer"] = generate_problem(state["level"])
                        while state["question"] == state["previous_question"]:
                            state["question"], state["answer"] = generate_problem(state["level"])
                        state["user_answer"] = ""
                elif event.type == pygame.KEYDOWN and not state["showing_answer"]:
                    if event.key == pygame.K_RETURN and state["user_answer"]:
                        # Check answer based on level type
                        try:
                            correct = False
                            
                            # Handle fraction inputs (e.g., "4/3" or "1 1/3")
                            if "/" in state["user_answer"] and state["level"] == 3:
                                parts = state["user_answer"].split()
                                if len(parts) > 1:  # Mixed number (e.g., "1 1/3")
                                    whole = int(parts[0])
                                    num, denom = map(int, parts[1].split("/"))
                                    user_value = whole + (num / denom)
                                else:  # Improper fraction (e.g., "4/3")
                                    num, denom = map(int, state["user_answer"].split("/"))
                                    user_value = num / denom
                                # For fraction problems, compare the actual values
                                correct = abs(user_value - state["answer"]) < 0.01
                            else:
                                # For non-fraction problems, convert to appropriate type
                                user_value = float(state["user_answer"]) if state["level"] == 3 else int(state["user_answer"])
                                if isinstance(state["answer"], float):
                                    # For decimal problems, allow small differences
                                    correct = abs(user_value - state["answer"]) < 0.01
                                else:
                                    correct = user_value == state["answer"]
                            
                            if correct:
                                # Correct answer handling
                                state["score"] += 10 * (1 + state["streak"] // 5)  # Bonus points for streaks
                                state["streak"] += 1
                                state["max_streak"] = max(state["streak"], state["max_streak"])
                                state["reward_count"] += 1
                                state["progress"] = state["streak"] / 10  # Update progress (10 streak needed for level up)
                                
                                # Play appropriate sound effects
                                if state["streak"] > 0 and state["streak"] % 5 == 0:  # Streak milestone (5, 10, etc.)
                                    streak_milestone_sound.play()
                                    state["message"] = f"🔥 {state['streak']} STREAK! AMAZING! 🔥"
                                    
                                    # Level up at streak of 10
                                    if state["streak"] % 10 == 0 and state["level"] < max(LEVELS.keys()):
                                        state["level"] += 1
                                        level_complete_sound.play()
                                        state["message"] = f"🌟 Level Up! Now trying {LEVELS[state['level']]['description']}! 🌟"
                                        state["message_timer"] = current_time + 3000
                                        state["progress"] = 0
                                else:
                                    correct_sound.play()
                                    state["message"] = f"{random.choice(LEVELS[state['level']]['encouragement'])} ({state['streak']} streak!)"
                                
                                # Progress bar increase sound
                                progress_sound.play()
                                
                                state["message_timer"] = current_time + 2000
                                
                                # Generate new question, ensuring it's different from the previous one
                                state["previous_question"] = state["question"]
                                state["question"], state["answer"] = generate_problem(state["level"])
                                while state["question"] == state["previous_question"]:  # Avoid repeating the same question
                                    state["question"], state["answer"] = generate_problem(state["level"])
                            else:
                                wrong_sound.play()
                                state["wrong_attempts"] += 1
                                if state["wrong_attempts"] >= 3:
                                    state["showing_answer"] = True
                                    state["message"] = f"The correct answer is: {state['answer']}"
                                    state["message_timer"] = current_time + 5000  # Show for 5 seconds
                                    # Level down if not at level 1
                                    if state["level"] > 1:
                                        state["level"] = max(1, state["level"] - 1)
                                        state["message"] = f"Let's try {LEVELS[state['level']]['description']} problems! The answer was {state['answer']}"
                                    # Add continue button
                                    state["continue_button"] = pygame.Rect(WIDTH//2 - 100, HEIGHT - 150, 200, 50)
                                else:
                                    state["message"] = f"Try again! ({state['wrong_attempts']}/3) 💫"
                                state["message_timer"] = current_time + 2000
                                state["streak"] = 0  # Reset streak on wrong answer
                                state["reward_count"] = 0  # Reset reward count on wrong answer
                                state["progress"] = state["streak"] / 10  # Update progress bar on wrong answer too
                            state["user_answer"] = ""
                        except ValueError:
                            state["user_answer"] = ""
                    elif event.key == pygame.K_BACKSPACE:
                        state["user_answer"] = state["user_answer"][:-1]
                    elif len(state["user_answer"]) < 15:  # Allow longer answers for mixed numbers
                        # Allow digits for all levels
                        if event.unicode.isdigit():
                            state["user_answer"] += event.unicode
                        # Allow decimal point, forward slash, and space for Level 3
                        elif state["level"] == 3 and event.unicode in [".", "/", " "]:
                            # Handle space separately
                            if event.unicode == " ":
                                # Only allow one space and only if there's already some input
                                if " " not in state["user_answer"] and state["user_answer"]:
                                    state["user_answer"] += " "
                            # Handle decimal point and slash
                            else:
                                # Split by space to check last part
                                parts = state["user_answer"].split()
                                # If no parts or the last part doesn't contain the symbol yet
                                if not parts or event.unicode not in parts[-1]:
                                    state["user_answer"] += event.unicode
            
            # Draw game state
            screen.fill(PINK)
            
            # Create white header bar
            header_height = 100
            pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, header_height))
            pygame.draw.line(screen, PURPLE, (0, header_height), (WIDTH, header_height), 2)
            
            # Draw level and score in top left
            draw_text(f"Level {state['level']}: {LEVELS[state['level']]['description']}", 20, 20)
            draw_text(f"Score: {state['score']}", 20, 55)
            
            # Layout for header elements (right side)
            right_margin = 20
            timer_section_width = 150  # Width reserved for timer
            streak_section_width = 200  # Width reserved for streak counters
            
            # Draw timer in far right
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            timer_text = f"Time: {minutes}:{seconds:02d}"
            timer_surface = FONT.render(timer_text, True, BLACK)
            timer_x = WIDTH - timer_surface.get_width() - right_margin
            screen.blit(timer_surface, (timer_x, 20))
            
            # Draw streak counters to the left of timer
            streak_x = timer_x - streak_section_width
            if state["streak"] > 0:
                streak_text = f"Streak: {state['streak']} 🔥"
                text_surface = SMALL_FONT.render(streak_text, True, BLACK)
                screen.blit(text_surface, (streak_x, 20))
            if state["max_streak"] > 0:
                best_text = f"Best: {state['max_streak']} ⭐"
                text_surface = SMALL_FONT.render(best_text, True, BLACK)
                screen.blit(text_surface, (streak_x, 50))
            
            # Draw progress bar below streak counters
            progress_width = 150
            progress_x = streak_x
            draw_progress_bar(screen, progress_x, 75, progress_width, 15, state["progress"], PURPLE)
            
            # Draw problem with word wrapping if needed, adjusted for header
            problem_start_y = header_height + 40  # Start below header
            if len(state["question"]) > 50:  # If it's a longer word problem
                words = state["question"].split()
                lines = []
                current_line = []
                
                for word in words:
                    current_line.append(word)
                    if len(' '.join(current_line)) > 40:  # Max chars per line
                        if len(current_line) > 1:
                            current_line.pop()
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            lines.append(' '.join(current_line))
                            current_line = []
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Calculate total height needed for the problem text
                text_height = len(lines) * 40
                problem_y = problem_start_y
                
                # Draw each line of the problem
                for i, line in enumerate(lines):
                    draw_text(line, 20, problem_y + (i * 40))
                draw_text("= ?", 20, problem_y + text_height + 10)
                
                # Draw answer box below the problem with padding
                answer_y = problem_y + text_height + 60
                pygame.draw.rect(screen, WHITE, (20, answer_y, 360, 50))
                draw_text(f"Your Answer: {state['user_answer']}", 30, answer_y + 10)
            else:
                # For simple problems
                draw_text(f"Problem: {state['question']} = ?", 20, 180)
                
                # Draw answer box with input format hint
                pygame.draw.rect(screen, WHITE, (20, 230, 360, 50))
                hint = "(Enter as mixed number like 1 1/3 or fraction like 4/3)" if state["level"] == 3 else ""
                draw_text(f"Your Answer: {state['user_answer']} {hint}", 30, 240)
            
            # Calculate positions for images at the bottom
            bottom_margin = 20
            image_y = HEIGHT - unicorn_image.get_height() - bottom_margin
            
            # Draw unicorn on right side at the bottom
            screen.blit(unicorn_image, (WIDTH - unicorn_image.get_width() - 20, image_y))
            
            # Draw rewards in a single row at the bottom (max 5 visible)
            rewards_x = 20
            rewards_spacing = 10
            visible_rewards = min(state["reward_count"], 5)  # Limit to 5 visible rewards
            for i in range(visible_rewards):
                screen.blit(reward_image, (rewards_x + (i * (reward_image.get_width() + rewards_spacing)), image_y))
            
            # Draw message if timer is active
            if current_time < state["message_timer"]:
                message_surface = FONT.render(state["message"], True, PURPLE)
                screen.blit(message_surface, (WIDTH//2 - message_surface.get_width()//2, HEIGHT - 80))
                
            # Draw continue button if showing answer
            if state["showing_answer"] and state["continue_button"]:
                draw_button("Continue", state["continue_button"].x, state["continue_button"].y, state["continue_button"].width, state["continue_button"].height)
            
            pygame.display.flip()
            clock.tick(30)
    
    return True  # Continue playing

def main():
    """Main game entry point."""
    while True:
        # Reset display and events before showing menu
        screen.fill(PINK)
        pygame.display.flip()
        pygame.event.clear()
        pygame.time.wait(100)  # Brief pause for stability
        
        # Show main menu and get starting level
        should_start, starting_level = main_menu()
        if not should_start:
            break
        
        # Run game loop
        if not game_loop(starting_level):
            break  # Exit if player quits

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
