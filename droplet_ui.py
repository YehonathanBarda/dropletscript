try:
    import os
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from droplet_functions import calculate_contact_angle
    from PIL import Image, ImageTk
    import subprocess
    import webbrowser
    from datetime import datetime

except ImportError as e:
    print(f"Error: {e}")
    print("Please make sure you have the required modules installed.")
    print("You can install the required modules by running 'pip install -r requirements.txt' in the terminal.")
    exit(1)


"""
Droplet Contact Angle Calculation GUI
@authors: Lyrie Edler and Yehonathan Barda
@date: 04/12/2024
@Copyright (c) 2024 Lyrie Edler and Yehonathan Barda. All rights reserved.
"""

class DropletApp:
    """
    A GUI application for calculating the contact angle of droplets in images.
    Attributes:
        root (tk.Tk): The root window of the Tkinter application.
        image_files (list): List of selected image file paths.
        log_file_name (tk.StringVar): The name of the log file where results will be stored.
        log_directory (tk.StringVar): The directory where the log file will be saved.
        image_label (tk.Label): Label to display selected image file names.
        directory_label (tk.Label): Label to display the selected log directory.
        open_log_button (tk.Button): Button to open the log file after processing.
    Methods:
        create_widgets(): Creates and places the widgets in the application window.
        load_images(): Opens a file dialog to select image files and updates the image label.
        choose_directory(): Opens a directory dialog to select the log directory and updates the directory label.
        run(): Processes the selected images to calculate contact angles and logs the results.
        open_log_file(): Opens the log file in Notepad.
        open_github(): Opens the GitHub repository link in a web browser.

    """
    def __init__(self, root):
        self.root = root
        self.root.title("Droplet Contact Angle Calculation")

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icon', 'droplet_icon.ico')
        self.root.iconbitmap(icon_path)

        self.image_files = []
        self.log_file_name = tk.StringVar(value="results.log")
        self.log_directory = tk.StringVar(value=os.getcwd())
        self.log_mode = tk.StringVar(value="Write")  # Default is write mode
        self.birthday = "27-2"
        self.date = datetime.now().strftime('%d-%m')

        self.create_widgets()

        self.key_sequence = []
        self.root.bind("<KeyPress>", self.unsuspicious_func)
        self.logo_click_count = 0
        self.root.after(1, self.delon_birthday)


    def create_widgets(self):
        # Load and resize the logo image
        logo_path = os.path.join(os.path.dirname(__file__), 'icon', 'droplet_icon.png')
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize the image to 100x100 pixels
        logo_photo = ImageTk.PhotoImage(logo_image)

        # Create and place widgets in the application window
        self.logo_label = tk.Label(self.root, image=logo_photo)
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.root.logo_photo = logo_photo  # Keep a reference to avoid garbage collection
        self.logo_label.bind("<Button-1>", self.on_logo_click)

        tk.Label(self.root, text="Select Images:").grid(row=1, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.load_images).grid(row=1, column=1, padx=10, pady=10)
        self.image_label = tk.Label(self.root, text="")
        self.image_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        tk.Label(self.root, text="Log File Name:").grid(row=3, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.log_file_name).grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Log File Directory:").grid(row=4, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.choose_directory).grid(row=4, column=1, padx=10, pady=10)
        self.directory_label = tk.Label(self.root, text=self.log_directory.get())
        self.directory_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        tk.Label(self.root, text="Log Mode:").grid(row=6, column=0, padx=0, pady=10)
        tk.Radiobutton(self.root, text="Overwrite", variable=self.log_mode, value="Write").grid(row=6, column=1, padx=1, pady=5, sticky=("w"))
        tk.Radiobutton(self.root, text="Append", variable=self.log_mode, value="Append").grid(row=6, column=1, padx=1, pady=5)

        tk.Button(self.root, text="Run", command=self.run).grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        self.open_log_button = tk.Button(self.root, text="Open Log File", command=self.open_log_file, state=tk.DISABLED)
        self.open_log_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        # Add GitHub repository link
        github_link = tk.Label(self.root, text="GitHub Repository", fg="blue", cursor="hand2", font=("Helvetica", 10, "underline"))
        github_link.grid(row=9, column=0, columnspan=2, padx=10, pady=5)
        github_link.bind("<Button-1>", lambda e: self.open_github())

        # Add copyright information at the bottom
        tk.Label(self.root, text="Copyright (c) 2024 Lyrie Edler and Yehonathan Barda. All rights reserved.", font=("Helvetica", 10)).grid(row=10, column=0, columnspan=2, padx=10, pady=5)

    def load_images(self):
        # Open a file dialog to select image files and update the image label
        files = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpeg;*.jpg")])
        if files:
            self.image_files = files
            self.image_label.config(text="\n".join(os.path.basename(file) for file in files))
            messagebox.showinfo("Selected Images", f"{len(files)} images selected")

    def choose_directory(self):
        # Open a directory dialog to select the log directory and update the directory label
        directory = filedialog.askdirectory()
        if directory:
            self.log_directory.set(directory)
            self.directory_label.config(text=self.log_directory.get())

    def on_logo_click(self, event):
        self.logo_click_count += 1
        if self.logo_click_count == 5:
            self.logo_click_count = 0
            self.animate_Delon_image()

    def animate_Delon_image(self):
        Delon_image_path = os.path.join(os.path.dirname(__file__), 'stuff', 'Delon.png')
        Delon_image = Image.open(Delon_image_path)
        Delon_image = Delon_image.resize((80, 220), Image.Resampling.LANCZOS)
        Delon_photo = ImageTk.PhotoImage(Delon_image)
        self.Delon_label = tk.Label(self.root, image=Delon_photo)
        self.Delon_label.image = Delon_photo

        self.Delon_label.place(x=self.root.winfo_width(), y=0)
        self.move_Delon_image(self.root.winfo_width(),self.root.winfo_width() -80)

    def move_Delon_image(self, start_x, end_x):
        step = 5
        if start_x > end_x:
            self.Delon_label.place(x=start_x, y=-12)
            self.root.after(20, self.move_Delon_image, start_x - step, end_x)
        else:
            self.root.after(900, self.move_Delon_image_back, end_x, self.root.winfo_width())

    def move_Delon_image_back(self, start_x, end_x):
        step = 8
        if start_x < end_x:
            self.Delon_label.place(x=start_x, y=-12)
            self.root.after(20, self.move_Delon_image_back, start_x + step, end_x)
        else:
            self.Delon_label.place_forget()
    
    def delon_birthday(self):
        if self.date == self.birthday:
            self.root.title("Droplet Contact Angle Calculation - Happy Birthday Omry!")
            Delon_image_path = os.path.join(os.path.dirname(__file__), 'stuff', 'Delon.png')
            Delon_image = Image.open(Delon_image_path)
            Delon_image = Delon_image.resize((80, 220), Image.Resampling.LANCZOS)
            Delon_photo = ImageTk.PhotoImage(Delon_image)
            self.Delon_label = tk.Label(self.root, image=Delon_photo)
            self.Delon_label.image = Delon_photo
            self.Delon_label.place(x=self.root.winfo_width() - 80, y=0-12)
            birthday_label = tk.Label(self.root, text="Happy Birthday Omry!!!", font=("Helvetica", 24), fg="red")
            birthday_label.place(relx=0.5, rely=0.4, anchor="center")

    def unsuspicious_func(self, event):
        self.key_sequence.append(event.keysym)
        if len(self.key_sequence) > 10:
            self.key_sequence.pop(0)
        if self.key_sequence[-5:] == ['r'] * 5:
                webbrowser.open_new("https://www.youtube.com/watch?v=oHg5SJYRHA0")

        konami_code = ['Up', 'Up', 'Down', 'Down', 'Left', 'Right', 'Left', 'Right', 'b', 'a']
        if self.key_sequence[-10:] == konami_code:
            script_path = os.path.join(os.path.dirname(__file__), 'stuff', 'italian_plumber.py')
            try:
                result = subprocess.run(
                    ['python', script_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(result.stdout)  # Print script output if needed
            except subprocess.CalledProcessError as e:
                # Display the error in a messagebox
                messagebox.showerror("Error", f"Sorry, easter egg failed.\nError: {e.stderr}")
            except Exception as e:
                # Handle unexpected exceptions
                messagebox.showerror("Error", f"Unexpected error occurred.\nError: {e}")


    def run(self):
        # Process the selected images to calculate contact angles and log the results
        if not self.image_files:
            messagebox.showwarning("No Images", "Please select images to process")
            return

        log_file_path = os.path.join(self.log_directory.get(), self.log_file_name.get())
        if not log_file_path.endswith('.log'):
            log_file_path += '.log'
        
        open_mode = 'a' if self.log_mode.get() == "Append" else 'w'
        if os.path.isfile(log_file_path) and open_mode == 'w':
            result = messagebox.askyesnocancel("File Exists", "Log file already exists. Do you want to overwrite it?\nClick 'No' to append, 'Cancel' to abort.")
            if result is None:  # Cancel
                return
            elif result is False:  # No
                open_mode = 'a'

        if not os.path.isfile(log_file_path):
            open_mode = 'w'

        with open(log_file_path, open_mode, encoding='utf-8') as log_file:
            if open_mode == 'w':
                log_file.write(f"Log started on {datetime.now().strftime('%H:%M %d-%m-%Y')}\n\n")

            for file_name in self.image_files:
                try:
                    # Try to open the image using PIL to check if the file is valid
                    with Image.open(file_name) as img:
                        img.verify()  # Verify that it is an image
                except (IOError, SyntaxError) as e:
                    log_file.write(f"Error: Image not found or invalid format. Path: {file_name}\n")
                    messagebox.showerror("Error", f"Image not found or invalid format. Path: {file_name}")
                    continue

                contact_angle = calculate_contact_angle(file_name)
                log_file.write(f"File: {os.path.basename(file_name)} | Contact Angle: {contact_angle} degrees\n")

        messagebox.showinfo("Completed", f"Results stored in {log_file_path}")
        self.open_log_button.config(state=tk.NORMAL)

    def open_log_file(self):
        # Open the log file in Notepad
        log_file_path = os.path.join(self.log_directory.get(), self.log_file_name.get())
        if not log_file_path.endswith('.log'):
            log_file_path += '.log'

        if os.path.isfile(log_file_path):
            subprocess.Popen(['notepad.exe', log_file_path])
        else:
            messagebox.showerror("Error", "Log file not found")
    
    def open_github(self):
        webbrowser.open_new("https://github.com/YehonathanBarda/dropletscript")

if __name__ == "__main__":
    root = tk.Tk()
    app = DropletApp(root)
    root.mainloop()