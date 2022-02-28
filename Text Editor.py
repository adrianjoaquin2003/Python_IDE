from tkinter import *
from tkinter import filedialog
from tkinter import font
from Text_Enctyption_Algorithm import Note

root = Tk()
root.title('Text Editor')
root.geometry("1200x660")

#Set variable for open file name (just incase of errors)
global open_status_name
open_status_name = False

#Create new file function
def new_file():
    my_text.delete(1.0, END)
    root.title('New File')
    status_bar.config(text = "New File        ")

    global open_status_name
    open_status_name = False


#Open files
def open_file():
    my_text.delete("1.0", END)

    #Grab filename
    text_file = filedialog.askopenfilename(title = "Open File", filetypes = (("Text Files", "*.txt"), ("HTML Files", "*.html"), ("Python Files", "*.py"), ("All Files", "*.*")))
    
    if text_file:
        global open_status_name
        open_status_name = text_file

    #Update status bars
    name = text_file
    status_bar.config(text = f'{name}        ')
    root.title(f'{name}')

    #Open file
    text_file = open(text_file, 'r', encoding = "utf-8")
    contents = text_file.read()

    #Add file to textbox
    my_text.insert(END, contents)
    text_file.close()


#Save file
def save_file():
    global open_status_name
    if open_status_name:
        text_file = open(open_status_name, 'w')
        text_file.write(my_text.get(1.0, END))

        text_file.close()

        status_bar.config(text = f'Saved: {open_status_name}        ')
    else:
        save_as_file()


#Save as file
def save_as_file():
    text_file = filedialog.asksaveasfilename(defaultextension = ".*", initialdir = "C:/Users/adria/Desktop", title = "Save File", filetypes = (("Text Files", "*.txt"), ("HTML Files", "*.html"), ("Python Files", "*.py"), ("All Files", "*.*")))
    if text_file:
        global open_status_name
        open_status_name = text_file
        name = text_file
        status_bar.config(text = f'{name}        ')
        root.title(f'{name}')

        #Save the file
        text_file = open(text_file, 'w')
        text_file.write(my_text.get(1.0, END))

        text_file.close()
        return str(name)


#Exit and encrypt
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


#Decrypt file
def decrypt_file():
    global open_status_name
    my_text.delete(1.0, END)
    text_file = open(open_status_name, 'r', encoding = "utf-8")
    entry = Note(open_status_name)
    entry.check_password = True
    entry.hash()
    contents = text_file.read()
    my_text.insert(END, contents)
    text_file.close()


#Create main frame
my_frame = Frame(root)
my_frame.pack(pady = 5)

#Create scrollbar
text_scroll = Scrollbar(my_frame)
text_scroll.pack(side = RIGHT, fill = Y)

#Create text box
my_text = Text(my_frame, width = 97, height = 25, font = ("Helvetica", 16), selectbackground = "yellow", selectforeground = "black", undo = True, yscrollcommand = text_scroll.set)
my_text.pack()

#Configure scrollbar
text_scroll.config(command = my_text.yview)

#Create menu
my_menu = Menu(root)
root.config(menu = my_menu)

#Add file menu
file_menu = Menu(my_menu, tearoff = False)
my_menu.add_cascade(label = "File", menu = file_menu)
file_menu.add_command(label = "Open", command = open_file)
file_menu.add_command(label = "New", command = new_file)
file_menu.add_command(label = "Save", command = save_file)
file_menu.add_command(label = "Save as", command = save_as_file)
file_menu.add_command(label = "Decrypt", command = decrypt_file)
file_menu.add_separator()
file_menu.add_command(label = "Exit and Encrypt", command = exit_and_encrypt)

#Add status bar to bottom of app
status_bar = Label(root, text = 'Ready        ', anchor = E)
status_bar.pack(fill = X, side = BOTTOM, ipady = 5)

root.mainloop()
