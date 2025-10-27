#Movie Database.Ver1.0 By Frank Potts Ver.1.0 10/14/2025
import webbrowser
import json
import os
import tkinter as tk
import io
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import logging
from PIL import Image
import threading
logging.basicConfig(level=logging.INFO)

# Define the Global variables
edit_index = None
movies = []
movie_list = []
APP_VERSION = "1.0"
movie_cache = {}
display_titles = []  # This will track raw titles for poster lookup
status_label = []

def rebuild_movie_list():
    display_titles.clear()
    movie_cache.clear()
    movie_listbox.delete(0, tk.END)

    for m in movies:
        title = m.get("title", "")
        year = m.get("year", "")
        display = f"{title} ({year})" if year else title

        display_titles.append(display)
        movie_cache[display] = m
        movie_listbox.insert(tk.END, display)

def show_splash_fade_in():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("800x650+400+175")  # Adjust size and position

    # Load splash image
    img_path = os.path.join("MovieDatabase_v1", "splash_screen.png")
    img = Image.open(img_path)
    img = img.resize((800, 650), Image.Resampling.LANCZOS)  # Resize the image here
    splash_img = ImageTk.PhotoImage(img)

    label = tk.Label(splash, image=splash_img)
    label.pack()

    # Start with full transparency
    splash.attributes("-alpha", 0.0)

    def fade_in(step=0):
        alpha = step / 20.0
        splash.attributes("-alpha", alpha)
        if step < 20:
            splash.after(50, fade_in, step + 1)
        else:
            splash.after(2000, splash.destroy)  # Show for 2 seconds after fade-in

    fade_in()
    splash.mainloop()

# Calling main app window
show_splash_fade_in()

def load_data():
    global movies
    if os.path.exists("movies.json"):
        with open("movies.json", "r") as file:
            try:
                movies = json.load(file)
            except json.JSONDecodeError:
                movies = []
    else:
        movies = []
        print(f"Loaded {len(movies)} movies from file.") #Line added 10/5

        for m in movies:  # Section added 10/5
            if not isinstance(m, dict) or 'title' not in m:
                print("Warning: Invalid movie entry:", m)
        
# Listbox population loop.
def populate_movie_listbox():
    global movie_cache, display_titles

    BASE_URL = "https://api.themoviedb.org/3"
    API_KEY = '40f11b1f4296b3e789f5fc449e4668cc'

    display_titles.clear()
    movie_cache.clear()
    movie_listbox.delete(0, tk.END)

    for movie in movies:
        title = movie.get('title', '').strip()
        display = f"{title} ({movie.get('year', '')}) - {movie.get('director', '')} - {movie.get('genre', '')} - {movie.get('star', '')} - {movie.get('rate', '')}"
        movie_listbox.insert(tk.END, display)
        display_titles.append(title)

        # 🔄 Preload TMDb poster data for each movie
        url = f"{BASE_URL}/search/movie"
        params = {'api_key': API_KEY, 'query': title}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            ## print(f"TMDb response for '{title}':", data)

            if data['results']:
                poster_path = data['results'][0].get('poster_path')
                #  print(f"✅ Poster for '{title}':", poster_path)
                movie_cache[title] = data['results'][0]
            else:
                print(f"❌ No TMDb results for: {title}")
        except Exception as e:
            print(f"Error fetching TMDb data for '{title}': {e}")

