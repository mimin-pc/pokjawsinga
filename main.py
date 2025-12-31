import tkinter as tk
from tkinter import messagebox
import random
import time
from card_logic import Card, RANKS, SUITS
from game_engine import GameEngine


class CapsaSuperAI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Singa Rawrrr")
        self.root.geometry("1150x850")

        self.coins = 10000
        self.bet = 0
        self.role = None
        self.start_time = None

        self.diff = tk.StringVar(value="Sulit")
        self.main_frame = tk.Frame(self.root, bg="#1b4d3e")
        self.main_frame.pack(fill="both", expand=True)

        # === TIMER (TAMBAHAN) ===
        self.timer_label = None
        self.timer_job = None

        self.show_login()

    # ================== BASIC ==================
    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ================== LOGIN ==================
    def show_login(self):
        self.clear_screen()
        frame = tk.Frame(self.main_frame, bg="#1b4d3e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame,
            text="LOGIN",
            font=("Impact", 50),
            fg="#f1c40f",
            bg="#1b4d3e"
        ).pack(pady=20)

        user_entry = tk.Entry(frame, font=("Arial", 16), width=25)
        pass_entry = tk.Entry(frame, font=("Arial", 16), width=25, show="*")
        user_entry.pack(pady=8)
        pass_entry.pack(pady=8)

        def do_login():
            u = user_entry.get()
            p = pass_entry.get()

            if u == "admin" and p == "admin":
                self.role = "admin"
                self.show_settings()
            elif u == "player" and p == "123":
                self.role = "player"
                self.show_bet()
            else:
                messagebox.showerror("Error", "Username / Password salah")

        tk.Button(
            frame, text="LOGIN",
            font=("Arial", 14, "bold"),
            width=20, bg="#27ae60", fg="white",
            command=do_login
        ).pack(pady=15)

    # ================== BET ==================
    def show_bet(self):
        self.clear_screen()
        frame = tk.Frame(self.main_frame, bg="#1b4d3e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame,
            text="PASANG BET",
            font=("Impact", 45),
            fg="#f1c40f",
            bg="#1b4d3e"
        ).pack(pady=20)

        tk.Label(
            frame,
            text=f"KOIN ANDA: {self.coins:,}",
            font=("Arial", 16),
            fg="white",
            bg="#1b4d3e"
        ).pack(pady=10)

        bet_entry = tk.Entry(frame, font=("Arial", 16), width=20)
        bet_entry.pack(pady=10)

        def start_game_from_bet():
            try:
                self.bet = int(bet_entry.get())
                if self.bet <= 0 or self.bet > self.coins:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Bet tidak valid")
                return

            if self.bet < 1000:
                self.diff.set("Mudah")
            elif self.bet < 5000:
                self.diff.set("Normal")
            else:
                self.diff.set("Sulit")

            self.start_game()

        tk.Button(
            frame, text="START GAME",
            font=("Arial", 14, "bold"),
            width=20, bg="#27ae60", fg="white",
            command=start_game_from_bet
        ).pack(pady=10)

        tk.Button(
            frame, text="BACK",
            font=("Arial", 12),
            width=20, bg="#e67e22", fg="white",
            command=self.show_login
        ).pack(pady=5)

    # ================== ADMIN ==================
    def show_settings(self):
        self.clear_screen()
        frame = tk.Frame(self.main_frame, bg="#1b4d3e")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame,
            text="ADMIN - DIFFICULTY",
            font=("Impact", 40),
            fg="#f1c40f",
            bg="#1b4d3e"
        ).pack(pady=20)

        for level in ["Mudah", "Normal", "Sulit"]:
            tk.Radiobutton(
                frame, text=level,
                variable=self.diff,
                value=level,
                font=("Arial", 14),
                bg="#1b4d3e",
                fg="white",
                selectcolor="#1b4d3e"
            ).pack(anchor="w")

        tk.Button(
            frame, text="LOGOUT",
            font=("Arial", 14),
            width=15, bg="#e74c3c", fg="white",
            command=self.show_login
        ).pack(pady=20)

    # ================== GAME ASLI ==================
    def start_game(self):
        self.clear_screen()
        self.start_time = time.time()

        # === START TIMER ===
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        

        self.table_cards = None
        self.table_type = None
        self.last_player = None
        self.passed = set()
        self.selected = []

        deck = [Card(r, s) for r in RANKS for s in SUITS]
        random.shuffle(deck)
        self.hands = [
            sorted(deck[i * 13:(i + 1) * 13], key=lambda x: x.score)
            for i in range(4)
        ]

        for i in range(4):
            if any(c.rank == '3' and c.suit == '♦' for c in self.hands[i]):
                self.turn = i
                break

        self.setup_arena_ui()
        self.update_timer()
        self.refresh_ui()
        if self.turn != 0:
            self.root.after(1500, self.bot_logic)

    def setup_arena_ui(self):
        arena = tk.Frame(self.main_frame, bg="#0d2b1e")
        arena.pack(fill="both", expand=True)

        # === TIMER LABEL ===
        self.timer_label = tk.Label(
            arena,
            text="⏱️ Waktu: 0 detik",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#0d2b1e"
        )
        self.timer_label.pack(pady=5)

        self.table_ui = tk.Frame(arena, bg="#32b482", width=850, height=300, relief="sunken", bd=8)
        self.table_ui.pack(pady=20)
        self.table_ui.pack_propagate(False)

        self.bot_info = []
        f_bot = tk.Frame(arena, bg="#0d2b1e")
        f_bot.pack(fill="x")
        names = ["🤖 BUDI", "👽 CHANDRA", "👹 SULTAN"]
        for i in range(3):
            l = tk.Label(f_bot, text=f"{names[i]}\n13 Kartu",
                         font=("Arial", 11, "bold"),
                         bg="#0d2b1e", fg="white")
            l.pack(side="left", expand=True)
            self.bot_info.append(l)

        self.hand_ui = tk.Frame(arena, bg="#0d2b1e")
        self.hand_ui.pack(pady=20)

        ctrl = tk.Frame(arena, bg="#0d2b1e")
        ctrl.pack()
        tk.Button(ctrl, text="PASANG!", font=("Impact", 22),
                  bg="#f1c40f", width=12,
                  command=self.player_play).grid(row=0, column=0, padx=10)
        tk.Button(ctrl, text="PASS", font=("Impact", 22),
                  bg="#e74c3c", fg="white", width=12,
                  command=self.player_pass).grid(row=0, column=1, padx=10)

    def refresh_ui(self):
        for w in self.table_ui.winfo_children():
            w.destroy()

        if self.table_cards:
            tk.Label(self.table_ui,
                     text=f"MEJA: {self.table_type[0].upper()}",
                     font=("Arial", 12, "bold"),
                     bg="#163d2e", fg="gold").pack()
            f = tk.Frame(self.table_ui, bg="#163d2e")
            f.pack(expand=True)
            for c in self.table_cards:
                color = "red" if c.suit in ["♦", "♥"] else "black"
                tk.Label(f, text=f"{c.rank}\n{c.suit}",
                         font=("Arial", 20, "bold"),
                         bg="white", fg=color,
                         width=5, height=4,
                         relief="raised").pack(side="left", padx=5)

        for w in self.hand_ui.winfo_children():
            w.destroy()

        for i, c in enumerate(self.hands[0]):
            color = "red" if c.suit in ["♦", "♥"] else "black"
            bg = "#f1c40f" if i in self.selected else "white"
            tk.Button(self.hand_ui,
                      text=f"{c.rank}{c.suit}",
                      bg=bg, fg=color,
                      font=("Arial", 10, "bold"),
                      width=4, height=3,
                      command=lambda idx=i: self.select_card(idx)
                      ).pack(side="left", padx=1)

        for i in range(3):
            color = "#f1c40f" if self.turn == i + 1 else "white"
            self.bot_info[i].config(
                text=f"BOT {i+1}\n{len(self.hands[i+1])} Kartu",
                fg=color
            )

    def select_card(self, i):
        if i in self.selected:
            self.selected.remove(i)
        else:
            self.selected.append(i)
        self.refresh_ui()

    def player_play(self):
        cards = sorted([self.hands[0][i] for i in self.selected], key=lambda x: x.score)
        info = GameEngine.get_combo_info(cards)
        if info and GameEngine.validate_move(self.table_cards, self.table_type, info):
            self.execute_move(0, cards, self.selected, info)
            self.selected = []
        else:
            messagebox.showerror("Error", "Kombinasi kartu tidak valid!")

    def player_pass(self):
        if self.last_player is None or self.last_player == 0:
            return
        self.passed.add(0)
        self.next_turn()

    def bot_logic(self):
        if self.turn == 0:
            return
        hand = self.hands[self.turn]
        move, info = None, None

        if not self.table_cards:
            move = [hand[0]]
            info = GameEngine.get_combo_info(move)
        else:
            for c in hand:
                test_info = GameEngine.get_combo_info([c])
                if GameEngine.validate_move(self.table_cards, self.table_type, test_info):
                    if self.diff.get() == "Sulit" and c.rank == '2' and len(hand) > 3:
                        continue
                    move = [c]
                    info = test_info
                    break

        if move:
            idxs = [hand.index(c) for c in move]
            self.execute_move(self.turn, move, idxs, info)
        else:
            self.passed.add(self.turn)
            self.next_turn()

    def execute_move(self, p_idx, cards, idx_list, info):
        self.table_cards = cards
        self.table_type = info
        self.last_player = p_idx
        for i in sorted(idx_list, reverse=True):
            self.hands[p_idx].pop(i)
        self.passed = set()
        if not self.hands[p_idx]:
            self.end_game(p_idx)
        else:
            self.next_turn()

    def next_turn(self):
        self.turn = (self.turn + 1) % 4
        if len(self.passed) >= 3:
            self.table_cards = None
            self.table_type = None
            self.passed = set()
            self.turn = self.last_player if self.last_player is not None else 0
        self.refresh_ui()
        if self.turn != 0:
            self.root.after(1000, self.bot_logic)

    def end_game(self, winner):
        # === STOP TIMER ===
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        duration = int(time.time() - self.start_time)
        if winner == 0:
            self.coins += self.bet * 2
            msg = f"MENANG!\n+{self.bet * 2} KOIN\nDurasi: {duration} detik"
        else:
            self.coins -= self.bet
            msg = f"KALAH!\n-{self.bet} KOIN\nDurasi: {duration} detik"

        messagebox.showinfo("HASIL", msg)
        self.show_login()

    # ================== TIMER UPDATE ==================
    def update_timer(self):
        if not self.start_time or not self.timer_label:
            return
        elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"⏱️ Waktu: {elapsed} detik")
        self.timer_job = self.root.after(1000, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    app = CapsaSuperAI(root)
    root.mainloop()
