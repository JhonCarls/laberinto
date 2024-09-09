import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import time

# Clase para representar el laberinto
class Maze:
    def __init__(self, filename):
        self.load_maze(filename)

    def load_maze(self, filename):
        with open(filename, 'r') as file:
            lines = file.read().splitlines()

        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        self.walls = []
        self.start = None
        self.goal = None

        for i, line in enumerate(lines):
            row = []
            for j, char in enumerate(line):
                if char == 'A':
                    self.start = (i, j)
                    row.append(False)
                elif char == 'B':
                    self.goal = (i, j)
                    row.append(False)
                elif char == '#':
                    row.append(True)
                else:
                    row.append(False)
            self.walls.append(row)

        if self.start is None or self.goal is None:
            raise Exception("El laberinto debe tener un punto de inicio (A) y un punto final (B).")

    def is_wall(self, position):
        x, y = position
        return self.walls[x][y]

    def neighbors(self, position):
        row, col = position
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((r, c))
        return result

    def solve_with_method(self, method):
        from collections import deque

        if method == 'stack':
            frontier = []
        elif method == 'queue':
            frontier = deque()

        frontier.append((self.start, []))
        explored = set()

        while frontier:
            current, path = frontier.pop() if method == 'stack' else frontier.popleft()

            if current == self.goal:
                return path + [current]

            explored.add(current)

            for neighbor in self.neighbors(current):
                if neighbor not in explored:
                    if method == 'stack':
                        frontier.append((neighbor, path + [current]))
                    else:
                        frontier.append((neighbor, path + [current]))
        return []

# Clase principal del juego
class MazeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maze Solver")
        self.geometry("1200x900")  # Tamaño ajustado para que el fondo y los botones estén visibles correctamente.

        self.current_window = None
        self.character_image = None
        self.character_label = None
        self.maze_canvas = None
        self.cell_size = 40
        self.move_count = 0
        self.maze = None
        self.auto_solve = False
        self.solve_method = None

        # Iniciar la primera ventana
        self.show_first_window()

    def set_gif_background(self, frame, gif_file):
        gif_image = Image.open(gif_file)
        gif_frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(gif_image)]

        def animate_gif(frame_index):
            frame.config(image=gif_frames[frame_index])
            frame_index = (frame_index + 1) % len(gif_frames)
            self.after(100, animate_gif, frame_index)

        frame = tk.Label(self.current_window)
        frame.pack(fill="both", expand=True)
        animate_gif(0)

    def show_first_window(self):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = tk.Frame(self, bg="lightblue")
        self.current_window.pack(expand=True, fill="both")

        # Cargar fondo animado .gif
        self.set_gif_background(self.current_window, "background1.gif")

        label = tk.Label(self.current_window, text="Seleccione el método de resolución automática", bg="lightblue", font=("Arial", 16))
        label.place(relx=0.5, rely=0.4, anchor="center")

        stack_button = tk.Button(self.current_window, text="Resolver con Pilas", command=lambda: self.start_auto_mode('stack'), bg="blue", font=("Arial", 14))
        stack_button.place(relx=0.5, rely=0.5, anchor="center")

        queue_button = tk.Button(self.current_window, text="Resolver con Colas", command=lambda: self.start_auto_mode('queue'), bg="purple", font=("Arial", 14))
        queue_button.place(relx=0.5, rely=0.6, anchor="center")

    def start_auto_mode(self, method):
        self.auto_solve = True
        self.solve_method = method
        self.show_difficulty_window()

    def show_difficulty_window(self):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = tk.Frame(self, bg="lightblue")
        self.current_window.pack(expand=True, fill="both")

        # Fondo animado para selección de dificultad
        self.set_gif_background(self.current_window, "background3.gif")

        label = tk.Label(self.current_window, text="Seleccione la dificultad del laberinto", bg="lightblue", font=("Arial", 16))
        label.place(relx=0.5, rely=0.2, anchor="center")

        # Botones para seleccionar nivel de dificultad
        difficulties = [("Fácil", "laberinto1.txt", "lightgreen"), 
                        ("Medio", "laberinto2.txt", "yellow"), 
                        ("Medio-Difícil", "laberinto3.txt", "orange"), 
                        ("Difícil", "laberinto4.txt", "red"), 
                        ("Maníaco", "laberinto5.txt", "purple")]

        for i, (text, file, color) in enumerate(difficulties):
            button = tk.Button(self.current_window, text=text, command=lambda f=file: self.load_maze(f), bg=color, font=("Arial", 14))
            button.place(relx=0.5, rely=0.3 + (i * 0.1), anchor="center")

    def load_maze(self, filename):
        self.maze = Maze(filename)
        self.show_maze_window()

    def show_maze_window(self):
        if self.current_window:
            self.current_window.destroy()

        self.current_window = tk.Frame(self, bg="lightblue")
        self.current_window.pack(expand=True, fill="both")

        self.maze_canvas = tk.Canvas(self.current_window, width=self.maze.width * self.cell_size, height=self.maze.height * self.cell_size, bg="black")
        self.maze_canvas.place(relx=0.5, rely=0.5, anchor="center")

        self.draw_maze()

        # Cargar la imagen del personaje
        self.character_image = Image.open("character.jpg")
        self.character_image = self.character_image.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
        self.character_image = ImageTk.PhotoImage(self.character_image)

        self.character_label = self.maze_canvas.create_image(self.maze.start[1] * self.cell_size, self.maze.start[0] * self.cell_size, anchor="nw", image=self.character_image)

        # Contador de movimientos
        self.move_count_label = tk.Label(self.current_window, text="Espacios recorridos: 0", bg="lightblue", font=("Arial", 14))
        self.move_count_label.pack(pady=10)

        if self.auto_solve:
            self.solve_maze()

    def draw_maze(self):
        for i in range(self.maze.height):
            for j in range(self.maze.width):
                color = "white" if not self.maze.is_wall((i, j)) else "black"
                self.maze_canvas.create_rectangle(j * self.cell_size, i * self.cell_size, (j + 1) * self.cell_size, (i + 1) * self.cell_size, fill=color)

    def update_character(self, new_position):
        self.maze_canvas.coords(self.character_label, new_position[1] * self.cell_size, new_position[0] * self.cell_size)
        self.move_count += 1
        self.move_count_label.config(text=f"Espacios recorridos: {self.move_count}")
        self.update()

    def solve_maze(self):
        solution = self.maze.solve_with_method(self.solve_method)
        for move in solution:
            self.update_character(move)
            time.sleep(0.5)
        self.show_end_game_message()

    def show_end_game_message(self):
        if messagebox.askyesno("¡Felicidades!", "Llegaste al final. ¿Quieres volver a jugar?"):
            self.show_first_window()
        else:
            self.quit()

# Iniciar el juego
if __name__ == "__main__":
    game = MazeGame()
    game.mainloop()