def update_movie_list():
    BASE_URL = "https://api.themoviedb.org/3"
    API_KEY = "your_actual_tmdb_api_key"
    global movie_cache, display_titles
    movie_cache.clear()
    display_titles.clear()
    movie_listbox.delete(0, tk.END)

    # Rebuild display_titles and movie_cache from movies list
    display_titles = [m.get("title", "") for m in movies]
    movie_cache = {m.get("title", ""): m for m in movies}


    

    # Repopulate the listbox
    for title in display_titles:
        movie_listbox.insert(tk.END, title)

    for movie in movies:
        title = movie.get('title', '')
        display = f"{title} ({movie.get('year', '')}) - {movie.get('director', '')} - {movie.get('genre', '')} - {movie.get('star', '')} - {movie.get('rate', '')}"
        movie_listbox.insert(tk.END, display)
        display_titles.append(title)  # ✅ This line is critical

        # Preload TMDb poster data
        url = f"{BASE_URL}/search/movie"
        params = {'api_key': API_KEY, 'query': title}
        try:
            response = requests.get(url, params=params)
            # print(f"TMDb status for '{title}': {response.status_code}")
            data = response.json()
            
            if 'results' in data and data['results']:
               movie_cache[title] = data['results'][0]
            # else:
               # print(f"No TMDb results for '{title}'")
                
        except Exception as e:
            print(f"Error fetching TMDb data for '{title}': {e}")
            
        # ✅ Add delay to avoid rate limits
            time.sleep(0.2)
            print ("time is ok")
def add_movie():
    global edit_index, add_button
    title = title_var.get().strip()

    if not title:
        print("⚠️ Skipping empty movie entry.")
        messagebox.showwarning("Missing Title", "Please enter a movie title.")
        return


    movie = {
        "title": title_var.get().strip(),
        "director": director_var.get().strip(),
        "year": year_var.get().strip(),
        "genre": genre_var.get().strip(),
        "star": star_var.get().strip(),
        "rate": rate_var.get().strip(),
        "poster_path": poster_path_var.get() or "",
        "tmdb_id": ""      # Optional for future TMDb lookup        
    }
    
# 2. Append to the movies list
    # print("📦 Appending movie to list")
    # movies.append(movie)

# 3. Save to file
    with open("movies.json", "w") as f:
        json.dump(movies, f, indent=4)

# 4. Refresh the listbox
        update_movie_list()



    if not movie["title"]:
        print("Skipping empty movie entry.")
        messagebox.showwarning("Missing Title", "Please enter a movie title.")
        return

    if edit_index is not None:
        movie["poster_path"] = movies[edit_index].get("poster_path", "")
        movies[edit_index] = movie
        messagebox.showinfo("Updated", f"🎬 '{movie['title']}' has been updated.")
        edit_index = None
    else:
        movies.append(movie)
        messagebox.showinfo("Added", f"🎬 '{movie['title']}' has been added.")

    with open("movies.json", "w") as f:
        json.dump(movies, f, indent=4)

    rebuild_movie_list()
    update_movie_list()
    populate_movie_listbox()
    save_movies()
    clear_fields()
    add_button.config(text="Add Movie")

# Clear values of all entry fields tied to StringVar() objects.  Ready for new entry...
def clear_fields():    
    title_var.set("")
    director_var.set("")
    year_var.set("")
    genre_var.set("")
    star_var.set("")
    rate_var.set("")
    print("Fields cleared.")

#  Begin Dummy Test Function...    
from PIL import Image, ImageDraw, ImageFont

def create_dummy_poster():
    # Create a blank image
    img = Image.new("RGB", (120, 180), color="#d0e7f9")

    # Draw placeholder text
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    draw.text((10, 80), "Poster Here", fill="#003366", font=font)

    # Convert to PhotoImage and display
    img = img.resize((120, 180), Image.Resampling.LANCZOS)
    poster_img = ImageTk.PhotoImage(img)
    poster_label.config(image=poster_img)
    poster_label.image = poster_img
    info_label.config(text="Dummy poster generated.")
    
# End Dummy Test Function

def clear_search():
    search_var.set("")
    update_movie_list()
    populate_movie_listbox()
    status_label.config(text="Showing all movies")
    messagebox.showinfo("Search Cleared", "All movies are now visible.")

def save_movies():
    with open("movies.json", "w") as f:
        json.dump(movies, f, indent=4)    
    messagebox.showinfo("Save Successful", "🎉 Your movie list has been saved!")
    
    # Create a scrollable popup window
    popup = tk.Toplevel()
    popup.title("✅ Movie saved to movies.json!")
    popup.geometry("600x400")

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(frame, yscrollcommand=scrollbar.set, wrap=tk.WORD)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=text_widget.yview)

    # Format and insert movie list
    formatted_movies = "\n".join(
        f"{m.get('title', '')} ({m.get('year', '')}) - {m.get('director', '')} [{m.get('genre', '')}] [{m.get('rate', '')}]"
        for m in movies
    )
    text_widget.insert(tk.END, formatted_movies)
    text_widget.config(state=tk.DISABLED)  # Make it read-only
    
