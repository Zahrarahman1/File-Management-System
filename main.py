import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageTk

root = tk.Tk()
root.title("File Management System")
root.geometry("1200x750")
root.configure(bg="#f5f6f8")

def center(win, w=300, h=200):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

desktop = os.path.join(os.path.expanduser("~"), "Desktop")

MAIN_FOLDER = os.path.join(desktop, "File Management System")
os.makedirs(MAIN_FOLDER, exist_ok=True)

BASE_DIR = os.path.join(MAIN_FOLDER, "FMS")
os.makedirs(BASE_DIR, exist_ok=True)

selected_file = None

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def load_icon(filename):
    try:
        path = os.path.join(BASE_PATH, "icons", filename)
        img = Image.open(path).resize((18, 18))
        return ImageTk.PhotoImage(img)
    except:
        return None

new_icon = load_icon("new.png")
read_icon = load_icon("read.png")
write_icon = load_icon("write.png")
rename_icon = load_icon("rename.png")
delete_icon = load_icon("delete.png")
list_icon = load_icon("list.png")

def save_meta(file_path, permission):
    with open(file_path + ".meta", "w") as f:
        f.write(permission)

def read_meta(file_path):
    meta = file_path + ".meta"
    if os.path.exists(meta):
        return open(meta).read().strip()
    return "RW"

def refresh():
    table.delete(*table.get_children())
    for file in os.listdir(BASE_DIR):
        if file.endswith(".txt"):
            path = os.path.join(BASE_DIR, file)
            size = os.path.getsize(path)
            modified = datetime.fromtimestamp(
                os.path.getmtime(path)
            ).strftime("%Y-%m-%d %H:%M:%S")
            permission = read_meta(path)

            table.insert("", "end", values=(
                "📄 " + file,
                permission,
                f"{size} bytes",
                modified
            ))

def on_select(event):
    global selected_file
    sel = table.focus()
    if not sel:
        return
    selected_file = table.item(sel)["values"][0].replace("📄 ", "")

def create_file():
    name = simpledialog.askstring("Create File", "Enter file name")
    if not name:
        return

    path = os.path.join(BASE_DIR, name + ".txt")

    if os.path.exists(path):
        messagebox.showerror("Error", "File exists")
        return

    win = tk.Toplevel(root)
    win.title("Permission")
    center(win, 300, 200)

    tk.Label(win, text="R = Read Only\nRW = Read & Write").pack(pady=10)

    perm_var = tk.StringVar(value="RW")

    tk.Radiobutton(win, text="R", variable=perm_var, value="R").pack()
    tk.Radiobutton(win, text="RW", variable=perm_var, value="RW").pack()

    def create():
        open(path, "w").close()
        save_meta(path, perm_var.get())
        win.destroy()
        refresh()

    tk.Button(win, text="Create", command=create).pack(pady=10)

def read_file():
    if not selected_file:
        messagebox.showerror("Error", "Select file")
        return

    path = os.path.join(BASE_DIR, selected_file)

    with open(path, "r") as f:
        content = f.read()

    output.delete("1.0", tk.END)
    output.insert(tk.END, f"📄 {selected_file}\n\n", "title")

    if content.strip() == "":
        output.insert(tk.END, "File is empty (nothing written)")
    else:
        output.insert(tk.END, content)

# ✅ WRITE FIXED
def write_file():
    if not selected_file:
        messagebox.showerror("Error", "Select file")
        return

    path = os.path.join(BASE_DIR, selected_file)

    if read_meta(path) == "R":
        messagebox.showerror("Denied", "Read-only file")
        return

    win = tk.Toplevel(root)
    win.title("Write File")
    center(win, 450, 320)

    tk.Label(win, text="Select Mode",
             font=("Segoe UI", 11, "bold")).pack(pady=5)

    selected_mode = tk.StringVar(value="a")

    frame = tk.Frame(win)
    frame.pack(pady=5)

    tk.Radiobutton(frame, text="Append",
                   variable=selected_mode, value="a").pack(side="left", padx=10)

    tk.Radiobutton(frame, text="Overwrite",
                   variable=selected_mode, value="w").pack(side="left", padx=10)

    # 👉 text frame (expand only this)
    text_frame = tk.Frame(win)
    text_frame.pack(fill="both", expand=True, padx=10, pady=5)

    text_area = tk.Text(text_frame)
    text_area.pack(fill="both", expand=True)

    # 👉 button fixed at bottom
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x")

    def save():
        with open(path, selected_mode.get()) as f:
            f.write(text_area.get("1.0", tk.END))
        win.destroy()
        refresh()

    tk.Button(btn_frame,
              text="SAVE",
              bg="#2563eb",
              fg="white",
              font=("Segoe UI", 10, "bold"),
              command=save).pack(pady=10)

def delete_file():
    global selected_file
    if not selected_file:
        return

    path = os.path.join(BASE_DIR, selected_file)

    if os.path.exists(path):
        os.remove(path)

    meta = path + ".meta"
    if os.path.exists(meta):
        os.remove(meta)

    selected_file = None
    refresh()

def rename_file():
    global selected_file
    if not selected_file:
        return

    new = simpledialog.askstring("Rename", "New name")
    if not new:
        return

    old_path = os.path.join(BASE_DIR, selected_file)
    new_path = os.path.join(BASE_DIR, new + ".txt")

    os.rename(old_path, new_path)

    if os.path.exists(old_path + ".meta"):
        os.rename(old_path + ".meta", new_path + ".meta")

    refresh()

def list_files():
    output.delete("1.0", tk.END)
    output.insert(tk.END, "LIST FILES\n\n", "title")

    files = [f for f in os.listdir(BASE_DIR) if f.endswith(".txt")]

    if not files:
        output.insert(tk.END, "No files created yet")
        return

    for f in files:
        path = os.path.join(BASE_DIR, f)
        size = os.path.getsize(path)
        output.insert(tk.END, f"{f} | {size} bytes\n")

top = tk.Frame(root, bg="#1f3a8a", height=50)
top.pack(fill="x")

tk.Label(top, text="FILE MANAGEMENT SYSTEM",
         bg="#1f3a8a", fg="white",
         font=("Segoe UI", 15, "bold")).pack(pady=10)

toolbar = tk.Frame(root, bg="#e9ecef")
toolbar.pack(fill="x", padx=10, pady=5)

def btn(parent, text, icon, cmd):
    return tk.Button(parent, text=text, image=icon, compound="left", command=cmd)

btn(toolbar, "Create", new_icon, create_file).pack(side="left")
btn(toolbar, "Write", write_icon, write_file).pack(side="left")
btn(toolbar, "Read", read_icon, read_file).pack(side="left")
btn(toolbar, "Rename", rename_icon, rename_file).pack(side="left")
btn(toolbar, "Delete", delete_icon, delete_file).pack(side="left")
btn(toolbar, "List", list_icon, list_files).pack(side="left")

frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

columns = ("Name", "Permission", "Size", "Modified")

table = ttk.Treeview(frame, columns=columns, show="headings")

for c in columns:
    table.heading(c, text=c)
    if c == "Name":
        table.column(c, width=300)
    elif c == "Size":
        table.column(c, width=120, anchor="center")
    else:
        table.column(c, width=200)

table.pack(fill="both", expand=True)
table.bind("<<TreeviewSelect>>", on_select)

tk.Frame(root, height=2, bg="#ccc").pack(fill="x", pady=5)

output = tk.Text(root, height=10, bg="white", fg="black")
output.pack(fill="x")

output.tag_config("title", font=("Segoe UI", 12, "bold"))

refresh()
root.mainloop()