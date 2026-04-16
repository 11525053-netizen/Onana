import pygame
import sys
import math
import random

from pygame.image import load

# graphics
def create_pixel_sprite(color_map, pixel_size=6, custom_colors=None):
    colors = {
        'W': (255, 255, 255), 'B': (0, 0, 0), 'S': (180, 180, 180),
        'C': (0, 255, 255), 'H': (255, 219, 172), 'D': (80, 40, 20),
        'A': (40, 40, 40), 'G': (34, 139, 34), 'Y': (255, 255, 150),
        'R': (200, 50, 50), 'M': (120, 120, 125), 'T': (255, 150, 50),
        'K': (230, 190, 120), 'O': (255, 165, 0), 'P': (255, 215, 0) 
    }
    if custom_colors: colors.update(custom_colors)
    width = len(color_map[0]) * pixel_size
    height = len(color_map) * pixel_size
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(color_map):
        for x, char in enumerate(row):
            if char in colors:
                pygame.draw.rect(surf, colors[char], (x*pixel_size, y*pixel_size, pixel_size, pixel_size))
    return surf
def load_sprite(filename, size=None):
    img = pygame.image.load(filename).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img


#inheritance
class Entity:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self.sprite = None

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self._x, self._y))

#encapsulation
class StaffRobot(Entity):   
    def __init__(self, x, y, color):
        super().__init__(x, y)
        self.__stage = "IDLE" 
        self.target = [x, y]
        self.cust_idx = None
        self.order_name = ""
        self.sprite = load_sprite("mambo.png", (88, 150 ))

    def move(self):
        dx, dy = self.target[0] - self._x, self.target[1] - self._y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 5:
            self._x += dx/dist * 8
            self._y += dy/dist * 8
            return False
        return True

    def get_stage(self): return self.__stage
    def set_stage(self, stage): self.__stage = stage

class Customer(Entity):
    def __init__(self, x, y, seat):
        super().__init__(x, y)
        self.seat = seat
        self.order = None
        design = ["  TTTTT  ", " TTTTTTT ", " T HHH T ", " H B H B ", " HHHHHHH ", "  XXXXX  ", " XXXXXXX ", "  DD DDD "]
        self.sprite = create_pixel_sprite(design, 7, {'X': (random.randint(50,250), 100, 100)})

    def draw_bubble(self, screen, font):
        if self.order:
            bx = self._x - 85 if self.seat == "left" else self._x + 110
            pygame.draw.ellipse(screen, (255, 255, 255), (bx, self._y - 60, 140, 40))
            screen.blit(font.render(self.order, True, (0,0,0)), (bx + 15, self._y - 50))

# polymorphism
class Plant(Entity):
    def draw(self, screen):
        pygame.draw.rect(screen, (80, 40, 10), (self._x, self._y, 35, 40))
        pygame.draw.ellipse(screen, (20, 80, 20), (self._x - 25, self._y - 35, 85, 45))
        pygame.draw.ellipse(screen, (34, 139, 34), (self._x - 15, self._y - 55, 65, 35))

