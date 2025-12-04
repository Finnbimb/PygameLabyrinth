import pygame
import sys
import time

# ----------------------------------------------
# Grundlegende Einstellungen
# ----------------------------------------------
FPS = 2
FENSTER_BREITE = 600
FENSTER_HOEHE = 600

SCHWARZ = (0, 0, 0)
WEISS = (255, 255, 255)
ROT = (255, 0, 0)
GRUEN = (0, 255, 0)
GRAU = (120, 120, 120)
GANG = (230, 230, 230)
GELB = (255, 255, 0)

# Richtungen
NORD = 0
OST = 1
SUED = 2
WEST = 3

RICHTUNGEN = [
    (-1, 0),  # Norden
    (0, 1),   # Osten
    (1, 0),   # Süden
    (0, -1)   # Westen
]


# ----------------------------------------------
# Labyrinth laden 
# ----------------------------------------------
def lade_labyrinth(datei):
    gitter = []
    start = None
    ziel = None

    with open(datei, "r", encoding="utf-8") as f:
        zeilen = f.readlines()

    for r in range(len(zeilen)):
        zeile = list(zeilen[r].strip())
        gitter.append(zeile)
        for c in range(len(zeile)):
            if zeile[c] == "S":
                start = (r, c)
            elif zeile[c] == "Z":
                ziel = (r, c)

    return gitter, start, ziel


# ----------------------------------------------
# Prüfen ob Feld frei ist
# ----------------------------------------------
def ist_frei(gitter, r, c):
    if r < 0 or c < 0:
        return False
    if r >= len(gitter) or c >= len(gitter[0]):
        return False
    return gitter[r][c] == "0" or gitter[r][c] == "Z"


# ----------------------------------------------
# Zeichnen (inkl. gelbem Prüf-Feld)
# ----------------------------------------------
def zeichne(win, gitter, reihen, spalten, zellgroesse, rob_r, rob_c, pruef):

    win.fill(SCHWARZ)

    for i in range(reihen):
        for j in range(spalten):

            feld = gitter[i][j]

            if feld == "1":
                farbe = GRAU
            elif feld == "S":
                farbe = ROT
            elif feld == "Z":
                farbe = GRUEN
            else:
                farbe = GANG

            pygame.draw.rect(win, farbe,
                (j * zellgroesse, i * zellgroesse, zellgroesse, zellgroesse))

    # gelb für Prüf-Feld
    if pruef is not None:
        pr, pc = pruef
        pygame.draw.rect(win, GELB,
            (pc * zellgroesse, pr * zellgroesse, zellgroesse, zellgroesse))

    # Roboter
    pygame.draw.circle(win, SCHWARZ,
        (rob_c * zellgroesse + zellgroesse // 2,
         rob_r * zellgroesse + zellgroesse // 2),
        zellgroesse // 3)

    pygame.display.update()


# ----------------------------------------------
# Hauptprogramm
# ----------------------------------------------
def main():
    pygame.init()

    # ------- Sound laden -------
    pygame.mixer.init()
    klick_sound = None
    ziel_sound = None

    try:
        klick_sound = pygame.mixer.Sound("Click.wav")
    except:
        print("Click.wav nicht gefunden")

    try:
        ziel_sound = pygame.mixer.Sound("Beep.wav")
    except:
        print("Beep.wav nicht gefunden")

    try:
        pygame.mixer.music.load("Soundtrack.ogg")
        pygame.mixer.music.play(-1)
    except:
        print("Soundtrack.ogg nicht gefunden")

    # ------- Labyrinth -------
    gitter, start, ziel = lade_labyrinth("labyrinth.txt")
    if gitter is None:
        print("Fehler beim Laden.")
        sys.exit()

    reihen = len(gitter)
    spalten = len(gitter[0])
    zellgroesse = min(FENSTER_BREITE // spalten, FENSTER_HOEHE // reihen)

    win = pygame.display.set_mode((spalten * zellgroesse, reihen * zellgroesse))
    pygame.display.set_caption("Labyrinth – Rechte-Hand-Regel (mit Sounds & Visualisierung)")

    clock = pygame.time.Clock()

    # Roboterposition
    r, c = start
    richtung = NORD
    ziel_erreicht = False

    running = True
    while running:

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # --------- Logik ---------
        if not ziel_erreicht:

            # === 1. Rechts prüfen ===
            rechts = (richtung + 1) % 4
            dr, dc = RICHTUNGEN[rechts]
            rr, rc = r + dr, c + dc

            zeichne(win, gitter, reihen, spalten, zellgroesse, r, c, (rr, rc))
            time.sleep(0.15)

            if ist_frei(gitter, rr, rc):
                richtung = rechts
                r, c = rr, rc

            else:
                # === 2. Geradeaus prüfen ===
                dr, dc = RICHTUNGEN[richtung]
                nr, nc = r + dr, c + dc

                zeichne(win, gitter, reihen, spalten, zellgroesse, r, c, (nr, nc))
                time.sleep(0.15)

                if ist_frei(gitter, nr, nc):
                    r, c = nr, nc
                else:
                    # === 3. Links prüfen ===
                    links = (richtung - 1) % 4
                    dr, dc = RICHTUNGEN[links]
                    lr, lc = r + dr, c + dc

                    zeichne(win, gitter, reihen, spalten, zellgroesse, r, c, (lr, lc))
                    time.sleep(0.15)

                    if ist_frei(gitter, lr, lc):
                        richtung = links
                        r, c = lr, lc
                    else:
                        # Sackgasse → umdrehen
                        richtung = (richtung + 2) % 4

        # Schritt-Sound
        if not ziel_erreicht:
            if klick_sound:
                klick_sound.play()

        # Ziel erreicht?
        if (r, c) == ziel and not ziel_erreicht:
            ziel_erreicht = True
            print("ZIEL ERREICHT!")
            if ziel_sound:
                ziel_sound.play()
            pygame.mixer.music.stop()

        # Zeichnen ohne Prüfmarkierung
        zeichne(win, gitter, reihen, spalten, zellgroesse, r, c, None)

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
