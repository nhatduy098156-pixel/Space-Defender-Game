import pygame
import random
import sys

# --- CẤU HÌNH ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (10, 10, 20)
RED = (255, 50, 50)       # Màu lính thường
BLUE = (50, 150, 255)     # Màu người chơi
YELLOW = (255, 255, 0)    # Màu đạn người chơi
GREEN = (0, 255, 0)
PURPLE = (150, 0, 200)    # MÀU BOSS
ORANGE = (255, 165, 0)    # Màu đạn Boss

# Khởi tạo Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Defender: BOSS BATTLE")
clock = pygame.time.Clock()

# Font chữ
font_title = pygame.font.SysFont("Arial", 60, bold=True)
font_text = pygame.font.SysFont("Arial", 25)
font_score = pygame.font.SysFont("Arial", 20)

# --- CÁC HÀM HỖ TRỢ ---
def draw_text_center(text, font, color, y_offset=0):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(surface, rect)

def create_particles(x, y, color):
    particles = []
    for _ in range(10):
        particles.append({
            'x': x, 'y': y,
            'vx': random.randint(-5, 5),
            'vy': random.randint(-5, 5),
            'size': random.randint(3, 6),
            'color': color,
            'life': 20
        })
    return particles

# --- CLASS XỬ LÝ GAME ---
class Game:
    def __init__(self):
        self.state = "MENU" 
        self.reset_game()
        
    def reset_game(self):
        self.player_x = SCREEN_WIDTH // 2 - 25
        self.player_y = SCREEN_HEIGHT - 60
        self.player_hp = 3
        self.score = 0
        
        self.bullets = []       # Đạn người chơi
        self.enemies = []       # Lính thường
        self.particles = []
        
        # Biến cho Boss
        self.boss_active = False
        self.boss = None        # Sẽ là dict chứa thông tin boss
        self.boss_bullets = []  # Đạn của boss
        
        self.spawn_timer = 0
        
    def spawn_boss(self):
        """Khởi tạo Boss"""
        self.boss_active = True
        self.boss = {
            'x': SCREEN_WIDTH // 2 - 50,
            'y': 50,
            'w': 100, 'h': 100,      # Kích thước to
            'hp': 50, 'max_hp': 50,  # Máu nhiều
            'speed': 3,
            'dir': 1                 # 1 là sang phải, -1 là sang trái
        }
        # Xóa hết lính thường khi boss ra
        self.enemies = []

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.state in ["MENU", "GAMEOVER", "VICTORY"]:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = "PLAYING"
                
                elif self.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        self.bullets.append([self.player_x + 20, self.player_y])
                    if event.key == pygame.K_p:
                        self.state = "PAUSED"
                        
                elif self.state == "PAUSED":
                    if event.key == pygame.K_p: self.state = "PLAYING"

        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.player_x > 0:
                self.player_x -= 6
            if keys[pygame.K_RIGHT] and self.player_x < SCREEN_WIDTH - 50:
                self.player_x += 6

    def update(self):
        if self.state != "PLAYING": return

        # --- LOGIC SPAWN BOSS ---
        # Nếu điểm > 20 và chưa có boss -> Gọi Boss
        if self.score >= 20 and not self.boss_active:
            self.spawn_boss()

        # --- CẬP NHẬT BOSS (Nếu đang có boss) ---
        if self.boss_active and self.boss:
            # 1. Di chuyển Boss (Sang trái phải)
            self.boss['x'] += self.boss['speed'] * self.boss['dir']
            if self.boss['x'] <= 0 or self.boss['x'] >= SCREEN_WIDTH - self.boss['w']:
                self.boss['dir'] *= -1 # Đổi hướng
            
            # 2. Boss bắn đạn (Xác suất ngẫu nhiên)
            if random.randint(0, 100) < 3: # 3% cơ hội mỗi khung hình
                # Bắn từ giữa bụng boss
                bx = self.boss['x'] + self.boss['w'] // 2
                by = self.boss['y'] + self.boss['h']
                self.boss_bullets.append([bx, by])

            # 3. Check đạn người chơi trúng Boss
            boss_rect = pygame.Rect(self.boss['x'], self.boss['y'], self.boss['w'], self.boss['h'])
            for b in self.bullets[:]:
                bullet_rect = pygame.Rect(b[0], b[1], 10, 15)
                if bullet_rect.colliderect(boss_rect):
                    self.boss['hp'] -= 1
                    self.bullets.remove(b)
                    self.particles.extend(create_particles(b[0], b[1], PURPLE))
                    
                    if self.boss['hp'] <= 0:
                        self.state = "VICTORY" # Thắng khi giết Boss
        
        # --- CẬP NHẬT LÍNH THƯỜNG (Chỉ khi KHÔNG CÓ Boss) ---
        else:
            self.spawn_timer += 1
            if self.spawn_timer > max(20, 60 - self.score):
                x = random.randint(0, SCREEN_WIDTH - 50)
                self.enemies.append([x, 0])
                self.spawn_timer = 0
                
            # Di chuyển lính thường
            for e in self.enemies: e[1] += (3 + self.score // 10 * 0.5)

        # --- DI CHUYỂN CÁC LOẠI ĐẠN ---
        # Đạn người chơi
        for b in self.bullets: b[1] -= 8
        self.bullets = [b for b in self.bullets if b[1] > 0]
        
        # Đạn Boss
        for b in self.boss_bullets: b[1] += 6 # Đạn boss bay xuống
        # Xóa đạn boss ra khỏi màn hình
        self.boss_bullets = [b for b in self.boss_bullets if b[1] < SCREEN_HEIGHT]

        # --- XỬ LÝ VA CHẠM (Chung) ---
        
        # 1. Đạn người chơi trúng lính thường
        if not self.boss_active:
            for b in self.bullets[:]:
                b_rect = pygame.Rect(b[0], b[1], 10, 15)
                hit = False
                for e in self.enemies[:]:
                    e_rect = pygame.Rect(e[0], e[1], 50, 50)
                    if b_rect.colliderect(e_rect):
                        self.enemies.remove(e)
                        self.score += 1
                        self.particles.extend(create_particles(e[0]+25, e[1]+25, RED))
                        hit = True; break
                if hit: self.bullets.remove(b)

        # 2. Kiểm tra Người chơi bị trúng đạn Boss hoặc chạm lính
        player_rect = pygame.Rect(self.player_x, self.player_y, 50, 50)
        
        # - Chạm lính thường
        for e in self.enemies[:]:
            if pygame.Rect(e[0], e[1], 50, 50).colliderect(player_rect):
                self.enemies.remove(e)
                self.player_hp -= 1
                self.particles.extend(create_particles(self.player_x+25, self.player_y+25, BLUE))
        
        # - Trúng đạn Boss
        for b in self.boss_bullets[:]:
            if pygame.Rect(b[0], b[1], 15, 15).colliderect(player_rect):
                self.boss_bullets.remove(b)
                self.player_hp -= 1
                self.particles.extend(create_particles(self.player_x+25, self.player_y+25, BLUE))

        # Check chết
        if self.player_hp <= 0:
            self.state = "GAMEOVER"

        # Hiệu ứng hạt
        for p in self.particles:
            p['x'] += p['vx']; p['y'] += p['vy']; p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self):
        screen.fill(BLACK)

        if self.state == "MENU":
            draw_text_center("SPACE DEFENDER", font_title, BLUE, -50)
            draw_text_center("Nhiệm vụ: Đạt 20 điểm để gọi Boss", font_text, WHITE, 20)
            draw_text_center("Nhấn SPACE để Bắt đầu", font_text, YELLOW, 80)

        elif self.state == "PLAYING" or self.state == "PAUSED":
            # Vẽ người chơi
            pygame.draw.polygon(screen, BLUE, [(self.player_x+25, self.player_y), (self.player_x, self.player_y+50), (self.player_x+50, self.player_y+50)])
            
            # Vẽ lính thường
            for e in self.enemies:
                pygame.draw.rect(screen, RED, (e[0], e[1], 50, 50), border_radius=5)
                
            # VẼ BOSS
            if self.boss_active and self.boss:
                # Thân boss
                pygame.draw.rect(screen, PURPLE, (self.boss['x'], self.boss['y'], self.boss['w'], self.boss['h']), border_radius=15)
                # Mắt boss (cho ngầu)
                pygame.draw.rect(screen, YELLOW, (self.boss['x'] + 20, self.boss['y'] + 30, 20, 20))
                pygame.draw.rect(screen, YELLOW, (self.boss['x'] + 60, self.boss['y'] + 30, 20, 20))
                
                # Thanh máu Boss (Ở ngay trên đầu boss)
                hp_width = (self.boss['hp'] / self.boss['max_hp']) * self.boss['w']
                pygame.draw.rect(screen, RED, (self.boss['x'], self.boss['y'] - 15, self.boss['w'], 10)) # Nền đỏ
                pygame.draw.rect(screen, GREEN, (self.boss['x'], self.boss['y'] - 15, hp_width, 10))     # Máu xanh
            
            # Vẽ đạn Boss
            for b in self.boss_bullets:
                pygame.draw.circle(screen, ORANGE, (b[0], b[1]), 8)

            # Vẽ đạn người chơi
            for b in self.bullets:
                pygame.draw.rect(screen, YELLOW, (b[0], b[1], 10, 15))
            
            # Hiệu ứng
            for p in self.particles:
                pygame.draw.rect(screen, p['color'], (p['x'], p['y'], p['size'], p['size']))

            # UI
            score_surf = font_score.render(f"Điểm: {self.score}", True, WHITE)
            screen.blit(score_surf, (10, 10))
            draw_text_center(f"{'♥ ' * self.player_hp}", font_score, GREEN if self.player_hp > 1 else RED, -SCREEN_HEIGHT//2 + 20)

            if self.state == "PAUSED":
                draw_text_center("TẠM DỪNG", font_title, WHITE, 0)

        elif self.state == "GAMEOVER":
            draw_text_center("THẤT BẠI!", font_title, RED, -50)
            draw_text_center(f"Điểm số: {self.score}", font_text, WHITE, 20)
            draw_text_center("Nhấn SPACE để thử lại", font_text, YELLOW, 60)
            
        elif self.state == "VICTORY":
            draw_text_center("CHIẾN THẮNG!", font_title, GREEN, -50)
            draw_text_center("Bạn đã tiêu diệt Boss!", font_text, WHITE, 20)
            draw_text_center("Nhấn SPACE để chơi lại", font_text, YELLOW, 60)

        pygame.display.flip()

def main():
    game = Game()
    while True:
        game.handle_input()
        game.update()
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e); pygame.quit()