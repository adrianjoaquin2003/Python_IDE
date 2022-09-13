from tkinter import *
from tkinter import filedialog
import time
from Text_Enctyption_Algorithm import Note
import re
import ctypes
import subprocess
from idlelib.percolator import Percolator
from idlelib.colorizer import ColorDelegator
import queue
from threading import Thread

ctypes.windll.shcore.SetProcessDpiAwareness(1)

root = Tk()
root.title('Text Editor')
root.geometry("1200x1060")

# Set variable for open file name (just in case of errors)
global open_status_name
open_status_name = False


# Create new file function
def new_file():
    my_text.delete(1.0, END)
    root.title('New File')
    status_bar.config(text="New File        ")

    global open_status_name
    open_status_name = False


# Open files
def open_file():
    my_text.delete("1.0", END)

    # Grab filename
    text_file = filedialog.askopenfilename(title="Open File", filetypes=(
        ("Text Files", "*.txt"), ("HTML Files", "*.html"), ("Python Files", "*.py"), ("All Files", "*.*")))

    if text_file:
        global open_status_name
        open_status_name = text_file

    # Update status bars
    name = text_file
    status_bar.config(text=f'{name}        ')
    root.title(f'{name}')

    # Open file
    text_file = open(text_file, 'r', encoding="utf-8")
    contents = text_file.read()

    # Add file to textbox
    my_text.insert(END, contents)
    text_file.close()


# Save file
def save_file():
    global open_status_name
    if open_status_name:
        text_file = open(open_status_name, 'w')
        text_file.write(my_text.get(1.0, END))

        text_file.close()

        status_bar.config(text=f'Saved: {open_status_name}        ')
    else:
        save_as_file()


# Save as file
def save_as_file():
    text_file = filedialog.asksaveasfilename(defaultextension=".*", initialdir="C:/Users/adria/Desktop",
                                             title="Save File", filetypes=(("Text Files", "*.txt"),
                                                                           ("HTML Files", "*.html"),
                                                                           ("Python Files", "*.py"),
                                                                           ("All Files", "*.*")))
    if text_file:
        global open_status_name
        open_status_name = text_file
        name = text_file
        status_bar.config(text=f'{name}        ')
        root.title(f'{name}')

        # Save the file
        text_file = open(text_file, 'w')
        text_file.write(my_text.get(1.0, END))

        text_file.close()
        return str(name)


# Exit and encrypt
def exit_and_encrypt():
    global open_status_name
    if open_status_name:
        root.destroy()
        entry = Note(open_status_name)
        entry.hash()
    else:
        entry = Note(save_as_file())
        root.destroy()
        entry.hash()


# Decrypt file
def decrypt_file():
    global open_status_name
    my_text.delete(1.0, END)
    text_file = open(open_status_name, 'r', encoding="utf-8")
    entry = Note(open_status_name)
    entry.check_password = True
    entry.hash()
    contents = text_file.read()
    my_text.insert(END, contents)
    text_file.close()


has_run = False


def auto_indent(event):
    text = event.widget

    # get leading whitespace from current line
    line = text.get("insert linestart", "insert")
    match = re.match(r'^(\s+)', line)
    whitespace = match.group(0) if match else ""

    # insert the newline and the whitespace
    text.insert("insert", f"\n{whitespace}")

    # return "break" to inhibit default insertion of newline
    return "break"


# Create main frame
my_frame = Frame(root)
my_frame.pack(fill=X, expand=True, pady=5)

# Create scrollbar
text_scroll = Scrollbar(my_frame)
text_scroll.pack(side=RIGHT, fill=Y)

# Create text box
my_text = Text(my_frame, height=10,
               font=("Courier", 16), selectbackground="yellow",
               selectforeground="black", undo=True, yscrollcommand=text_scroll.set)
my_text.pack(fill=X)
my_text.bind("<Return>", auto_indent)

# Configure scrollbar
text_scroll.config(command=my_text.yview)

# Create menu
my_menu = Menu(root)
root.config(menu=my_menu)

# Add status bar to bottom of app
status_bar = Label(root, text='Ready        ', anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=5)


