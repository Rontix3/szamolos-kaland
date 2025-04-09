import pygame
import random
import math

# --- Initialization ---
pygame.init()

# --- Game Settings ---
WIDTH, HEIGHT = 800, 600
TEXT_COLOR = (255, 255, 0)  # Yellow text          
OUTLINE_COLOR = (0, 0, 0)    # Black outline         
DRAGON_SIZE = 100
MIN_DISTANCE = 350
BOX_BG_COLOR = (30, 30, 30)  # Dark gray for text boxes

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Adventure - Knight Edition")

# Fonts
font = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)
font_large = pygame.font.Font(None, 48)

def render_outlined_text(text, font, text_color, outline_color):
    """Render text with outline"""
    text_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)
    final_surface = pygame.Surface((text_surface.get_width()+2, text_surface.get_height()+2), pygame.SRCALPHA)
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                final_surface.blit(outline_surface, (1+dx, 1+dy))
    
    final_surface.blit(text_surface, (1, 1))
    return final_surface

def draw_text_box(text, font, text_color, outline_color, bg_color, x, y, padding=10):
    """Draw text in a framed box"""
    text_surface = render_outlined_text(text, font, text_color, outline_color)
    box_width = text_surface.get_width() + 2*padding
    box_height = text_surface.get_height() + 2*padding
    box_rect = pygame.Rect(x, y, box_width, box_height)
    
    # Draw background
    pygame.draw.rect(screen, bg_color, box_rect)
    # Draw frame (2px thick)
    pygame.draw.rect(screen, text_color, box_rect, 2)
    # Draw text
    screen.blit(text_surface, (x + padding, y + padding))
    
    return box_rect

# --- Mute/Unmute buttons ---
mute_img = pygame.image.load("mute.png").convert_alpha()
unmute_img = pygame.image.load("unmute.png").convert_alpha()
button_size = 50
mute_img = pygame.transform.scale(mute_img, (button_size, button_size))
unmute_img = pygame.transform.scale(unmute_img, (button_size, button_size))
mute_button_rect = pygame.Rect(WIDTH - button_size - 20, 20, button_size, button_size)
is_muted = False

# --- Load animation images ---
dragon_images = [
    pygame.transform.scale(pygame.image.load(f"dragon_{i}.png"), (DRAGON_SIZE, DRAGON_SIZE)) 
    for i in range(1, 5)
]

explosion_images = [
    pygame.transform.scale(pygame.image.load(f"explosion_{i}.png"), (DRAGON_SIZE, DRAGON_SIZE)) 
    for i in range(1, 6)
]

# --- Load backgrounds ---
backgrounds = [pygame.image.load(f"background{i}.png") for i in range(1, 4)]
for i in range(len(backgrounds)):
    backgrounds[i] = pygame.transform.scale(backgrounds[i], (WIDTH, HEIGHT))
current_background = 0

# Start and victory screens
start_screen_background = pygame.transform.scale(pygame.image.load("start_background.png"), (WIDTH, HEIGHT))
victory_screen_background = pygame.transform.scale(pygame.image.load("victory_background.png"), (WIDTH, HEIGHT))

# --- Knight character ---
knight_images = [pygame.transform.scale(pygame.image.load(f"knight{i}.png"), (50, 50)) 
                for i in range(1, 5)]
knight_index = 0
animation_speed = 5
animation_counter = 0

# --- Player settings ---
player_x, player_y = 100, HEIGHT - 100
score = 0
player_name = ""
error_message = ""
error_timer = 0
victory_music_played = False

# --- Load sounds ---
pygame.mixer.music.load("background_music.mp3")
victory_music = pygame.mixer.Sound("victory_music.mp3")
explosion_sound = pygame.mixer.Sound("explosion.mp3")

# --- Dragon class ---
class Dragon:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, DRAGON_SIZE, DRAGON_SIZE)
        self.animation_index = 0
        self.is_exploding = False
        self.explosion_frame = 0
        self.is_selected = False
        self.sound_played = False

    def update(self):
        if not self.is_exploding:
            self.animation_index = (self.animation_index + 1) % 20
            
    def draw(self):
        if self.is_exploding:
            if not self.sound_played:
                explosion_sound.play()
                self.sound_played = True
                
            if self.explosion_frame < len(explosion_images):
                screen.blit(explosion_images[self.explosion_frame], self.rect)
                self.explosion_frame += 1
                return True
            return False
        else:
            frame = self.animation_index // 5
            screen.blit(dragon_images[frame], self.rect)
            if self.is_selected:
                pygame.draw.rect(screen, (255, 0, 0), self.rect, 3)
            return True

