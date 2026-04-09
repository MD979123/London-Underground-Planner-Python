import heapq
import customtkinter as ctk
import tkinter.messagebox as tkmb
import csv
import re

circular_termini = {"circle line": ["Hammersmith", "Edgware Road (Circle/District)"]}
def find_terminus_from_path(graph, path, index, line_id):
    current_station = path[index][0]
    prev_station = path[index - 1][0] if index > 0 else None

    line_name = line_map.get(line_id, {}).get("name", "").lower()
    termini = circular_termini.get(line_name)

    visited = set()

    while True:
        # If it is a circular line and we've reached a terminus, return the station
        if termini and current_station in termini:
            return current_station

        if current_station in visited:
            return current_station

        visited.add(current_station)

        next_stations = [
            n for (n, _, l) in graph.get(current_station, [])
            if l == line_id and n != prev_station
        ]

        if not next_stations:
            return current_station

        if len(next_stations) > 1:
            next_station = None
            for candidate in next_stations:
                if candidate not in visited:
                    next_station = candidate
                    break

            if next_station is None:
                next_station = next_stations[0]
        else:
            next_station = next_stations[0]

        prev_station = current_station
        current_station = next_station

# User database is empty so that login/register details are stored later
users_db = {}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1920x1080")
app.title("London Underground Shortest Route Planner")

# -------------------------------------------------------------------------------- Login/Register Functions
def login():
    user = user_entry.get() # Both variables gather the input from the user
    password = user_password.get()
    if user in users_db and users_db[user] == password: # Checks if the credentials match
        tkmb.showinfo("Success", "Login Successful!")
        show_main_menu(user)
    else: # Counter-result if login unsuccessful
        tkmb.showerror("Error", "Invalid Username/Email or Password")

def register():
    user = user_entry.get()
    password = user_password.get() # Register details
    if not user or not password: # Checks if both fields are inputted
        tkmb.showwarning("Input Error", "Please enter both a username and password.")
        return
    if "@" in user:
        if not valid_email(user):
            tkmb.showerror("Error", "Invalid email format")
            return
    else:
        if not valid_username(user):
            tkmb.showerror("Error", "Username must have no spaces or dots")
            return
    if user in users_db:
        tkmb.showwarning("Error", "Username already exists!")
    if not valid_password(password):
        tkmb.showerror(
            "Error",
            "Password must be minimum 8 characters, including an uppercase letter, lowercase letter, and a number")
        return
    else:
        users_db[user] = password
        tkmb.showinfo("Success", f"Account created for {user}!\nYou can now login.") # Register confirmation
        # Clear entries after registration so for security purposes the user has to re-enter their credentials
        user_entry.delete(0, 'end')
        user_password.delete(0, 'end')

def valid_username(username):
    if " " in username: # Checks if username criteria is met
        return False
    if "@" in username:
        return False
    if "." in username:
        return False
    return True

def valid_password(password):
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password): # Checks if password criteria is met
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    return True

def valid_email(email):
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    return re.match(pattern, email)


def show_main_menu(username):
    # Hides the login page and now will display the main menu page responsible for route finder
    login_frame.pack_forget()
    welcome_label.configure(text=f"Welcome, {username}!") # Welcome message
    menu_frame.pack(pady=20, padx=40, fill='both', expand=True)


# --------------------------------------------------------------------------------------- Login and Register Page
login_frame = ctk.CTkFrame(master=app)
login_frame.pack(pady=20, padx=40, fill='both', expand=True)

ctk.CTkLabel(login_frame, text="Login System", font=("Calibri", 24, "bold")).pack(pady=12)

user_entry = ctk.CTkEntry(login_frame, placeholder_text="Username") # Entry box for username
user_entry.pack(pady=12, padx=10)

user_password = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*") # Entry box for password and covers the password with asterisks
user_password.pack(pady=12, padx=10)

# Buttons
login_btn = ctk.CTkButton(login_frame, text="Login", fg_color="dodgerblue4", border_width=2, command=login)
login_btn.pack(pady=6, padx=10)