class Console(Frame):
    def __init__(self, parent=None, **kwargs):

        global has_run
        if not has_run:
            has_run = True

        Frame.__init__(self, parent, **kwargs)
        self.parent = parent

        # create widgets
        self.terminal_output = Text(terminal, height=200, font=("Courier", 16), selectbackground="yellow",
                                    selectforeground="black",
                                    yscrollcommand=text_scroll.set)
        self.terminal_output.pack(fill=X, expand=YES, pady=5)
        self.p = subprocess.Popen(f'python {open_status_name}', stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

        # make queues for keeping stdout and stderr whilst it is transferred between threads
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()

        # keep track of where any line that is submitted starts
        self.line_start = 0

        # a daemon to keep track of the threads, so they can stop running
        self.alive = True
        self.running = True

        # start the functions that get stdout and stderr in separate threads
        Thread(target=self.read_from_process_out).start()
        Thread(target=self.read_from_process_err).start()

        # start write loop in the main thread
        self.write_loop()

        # key bindings for events
        self.terminal_output.bind("<Return>", self.enter)
        self.terminal_output.bind('<BackSpace>', self.on_bkspace)
        self.terminal_output.bind('<Delete>', self.on_delete)

    def enter(self, event):
        """The <Return> key press handler"""
        self.terminal_output.configure(state='normal')
        cur_ind = str(self.terminal_output.index(INSERT))
        if int(cur_ind.split('.')[0]) < int(self.terminal_output.search(': ', END, backwards=True).split('.')[0]):
            try:
                selected = self.terminal_output.get('sel.first', 'sel.last')
                if len(selected) > 0:
                    self.terminal_output.insert(END, selected)
                    self.terminal_output.mark_set(INSERT, END)
                    self.terminal_output.see(INSERT)
                    return 'break'
            except:
                selected = self.terminal_output.get(
                    self.terminal_output.search(': ', INSERT, backwards=True), INSERT)
                self.terminal_output.insert(END, selected.strip(': '))
                self.terminal_output.mark_set(INSERT, END)
                self.terminal_output.see(INSERT)
            return 'break'
        string = self.terminal_output.get(1.0, END)[self.line_start:]
        self.line_start += len(string)
        self.p.stdin.write(string.encode())
        self.p.stdin.flush()

    def on_bkspace(self, event):
        pass

    def on_delete(self, event):
        pass

    def on_key(self, event):
        """The typing control (<KeyRelease>) handler"""
        cur_ind = str(self.terminal_output.index(INSERT))
        try:
            if int(cur_ind.split('.')[0]) < int(
                    self.terminal_output.search(r'In [0-9]?', END, backwards=True).split('.')[0]):
                return 'break'
        except:
            return

    def read_from_process_out(self):
        """To be executed in a separate thread to make read non-blocking"""
        while self.alive:
            data = self.p.stdout.raw.read(1024).decode()
            self.outQueue.put(data)

    def read_from_process_err(self):
        """To be executed in a separate thread to make read non-blocking"""
        while self.alive:
            data = self.p.stderr.raw.read(1024).decode()
            self.errQueue.put(data)

    def write_loop(self):
        """Used to write data from stdout and stderr to the Text widget"""
        # if there is anything to write from stdout or stderr, then write it
        if not self.errQueue.empty():
            self.write(self.errQueue.get())
        if not self.outQueue.empty():
            self.write(self.outQueue.get())

        # run this method again after 10ms
        if self.alive:
            self.after(10, self.write_loop)
        else:
            self.p.terminate()

    def write(self, string):
        self.terminal_output.configure(state='normal')
        self.terminal_output.insert(END, string)
        self.terminal_output.see(END)
        self.line_start += len(string)


terminal = Frame(root, height=200, bg="blue")

terminal.pack(fill=X, expand=YES, pady=5)


# Run code file
def run_file():
    global has_run

    terminal_output = Console(root)
    terminal_output.pack(fill=X, expand=True)

    del terminal_output


# Add file menu
file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save as", command=save_as_file)
file_menu.add_command(label="Run", command=run_file)
file_menu.add_command(label="Decrypt", command=decrypt_file)
file_menu.add_separator()
file_menu.add_command(label="Exit and Encrypt", command=exit_and_encrypt)

Percolator(my_text).insertfilter(ColorDelegator())
root.mainloop()