def generate_valid_position(existing_dragons):
    base_positions = [
        (WIDTH//5, HEIGHT//5),
        (WIDTH//5*4, HEIGHT//5),
        (WIDTH//5, HEIGHT//5*4),
        (WIDTH//5*4, HEIGHT//5*4),
        (WIDTH//2, HEIGHT//5),
        (WIDTH//2, HEIGHT//5*4),
        (WIDTH//2, HEIGHT//2)
    ]
    
    for pos in base_positions:
        x = pos[0] + random.randint(-50, 50)
        y = pos[1] + random.randint(-50, 50)
        
        valid = True
        for dragon in existing_dragons:
            dx = abs(x - dragon.rect.x)
            dy = abs(y - dragon.rect.y)
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < MIN_DISTANCE:
                valid = False
                break
                
        if valid and 150 < x < WIDTH-250 and 150 < y < HEIGHT-250:
            return (x, y)
    
    return (random.randint(200, WIDTH-200), random.randint(200, HEIGHT-200))

def create_dragons(_):
    dragons = []
    for _ in range(7):
        x, y = generate_valid_position(dragons)
        dragons.append(Dragon(x, y))
    return dragons

dragons = create_dragons(current_background)

# --- Question generation ---
def generate_question():
    num1, num2 = random.randint(1, 10), random.randint(1, 10)
    operation = random.choice(["+", "-", "*"])
    return f"{num1} {operation} {num2}", eval(f"{num1}{operation}{num2}")

math_question, correct_answer = generate_question()

def reset_game():
    global player_x, score, current_background, player_name, entering_name, show_scores, victory_music_played, game_started, victory, dragons, target_x
    
    player_x = 100
    target_x = 100
    score = 0
    current_background = 0
    player_name = ""
    entering_name = False
    show_scores = False
    victory_music_played = False
    game_started = False
    victory = False
    dragons = create_dragons(current_background)
    pygame.mixer.music.play(-1)

def draw_button(text, x, y, w, h, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, TEXT_COLOR, button_rect, 2)
    text_surface = render_outlined_text(text, font, TEXT_COLOR, OUTLINE_COLOR)
    screen.blit(text_surface, (x + (w - text_surface.get_width())//2, y + (h - text_surface.get_height())//2))
    if button_rect.collidepoint(mouse) and click[0] == 1 and action:
        action()

# --- Start screen ---
def show_start_screen():
    screen.blit(start_screen_background, (0, 0))
    # White text for start screen
    title_text = render_outlined_text("Math Adventure - Knight Edition", font_large, (255, 255, 255), OUTLINE_COLOR)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 200))
    
    good_game_text = render_outlined_text("Good luck!", font, (255, 255, 255), OUTLINE_COLOR)
    screen.blit(good_game_text, (WIDTH//2 - good_game_text.get_width()//2, HEIGHT//2 - 150))

    description_lines = [
        "Answer math questions correctly,",
        "move forward, and defeat the dragons!",
        "Use mouse to select dragons,",
        "and Enter to submit answers!"
    ]
    
    y_offset = HEIGHT//2 - 80
    for line in description_lines:
        desc_text = render_outlined_text(line, font_small, (255, 255, 255), OUTLINE_COLOR)
        screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, y_offset))
        y_offset += 30
    
    # Yellow button for start screen
    BUTTON_COLOR = (255, 255, 0)
    button_text = render_outlined_text("Start", font, BUTTON_COLOR, OUTLINE_COLOR)
    button_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 100, 200, 50)
    
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect, 2)
    screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width())//2, 
                             button_rect.y + (button_rect.height - button_text.get_height())//2))
    
    if button_rect.collidepoint(mouse) and click[0] == 1:
        start_game()
    
    pygame.display.flip()

def start_game():
    global game_started
    game_started = True
    pygame.mixer.music.play(-1)

def show_victory_screen():
    screen.blit(victory_screen_background, (0, 0))
    victory_text = render_outlined_text(f"VICTORY! Score: {score}", font_large, (255, 255, 255), OUTLINE_COLOR)
    screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 150))
    
    try:
        with open("scoreboard.txt", "a+") as file:
            file.seek(0)
            scores = file.readlines()
            if player_name:
                file.write(f"{player_name}: {score}\n")
        
        score_data = []
        for s in scores:
            try:
                name, scr = s.strip().split(": ")
                score_data.append((name, int(scr)))
            except ValueError:
                continue
        
        score_data.sort(key=lambda x: x[1], reverse=True)
        y_offset = HEIGHT//2 - 50
        for i, (name, scr) in enumerate(score_data[:5]):
            place_text = f"{i+1}. {name.ljust(15)} {scr} points"
            place_surface = render_outlined_text(place_text, font, (255, 255, 255), OUTLINE_COLOR)
            screen.blit(place_surface, (WIDTH//2 - 200, y_offset))
            y_offset += 40
    
    except Exception as e:
        error_text = render_outlined_text("No saved scores!", font, (255, 255, 255), OUTLINE_COLOR)
        screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2 + 100))

# --- Main game loop ---
running = True
game_started = False
answer = ""
victory = False
entering_name = False
show_scores = False
target_x = player_x

while running:
    if not game_started:
        show_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                start_game()
        continue

    if error_timer > 0:
        error_timer -= 1
    else:
        error_message = ""

    screen.fill((0, 0, 0))
    screen.blit(backgrounds[current_background], (0, 0))
    
    if show_scores:
        show_victory_screen()
        if is_muted:
            screen.blit(unmute_img, mute_button_rect)
        else:
            screen.blit(mute_img, mute_button_rect)
        pygame.display.flip()
        pygame.time.delay(5000)
        reset_game()
        game_started = False
        continue
    
    if entering_name:
        name_prompt = render_outlined_text("Enter your name: " + player_name, font, (255, 255, 255), OUTLINE_COLOR)
        screen.blit(name_prompt, (WIDTH//2 - name_prompt.get_width()//2, HEIGHT//2))
        if is_muted:
            screen.blit(unmute_img, mute_button_rect)
        else:
            screen.blit(mute_img, mute_button_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    with open("scoreboard.txt", "a") as file:
                        file.write(f"{player_name}: {score}\n")
                    entering_name = False
                    show_scores = True
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode
        continue
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if mute_button_rect.collidepoint(mouse_pos):
                is_muted = not is_muted
                if is_muted:
                    pygame.mixer.music.set_volume(0)
                    explosion_sound.set_volume(0)
                    victory_music.set_volume(0)
                else:
                    pygame.mixer.music.set_volume(1.0)
                    explosion_sound.set_volume(1.0)
                    victory_music.set_volume(1.0)
            else:
                for dragon in dragons:
                    if dragon.rect.collidepoint(mouse_pos):
                        dragon.is_selected = not dragon.is_selected
                    else:
                        dragon.is_selected = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not any(d.is_selected for d in dragons):
                    error_message = "First select a dragon!"
                    error_timer = 30
                else:
                    try:
                        if int(answer) == correct_answer:
                            score += 10
                            target_x = min(player_x + 100, WIDTH - 100)
                            for dragon in dragons[:]:
                                if dragon.is_selected:
                                    dragon.is_exploding = True
                            dragons = [d for d in dragons if d.draw() and not d.is_exploding]
                            
                            if target_x >= WIDTH - 100:
                                if current_background == len(backgrounds) - 1:
                                    victory = True
                                    entering_name = True
                                    if not victory_music_played:
                                        pygame.mixer.music.stop()
                                        victory_music.play()
                                        victory_music_played = True
                                else:
                                    current_background += 1
                                    dragons = create_dragons(current_background)
                                    target_x = 100
                            math_question, correct_answer = generate_question()
                            answer = ""
                        else:
                            score -= 5
                            target_x = max(player_x - 100, 100)
                            new_x, new_y = generate_valid_position(dragons)
                            dragons.append(Dragon(new_x, new_y))
                            answer = ""
                    except ValueError:
                        pass
            elif event.key == pygame.K_BACKSPACE:
                answer = answer[:-1]
            elif event.key in (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                             pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_MINUS):
                answer += event.unicode
    
    player_x += (target_x - player_x) * 0.1
    animation_counter += 1
    if animation_counter >= animation_speed:
        knight_index = (knight_index + 1) % len(knight_images)
        animation_counter = 0
    
    for dragon in dragons:
        dragon.update()
    
    screen.blit(knight_images[knight_index], (int(player_x), player_y))
    
    for dragon in dragons:
        dragon.draw()
    
    # Draw UI elements with yellow frames
    draw_text_box(f"Question: {math_question} = ?", font, TEXT_COLOR, OUTLINE_COLOR, BOX_BG_COLOR, 20, 20)
    draw_text_box(f"Answer: {answer}", font, TEXT_COLOR, OUTLINE_COLOR, BOX_BG_COLOR, 20, 70)
    draw_text_box(f"Score: {score}", font, TEXT_COLOR, OUTLINE_COLOR, BOX_BG_COLOR, WIDTH - 250, 20)
    
    if is_muted:
        screen.blit(unmute_img, mute_button_rect)
    else:
        screen.blit(mute_img, mute_button_rect)
    
    if error_message:
        error_rect = draw_text_box(error_message, font, TEXT_COLOR, OUTLINE_COLOR, BOX_BG_COLOR, 
                                 WIDTH//2 - 150, HEIGHT - 60, 20)
    
    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()