# Creating the root creates the main window  
root = tk.Tk()
root.title("🎬 Simple Movie Database") # Title of the program

#Declaring String Variables
title_var = tk.StringVar()
director_var = tk.StringVar()
year_var = tk.StringVar()
genre_var = tk.StringVar()
star_var = tk.StringVar()
delete_movie_var = tk.StringVar()
rate_var = tk.StringVar()
search_var = tk.StringVar()
poster_path_var = tk.StringVar()

# 🔧 Column weight control to prevent layout stretching
root.columnconfigure(0, weight=0)
root.columnconfigure(1, weight=0)
root.columnconfigure(2, weight=0)  # Poster column
root.columnconfigure(3, weight=1)  # Info label column

# Row weight control (optional but helpful)
for i in range(10):  # Adjust range to match your layout depth
    root.rowconfigure(i, weight=0)
    
root.configure(bg="#d0e7f9")  # App’s background
root.geometry("1000x700") # Width x Height in pixels
# Status label for feedback messages
status_label = tk.Label(root, text="", anchor="w", fg="gray", bg="#d0e7f9", font=("Segoe UI", 10))
status_label.grid(row=99, column=0, columnspan=4, sticky="ew", padx=10, pady=(0, 5))

# Setting op the option menu
options = ["Title", "Year", "Rate", "genre"] # Prepares Drop Down
variable = tk.StringVar()                   # Dynamic access
variable.set("Select a movie")  # Optional: default value

# Apply white background and flat relief, OptionMenu Style
option_menu = tk.OptionMenu(root, variable, *options)
option_menu.config(
    bg="#FFFFFF",
    fg="#000000",
    activebackground="#d0e7f9",
    highlightthickness=0,
    bd=0,
    font=("Arial", 10)
)

def load_movies():
    global movies
    try:
        with open("movies.json", "r") as f:
            movies = json.load(f)

        # Patch missing poster_path fields
        for movie in movies:
            if not movie.get("poster_path"):
                print(f"🔄 Re-fetching poster for: {movie.get('title')}")
                search_tmdb(movie.get("title"), silent=True)
        
        # ✅ Collect titles with missing poster paths
        missing_posters = [m.get("title", "Unknown") for m in movies if not m.get("poster_path")]
        
        if missing_posters:
            print("⚠️ Movies missing poster_path:", ", ".join(missing_posters))

        # ✅ Refresh listbox and poster display ONCE after loading
        update_movie_list()

        if movie_listbox.size() > 0:
            movie_listbox.select_set(0)
            movie_listbox.event_generate("<<ListboxSelect>>")

        print("📂 Movies loaded from movies.json")

    except FileNotFoundError:
        print("⚠️ No saved file found. Starting fresh.")
        movies = []
    except Exception as e:
        print("Error loading movies:", e)
        search_tmdb(silent=True)

def update_movie_list():
    populate_movie_listbox
    global display_titles, movie_cache
    movie_listbox.delete(0, tk.END)
    display_titles = []
    movie_cache = {}
    if movie_listbox.size() > 0:
        movie_listbox.select_set(0)
        movie_listbox.event_generate("<<ListboxSelect>>")
    for movie in movies:
        if not isinstance(movie, dict):
            print("⚠️ Skipping non-dictionary entry:", movie)
            continue
        if not movie.get("title"):
            print("⚠️ Skipping movie with missing title:", movie)
            continue

        display = f"{movie.get('title', '')} ({movie.get('year', '')}) - {movie.get('director', '')} - {movie.get('genre', '')} - {movie.get('star', '')} - {movie.get('rate', '')}"
        display_titles.append(display)
        movie_cache[display] = movie
        movie_listbox.insert(tk.END, display)

    # Rebind selection event to ensure poster shows
    movie_listbox.bind("<<ListboxSelect>>", on_movie_select)