class Gramophone(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sprite = create_pixel_sprite(["  PPP  "," P   P ","  PPP  ","   P   ","  DDD  "," DDDDD "], 😎
        self.notes = []

    def update(self, screen):
        super().draw(screen)
        if random.random() < 0.05: self.notes.append([self._x + 30, self._y, 1.0])
        for n in self.notes[:]:
            n[1] -= 2; n[2] -= 0.01
            if n[2] <= 0: self.notes.remove(n)
            else: pygame.draw.circle(screen, (255, 255, 255, int(n[2]*255)), (int(n[0]), int(n[1])), 4)

#drinks and snacks
class CoffeeMachineSystem:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.steam = []

    def run(self, screen, time):
        pygame.draw.rect(screen, (45, 45, 50), self.rect, border_radius=10)
        scan = (time // 100) % 15
        for j in range(15):
            c = (255, 50, 50) if j == scan else (60, 20, 20)
            pygame.draw.rect(screen, c, (self.rect.x + 20 + j*15, self.rect.y + 20, 10, 5))
        if random.random() < 0.15: self.steam.append([self.rect.centerx, self.rect.y, 2])
        for p in self.steam[:]:
            p[1] -= 2; p[2] += 0.05; alpha = max(0, 180 - p[2]*15)
            s_surf = pygame.Surface((30, 30), pygame.SRCALPHA); pygame.draw.circle(s_surf, (220, 220, 220, alpha), (15, 15), int(p[2]))
            screen.blit(s_surf, (p[0]-15, p[1]-15))
            if alpha <= 0: self.steam.remove(p)

def main():
    pygame.init()   
    pygame.mixer.init()
    pygame.mixer.music.load("arknights.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    serve_sound = pygame.mixer.Sound("mambosound.mp3")
    serve_sound.set_volume(0.5)
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    
    # --- INDIVIDUAL ICONS FOR EACH MENU ITEM ---
    coffee_icon = create_pixel_sprite([" WW ","S  S","SSSS"," SS "], 5, {'S': (100, 60, 20)})
    tea_icon = create_pixel_sprite([" WW ","WGGW","WGGW  WW "], 5, {'G': (50, 150, 50)})
    milktea_icon = create_pixel_sprite([" C  ","SSSS","SBB S","SSSS"], 5, {'S': (240, 220, 200)})
    pancake_icon = create_pixel_sprite(["YYYY","YYYY","YYYY"], 5)
    croissant_icon = create_pixel_sprite(["  OO  "," OOOO ","  OO  "], 5, {'O': (255, 165, 0)})
    
    icons = [None, coffee_icon, tea_icon, milktea_icon, pancake_icon, croissant_icon]
    
    # OOP Initialization
    robots = [StaffRobot(W//2-150, H//2, (0,255,255)), StaffRobot(W//2+150, H//2, (200,100,255))]
    tables = [(W//5, H//2, "left"), (W//5, H*3//4, "right"), (W*4//5-150, H//2, "left"), (W*4//5-150, H*3//4, "right")]
    clients = [Customer(t[0]-55 if t[2]=="left" else t[0]+140, t[1]-50, t[2]) for t in tables]
    machine = CoffeeMachineSystem(W//2-350, H//3-160, 700, 130)
    plants = [Plant(30, H//3+20), Plant(W-80, H//3+20), Plant(30, H-120), Plant(W-80, H-120)]
    player = Gramophone(W-170, H//3 + 10)
    
    bar_rect = pygame.Rect(W//2 - 400, H//3 - 30, 600, 100)
    cake_rect = pygame.Rect(W//2 + 220, H//3 - 40, 180, 110)
    
    clock = pygame.time.Clock()
    font_menu = pygame.font.SysFont("Courier New", 20, bold=True)
    font_bubble = pygame.font.SysFont("Arial", 16, bold=True)
    last_order = pygame.time.get_ticks()
    turn = 0

    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        if current_time - last_order > 3500:
            idx = random.randint(0, 3)
            if not clients[idx].order and not any(r.cust_idx == idx for r in robots):
                rb = robots[turn]
                if rb.get_stage() == "IDLE":
                    item = random.choice(["COFFEE", "TEA", "MILK TEA", "PANCAKE", "CROISSANT"])
                    clients[idx].order, rb.order_name, rb.cust_idx = item, item, idx
                    rb.set_stage("PICKING")
                    # Destination logic
                    if item in ["PANCAKE", "CROISSANT"]:
                        rb.target = [cake_rect.centerx, bar_rect.centery+30]
                    else:
                        rb.target = [bar_rect.centerx-40, bar_rect.centery+30]
                    turn = (turn + 1) % 2
            last_order = current_time

        for i, rb in enumerate(robots):
            if rb.move():
                if rb.get_stage() == "PICKING":
                    rb.target = [tables[rb.cust_idx][0], tables[rb.cust_idx][1]]
                    rb.set_stage("DELIVERING")
                elif rb.get_stage() == "DELIVERING":
                    clients[rb.cust_idx].order = None; rb.cust_idx = None
                    serve_sound.play()
                    rb.target = [W//2 + (150 if i==1 else -150), H//2]; rb.set_stage("RETURNING")
                elif rb.get_stage() == "RETURNING": rb.set_stage("IDLE")

        # --- DRAWING ---
        screen.fill((25, 22, 20))
        pygame.draw.rect(screen, (55, 35, 20), (0, H//3, W, H*2//3)) # Floor

        # Window
        pygame.draw.rect(screen, (80, 120, 160), (W-200, 40, 140, 180))
        pygame.draw.rect(screen, (40, 25, 10), (W-200, 40, 140, 180), 😎
        pygame.draw.line(screen, (40, 25, 10), (W-130, 40), (W-130, 220), 4)
        pygame.draw.line(screen, (40, 25, 10), (W-200, 130), (W-60, 130), 4)

        player.update(screen)
        machine.run(screen, current_time)
        pygame.draw.rect(screen, (100, 100, 110), (bar_rect.centerx-10, H//3-50, 20, 50)) 
        pygame.draw.rect(screen, (40, 20, 5), bar_rect, border_radius=5)
        
        # Cake Case (Synced with Menu)
        pygame.draw.rect(screen, (50, 30, 10), cake_rect, border_radius=5)
        pygame.draw.rect(screen, (150, 200, 210, 120), cake_rect.inflate(-10,-10))
        for j in range(2): 
            # Pancake (Matches Icon)
            pygame.draw.ellipse(screen, (230,190,120), (cake_rect.x+25, cake_rect.y+20+j*40, 45, 25))
            # Croissant (Matches Icon)
            pygame.draw.arc(screen, (255,165,0), (cake_rect.x+105, cake_rect.y+25+j*40, 45, 30), 0, 3.14, 6)

        # Full Menu with Individual Icons
        pygame.draw.rect(screen, (15, 15, 15), (40, 50, 280, 240), border_radius=10)
        menu_labels = ["MENU", "COFFEE", "TEA", "MILK TEA", "PANCAKE", "CROISSANT"]
        for j, item in enumerate(menu_labels):
            color = (255, 215, 0) if j == 0 else (200, 200, 200)
            screen.blit(font_menu.render(item, True, color), (90, 70 + j * 35))
            if j > 0 and icons[j]: screen.blit(icons[j], (55, 70 + j * 35))

        for p in plants: p.draw(screen)
        for i, c in enumerate(clients):
            pygame.draw.rect(screen, (80, 50, 30), (tables[i][0], tables[i][1], 130, 75), border_radius=5)
            c.draw(screen); c.draw_bubble(screen, font_bubble)
        
        for rb in robots:
            rb.draw(screen)
            if rb.get_stage() == "PICKING" and rb.order_name not in ["PANCAKE", "CROISSANT"]:
                pygame.draw.rect(screen, (0, 191, 255), (bar_rect.centerx-42, bar_rect.y, 4, 40))

        pygame.display.flip(); clock.tick(60)

if _name_ == "_main_":
    main()
