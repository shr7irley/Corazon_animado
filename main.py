import math
import random
import pygame


# ============================================================
# CONFIGURACIÓN
# ============================================================

WIDTH, HEIGHT = 1400, 800

BACKGROUND_COLOR = (0, 0, 0)

FPS = 60

# Tamaño del corazón
SCALE = 18

WORDS = [
    "Te amo",
    "I love you",
    "Je t’aime", 
    "Ti amo"
]

CENTER_TEXT = "Love You"

COLORS = [
    (70, 130, 180),
    (30, 144, 255),
    (0, 191, 255),
    (100, 149, 237),
    (65, 105, 225)
]


# ============================================================
# PARTÍCULA
# ============================================================

class Particle:

    __slots__ = (
        'x',
        'y',
        'order',
        'kind',
        'word',
        'color',
        'alpha',
        'flicker',
        'font',
        'delay',
        'size_mult'
    )

    def __init__(self, x, y, order, kind):

        self.x = x
        self.y = y

        self.order = order
        self.kind = kind

        self.word = random.choice(WORDS)
        self.color = random.choice(COLORS)

        self.alpha = 0

        self.flicker = random.uniform(
            0,
            math.pi * 2
        )

        self.font = None

        self.delay = 0

        self.size_mult = random.uniform(
            0.85,
            1.15
        )


# ============================================================
# ECUACIÓN DEL CORAZÓN
# ============================================================

def heart_xy(t):

    x = 16 * (math.sin(t) ** 3)

    y = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )

    return x, -y


# ============================================================
# CENTRAR EL CORAZÓN
# ============================================================

def get_heart_center():

    points = []

    samples = 2000

    for i in range(samples):

        t = (
            i / samples
        ) * 2 * math.pi

        x, y = heart_xy(t)

        points.append(
            (x, y)
        )

    min_x = min(
        p[0] for p in points
    )

    max_x = max(
        p[0] for p in points
    )

    min_y = min(
        p[1] for p in points
    )

    max_y = max(
        p[1] for p in points
    )

    center_x = (
        min_x + max_x
    ) / 2

    center_y = (
        min_y + max_y
    ) / 2

    return center_x, center_y


HEART_CENTER_X, HEART_CENTER_Y = (
    get_heart_center()
)


# ============================================================
# CONVERTIR COORDENADAS
# ============================================================

def to_screen(x, y):

    x -= HEART_CENTER_X
    y -= HEART_CENTER_Y

    return (
        x * SCALE + WIDTH / 2,
        y * SCALE + HEIGHT / 2
    )


# ============================================================
# CREAR CONTORNO
# ============================================================

def build_outline_particles(
    n_outline,
    min_gap=24
):

    particles = []

    placed = []

    for i in range(n_outline):

        t = (
            i / n_outline
        ) * 2 * math.pi

        bx, by = heart_xy(t)

        sx, sy = to_screen(
            bx,
            by
        )

        too_close = False

        for px, py in placed:

            if math.hypot(
                sx - px,
                sy - py
            ) < min_gap:

                too_close = True
                break

        if too_close:
            continue

        placed.append(
            (sx, sy)
        )

        particles.append(
            Particle(
                sx,
                sy,
                i,
                "outline"
            )
        )

    return particles


# ============================================================
# CREAR RELLENO
# ============================================================

def build_fill_particles(
    n_fill,
    min_gap=36
):

    particles = []

    placed = []

    attempts = 0

    max_attempts = n_fill * 60

    while (
        len(particles) < n_fill
        and attempts < max_attempts
    ):

        attempts += 1

        t = random.uniform(
            0,
            2 * math.pi
        )

        r = random.uniform(
            0.05,
            0.86
        )

        bx, by = heart_xy(t)

        px = bx * r
        py = by * r

        sx, sy = to_screen(
            px,
            py
        )

        too_close = False

        for qx, qy in placed:

            if math.hypot(
                sx - qx,
                sy - qy
            ) < min_gap:

                too_close = True
                break

        if too_close:
            continue

        placed.append(
            (sx, sy)
        )

        particles.append(
            Particle(
                sx,
                sy,
                random.randint(0, 80),
                "fill"
            )
        )

    return particles