def delete_selected_movie():
    global movies
    selected = movie_listbox.curselection()
    if selected:
        index = selected[0]
        movie = movies[index]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{movie['title']}'?"
        )
        if confirm:
            del movies[index]
            update_movie_list()
            save_movies()
            movie_listbox.selection_clear(0, tk.END)
            messagebox.showinfo("Deleted", f"'{movie['title']}' has been removed.")
            
            if movie_listbox.size() > 0:
                movie_listbox.select_set(0)
                movie_listbox.event_generate("<<ListboxSelect>>")
            else:
                show_poster("")  # Clear poster if no movies left
                
    else:
        messagebox.showwarning("No Selection", "Please select a movie to delete.")

    ## save_movies()
    ## movie_listbox.selection_clear(0, tk.END)

def edit_movie():
    global edit_index, title_var, director_var, year_var, genre_var, star_var, rate_var
    global title_entry

    print("Edit button clicked")

    selected = movie_listbox.curselection()

    if not selected:
        print("No movie selected — warning shown")
        messagebox.showwarning("No Selection", "Please select a movie to edit.")
        return

    edit_index = selected[0]

    print("Selected index:", edit_index)
    print("Total movies:", len(movies))
    print("Movie at index:", movies[edit_index])
    
    if edit_index >= len(movies):
        print("Invalid edit_index:", edit_index)
        return

    movie = movies[edit_index]

    print("Setting title to:", movie.get("title", ""))
    title_var.set(movie.get("title", ""))
    print("Title field now contains:", title_var.get())
    
    # Populate entry fields
    title_var.set(movie.get("title", ""))
    director_var.set(movie.get("director", ""))
    year_var.set(movie.get("year", ""))
    genre_var.set(movie.get("genre", ""))
    star_var.set(movie.get("star", ""))
    rate_var.set(movie.get("rate", ""))
    add_button.config(text="Update Movie")

    # poster_url = movie.get("poster_path", "")
    # if poster_url:
      #       show_poster(poster_url)
    # else:
      #       show_fallback_image()  # or clear_poster()
        
    # Highlight and scroll to selected item
    movie_listbox.selection_clear(0, tk.END)
    movie_listbox.selection_set(edit_index, edit_index)
    movie_listbox.activate(edit_index)
    movie_listbox.see(edit_index)
        
    title_var.set(movie.get("title", ""))
    print("Title field now contains:", title_var.get())
    
    messagebox.showinfo("Edit Mode", f"Editing '{movie.get('title', '')}'. Make changes and click 'Update Movie'.")
        
def search_movies():
    global display_titles, movie_cache
    
    keyword = search_var.get().lower()
    movie_listbox.delete(0, tk.END)
    filtered = []
    display_titles = []
    movie_cache ={}
    
    for movie in movies:
        if (
            keyword in movie.get("title", "").lower()
            or keyword in movie.get("director", "").lower()
            or keyword in movie.get("genre", "").lower()
            or keyword in movie.get("star", "").lower()
            or keyword in movie.get("rate", "").lower()
        ):
            filtered.append(movie)
            display = f"{movie.get('title', '')} ({movie.get('year', '')}) - {movie.get('director', '')} - {movie.get('genre', '')} - {movie.get('star', '')} - {movie.get('rate', '')}"
            display_titles.append(display)
            movie_cache[display] = movie
            movie_listbox.insert(tk.END, display)
            
    if movie_listbox.size() == 0:
        messagebox.showinfo("No Results", f"No movies found matching '{keyword}'.")

def send_feedback_email():
    try:
        webbrowser.open("mailto:spymaster49637@outlook.com?subject=Movie%20App%20Feedback")
        
    except:
        messagebox.showinfo("Feedback", "If clicking doesn't work, please email:\nspymaster49637@outlook.com")

def save_data():
    with open("movies.json", "w") as file:
        json.dump(movies, file, indent=4)

