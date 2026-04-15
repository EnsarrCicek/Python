import pygame
import math

# Pygame'i başlatır
pygame.init()

# Pencere oluşturur
screen = pygame.display.set_mode((900, 700))

# Pencerenin üst kısmındaki başlığı ayarlar
pygame.display.set_caption("Kalp Hediyesi")

# Yazı tipi oluşturur
font = pygame.font.SysFont("arial", 48)

# Ekranda görünecek yazıyı oluşturur
text = font.render("İyi ki varsın", True, (255, 255, 255))

# Yazıyı pencerenin üst tarafına ortalar
text_rect = text.get_rect(center=(450, 100))

# Bu fonksiyon matematik formülüyle kalp çizer
def draw_heart(surface, center_x, center_y, scale, color):
    # Kalbi oluşturan noktaları burada tutacağız
    points = []

    # 0'dan 359'a kadar açıları dolaşıyoruz
    for degree in range(360):
        # Dereceyi radyana çeviriyoruz
        t = math.radians(degree)

        # Kalp eğrisinin x koordinatı
        x = 16 * math.sin(t) ** 3

        # Kalp eğrisinin y koordinatı
        y = (
            13 * math.cos(t)
            - 5 * math.cos(2 * t)
            - 2 * math.cos(3 * t)
            - math.cos(4 * t)
        )

        # Hesaplanan noktayı ekrandaki konuma taşıyoruz
        draw_x = center_x + x * scale
        draw_y = center_y - y * scale

        # Noktayı listeye ekliyoruz
        points.append((draw_x, draw_y))

    # Noktaları birleştirip içi dolu kalp çiziyoruz
    if len(points) > 2:
        pygame.draw.polygon(surface, color, points)

# Program açık kalsın mı kontrolü
running = True

while running:
    # Kullanıcının yaptığı olayları kontrol eder
    for event in pygame.event.get():
        # Pencere kapatılırsa program kapanır
        if event.type == pygame.QUIT:
            running = False

    # Arka planı koyu renge boyar
    screen.fill((10, 10, 20))

    # Yazıyı ekrana çizer
    screen.blit(text, text_rect)

    # Geçen zamanı saniye cinsinden alır
    # Bu değer sürekli artar
    current_time = pygame.time.get_ticks() / 1000

    # Kalbin boyutunu zamanla hafifçe değiştirir
    # 12 temel boyut
    # math.sin(...) kısmı kalbi biraz büyütüp biraz küçültür
    animated_scale = 12 + math.sin(current_time * 2) * 1.5

    # Hareketli boyutla kalbi çizer
    draw_heart(screen, 450, 380, animated_scale, (255, 80, 140))

    # Yapılan çizimleri ekrana yansıtır
    pygame.display.update()

# Program kapanırken pygame'i düzgün şekilde sonlandırır
pygame.quit()