# Outlined style for Register button
register_btn = ctk.CTkButton(login_frame, text="Register", fg_color="dodgerblue4", border_width=2, command=register)
register_btn.pack(pady=6, padx=10)

# --------------------------------------------------------------------------- Main Menu Page (Displayed after login)
menu_frame = ctk.CTkFrame(master=app)

welcome_label = ctk.CTkLabel(menu_frame, text="Welcome!", font=("Arial", 18, "bold"))
welcome_label.pack(pady=20)

def logout():
    menu_frame.pack_forget()
    user_entry.delete(0, 'end') # Logouts the user
    user_password.delete(0, 'end')
    login_frame.pack(pady=20, padx=40, fill='both', expand=True)


ctk.CTkButton(menu_frame, text="Logout", fg_color="red", command=logout).pack(pady=20) # Logout button on main page

station_map = {} # Initially empty after which the database below is imported

with open("londonstations.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    reader.fieldnames = [h.strip() for h in reader.fieldnames]

    for row in reader:
        station_map[row["id"]] = row["name"]

stations = list(station_map.values()) # Lists all the stations

# Dropdown 1
ctk.CTkLabel(menu_frame, text="Enter the first two letters of the Start station:").pack(pady=(10, 0))
start_station_box = ctk.CTkComboBox(menu_frame, values= stations)
start_station_box.pack(pady=10) # Selects start station

# Dropdown 2
ctk.CTkLabel(menu_frame, text="Enter the first two letters of the End station:").pack(pady=(10, 0))
end_station_box = ctk.CTkComboBox(menu_frame, values= stations)
end_station_box.pack(pady=10) # Selects end station

def filter_start_station(event=None):
    typed = start_station_box.get().lower() # Converts user input to lowercase

    if typed == "":
        start_station_box.configure(values = stations) # Shows the full list of stations if the user doesn't enter anything
        return

    filtered = [s for s in stations if s.lower().startswith(typed)] # Filters which shows only stations that start with what the user types
    start_station_box.configure(values=filtered) # Updates dropdown list

start_station_box.bind("<KeyRelease>", filter_start_station) # Calls the filter function every time user release key

def filter_end_station(event=None):
    typed_end = end_station_box.get().lower() # Converts to lowercase

    if typed_end == "":
        end_station_box.configure(values = stations)
        return

    filtered_end = [s for s in stations if s.lower().startswith(typed_end)] # Shows stations which only start with letters user types
    end_station_box.configure(values=filtered_end)

end_station_box.bind("<KeyRelease>", filter_end_station)

# ----------------------------------------------------------------------------------------- Creating the graph for Dijkstra's

graph = {}

with open("londonconnections.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f) # Open connections file and reads it as a dictionary

    for row in reader:
        a_id = row["station1"] # Iterates through the dictionary
        b_id = row["station2"] # and finds the travel time between
        time = int(row["time"]) # each station on the route

        a = (station_map[a_id])
        b = (station_map[b_id])

        graph.setdefault(a, []).append((b, time, row["line_id"])) # Appends the connections in both ways to the graph since travel is bidirectional
        graph.setdefault(b, []).append((a, time, row["line_id"]))
# ------------------------------------------------------------------------------------------ Dijkstra's Algorithm

def dijkstra(graph, start, end): # Dijkstra's Algorithm which is behind the route finder
    queue = [(0, start, [(start, None)])] # Currently the time is 0, the start of the graph is the start station, and None represents the chosen line
    visited = set()

    while queue:
        time, node, path = heapq.heappop(queue) # Picks the smallest unvisited route in the queue

        state = (node, path[-1][1])  # The node is the current station and the path is the line

        if state in visited: # Checks if current station and line is in the set of visited stations
            continue

        visited.add(state)

        if node == end:
            return time, path # Once it reaches the end, the time taken and the specified route is outputted

        InterchangePenalty = 5 # Penalty added to the time if interchange is required; reduces chance of interchange on a route which requires only one line
        # this can also account for having to walk to a different platform which adds more realism as platform transfer is not instantaneous
        for neighbor, weight, line_id in graph.get(node, []):
            prev_line = path[-1][1]

            penalty = 0 # The initial penalty at the start of the route
            if prev_line is not None and prev_line != line_id:
                penalty = InterchangePenalty # Adds a penalty if the next station is on a different line

            new_time = time + weight + penalty # adds the penalty to the total time
            new_path = path + [(neighbor, line_id)] # Updated route with interchange

            heapq.heappush(queue, (new_time, neighbor, new_path))
# --------------------------------------------------------------------------------------------- Route Finder Subroutine
def find_route():

    start = (start_station_box.get())
    end = (end_station_box.get())
    save_button.configure(state="normal")

    if not start or not end:
        tkmb.showerror("Error", "Please enter both stations") # Different if statements for different stations
        return

    if start == end:
        tkmb.showerror("Error", "Start and end stations must be different") # If both stations are the same
        return

    if start not in graph or end not in graph:
        tkmb.showerror("Error", "Station not recognised")
        return

    result = dijkstra(graph, start, end)

    if result is None:
        tkmb.showerror("Error", "No route found")
        return

    time, path = result # splits the tuple returned by Dijkstra's algorithm into two variables

    global current_path # declares that the variable current_path is global so any changes affect the variable outside the function
    current_path = path

    global current_time
    current_time = time

    result_title.configure(text=f"{start} → {end}  |  {time} mins") # Displays main route summary
    back_button.configure(command=back_to_menu)
    save_button.pack(pady=10)
    display_route(path)
    show_result_page()

ctk.CTkButton(menu_frame, text="Find Route", fg_color="dodgerblue4", border_width=2, command=find_route).pack(pady=20) # Find Route button

line_map = {}

with open("londonlines.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader: # Builds a dictionary which maps the line ID to its name and colour so both can be displayed
        line_map[row["line_id"]] = { "name": row["name"], "colour": "#" + row["colour"] } # The # is added in order for Python to recognise
        # the Hex code of the colour

# ------------------------------------------------------------------------------------ Route Displayer Subroutine
def display_route(path):
    for widget in result_frame.winfo_children():
        widget.destroy() # Deletes any previous results for routes before displaying the current one

    if len(path) >= 2 and path[-1][0] == path[-2][0]:
        path = path[:-1] # If the last station is the same as 2nd to last station it is removed

    legs = []
    current_line = None
    current_leg = [path[0][0]]  # Groups consecutive stations on the same line into a 'leg' of the journey

    for station, line_id in path[1:]:
        if current_line is None:
            current_line = line_id # If Current Line has no value it is assigned the ID from the database

        if line_id == current_line:
            current_leg.append(station) # Adds a station on the same line to the journey
        else:
            legs.append((current_line, current_leg))
            current_line = line_id # Creates a new leg of the journey when an interchange happens
            current_leg = [current_leg[-1], station]

    if current_leg:
        legs.append((current_line, current_leg))

    for line_id, stations in legs:
        if line_id is None:
            continue

        line_info = line_map[line_id]

        last_station = stations[-1]

        direction = last_station  # fallback

        for i, (s, l) in enumerate(path):
            if s == last_station and l == line_id:
                direction = find_terminus_from_path(graph, path, i, line_id)
                break


        container = ctk.CTkFrame(result_frame)
        container.pack(fill="x", pady=5)

        row = ctk.CTkFrame(container)
        row.pack(fill="x")

        # coloured bar
        bar = ctk.CTkFrame(row, width=10, fg_color=line_info["colour"]) # Adds a bar with the colour of the line next to each leg of the journey
        bar.pack(side="left", fill="y")


        text = f"{stations[0]} → {stations[-1]} ({line_info['name']} towards {direction})"
        # Displays main summary for each leg of journey
        label = ctk.CTkLabel(row, text=text)
        label.pack(side="left", padx=10)

        details = ctk.CTkFrame(container)

        for s in stations:
            ctk.CTkLabel(details, text=s).pack(anchor="w")


        def toggle(frame=details): # Creating the dropdown for each leg of the journey which shows start and end station on each leg of the journey
            if frame.winfo_ismapped(): # and then gives the option to see all the individual stations on that leg
                frame.pack_forget()
            else:
                frame.pack(fill="x", padx=20)

        # arrow button which shows all stations in a leg
        btn = ctk.CTkButton(row, text="▼", width=30, command=toggle)
        btn.pack(side="right") # Button for dropdown toggle

# ---------------------------------------------------------------------------------- Route Saving Subroutine
saved_routes = []
def save_route():
    saved_routes.append({ #
        "start": start_station_box.get(),
        "end": end_station_box.get(),
        "path": current_path,
        "time": current_time # Stores the current route into the Saved Routes page
    })

    tkmb.showinfo("Saved", "Route saved successfully") # Confirmation message

# ------------------------------------------------------------------------------------------ Route Result Widgets
result_page = ctk.CTkFrame(master=app) # Route result page frame

def show_result_page():
    menu_frame.pack_forget()
    result_page.pack(fill='both', expand=True) # Shows the result page for the route found

result_title = ctk.CTkLabel(result_page, text="Route", font=("Arial", 20, "bold"))
result_title.pack(pady=20)

back_button = ctk.CTkButton(result_page, text="Back", fg_color="dodgerblue4", border_width=2)
back_button.pack(pady=10) # Back button on saved route

save_button = ctk.CTkButton(result_page, text="Save Route", fg_color="dodgerblue4", border_width=2, command=save_route)
save_button.pack(pady=10)

result_frame = ctk.CTkScrollableFrame(result_page, height=600) # Enables scrolling if there are many interchanges which don't fit on the page
result_frame.pack(fill="both", expand=True, pady=20)

#---------------------------------------------------------------------------------------------------- Saved Routes Manager
saved_page = ctk.CTkFrame(app) # Saved Routes page

ctk.CTkLabel(saved_page, text="Saved Routes", font=("Arial", 20, "bold")).pack(pady=20)

saved_list = ctk.CTkScrollableFrame(saved_page) # Enables scrolling if there are many routes saved in the Saved Routes page
saved_list.pack(fill="both", expand=True)

def show_saved_routes():
    menu_frame.pack_forget()
    result_page.pack_forget()

    for widget in saved_list.winfo_children():
        widget.destroy() # Prevents from each saved route from duplicating every time you open the Save Routes page

    for route in saved_routes:
        text = f"{route['start']} → {route['end']}" # Shows main summary for each route saved (i.e. start and end station)

        ctk.CTkButton(
            saved_list, # Creates a clickable button for every saved route so it can be re-viewed.
            text=text, fg_color="dodgerblue4", border_width=2,
            command=lambda r=route: open_saved_route(r) # Necessary otherwise any button would display the most recently saved route
        ).pack(fill="x", pady=5)

    saved_page.pack(fill="both", expand=True) # Shows Saved Routes page

def open_saved_route(route):
    saved_page.pack_forget() # Hides Saved Routes menu and switches to the saved route
    save_button.pack_forget()

    global current_path
    current_path = route["path"]

    result_title.configure(text=f"{route['start']} → {route['end']} | {route['time']} mins")

    back_button.configure(command=back_to_saved)

    display_route(route["path"]) # Loads the specific route
    result_page.pack(fill="both", expand=True)

def back_to_menu():
    result_page.pack_forget() # Return to main menu
    saved_page.pack_forget()
    menu_frame.pack(fill="both", expand=True)
ctk.CTkButton(menu_frame, text="Saved Routes", fg_color="dodgerblue4", border_width=2, command=show_saved_routes).pack(pady=10)

def back_to_saved():
    result_page.pack_forget()
    show_saved_routes()
    saved_page.pack(fill="both", expand=True)

ctk.CTkButton(saved_page, text="Back", fg_color="dodgerblue4", border_width=2, command=back_to_menu).pack(pady=10)

app.mainloop()