def sort_movies(by="title", reverse=False):
    global movies
    try:
        movies.sort(key=lambda m: m.get(by, "").lower(), reverse=reverse)
        populate_movie_listbox()
    except Exception as e:
        messagebox.showerror("Sort Error", f"Could not sort by '{by}': {e}")

import requests
import io
from PIL import Image, ImageTk

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = '40f11b1f4296b3e789f5fc449e4668cc'  # Actual API Key

def get_genre_map():
    url = f"{BASE_URL}/genre/movie/list"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    return {genre['id']: genre['name'] for genre in data['genres']}

genre_map = get_genre_map()  # Call this once at startup

def open_full_poster(full_poster_path):
    if not full_poster_path:
        messagebox.showwarning("No Poster", "No poster available for this movie.")
        return

    try:
        top = tk.Toplevel()
        top.title("Full-Size Poster")

        full_url = f"https://image.tmdb.org/t/p/w500{full_poster_path}"
        img_data = requests.get(full_url).content
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((300, 450))

        full_img = ImageTk.PhotoImage(img)
        full_label = tk.Label(top, image=full_img)
        full_label.image = full_img
        full_label.grid()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load poster: {e}")

def show_about():
    tk.messagebox.showinfo(
        "About",
        f"🎬 Movie Database App\nVersion {APP_VERSION}\nCreated by Frank Potts\n\nPowered by TMDb API"
    )

def on_movie_select(event):
    global movie_cache, movies

    poster_label.config(image='', text='', width=120, height=220)
    poster_label.image = None

    selection = event.widget.curselection()
    if not selection:
        return
    
    index = selection[0]
    
    if index >= len(display_titles):
        print("Selection index out of range for display_titles")
        return
    
    selected_display = display_titles[index]
    movie = movie_cache.get(selected_display)

    if not movie or not isinstance(movie, dict):
        poster_label.config(image='', text='No movie data available', width=120, height=220)
        poster_label.image = None
        poster_label.unbind("<Button-1>")
        return

# Clean Up Movies List    
    movies = [m for m in movies if m and isinstance(m, dict)]

    # Find the actual index in movies
    edit_index = next((i for i, m in enumerate(movies)
                   if m.get("title", "") == movie.get("title", "") and
                      m.get("year", "") == movie.get("year", "")), None)

# 🔍 Debug prints to check alignment
    ## print("Listbox size:", movie_listbox.size())
    ## print("Display titles:", len(display_titles))
        
    poster_path = movie.get("poster_path", "")    
    show_poster(poster_path)
    
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w185{poster_path}"
        print("Poster URL:", poster_url)
        try:
            response = requests.get(poster_url)
            response.raise_for_status()  # Raise error for bad status codes            
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((120, 220), Image.LANCZOS)
            poster_img = ImageTk.PhotoImage(img)
            
            poster_label.config(image=poster_img, text='', width=120, height=220)
            poster_label.image = poster_img  # Keep reference
            # Bind click to open full-size poster and makes poster clickable...
            poster_label.bind("<Button-1>", lambda e, path=poster_path: open_full_poster(path))

        except Exception as e:
            print("Error loading poster:", e)
            poster_label.config(image='', text='Poster failed to load', width=120, height=220)
            poster_label.image=None
            poster_label.unbind("<Button-1>")
        
    else:
        poster_label.config(image='', text='No poster available', width=120, height=220 )
        poster_label.image = None
        poster_label.unbind("<Button-1>")  #Remove Click binding if no poster

# Poster display helper
def show_poster(path):
    if not path:
        poster_label.config(image='', text='No poster available')
        poster_label.image = None
        return

    if getattr(poster_label, "current_path", None) == path:
        return  # Already showing this poster

    poster_label.current_path = path

    try:
        response = requests.get(f"https://image.tmdb.org/t/p/w185{path}")
        response.raise_for_status()
        img_data = response.content
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((120, 180), Image.LANCZOS)
        poster_img = ImageTk.PhotoImage(img)

        poster_label.config(image=poster_img, text='')
        poster_label.image = poster_img

    except Exception as e:
        print("Error loading poster:", e)
        poster_label.config(image='', text='Poster failed to load')
        poster_label.image = None