# ============================================================
# DIBUJAR TEXTO CON BRILLO
# ============================================================

def draw_glow_text(
    glow_layer,
    screen_layer,
    font,
    word,
    color,
    x,
    y,
    alpha,
    size_mult=1.0
):

    if alpha <= 0:
        return

    # --------------------------------------------------------
    # CREAR TEXTO
    # --------------------------------------------------------

    if size_mult != 1.0:

        scaled_font = pygame.font.Font(
            None,
            max(
                10,
                int(
                    font.get_height()
                    * size_mult
                )
            )
        )

        txt = scaled_font.render(
            word,
            True,
            color
        )

    else:

        txt = font.render(
            word,
            True,
            color
        )

    txt.set_alpha(alpha)

    txt_rect = txt.get_rect(
        center=(
            int(x),
            int(y)
        )
    )

    # --------------------------------------------------------
    # BRILLO
    # --------------------------------------------------------

    if alpha > 10:

        # Glow grande
        glow_big = pygame.transform.smoothscale(
            txt,
            (
                int(
                    txt.get_width() * 2.0
                ),
                int(
                    txt.get_height() * 2.0
                )
            )
        )

        glow_big.set_alpha(
            max(
                0,
                alpha // 8
            )
        )

        glow_rect = glow_big.get_rect(
            center=(
                int(x),
                int(y)
            )
        )

        glow_layer.blit(
            glow_big,
            glow_rect
        )

        # Glow pequeño
        glow_small = pygame.transform.smoothscale(
            txt,
            (
                int(
                    txt.get_width() * 1.4
                ),
                int(
                    txt.get_height() * 1.4
                )
            )
        )

        glow_small.set_alpha(
            max(
                0,
                alpha // 3
            )
        )

        glow_rect = glow_small.get_rect(
            center=(
                int(x),
                int(y)
            )
        )

        glow_layer.blit(
            glow_small,
            glow_rect
        )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    screen_layer.blit(
        txt,
        txt_rect
    )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    pygame.init()

    # ========================================================
    # MÚSICA
    # ========================================================

    try:

        pygame.mixer.init()

        pygame.mixer.music.load(
            "love_you.mp3"
        )

        pygame.mixer.music.play()

    except Exception as e:

        print(
            "No se pudo reproducir la música:",
            e
        )

    # ========================================================
    # VENTANA
    # ========================================================

    screen = pygame.display.set_mode(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.DOUBLEBUF
    )

    pygame.display.set_caption(
        "I love you <3"
    )

    clock = pygame.time.Clock()

    # ========================================================
    # FUENTES
    # ========================================================

    font_outline = pygame.font.SysFont(
        "arial",
        20,
        bold=True
    )

    font_fill = pygame.font.SysFont(
        "arial",
        17,
        bold=True
    )

    font_center = pygame.font.SysFont(
        "georgia",
        54,
        bold=True
    )

    # ========================================================
    # FONDO
    # ========================================================

    background = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        )
    )

    background.fill(
        BACKGROUND_COLOR
    )

    # ========================================================
    # CREAR CORAZÓN
    # ========================================================

    outline = build_outline_particles(
        n_outline=160
    )

    fill = build_fill_particles(
        n_fill=130
    )

    # ========================================================
    # VELOCIDAD
    # ========================================================

    # Ajustado a 0.12 (más lento que antes, que era 0.05)
    frames_per_step = 0.12

    outline_span = (
        max(
            p.order
            for p in outline
        )
        if outline
        else 0
    )

    # Ajustado a 18 (el relleno tarda más en aparecer)
    fill_start_frame = 18

    # ========================================================
    # CONTORNO
    # ========================================================

    for p in outline:

        p.delay = int(
            p.order
            * frames_per_step
        )

    # ========================================================
    # RELLENO
    # ========================================================

    for p in fill:

        # Ahora el retraso de cada partícula de relleno depende de su orden
        p.delay = (
            fill_start_frame
            + int(p.order * 0.08)
        )

    # ========================================================
    # PARTICULAS
    # ========================================================

    particles = (
        outline
        + fill
    )

    for p in particles:

        if p.kind == "outline":

            p.font = font_outline

        else:

            p.font = font_fill

    # ========================================================
    # CAPAS
    # ========================================================

    glow_layer = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    text_layer = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    # ========================================================
    # ANIMACIÓN
    # ========================================================

    running = True

    frame = 0

    while running:

        # ====================================================
        # EVENTOS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                running = False

        # ====================================================
        # LIMPIAR
        # ====================================================

        screen.blit(
            background,
            (0, 0)
        )

        glow_layer.fill(
            (0, 0, 0, 0)
        )

        text_layer.fill(
            (0, 0, 0, 0)
        )

        frame += 1

        # ====================================================
        # DIBUJAR PARTÍCULAS
        # ====================================================

        for p in particles:

            # -----------------------------------------------
            # APARICIÓN INMEDIATA
            # -----------------------------------------------

            if frame >= p.delay:

                # Aparece instantáneamente
                p.alpha = 255

            # -----------------------------------------------
            # BRILLO
            # -----------------------------------------------

            if p.alpha >= 255:

                flick = (
                    0.75
                    + 0.25
                    * math.sin(
                        frame * 0.04
                        + p.flicker
                    )
                )

            else:

                flick = 1.0

            alpha = int(
                p.alpha
                * flick
            )

            if alpha <= 0:
                continue

            # -----------------------------------------------
            # DIBUJAR
            # -----------------------------------------------

            draw_glow_text(
                glow_layer,
                text_layer,
                p.font,
                p.word,
                p.color,
                p.x,
                p.y,
                alpha,
                p.size_mult
            )

        # ====================================================
        # MOSTRAR GLOW
        # ====================================================

        screen.blit(
            glow_layer,
            (0, 0)
        )

        # ====================================================
        # MOSTRAR TEXTO
        # ====================================================

        screen.blit(
            text_layer,
            (0, 0)
        )

        # ====================================================
        # LOVE YOU CENTRAL
        # ====================================================

        # Ajustado a 65 (tarda más en aparecer que antes, que era 35)
        center_start = 25

        if frame >= center_start:

            progress = min(
                1.0,
                (
                    frame
                    - center_start
                ) / 12
            )

            # Aparición rápida
            center_alpha = int(
                255
                * (
                    1
                    - math.exp(
                        -progress * 10
                    )
                )
            )

            # -----------------------------------------------
            # PULSO
            # -----------------------------------------------

            pulse = (
                1.0
                + 0.025
                * math.sin(
                    frame * 0.05
                )
            )

            center_surf = (
                font_center.render(
                    CENTER_TEXT,
                    True,
                    (
                        255,
                        250,
                        245
                    )
                )
            )

            new_width = int(
                center_surf.get_width()
                * pulse
            )

            new_height = int(
                center_surf.get_height()
                * pulse
            )

            if (
                new_width > 0
                and new_height > 0
            ):

                center_surf = (
                    pygame.transform.smoothscale(
                        center_surf,
                        (
                            new_width,
                            new_height
                        )
                    )
                )

            center_surf.set_alpha(
                center_alpha
            )

            # -----------------------------------------------
            # GLOW CENTRAL
            # -----------------------------------------------

            if center_alpha > 10:

                glow_center = (
                    pygame.transform.smoothscale(
                        center_surf,
                        (
                            int(
                                center_surf.get_width()
                                * 1.5
                            ),
                            int(
                                center_surf.get_height()
                                * 1.5
                            )
                        )
                    )
                )

                glow_center.set_alpha(
                    center_alpha // 5
                )

                glow_rect = (
                    glow_center.get_rect(
                        center=(
                            WIDTH // 2,
                            HEIGHT // 2
                        )
                    )
                )

                screen.blit(
                    glow_center,
                    glow_rect
                )

            # -----------------------------------------------
            # LOVE YOU
            # -----------------------------------------------

            text_rect = (
                center_surf.get_rect(
                    center=(
                        WIDTH // 2,
                        HEIGHT // 2
                    )
                )
            )

            screen.blit(
                center_surf,
                text_rect
            )

        # ====================================================
        # ACTUALIZAR
        # ====================================================

        pygame.display.flip()

        clock.tick(FPS)

    # ========================================================
    # CERRAR
    # ========================================================

    pygame.quit()


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print(
            "OCURRIÓ UN ERROR:",
            e
        )

        import traceback

        traceback.print_exc()