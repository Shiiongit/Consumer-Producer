import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas, PhotoImage, Button
from threading import Semaphore
import sys

# --- Figma-related paths (REPLACE WITH YOUR ACTUAL PATHS) ---
def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets" / "frame0"
    return Path(__file__).parent / "assets" / "frame0"

ASSETS_PATH = get_base_path()


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# --- Buffer and Semaphores ---
BUFFER_SIZE = 5
buffer = []
mutex = Semaphore(1)
empty_slots = Semaphore(BUFFER_SIZE)
full_slots = Semaphore(0)

consumer_sleep = 2.5
producer_sleep = 1

# --- GUI Setup ---
class ProducerConsumerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Producer-Consumer Simulation")

        # Set initial window size (before creating elements)
        root.geometry("1069x654") 

        # Prevent window resizing
        root.resizable(False, False) 

        # Canvas setup (Figma design)
        self.canvas = Canvas(root, bg="#FFFFFF", height=654, width=1069, bd=0, highlightthickness=0, relief="ridge")  
        self.canvas.place(x=0, y=0)

        image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))  
        root.image_image_1 = image_image_1
        self.bg_label = self.canvas.create_image(534.5, 40.0, image=image_image_1)  

        self.canvas.create_text(2, 5, anchor="nw", text="SHELOU L. ASARIA", fill="#F8FFF7", font=("Baloo Regular", 24 * -1))
        self.canvas.create_text(2, 25, anchor="nw", text="CSPC 112", fill="#FFFFFF", font=("Baloo Regular", 24 * -1))
        self.canvas.create_text(2, 45, anchor="nw", text="CONSUMER PRODUCER", fill="#FFFFFF", font=("Baloo Regular", 30 * -1))

        # --- Updated Dark Green Rectangle (Table Background) ---
        RECT_X1, RECT_Y1 = 230, 120  
        RECT_X2, RECT_Y2 = 850, 540  
        self.canvas.create_rectangle(RECT_X1, RECT_Y1, RECT_X2, RECT_Y2, fill="#001e00", outline="")

        # --- Table setup (Centered) ---
        TABLE_WIDTH = 600 
        TABLE_HEIGHT = 400  
        TABLE_X = RECT_X1 + (RECT_X2 - RECT_X1 - TABLE_WIDTH) // 2
        TABLE_Y = RECT_Y1 + (RECT_Y2 - RECT_Y1 - TABLE_HEIGHT) // 2

        table_frame = ttk.Frame(root)
        table_frame.place(x=TABLE_X, y=TABLE_Y, width=TABLE_WIDTH, height=TABLE_HEIGHT)

        columns = ("Step", "Producer Action", "Consumer Action", "Buffer Contents", "Empty", "Full")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="none")

        fixed_widths = [50, 140, 140, 135, 50, 40]
        for col, width in zip(columns, fixed_widths):
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=width, stretch=False)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=22)

        self.tree.pack(fill="both", expand=True)

        # Step Counter
        self.step = 0

        # Done Button
        button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        root.button_image_1 = button_image_1
        self.done_button = Button(root, image=button_image_1, borderwidth=0, highlightthickness=0, command=self.clear_table, relief="flat")  # Call clear_table method
        self.done_button.place(x=871.0, y=584.0, width=145.0, height=43.0)

    def update_table(self, producer_action, consumer_action):
        self.step += 1
        buffer_state = list(buffer)
        self.tree.insert("", "end", values=(self.step, producer_action, consumer_action, str(buffer), empty_slots._value, full_slots._value))
        self.root.update_idletasks()

    def clear_table(self):
        self.tree.delete(*self.tree.get_children())  # Clear all rows
        self.step = 0 
        buffer.clear() # Clear the buffer
        empty_slots._value = BUFFER_SIZE 
        full_slots._value = 0 

# --- Producer and Consumer Functions ---
def producer(gui):
    for i in range(1, 11):
        time.sleep(producer_sleep if i == 1 else 1)

        empty_slots.acquire()
        mutex.acquire()

        buffer.append(i)
        gui.update_table(f"Produced {i}", "")

        mutex.release()
        full_slots.release()

def consumer(gui):
    for i in range(1, 11):
        time.sleep(consumer_sleep)

        full_slots.acquire()
        mutex.acquire()

        item = buffer.pop(0)
        gui.update_table("", f"Consumed {item}")

        mutex.release()
        empty_slots.release()

# --- Main Function (with after_idle) ---
def main():
    root = tk.Tk()
    gui = ProducerConsumerGUI(root)

    def start_threads():
        producer_thread = threading.Thread(target=producer, args=(gui,))
        consumer_thread = threading.Thread(target=consumer, args=(gui,))

        producer_thread.start()
        consumer_thread.start()

    root.after_idle(start_threads) 
    root.mainloop()

if __name__ == "__main__":
    main()
