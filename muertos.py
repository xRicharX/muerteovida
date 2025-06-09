import pygame
import random
import sys
import math

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla (tamaño adaptable)
SCREEN_INFO = pygame.display.Info()
WIDTH = min(1000, SCREEN_INFO.current_w - 100)
HEIGHT = min(700, SCREEN_INFO.current_h - 100)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Población - Cálculo 1")

# Colores
BACKGROUND = (15, 25, 40)
PANEL_COLOR = (30, 45, 70)
ACCENT_COLOR = (70, 130, 180)
BUTTON_COLOR = (50, 90, 140)
BUTTON_HOVER = (80, 150, 220)
BUTTON_ACTIVE = (120, 200, 100)
TEXT_COLOR = (220, 220, 240)
DISABLED_COLOR = (80, 80, 100)
SLIDER_COLOR = (100, 150, 200)
SLIDER_HANDLE = (180, 200, 255)
GRAPH_COLOR = (70, 200, 100)
GRAPH_BG = (20, 35, 60)
CALC_PANEL = (40, 35, 80)
DOT_COLORS = [
    (255, 150, 150), (150, 255, 150), (150, 200, 255),
    (255, 200, 150), (200, 150, 255), (150, 255, 255)
]

# Fuentes
font_large = pygame.font.SysFont("Arial", min(36, int(WIDTH/30)), bold=True)
font_medium = pygame.font.SysFont("Arial", min(28, int(WIDTH/35)))
font_small = pygame.font.SysFont("Arial", min(22, int(WIDTH/45)))
font_tiny = pygame.font.SysFont("Arial", min(18, int(WIDTH/55)))
font_credits = pygame.font.SysFont("Arial", 14)

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.active = False
        self.enabled = True
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        if not self.enabled:
            color = DISABLED_COLOR
        elif self.active:
            color = BUTTON_ACTIVE
            
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, ACCENT_COLOR, self.rect, 2, border_radius=8)
        
        text_surf = font_small.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos) and self.enabled
        return self.is_hovered
    
    def check_click(self, pos):
        return self.rect.collidepoint(pos) and self.enabled

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(6, 10)
        self.color = random.choice(DOT_COLORS)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.lifetime = random.randint(200, 300)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        
        # Rebotar en los bordes
        if self.x < 50 or self.x > WIDTH - 50:
            self.speed_x *= -1
        if self.y < 350 or self.y > HEIGHT - 50:
            self.speed_y *= -1
        
        return self.lifetime > 0
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# Crear elementos de UI
# Botones de configuración
pop_plus_btn = Button(WIDTH//2 - 120, 120, 50, 40, "+10")
pop_minus_btn = Button(WIDTH//2 + 70, 120, 50, 40, "-10")
birth_plus_btn = Button(WIDTH//2 - 120, 190, 50, 40, "+1")
birth_minus_btn = Button(WIDTH//2 + 70, 190, 50, 40, "-1")
death_plus_btn = Button(WIDTH//2 - 120, 260, 50, 40, "+1")
death_minus_btn = Button(WIDTH//2 + 70, 260, 50, 40, "-1")
k_plus_btn = Button(WIDTH//2 - 120, 330, 50, 40, "+500")
k_minus_btn = Button(WIDTH//2 + 70, 330, 50, 40, "-500")
start_btn = Button(WIDTH//2 - 100, 400, 200, 50, "Iniciar Simulación", BUTTON_HOVER)

# Botones de eventos 
disease_btns = [
    Button(50, 420, 150, 40, "Ébola"),
    Button(220, 420, 150, 40, "Gripe"),
    Button(390, 420, 150, 40, "COVID")
]

disaster_btns = [
    Button(50, 480, 150, 40, " Tornado"),
    Button(220, 480, 150, 40, " Rayos"),
    Button(390, 480, 150, 40, " Terremoto")
]

# Botones de ayuda 
help_btns = [
    Button(550, 420, 150, 40, " Cura"),
    Button(550, 480, 150, 40, " Clonación"),
    Button(550, 540, 150, 40, " Superpotenciador")
]

# Botones de simulación
pause_btn = Button(WIDTH - 220, 20, 100, 40, "Pausar")
reset_btn = Button(WIDTH - 110, 20, 100, 40, "Reiniciar")

# Variables de simulación
population = 1000
year = 0
birth_rate = 1.0  # Tasa inicial de natalidad
death_rate = 0.5  # Tasa inicial de mortalidad
capacidad_carga = 5000  # Capacidad de carga K (nuevo concepto)
simulation_active = False
paused = False
simulation_time = 0
dots = []
active_diseases = []
active_disasters = []
active_helps = []
population_history = []  # Historial de población para el gráfico
max_population = 1000  # Máxima población para escalar el gráfico
derivada = 0  # Tasa de cambio poblacional
pendiente = 0  # Pendiente de la recta tangente

# Crear puntos iniciales
for _ in range(min(population, 500)):
    dots.append(Dot(random.randint(100, WIDTH-100), random.randint(400, HEIGHT-100)))

def draw_graph(surface, history, max_value, rect):
    """Dibuja un gráfico de la población a lo largo del tiempo con elementos de cálculo"""
    # Fondo del gráfico
    pygame.draw.rect(surface, GRAPH_BG, rect, border_radius=5)
    pygame.draw.rect(surface, ACCENT_COLOR, rect, 1, border_radius=5)
    
    # Dibujar capacidad de carga (K)
    if max_value > 0:
        k_y = rect.bottom - (capacidad_carga / max_value) * rect.height
        pygame.draw.line(surface, (255, 100, 100), 
                        (rect.left, k_y),
                        (rect.right, k_y), 2)
        k_text = font_tiny.render(f"K = {capacidad_carga}", True, (255, 100, 100))
        surface.blit(k_text, (rect.right - k_text.get_width() - 5, k_y - 15))
    
    if len(history) < 2:
        return
    
    # Calcular puntos para el gráfico
    points = []
    max_points = min(100, len(history))  # Máximo de puntos a mostrar
    start_index = max(0, len(history) - max_points)
    
    for i, pop in enumerate(history[start_index:]):
        x = rect.left + (i / (max_points - 1)) * rect.width
        y = rect.bottom - (pop / max_value) * rect.height
        points.append((x, y))
    
    # Dibujar línea del gráfico
    if len(points) > 1:
        pygame.draw.lines(surface, GRAPH_COLOR, False, points, 3)
    
    # Dibujar recta tangente en el último punto
    if len(points) >= 2:
        # Calcular pendiente entre últimos dos puntos
        x1, y1 = points[-2]
        x2, y2 = points[-1]
        m = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
        
        # Extender línea 20 píxeles en ambas direcciones
        extended_x1 = max(rect.left, x2 - 20)
        extended_y1 = y2 - m * (x2 - extended_x1)
        extended_x2 = min(rect.right, x2 + 20)
        extended_y2 = y2 + m * (extended_x2 - x2)
        
        pygame.draw.line(surface, (255, 200, 100), 
                        (extended_x1, extended_y1), 
                        (extended_x2, extended_y2), 2)
        
        # Punto de tangencia
        pygame.draw.circle(surface, (255, 255, 0), (int(x2), int(y2)), 6)
    
    # Etiquetas
    start_year = year - len(history) + start_index
    end_year = year
    
    # Etiqueta de población inicial
    if start_index < len(history):
        start_text = font_tiny.render(f"{history[start_index]}", True, TEXT_COLOR)
        surface.blit(start_text, (rect.left + 5, rect.top + 5))
    
    # Etiqueta de población actual
    end_text = font_tiny.render(f"{history[-1]}", True, TEXT_COLOR)
    surface.blit(end_text, (rect.right - end_text.get_width() - 5, rect.top + 5))
    
    # Etiqueta de año
    year_text = font_tiny.render(f"Año: {start_year}-{end_year}", True, TEXT_COLOR)
    surface.blit(year_text, (rect.centerx - year_text.get_width()//2, rect.top + 5))

# Bucle principal
clock = pygame.time.Clock()
running = True
last_time = pygame.time.get_ticks()

while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0
    last_time = current_time
    
    mouse_pos = pygame.mouse.get_pos()
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Configuración inicial
            if not simulation_active:
                if pop_plus_btn.check_click(mouse_pos):
                    population += 10
                if pop_minus_btn.check_click(mouse_pos):
                    population = max(0, population - 10)
                
                if birth_plus_btn.check_click(mouse_pos):
                    birth_rate += 1
                if birth_minus_btn.check_click(mouse_pos):
                    birth_rate = max(0, birth_rate - 1)
                
                if death_plus_btn.check_click(mouse_pos):
                    death_rate += 1
                if death_minus_btn.check_click(mouse_pos):
                    death_rate = max(0, death_rate - 1)
                
                if k_plus_btn.check_click(mouse_pos):
                    capacidad_carga += 500
                if k_minus_btn.check_click(mouse_pos):
                    capacidad_carga = max(100, capacidad_carga - 500)
                
                if start_btn.check_click(mouse_pos):
                    simulation_active = True
                    # Crear puntos iniciales para simulación
                    dots = []
                    for _ in range(min(population, 500)):
                        dots.append(Dot(random.randint(100, WIDTH-100), random.randint(400, HEIGHT-100)))
                    population_history = [population]  # Inicializar historial
                    max_population = max(population, capacidad_carga)  # Inicializar máxima población
                    year = 0
                    derivada = 0
                    pendiente = 0
            
            # Botones de eventos
            if simulation_active and not paused:
                for i, btn in enumerate(disease_btns):
                    if btn.check_click(mouse_pos):
                        disease = ["Ébola", "Gripe", "COVID"][i]
                        if disease in active_diseases:
                            active_diseases.remove(disease)
                            btn.active = False
                        else:
                            active_diseases.append(disease)
                            btn.active = True
                
                for i, btn in enumerate(disaster_btns):
                    if btn.check_click(mouse_pos):
                        disaster = ["Tornado", "Rayos", "Terremoto"][i]
                        if disaster in active_disasters:
                            active_disasters.remove(disaster)
                            btn.active = False
                        else:
                            active_disasters.append(disaster)
                            btn.active = True
                
                for i, btn in enumerate(help_btns):
                    if btn.check_click(mouse_pos):
                        help_name = ["Cura", "Clonación", "Superpot."][i]
                        if help_name in active_helps:
                            active_helps.remove(help_name)
                            btn.active = False
                        else:
                            # Verificar condiciones para activar
                            if help_name == "Cura" and not active_diseases:
                                continue
                            if help_name == "Clonación" and not active_disasters:
                                continue
                            active_helps.append(help_name)
                            btn.active = True
            
            # Botones de simulación
            if simulation_active:
                if pause_btn.check_click(mouse_pos):
                    paused = not paused
                    pause_btn.text = "Continuar" if paused else "Pausar"
                if reset_btn.check_click(mouse_pos):
                    # Reiniciar simulación
                    simulation_active = False
                    paused = False
                    population = 1000
                    year = 0
                    birth_rate = 1.0
                    death_rate = 0.5
                    capacidad_carga = 5000
                    dots = []
                    active_diseases = []
                    active_disasters = []
                    active_helps = []
                    derivada = 0
                    pendiente = 0
                    
                    # Reiniciar estados de botones
                    for btn in disease_btns + disaster_btns + help_btns:
                        btn.active = False
                    
                    # Crear nuevos puntos
                    for _ in range(min(population, 500)):
                        dots.append(Dot(random.randint(100, WIDTH-100), random.randint(400, HEIGHT-100)))
    
    # Actualizar hover de botones
    if not simulation_active:
        pop_plus_btn.check_hover(mouse_pos)
        pop_minus_btn.check_hover(mouse_pos)
        birth_plus_btn.check_hover(mouse_pos)
        birth_minus_btn.check_hover(mouse_pos)
        death_plus_btn.check_hover(mouse_pos)
        death_minus_btn.check_hover(mouse_pos)
        k_plus_btn.check_hover(mouse_pos)
        k_minus_btn.check_hover(mouse_pos)
        start_btn.check_hover(mouse_pos)
        
        # Deshabilitar botones cuando no se pueden usar
        pop_minus_btn.enabled = population > 0
        birth_minus_btn.enabled = birth_rate > 0
        death_minus_btn.enabled = death_rate > 0
        k_minus_btn.enabled = capacidad_carga > 100
    
    if simulation_active:
        pause_btn.check_hover(mouse_pos)
        reset_btn.check_hover(mouse_pos)
        
        if not paused:
            for btn in disease_btns + disaster_btns + help_btns:
                btn.check_hover(mouse_pos)
                
                # Habilitar/deshabilitar botones de ayuda según condiciones
                if btn == help_btns[0]:  # Cura
                    btn.enabled = len(active_diseases) > 0
                elif btn == help_btns[1]:  # Clonación
                    btn.enabled = len(active_disasters) > 0
                else:  # Superpotenciador
                    btn.enabled = True
    
    # Actualizar simulación
    if simulation_active and not paused:
        simulation_time += delta_time
        
        # Avanzar más rápido segundos cada año
        if simulation_time >= 0.2:
            simulation_time = 0
            year += 1
            
            # Calcular tasas modificadas
            effective_birth_rate = birth_rate
            effective_death_rate = death_rate
            
            # Efectos de enfermedades
            for _ in active_diseases:
                effective_death_rate += random.uniform(1.0, 5.0)
            
            # Efectos de desastres
            for _ in active_disasters:
                effective_death_rate += random.uniform(2.0, 8.0)
            
            # Efectos de ayudas
            if "Cura" in active_helps:
                effective_birth_rate += 15.0
            if "Clonación" in active_helps:
                effective_birth_rate += 25.0
            if "Superpot." in active_helps:
                effective_birth_rate += 50.0
            
            # MODELO DE CRECIMIENTO LOGÍSTICO (ECUACIÓN DIFERENCIAL)
            # dP/dt = rP(1 - P/K)
            r = (effective_birth_rate - effective_death_rate) / 100.0
            K = capacidad_carga
            
            # Solución aproximada: P(t+Δt) = P(t) + rP(1 - P/K)Δt
            delta_p = r * population * (1 - population/K) * 1  # Δt = 1 año
            
            # Aplicar cambios a la población
            population = max(0, population + int(delta_p))
            population_history.append(population)
            max_population = max(max_population, population, capacidad_carga)
            
            # Calcular derivada (dP/dt)
            if len(population_history) > 1:
                derivada = population_history[-1] - population_history[-2]
            
            # Calcular pendiente (aproximación de segunda derivada)
            if len(population_history) > 2:
                pendiente = population_history[-1] - 2*population_history[-2] + population_history[-3]
            
            # Actualizar puntos (personas)
            # Mantener entre 100 y 500 puntos para rendimiento
            target_dots = min(500, max(100, population // 2))
            
            # Añadir nuevos puntos si es necesario
            if len(dots) < target_dots:
                for _ in range(target_dots - len(dots)):
                    dots.append(Dot(random.randint(100, WIDTH-100), random.randint(400, HEIGHT-100)))
            # Eliminar puntos si es necesario
            elif len(dots) > target_dots:
                dots = dots[:target_dots]
            
            # Actualizar puntos existentes
            dots = [dot for dot in dots if dot.update()]
    
    # Dibujar
    screen.fill(BACKGROUND)
    
    if not simulation_active:
        # Pantalla de configuración
        # Título
        title = font_large.render("Simulación de Población - Cálculo 1", True, TEXT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Configuración de población
        pop_text = font_medium.render(f"Población Inicial: {population}", True, TEXT_COLOR)
        screen.blit(pop_text, (WIDTH//2 - pop_text.get_width()//2, 90))
        
        pop_plus_btn.draw(screen)
        pop_minus_btn.draw(screen)
        
        # Configuración de natalidad
        birth_text = font_medium.render(f"Tasa de Natalidad: {birth_rate}%", True, TEXT_COLOR)
        screen.blit(birth_text, (WIDTH//2 - birth_text.get_width()//2, 160))
        
        birth_plus_btn.draw(screen)
        birth_minus_btn.draw(screen)
        
        # Configuración de mortalidad
        death_text = font_medium.render(f"Tasa de Mortalidad: {death_rate}%", True, TEXT_COLOR)
        screen.blit(death_text, (WIDTH//2 - death_text.get_width()//2, 230))
        
        death_plus_btn.draw(screen)
        death_minus_btn.draw(screen)
        
        # Configuración de capacidad de carga
        k_text = font_medium.render(f"Capacidad de Carga (K): {capacidad_carga}", True, TEXT_COLOR)
        screen.blit(k_text, (WIDTH//2 - k_text.get_width()//2, 300))
        
        k_plus_btn.draw(screen)
        k_minus_btn.draw(screen)
        
        # Tasa de crecimiento (r = birth - death)
        r_text = font_medium.render(f"Tasa crecimiento (r): {birth_rate - death_rate}%", True, TEXT_COLOR)
        screen.blit(r_text, (WIDTH//2 - r_text.get_width()//2, 360))
        
        start_btn.draw(screen)
        
        # Instrucciones
        help_text = font_tiny.render("Configura los parámetros antes de iniciar la simulación", 
                                    True, (180, 180, 200))
        screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, 450))
        
        # Explicación matemática
        math_text1 = font_tiny.render("Modelo Logístico: dP/dt = rP(1 - P/K)", True, (150, 255, 150))
        math_text2 = font_tiny.render("P = Población, r = Tasa crecimiento, K = Capacidad de carga", True, (150, 255, 150))
        screen.blit(math_text1, (WIDTH//2 - math_text1.get_width()//2, 500))
        screen.blit(math_text2, (WIDTH//2 - math_text2.get_width()//2, 525))
        
        # Créditos
        credits = font_credits.render("Hecho por :)Richar para Calculo1 - Modelos de Crecimiento Poblacional", True, (150, 150, 170))
        screen.blit(credits, (WIDTH//2 - credits.get_width()//2, HEIGHT - 30))
    
    else:
        # Pantalla de simulación
        # Barra superior
        pygame.draw.rect(screen, PANEL_COLOR, (0, 0, WIDTH, 80))
        pygame.draw.line(screen, ACCENT_COLOR, (0, 80), (WIDTH, 80), 2)
        
        # Información de simulación
        pop_text = font_large.render(f"Población: {population}", True, TEXT_COLOR)
        screen.blit(pop_text, (30, 20))
        
        year_text = font_medium.render(f"Año: {year}", True, TEXT_COLOR)
        screen.blit(year_text, (WIDTH - 300, 30))
        
        # Botones de control
        pause_btn.draw(screen)
        reset_btn.draw(screen)
        
        # Panel de eventos (mejorado)
        panel_height = 150
        pygame.draw.rect(screen, PANEL_COLOR, (20, 100, WIDTH - 40, panel_height), border_radius=10)
        pygame.draw.rect(screen, ACCENT_COLOR, (20, 100, WIDTH - 40, panel_height), 2, border_radius=10)
        
        # Título del panel
        events_title = font_medium.render("Eventos Especiales", True, TEXT_COLOR)
        screen.blit(events_title, (WIDTH//2 - events_title.get_width()//2, 110))
        
        # Sección de enfermedades
        disease_title = font_small.render("Enfermedades:", True, TEXT_COLOR)
        screen.blit(disease_title, (50, 140))
        
        for i, btn in enumerate(disease_btns):
            btn.rect.y = 140
            btn.draw(screen)
        
        # Sección de desastres
        disaster_title = font_small.render("Desastres:", True, TEXT_COLOR)
        screen.blit(disaster_title, (50, 190))
        
        for i, btn in enumerate(disaster_btns):
            btn.rect.y = 190
            btn.draw(screen)
        
        # Sección de ayudas
        help_title = font_small.render("Ayudas:", True, TEXT_COLOR)
        screen.blit(help_title, (550, 140))
        
        for i, btn in enumerate(help_btns):
            btn.rect.y = 140
            # Ocultar ayudas si no cumplen condiciones
            if i == 0 and not active_diseases:  # Cura
                continue
            if i == 1 and not active_disasters:  # Clonación
                continue
            btn.rect.x = 550  # Posición fija en X
            btn.rect.y = 140 + i * 50  # Posición en Y ajustada
            btn.draw(screen)
        
        # Visualización de población (puntos)
        viz_height = HEIGHT - 400
        pygame.draw.rect(screen, PANEL_COLOR, (20, 270, WIDTH - 40, viz_height), border_radius=10)
        pygame.draw.rect(screen, ACCENT_COLOR, (20, 270, WIDTH - 40, viz_height), 2, border_radius=10)
        
        # Título de visualización
        viz_title = font_medium.render(f"Población Actual: {population} personas", True, TEXT_COLOR)
        screen.blit(viz_title, (WIDTH//2 - viz_title.get_width()//2, 280))
        
        # Actualizar y dibujar puntos
        for dot in dots:
            dot.draw(screen)
        
        # Dibujar gráfico de población
        graph_rect = pygame.Rect(WIDTH - 250, 300, 200, 100)
        draw_graph(screen, population_history, max_population, graph_rect)
        
        # Panel de Análisis Matemático
        pygame.draw.rect(screen, CALC_PANEL, (20, HEIGHT-130, WIDTH-40, 110), border_radius=10)
        pygame.draw.rect(screen, ACCENT_COLOR, (20, HEIGHT-130, WIDTH-40, 110), 2, border_radius=10)
        
        # Título
        calc_title = font_small.render("Análisis de Cálculo Diferencial", True, (200, 200, 255))
        screen.blit(calc_title, (WIDTH//2 - calc_title.get_width()//2, HEIGHT-125))
        
        # Información matemática
        if len(population_history) > 1:
            # Límite cuando t→∞
            if derivada > 0:
                limite = f"K = {capacidad_carga}"
            elif derivada < 0:
                limite = "0"
            else:
                limite = "Equilibrio"
            
            # Pendiente de la recta tangente
            if len(population_history) > 2:
                pendiente = population_history[-1] - 2*population_history[-2] + population_history[-3]
            
            # Determinar modelo
            if abs(pendiente) < 5:
                modelo = "Exponencial: P(t) = P₀eʳᵗ"
            else:
                modelo = f"Logístico: P(t) = {capacidad_carga}/(1+Ae⁻ʳᵗ)"
            
            # Mostrar conceptos matemáticos
            deriv_text = font_tiny.render(f"dP/dt ≈ {derivada} (tasa de cambio instantánea)", True, TEXT_COLOR)
            screen.blit(deriv_text, (40, HEIGHT-100))
            
            limite_text = font_tiny.render(f"Límite cuando t→∞: {limite}", True, TEXT_COLOR)
            screen.blit(limite_text, (40, HEIGHT-80))
            
            pend_text = font_tiny.render(f"Concavidad: {pendiente:.2f} (2da derivada)", True, TEXT_COLOR)
            screen.blit(pend_text, (40, HEIGHT-60))
            
            func_text = font_tiny.render(f"Modelo: {modelo}", True, (150, 255, 150))
            screen.blit(func_text, (WIDTH - func_text.get_width() - 40, HEIGHT-80))
        
        # Leyenda
        legend_y = HEIGHT - 30
        pygame.draw.circle(screen, DOT_COLORS[0], (50, legend_y), 8)
        label = font_tiny.render("Personas", True, TEXT_COLOR)
        screen.blit(label, (65, legend_y - 8))
        
        # Créditos
        credits = font_credits.render("Hecho por :) Richar para Calculo1 - Ecuaciones Diferenciales y Límites", True, (150, 150, 170))
        screen.blit(credits, (WIDTH//2 - credits.get_width()//2, HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