# 🔹 Tooltip function
def show_tooltip(event):
    info_label.config(text="Click poster to enlarge")

def hide_tooltip(event):
    info_label.config(text="")

# New def enlarge_poster function 10/14/25
def enlarge_poster():
    try:
        img = Image.open(io.BytesIO(current_poster_data))
        img = img.resize((300, 450), Image.Resampling.LANCZOS)
        enlarged_img = ImageTk.PhotoImage(img)

        top = tk.Toplevel(root)
        top.title("Enlarged Poster")

        label = tk.Label(top, image=enlarged_img)
        label.image = enlarged_img  # 🔥 Keep a reference!
        label.pack()
    except Exception as e:
        print("Enlarge failed:", e)

# SEARCH TMDB
def search_tmdb(silent=False):
    global full_poster_path
    poster_url = None   # Fall Back
    # 🧹 Clear non-search fields
    director_var.set("")
    genre_var.set("")
    year_var.set("")
    star_var.set("")

    # 🖼️ Reset poster and info labels
    poster_label.config(image='', text='No poster available')
    poster_label.image = None
    info_label.config(text='Searching TMDb...')
    poster_label.bind("<Button-1>", lambda e: enlarge_poster()) # New binding 10/14/25
    
    # 🔍 Get title before clearing it
    title = title_var.get().strip()
    if not title:
        if not silent:
            logging.info("search_tmdb() skipped: title is empty")
        info_label.config(text="Please enter a movie title before searching.")
        return


    url = f"{BASE_URL}/search/movie"
    params = {'api_key': API_KEY, 'query': title}
    response = requests.get(url, params=params)
    data = response.json()

    # ✅ Check if results were returned
    if data['results']:
        movie = data['results'][0]
        title_var.set(movie.get('title', ''))
    
        # 🎬 Genre
        genre_ids = movie.get('genre_ids', [])
        genre_name = genre_map.get(genre_ids[0], "Unknown") if genre_ids else "Unknown"
        genre_var.set(genre_name)

        # 🎬 Director
        movie_id = movie['id']
        credits_url = f"{BASE_URL}/movie/{movie_id}/credits"
        credits = requests.get(credits_url, params={'api_key': API_KEY}).json()
        director = next((person['name'] for person in credits['crew'] if person['job'] == 'Director'), "Unknown")
        director_var.set(director)

        # 🎬 Year
        release_date = movie.get('release_date', '')
        release_year = release_date.split('-')[0] if release_date else "Unknown"
        year_var.set(release_year)

        # 🎬 Main Star
        main_star = credits['cast'][0]['name'] if credits['cast'] else "Unknown"
        star_var.set(main_star)

        # 🖼️ Poster
        poster_path = movie.get('poster_path')
        if poster_path:
            full_poster_path = poster_path
            poster_url = f"https://image.tmdb.org/t/p/w185{poster_path}"
            img_data = requests.get(poster_url).content
            
            global current_poster_data
            current_poster_data = img_data
            
            img = Image.open(io.BytesIO(img_data))
            
            # Resize image
            img = img.resize((120, 180), Image.Resampling.LANCZOS)
            poster_img = ImageTk.PhotoImage(img)
            poster_label.config(image=poster_img)
            poster_label.image = poster_img   # Prevents garbage collection
        else:
            poster_label.config(image='', text='No poster available')
            full_poster_path = None

        # ✅ Clear info label
        info_label.config(text='')

    else:
        if not silent:
            logging.info(f"No TMDb results for '{title}'")
        poster_label.config(image='', text='No poster available')
        poster_label.image = None
        info_label.config(text='Information not available at this time')

        if not poster_url:
            create_dummy_poster()
            info_label.config(text="No poster found. Showing placeholder.")
            return

# Input fields Rating input, Labels  GUI Begins
form_frame = tk.Frame(root, bg="#d0e7f9")    # bg="#d0e7f9")"blue"
form_frame.grid(row=0, column=0, columnspan=1, sticky="w", padx=10, pady=10)
form_frame.grid_columnconfigure(1, weight=1)

