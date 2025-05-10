import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import json
from PIL import Image, ImageTk
from io import BytesIO

class SimpleLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Login API Client")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # API base URL - change this to your actual API URL
        self.api_base_url = "http://localhost:8000/api/auth/"
        self.token = None
        self.current_user = None
        
        # Create the main notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create login frame
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        
        # Create users frame (will be populated after login)
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="Users")
        
        # Create profile frame
        self.profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_frame, text="My Profile")
        
        # Setup the login UI
        self.setup_login_ui()
        
        # Disable tabs until login
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")

    def setup_login_ui(self):
        # Create a frame for login form with some padding and styling
        login_form = ttk.LabelFrame(self.login_frame, text="Login to API", padding=(20, 10))
        login_form.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Service Number
        ttk.Label(login_form, text="Service Number:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.service_number_var = tk.StringVar()
        self.service_number_entry = ttk.Entry(login_form, textvariable=self.service_number_var, width=30)
        self.service_number_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Check Username button
        check_button = ttk.Button(login_form, text="Check Service Number", command=self.check_username)
        check_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Phone number display (will be shown after username check)
        self.phone_label = ttk.Label(login_form, text="")
        self.phone_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Passcode (initially hidden)
        ttk.Label(login_form, text="Passcode:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.passcode_var = tk.StringVar()
        self.passcode_entry = ttk.Entry(login_form, textvariable=self.passcode_var, show="*", width=30)
        self.passcode_entry.grid(row=3, column=1, pady=5, padx=5)
        self.passcode_entry.config(state="disabled")  # Initially disabled
        
        # Login button (initially hidden)
        self.login_button = ttk.Button(login_form, text="Login", command=self.verify_code)
        self.login_button.grid(row=4, column=0, columnspan=2, pady=15)
        self.login_button.config(state="disabled")  # Initially disabled
        
        # Status message
        self.status_var = tk.StringVar()
        ttk.Label(login_form, textvariable=self.status_var, foreground="red").grid(row=5, column=0, columnspan=2)

    def setup_users_ui(self):
        # Clear existing widgets
        for widget in self.users_frame.winfo_children():
            widget.destroy()
            
        # Create a frame for the users list
        list_frame = ttk.Frame(self.users_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for users
        columns = ("Service Number", "Name", "Email", "Phone")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_button = ttk.Button(self.users_frame, text="Refresh Users", command=self.fetch_users)
        refresh_button.pack(pady=10)
        
        # Fetch users
        self.fetch_users()

    def setup_profile_ui(self):
        # Clear existing widgets
        for widget in self.profile_frame.winfo_children():
            widget.destroy()
            
        if not self.current_user:
            ttk.Label(self.profile_frame, text="Please login to view your profile").pack(pady=20)
            return
            
        # Create a frame for profile info
        profile_info = ttk.LabelFrame(self.profile_frame, text="My Profile", padding=(20, 10))
        profile_info.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Display user information
        row = 0
        for field, value in [
            ("Service Number", self.current_user.get("serviceNumber", "N/A")),
            # ("Username", self.current_user.get("username", "N/A")),
            ("Name", self.current_user.get("name", "N/A")),
            ("Email", self.current_user.get("email", "N/A")),
            ("Phone", self.current_user.get("phone", "N/A"))
        ]:
            ttk.Label(profile_info, text=f"{field}:", font=("TkDefaultFont", 10, "bold")).grid(
                row=row, column=0, sticky=tk.W, pady=5)
            ttk.Label(profile_info, text=value).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
            row += 1
        
        # Display profile image if available
        if "profile_image" in self.current_user and self.current_user["profile_image"]:
            try:
                response = requests.get(self.current_user["profile_image"])
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    img = Image.open(img_data)
                    img = img.resize((150, 150), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    img_label = ttk.Label(profile_info)
                    img_label.image = photo  # Keep a reference to prevent garbage collection
                    img_label.configure(image=photo)
                    img_label.grid(row=row, column=0, columnspan=2, pady=10)
            except Exception as e:
                print(f"Error loading profile image: {e}")

    def check_username(self):
        service_number = self.service_number_var.get()
        
        if not service_number:
            self.status_var.set("Please enter a service number")
            return
            
        try:
            response = requests.post(
                f"{self.api_base_url}check-username/", 
                data={"username": service_number}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("exists", False):
                    # Show masked phone number
                    self.phone_label.config(text=f"Phone: {data.get('phone', '')}")
                    
                    # Enable passcode entry and login button
                    self.passcode_entry.config(state="normal")
                    self.login_button.config(state="normal")
                    
                    # Focus on passcode entry
                    self.passcode_entry.focus()
                    
                    self.status_var.set("Service number found. Please enter your passcode.")
                else:
                    self.status_var.set("Service number not found.")
                    self.phone_label.config(text="")
            elif response.status_code == 404:
                self.status_var.set("Service number not found.")
                self.phone_label.config(text="")
            else:
                self.status_var.set("Error checking service number.")
                
        except requests.RequestException as e:
            self.status_var.set(f"Connection error: {str(e)}")

    def verify_code(self):
        service_number = self.service_number_var.get()
        passcode = self.passcode_var.get()
        
        if not service_number or not passcode:
            self.status_var.set("Please enter both service number and passcode")
            return
            
        try:
            response = requests.post(
                f"{self.api_base_url}verify-code/", 
                data={
                    "username": service_number,
                    "code": passcode
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.current_user = data
                
                # Enable other tabs
                self.notebook.tab(1, state="normal")
                self.notebook.tab(2, state="normal")
                
                # Setup other UIs
                self.setup_users_ui()
                self.setup_profile_ui()
                
                # Switch to users tab
                self.notebook.select(1)
                
                self.status_var.set("Login successful!")
            else:
                error_msg = "Login failed"
                if response.status_code == 401:
                    error_msg = "Invalid credentials"
                self.status_var.set(error_msg)
                
        except requests.RequestException as e:
            self.status_var.set(f"Connection error: {str(e)}")

    def fetch_users(self):
        if not self.token:
            return
            
        try:
            response = requests.get(
                f"{self.api_base_url}users/",
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                users = response.json()
                
                # Clear existing items
                for item in self.users_tree.get_children():
                    self.users_tree.delete(item)
                    
                # Add users to treeview
                for user in users:
                    self.users_tree.insert("", tk.END, values=(
                        user.get("serviceNumber", ""),
                        # user.get("username", ""),
                        user.get("name", ""),
                        user.get("email", ""),
                        user.get("phone", "")
                    ))
            else:
                messagebox.showerror("Error", "Failed to fetch users")
                
        except requests.RequestException as e:
            messagebox.showerror("Connection Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleLoginApp(root)
    root.mainloop()
