"""
Lyric Float Overlay
--------------------
Kagaya ng nasa video: nagpe-play ng music habang lumulutang (floating) ang
mga lyric card paakyat sa screen, may typewriter effect, parang sticky
notes/overlay, naka-sync sa oras ng kanta.

SETUP:
    1. pip install pygame
    2. Ilagay ang audio file mo (mp3/wav) sa parehong folder ng script na ito
    3. I-set ang MUSIC_FILE sa pangalan ng file mo
    4. I-edit ang LYRICS list sa ibaba: (oras_sa_segundo, "linya ng lyrics")
       ayon mismo sa timing ng sarili mong kanta
    5. python lyric_float_overlay.py

PAALALA (GitHub Codespaces):
Walang display ang Codespaces by default (headless), kaya hindi lalabas
ang floating overlay doon maliban kung may GUI forwarding ka (hal. VNC /
desktop-lite devcontainer feature). Pinaka-madali: i-download/clone at
patakbuhin sa sarili mong computer na may screen.

Paalala din: dahil sa copyright, wag mag-copy-paste ng eksaktong lyrics
ng commercial na kanta papunta dito kung ipo-post/ibabahagi mo publicly
ang app na ito. Placeholder lyrics muna ang nakalagay sa baba.
"""

import random
import tkinter as tk

import pygame

# ------------------------------------------------------------------
# CONFIG - i-edit mo ito
# ------------------------------------------------------------------
MUSIC_FILE = "song.mp3"        # palitan ng path/pangalan ng sarili mong music file

# (oras_sa_segundo mula simula ng kanta, linya ng lyrics)
LYRICS = [
    (2,  "hello, can you hear this"),
    (5,  "floating words on the screen"),
    (9,  "syncing with every beat"),
    (13, "just like sticky notes"),
    (17, "rising up and fading out"),
    (21, "one line at a time"),
    (25, "make it your own song"),
    (29, "edit the LYRICS list above"),
]

BOX_W, BOX_H = 260, 100
RISE_SPEED = 2          # pixels na igagalaw paitaas kada frame
FRAME_MS = 30            # bilis ng animation loop (milliseconds)
TYPE_SPEED_MS = 40       # bilis ng typewriter effect (milliseconds per letter)


class LyricCard(tk.Toplevel):
    """Isang floating card na nagta-type ng linya, tapos lumulutang paitaas."""

    def __init__(self, master, text, x, y):
        super().__init__(master)
        self.overrideredirect(True)          # walang title bar
        self.attributes("-topmost", True)    # laging nasa ibabaw = overlay
        self.configure(bg="#f5f5dc")

        self.x = x
        self.y = y
        self.full_text = text
        self.typewriter_index = 0

        self.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

        self.label = tk.Label(
            self, text="", wraplength=BOX_W - 20, justify="left",
            bg="#f5f5dc", fg="#222222", font=("Segoe UI", 13, "bold")
        )
        self.label.pack(expand=True, fill="both", padx=10, pady=10)

        self.typewriter()

    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[:self.typewriter_index])
            self.typewriter_index += 1
            self.after(TYPE_SPEED_MS, self.typewriter)

    def rise(self, dy):
        self.y -= dy
        self.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_H < -50


class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # itago ang pangunahing/root window (invisible)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.current_side = "left"

        pygame.mixer.init()
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play()
        self.start_time = pygame.time.get_ticks()

        self.animate()

    def random_safe_x(self):
        """Alternating left/right na posisyon para hindi magkapatong ang cards."""
        center_x = self.screen_w // 2
        spacing = BOX_W + 60

        left_x = center_x - spacing
        right_x = center_x + 60

        if self.current_side == "left":
            self.current_side = "right"
            return right_x + random.randint(-20, 20)
        else:
            self.current_side = "left"
            return left_x + random.randint(-20, 20)

    def animate(self):
        elapsed_sec = (pygame.time.get_ticks() - self.start_time) / 1000

        # I-spawn ang susunod na linya kung nakarating na tayo sa timestamp nito
        if self.next_lyric_idx < len(LYRICS):
            t, text = LYRICS[self.next_lyric_idx]
            if elapsed_sec >= t:
                x = self.random_safe_x()
                y = self.screen_h - BOX_H - 40
                card = LyricCard(self.root, text, x, y)
                self.boxes.append(card)
                self.next_lyric_idx += 1

        # I-move paitaas ang lahat ng aktibong cards; alisin kung offscreen na
        for card in list(self.boxes):
            if card.is_offscreen():
                card.destroy()
                self.boxes.remove(card)
            else:
                card.rise(RISE_SPEED)

        # Itigil ang app kung tapos na ang kanta at wala nang lyrics/cards
        if (self.next_lyric_idx >= len(LYRICS) and not self.boxes
                and not pygame.mixer.music.get_busy()):
            self.root.after(500, self.root.quit)
            return

        self.root.after(FRAME_MS, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()