for i in range(5):  # Columns 0 to 4
    form_frame.grid_columnconfigure(i, weight=0, minsize=100)

# Entry Widgets and Labels   
tk.Label(form_frame, text="Title", bg="#d0e7f9").grid(row=0, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(form_frame, textvariable=title_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)   # TTK Entry Widgets Typ.

tk.Label(form_frame, text="Director", bg="#d0e7f9").grid(row=1, column=0, sticky="e", padx=5, pady=0)
ttk.Entry(form_frame, textvariable=director_var).grid(row=1, column=1, sticky="w", padx=5, pady=0)

tk.Label(form_frame, text="Year", bg="#d0e7f9").grid(row=2, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(form_frame, textvariable=year_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)

tk.Label(form_frame, text="Genre", bg="#d0e7f9").grid(row=3, column=0, sticky="e", padx=5, pady=0)
ttk.Entry(form_frame, textvariable=genre_var).grid(row=3, column=1, sticky="w", padx=5, pady=0)

tk.Label(form_frame, text="Main Star", bg="#d0e7f9").grid(row=4, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(form_frame, textvariable=star_var).grid(row=4, column=1, sticky="w", padx=5, pady=5)

tk.Label(form_frame, text="Your Rating", bg="#d0e7f9").grid(row=5, column=0, sticky="e", padx=5, pady=0)
ttk.Entry(form_frame, textvariable=rate_var).grid(row=5, column=1, sticky="w", padx=5, pady=0)

# 🎬 Buttons button_frame.configure(bg="#d0e7f9")
add_button = tk.Button(form_frame, text="Add Movie", width=12, command=add_movie, bg="#d0e7f9",activebackground="#b0d4ec")
add_button.grid(row=9, column=0, padx=(10,5), pady=(10,5))

tk.Button(form_frame, text="Save Movies", width=10,anchor="center", command=save_movies, bg="#d0e7f9").grid(row=9, column=1, sticky="ew", padx=(0,5), pady=(10,5))
tk.Button(form_frame, text="Load Movies", width=12, command=load_movies, bg="#d0e7f9").grid(row=9, column=2, sticky="ew", padx=(0,5), pady=(10,5))
tk.Button(form_frame, text="Delete A Movie", width=12, command=delete_selected_movie, bg="#d0e7f9").grid(row=9, column=3, sticky="w", padx=(0,5), pady=(10,5))
tk.Button(form_frame, text="Edit Movie", width=12, command=edit_movie, bg="#d0e7f9").grid(row=9, column=4, sticky="w", padx=(0,0), pady=(10,5))

# Create Poster Label Display...
poster_frame = tk.Frame(root, width=120, height=260, bg="#d0e7f9")
poster_frame.grid(row=0, column=1, padx=0, pady=5)
poster_frame.grid_propagate(False)  # Prevent resizing base on contentsw

# Poster label inside poster_frame.
def on_mouse_enter(event):
    print("🖱️ Mouse entered poster zone")
    
poster_label = tk.Label(
    poster_frame,
    bg="#d0e7f9",
    bd=2,
    relief="ridge",
    width=120,
    height=220,
    anchor="center"
)
poster_label.grid(row=1, column=0, sticky="nsew")
poster_label.bind("<Button-1>", lambda e: open_full_poster(poster_label.current_path))
poster_label.bind("<Enter>", on_mouse_enter)

# TMDb button inside poster_frame (NOT inside poster_label)
tmdb_button = tk.Button(poster_frame, text="Search TMDb", command=search_tmdb, bg="#d0e7f9")
tmdb_button.grid(row=0, column=0, padx=5, pady=(10, 5), sticky="n")
poster_frame.grid_rowconfigure(0, weight=0)  # TMDb button stays fixed
poster_frame.grid_rowconfigure(1, weight=1)  # Poster label can expand
poster_frame.grid_columnconfigure(0, weight=1)

## poster_label.config(width=120, height=180)
info_label = tk.Label(root, text="", fg="#333333", font=("Arial", 10, "italic"), bg="#d0e7f9")
info_label.grid(row=1, column=1, rowspan=1, columnspan=1, padx= 50, pady=0)
info_label.config(text="Please enter a movie title before searching.")
poster_label.bind("<Enter>", show_tooltip)
poster_label.bind("<Leave>", hide_tooltip)

# The search frame and buttons...
search_frame = tk.Frame(root, bg="#d0e7f9")  ##d0e7f9  blue
search_frame.grid(row=1, column=0, columnspan=3, sticky="w", padx=(225,0), pady=(5,0))
root.grid_columnconfigure(1, weight=0)

# Label on far left
tk.Label(search_frame, text="Search", bg="#d0e7f9").grid(row=0, column=0, padx=(0,5), pady=(0,0), sticky = "w")

# Search Button
tk.Button(search_frame, text="Search", command=search_movies, bg="#d0e7f9").grid(row=0, column=1, padx=(0,5), pady=(0,0))

# Search Entry box
ttk.Entry(search_frame, textvariable=search_var, width=30).grid(row=0, column=2, padx=(0,5), pady=(0,0))

# Clear search button
tk.Button(search_frame, text="Clear Search", command=clear_search, bg="#d0e7f9").grid(row=0, column=3, padx=(0,5), pady=5)

# Create a header frame near the top
header_frame = tk.Frame(root, bg="#d0e7f9")  # "green" or "#d0e7f9" for consistency
header_frame.grid(row=0, column=0, columnspan=2, sticky="wn", padx=(300,0), pady=(10, 0))

# About button
about_button = tk.Button(header_frame, text="About", bg="#d0e7f9", command=show_about)
about_button.pack(side="left", padx=10, pady=(5,0))

# Email Feedback button
feedback_button = tk.Button(header_frame, text="Email Feedback", command=send_feedback_email, bg="#d0e7f9", fg="#003366")
feedback_button.pack(side="left", padx=10, pady=(5,0))

# Row 6: Sort Frame, Sort Button and OptionMenu
sort_frame = tk.Frame(root, bg="#d0e7f9")  # Match your app’s background      #d0e7f9   blue
sort_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=(30, 0), pady=(20, 20))
sort_var = tk.StringVar(value="title")

# Sort Label (optional for clarity)
tk.Label(
    sort_frame,
    text="Sort by:",
    bg="#d0e7f9",
    font=("Arial", 10)
).grid(row=0, column=0, padx=(0, 5), pady=(0, 0), sticky="w")

# Option Menu: Sort Drop Down Menu
option_menu = tk.OptionMenu(sort_frame, sort_var, "title", "year", "rate", "genre")
option_menu.config(
    bg="#FFFFFF",
    fg="#000000",
    activebackground="#d0e7f9",
    highlightthickness=0,
    bd=0,
    font=("Arial", 10)
)

# Option Menu, sort button: 
option_menu.grid(row=0, column=1, padx=(0, 10), pady=(0, 0), sticky="e")
tk.Button(
    sort_frame,
    text="Sort",
    bg="#d0e7f9",
    font=("Arial", 10),
    command=lambda: sort_movies(sort_var.get())
).grid(row=0, column=2, padx=(0, 5), pady=(0, 0), sticky="e")

# ******  Movie listbox display ****** With SortButton Shared Frame....
list_frame = tk.Frame(root, bg="#d0e7f9") 
list_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=(20,0), pady=(10, 0))

#List Box
movie_listbox = tk.Listbox(
    list_frame,
    width=70,
    height=10,
    font=("Segoe UI", 11),
    yscrollcommand=lambda *args: scrollbar.set(*args)
)
movie_listbox.grid(row=10, column=0)

#Scrollbar
scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=movie_listbox.yview)  # ✅ Correct
scrollbar.grid(row=10, column=2, sticky="nsew")
yscrollcommand=lambda *args: scrollbar.set(*args)
command=movie_listbox.yview

# Bind the movie_listbox to
movie_listbox.bind("<<ListboxSelect>>", on_movie_select)

# ✅ Now it's safe to load and populate
load_data()
populate_movie_listbox()

# 🏁 Start the GUI loop
root.configure(bg="#d0e7f9") # Light Blue
root.mainloop()











