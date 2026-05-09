"""
World Explorer Data App
CodeLab II - Assessment 2

A Tkinter app using the REST Countries API to search, compare,
save and display country information.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from io import BytesIO
import webbrowser

import requests
from PIL import Image, ImageTk


BASE_URL = "https://restcountries.com/v3.1"

# Coffee / camel colour theme
BG = "#D6C2A8"              # camel beige
CARD = "#4A3426"            # coffee brown
TEXT = "#2F241C"            # espresso text
CREAM = "#F8F1E7"           # cream text
MUTED = "#6F5B4B"           # soft brown-grey
ACCENT = "#A86F4C"          # soft copper
ACCENT_HOVER = "#C08A5A"    # lighter copper

search_history = []
favourites = []
current_country = None
current_flag_image = None


# ---------------- BASIC HELPERS ----------------

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def show_frame(frame):
    frame.tkraise()


def make_label(parent, text, size=12, bold=False, bg=BG, fg=TEXT, pady=4, wrap=None):
    font = ("Arial", size, "bold") if bold else ("Arial", size)
    label = tk.Label(parent, text=text, font=font, bg=bg, fg=fg,
                     wraplength=wrap, justify="center")
    label.pack(pady=pady)
    return label


def make_title(parent, title, subtitle=""):
    make_label(parent, title, size=30, bold=True, pady=(25, 5))
    if subtitle:
        make_label(parent, subtitle, size=12, fg=MUTED, pady=(0, 10), wrap=760)


def create_planet_logo(parent):
    """Creates a small planet-style drawing for the welcome page."""
    canvas = tk.Canvas(parent, width=62, height=62, bg=BG, highlightthickness=0)
    canvas.create_oval(8, 8, 54, 54, fill="#6A8EAE", outline=TEXT, width=2)
    canvas.create_arc(5, 19, 57, 44, start=15, extent=150, outline=CREAM, width=2)
    canvas.create_arc(5, 19, 57, 44, start=195, extent=150, outline=CREAM, width=2)
    canvas.create_oval(20, 18, 29, 27, fill="#7A8B58", outline="")
    canvas.create_oval(34, 32, 45, 43, fill="#7A8B58", outline="")
    canvas.create_oval(29, 12, 40, 20, fill="#7A8B58", outline="")
    return canvas


def get_api_data(url):
    try:
        response = requests.get(url, timeout=8)

        if response.status_code == 404:
            messagebox.showerror("No Results", "No country data was found. Try another search.")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error", "Please check your internet connection.")
    except requests.exceptions.Timeout:
        messagebox.showerror("Timeout Error", "The request took too long. Try again.")
    except requests.exceptions.RequestException:
        messagebox.showerror("API Error", "Something went wrong while loading the data.")

    return None


def add_to_history(text):
    if text not in search_history:
        search_history.insert(0, text)

    if len(search_history) > 10:
        search_history.pop()

    update_history_page()


def format_languages(languages):
    return ", ".join(languages.values()) if languages else "Not available"


def format_currencies(currencies):
    if not currencies:
        return "Not available"

    items = []
    for code, details in currencies.items():
        name = details.get("name", "Unknown")
        symbol = details.get("symbol", "")
        items.append(f"{name} ({code}) {symbol}")

    return ", ".join(items)


# ---------------- SEARCH FUNCTION ----------------

def search_countries():
    search_type = search_type_box.get()
    user_input = search_entry.get().strip()

    if not search_type:
        messagebox.showwarning("Input Needed", "Please choose a search option.")
        return

    if not user_input:
        messagebox.showwarning("Input Needed", "Please type something to search.")
        return

    if search_type.startswith("🌍"):
        url = f"{BASE_URL}/name/{user_input}"
        history_text = f"Name search: {user_input}"
        title = "Search Results"

    elif search_type.startswith("🧭"):
        region = user_input.title()
        url = f"{BASE_URL}/region/{region}"
        history_text = f"Region search: {region}"
        title = f"Countries in {region}"

    elif search_type.startswith("💱"):
        currency = user_input.upper()
        url = f"{BASE_URL}/currency/{currency}"
        history_text = f"Currency search: {currency}"
        title = f"Countries using {currency}"

    elif search_type.startswith("🗣"):
        language = user_input.lower()
        url = f"{BASE_URL}/lang/{language}"
        history_text = f"Language search: {language}"
        title = f"Countries using {language}"

    else:
        messagebox.showerror("Search Error", "Invalid search option selected.")
        return

    data = get_api_data(url)

    if data:
        add_to_history(history_text)
        show_results(data, title)


def clear_search_inputs():
    search_entry.delete(0, tk.END)
    search_type_box.set("")


# ---------------- RESULTS FUNCTIONS ----------------

def show_results(countries, title):
    """Shows the country result list."""
    global current_country

    current_country = None
    clear_frame(result_list_frame)
    clear_frame(details_frame)

    results_title.config(text=title)

    tk.Label(
        result_list_frame,
        text="Pick a country",
        font=("Arial", 13, "bold"),
        bg=CARD,
        fg=ACCENT
    ).pack(pady=(5, 8))

    # Extra navigation so the user does not feel stuck on the results page
    nav_buttons = tk.Frame(result_list_frame, bg=CARD)
    nav_buttons.pack(pady=(0, 8))

    ttk.Button(
        nav_buttons,
        text="Back",
        width=10,
        command=lambda: show_frame(search_frame)
    ).grid(row=0, column=0, padx=3)

    ttk.Button(
        nav_buttons,
        text="Menu",
        width=10,
        command=lambda: show_frame(menu_frame)
    ).grid(row=0, column=1, padx=3)

    countries = sorted(countries, key=lambda c: c.get("name", {}).get("common", ""))

    for country in countries[:25]:
        name = country.get("name", {}).get("common", "Unknown")

        ttk.Button(
            result_list_frame,
            text=name,
            width=25,
            command=lambda selected=country: show_country_details(selected)
        ).pack(pady=3)

    if len(countries) > 25:
        tk.Label(
            result_list_frame,
            text="Only first 25 results shown",
            bg=CARD,
            fg=CREAM,
            font=("Arial", 9)
        ).pack(pady=8)

    tk.Label(
        details_frame,
        text="Select a country from the left to see its details.",
        font=("Arial", 14),
        bg=CARD,
        fg=CREAM,
        wraplength=520,
        justify="center"
    ).pack(expand=True)

    show_frame(results_frame)


def show_country_details(country):
    global current_country, current_flag_image

    current_country = country
    clear_frame(details_frame)

    name = country.get("name", {}).get("common", "Unknown")
    official = country.get("name", {}).get("official", "Not available")
    capital = ", ".join(country.get("capital", ["Not available"]))
    region = country.get("region", "Not available")
    subregion = country.get("subregion", "Not available")
    population = country.get("population", 0)
    area = country.get("area", 0)
    languages = format_languages(country.get("languages", {}))
    currencies = format_currencies(country.get("currencies", {}))
    timezones = ", ".join(country.get("timezones", ["Not available"]))
    maps_link = country.get("maps", {}).get("googleMaps", "")

    density = f"{population / area:.2f} people/km²" if area else "Not available"

    tk.Label(
        details_frame,
        text=name,
        font=("Arial", 24, "bold"),
        bg=CARD,
        fg=ACCENT
    ).pack(pady=(5, 8))

    flag_url = country.get("flags", {}).get("png")
    flag_emoji = country.get("flag", "🏳️")

    if flag_url:
        try:
            flag_response = requests.get(flag_url, timeout=8)
            flag_response.raise_for_status()

            image = Image.open(BytesIO(flag_response.content))
            image.thumbnail((180, 110))
            current_flag_image = ImageTk.PhotoImage(image)

            tk.Label(
                details_frame,
                image=current_flag_image,
                bg=CARD
            ).pack(pady=5)

        except Exception:
            tk.Label(
                details_frame,
                text=f"{flag_emoji}\nFlag image unavailable",
                font=("Arial", 14),
                bg=CARD,
                fg=CREAM,
                justify="center"
            ).pack(pady=5)
    else:
        tk.Label(
            details_frame,
            text=f"{flag_emoji}\nFlag image unavailable",
            font=("Arial", 14),
            bg=CARD,
            fg=CREAM,
            justify="center"
        ).pack(pady=5)

    details = (
        f"Official Name: {official}\n"
        f"Capital: {capital}\n"
        f"Region: {region}\n"
        f"Subregion: {subregion}\n\n"
        f"Population: {population:,}\n"
        f"Area: {area:,} km²\n"
        f"Density: {density}\n\n"
        f"Languages: {languages}\n"
        f"Currencies: {currencies}\n"
        f"Timezones: {timezones}"
    )

    tk.Label(
        details_frame,
        text=details,
        font=("Arial", 12),
        bg=CARD,
        fg=CREAM,
        justify="left",
        wraplength=620
    ).pack(pady=10, anchor="w")

    button_area = tk.Frame(details_frame, bg=CARD)
    button_area.pack(pady=6)

    ttk.Button(
        button_area,
        text="Add to Favourites",
        command=add_to_favourites
    ).grid(row=0, column=0, padx=6)

    if maps_link:
        ttk.Button(
            button_area,
            text="Open Map",
            command=lambda: webbrowser.open(maps_link)
        ).grid(row=0, column=1, padx=6)


# ---------------- FAVOURITES FUNCTIONS ----------------

def add_to_favourites():
    if current_country is None:
        messagebox.showwarning("No Country Selected", "Open a country first before saving it.")
        return

    name = current_country.get("name", {}).get("common", "Unknown")

    for country in favourites:
        if country.get("name", {}).get("common", "") == name:
            messagebox.showinfo("Already Saved", "This country is already saved.")
            return

    favourites.append(current_country)
    update_favourites_page()
    messagebox.showinfo("Saved", f"{name} has been added to favourites.")


def remove_favourite(country_name):
    global favourites

    favourites = [
        country for country in favourites
        if country.get("name", {}).get("common", "") != country_name
    ]

    update_favourites_page()


def open_favourite(country):
    show_results([country], "Favourite Country")
    show_country_details(country)


def update_favourites_page():
    clear_frame(favourites_list_frame)

    if not favourites:
        make_label(
            favourites_list_frame,
            "No favourites yet.\nSearch a country, open it, then save it here.",
            size=13,
            pady=40
        )
        return

    for country in favourites:
        name = country.get("name", {}).get("common", "Unknown")

        row = tk.Frame(favourites_list_frame, bg=BG)
        row.pack(fill="x", pady=6)

        tk.Label(
            row,
            text=name,
            width=32,
            anchor="w",
            bg=BG,
            fg=TEXT,
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=8)

        ttk.Button(
            row,
            text="View",
            command=lambda c=country: open_favourite(c)
        ).pack(side="left", padx=5)

        ttk.Button(
            row,
            text="Remove",
            command=lambda n=name: remove_favourite(n)
        ).pack(side="left", padx=5)


# ---------------- HISTORY FUNCTIONS ----------------

def update_history_page():
    clear_frame(history_list_frame)

    if not search_history:
        make_label(
            history_list_frame,
            "No searches yet.\nYour recent searches will appear here.",
            size=13,
            pady=40
        )
        return

    for number, item in enumerate(search_history, start=1):
        tk.Label(
            history_list_frame,
            text=f"{number}. {item}",
            bg=BG,
            fg=TEXT,
            font=("Arial", 12),
            anchor="w",
            padx=10,
            pady=6
        ).pack(fill="x", pady=3)


# ---------------- COMPARE FUNCTIONS ----------------

def compare_countries():
    first = compare_entry_1.get().strip()
    second = compare_entry_2.get().strip()

    if not first or not second:
        messagebox.showwarning("Input Needed", "Please enter both country names.")
        return

    first_data = get_api_data(f"{BASE_URL}/name/{first}?fullText=true")
    second_data = get_api_data(f"{BASE_URL}/name/{second}?fullText=true")

    if first_data and second_data:
        add_to_history(f"Compared: {first} and {second}")
        show_comparison(first_data[0], second_data[0])


def show_comparison(country_one, country_two):
    clear_frame(compare_output_frame)

    make_compare_card(country_one).grid(row=0, column=0, padx=15, sticky="nsew")
    make_compare_card(country_two).grid(row=0, column=1, padx=15, sticky="nsew")

    compare_output_frame.grid_columnconfigure(0, weight=1)
    compare_output_frame.grid_columnconfigure(1, weight=1)


def make_compare_card(country):
    card = tk.Frame(compare_output_frame, bg=CARD, padx=18, pady=18)

    name = country.get("name", {}).get("common", "Unknown")
    capital = ", ".join(country.get("capital", ["Not available"]))
    region = country.get("region", "Not available")
    population = country.get("population", 0)
    area = country.get("area", 0)
    languages = format_languages(country.get("languages", {}))
    currencies = format_currencies(country.get("currencies", {}))
    density = f"{population / area:.2f} people/km²" if area else "Not available"

    tk.Label(
        card,
        text=name,
        font=("Arial", 20, "bold"),
        bg=CARD,
        fg=ACCENT
    ).pack(pady=5)

    text = (
        f"Capital: {capital}\n"
        f"Region: {region}\n"
        f"Population: {population:,}\n"
        f"Area: {area:,} km²\n"
        f"Density: {density}\n"
        f"Languages: {languages}\n"
        f"Currencies: {currencies}"
    )

    tk.Label(
        card,
        text=text,
        font=("Arial", 11),
        bg=CARD,
        fg=CREAM,
        justify="left",
        wraplength=390
    ).pack(anchor="w", pady=8)

    return card


# ---------------- GUI SETUP ----------------

root = tk.Tk()
root.title("World Explorer Data App")
root.geometry("1000x680")
root.minsize(900, 620)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TButton",
    font=("Arial", 11, "bold"),
    padding=8,
    background=ACCENT,
    foreground="white",
    borderwidth=0
)

style.map(
    "TButton",
    background=[("active", ACCENT_HOVER)],
    foreground=[("active", "white")]
)

style.configure(
    "Menu.TButton",
    font=("Arial", 12, "bold"),
    padding=10,
    background=ACCENT,
    foreground="white",
    borderwidth=0
)

style.map(
    "Menu.TButton",
    background=[("active", ACCENT_HOVER)],
    foreground=[("active", "white")]
)

style.configure(
    "TCombobox",
    font=("Arial", 11),
    padding=5
)

container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True)

welcome_frame = tk.Frame(container, bg=BG)
menu_frame = tk.Frame(container, bg=BG)
search_frame = tk.Frame(container, bg=BG)
results_frame = tk.Frame(container, bg=BG)
compare_frame = tk.Frame(container, bg=BG)
favourites_frame = tk.Frame(container, bg=BG)
history_frame = tk.Frame(container, bg=BG)

for frame in (
    welcome_frame,
    menu_frame,
    search_frame,
    results_frame,
    compare_frame,
    favourites_frame,
    history_frame
):
    frame.grid(row=0, column=0, sticky="nsew")

container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)


# ---------------- WELCOME PAGE ----------------

welcome_box = tk.Frame(welcome_frame, bg=BG)
welcome_box.pack(expand=True)

title_row = tk.Frame(welcome_box, bg=BG)
title_row.pack(pady=(10, 4))

create_planet_logo(title_row).pack(side="left", padx=(0, 14))

tk.Label(
    title_row,
    text="World Explorer",
    font=("Arial", 44, "bold"),
    bg=BG,
    fg=TEXT
).pack(side="left")

make_label(welcome_box, "Country data made simple.", size=15, fg=MUTED, pady=5)

make_label(
    welcome_box,
    '"The world is wide, and every country has a story."',
    size=12,
    fg=TEXT,
    pady=18
)

welcome_buttons = tk.Frame(welcome_box, bg=BG)
welcome_buttons.pack(pady=12)

ttk.Button(
    welcome_buttons,
    text="Start Searching",
    width=20,
    style="Menu.TButton",
    command=lambda: show_frame(search_frame)
).grid(row=0, column=0, padx=8)

ttk.Button(
    welcome_buttons,
    text="Main Menu",
    width=20,
    style="Menu.TButton",
    command=lambda: show_frame(menu_frame)
).grid(row=0, column=1, padx=8)

make_label(welcome_box, "Search by name • region • currency • language", size=11, fg=MUTED, pady=12)


# ---------------- MAIN MENU PAGE ----------------

make_title(menu_frame, "Main Menu", "Choose what you want to do with the country data.")

menu_area = tk.Frame(menu_frame, bg=BG)
menu_area.pack(pady=25)

for text, frame in [
    ("Search Countries", search_frame),
    ("Compare Countries", compare_frame),
    ("View Favourites", favourites_frame),
    ("View Search History", history_frame)
]:
    ttk.Button(
        menu_area,
        text=text,
        width=28,
        style="Menu.TButton",
        command=lambda f=frame: show_frame(f)
    ).pack(pady=8)

make_label(
    menu_frame,
    "Tip: Use the search page to explore countries by different data types.",
    size=11,
    fg=MUTED,
    pady=12
)


# ---------------- SEARCH PAGE ----------------

make_title(search_frame, "Search Countries", "Choose a search type, then enter your search value.")

search_area = tk.Frame(search_frame, bg=BG)
search_area.pack(pady=20)

tk.Label(
    search_area,
    text="Search Type",
    bg=BG,
    fg=TEXT,
    font=("Arial", 12, "bold")
).grid(row=0, column=0, pady=10, padx=8, sticky="w")

search_type_box = ttk.Combobox(
    search_area,
    values=["🌍 Country Name", "🧭 Region", "💱 Currency Code", "🗣 Language Code"],
    state="readonly",
    width=28
)
search_type_box.grid(row=0, column=1, padx=10)

tk.Label(
    search_area,
    text="Search Value",
    bg=BG,
    fg=TEXT,
    font=("Arial", 12, "bold")
).grid(row=1, column=0, pady=10, padx=8, sticky="w")

search_entry = tk.Entry(search_area, width=31, font=("Arial", 12))
search_entry.grid(row=1, column=1, padx=10)

ttk.Button(
    search_area,
    text="Search",
    width=15,
    command=search_countries
).grid(row=0, column=2, rowspan=2, padx=12)

make_label(search_frame, "Examples: Japan | Asia | AED | eng", size=11, fg=MUTED, pady=8)

search_buttons = tk.Frame(search_frame, bg=BG)
search_buttons.pack(pady=8)

ttk.Button(
    search_buttons,
    text="Clear",
    width=14,
    command=clear_search_inputs
).grid(row=0, column=0, padx=6)

ttk.Button(
    search_buttons,
    text="Main Menu",
    width=16,
    command=lambda: show_frame(menu_frame)
).grid(row=0, column=1, padx=6)


# ---------------- RESULTS PAGE ----------------

results_title = tk.Label(
    results_frame,
    text="Results",
    font=("Arial", 27, "bold"),
    bg=BG,
    fg=TEXT
)
results_title.pack(pady=16)

results_area = tk.Frame(results_frame, bg=BG)
results_area.pack(fill="both", expand=True, padx=25, pady=10)

result_list_frame = tk.Frame(results_area, bg=CARD, padx=12, pady=12)
result_list_frame.pack(side="left", fill="y", padx=10)

details_frame = tk.Frame(results_area, bg=CARD, padx=20, pady=20)
details_frame.pack(side="right", fill="both", expand=True, padx=10)

bottom_buttons = tk.Frame(results_frame, bg=BG)
bottom_buttons.pack(pady=8)

ttk.Button(
    bottom_buttons,
    text="Back to Search",
    command=lambda: show_frame(search_frame)
).grid(row=0, column=0, padx=6)

ttk.Button(
    bottom_buttons,
    text="Main Menu",
    command=lambda: show_frame(menu_frame)
).grid(row=0, column=1, padx=6)


# ---------------- COMPARE PAGE ----------------

make_title(compare_frame, "Compare Countries", "Enter two full country names to compare them side by side.")

compare_input = tk.Frame(compare_frame, bg=BG)
compare_input.pack(pady=15)

tk.Label(
    compare_input,
    text="First Country",
    bg=BG,
    fg=TEXT,
    font=("Arial", 12, "bold")
).grid(row=0, column=0, padx=6)

compare_entry_1 = tk.Entry(compare_input, width=24, font=("Arial", 12))
compare_entry_1.grid(row=0, column=1, padx=8)

tk.Label(
    compare_input,
    text="Second Country",
    bg=BG,
    fg=TEXT,
    font=("Arial", 12, "bold")
).grid(row=0, column=2, padx=6)

compare_entry_2 = tk.Entry(compare_input, width=24, font=("Arial", 12))
compare_entry_2.grid(row=0, column=3, padx=8)

ttk.Button(
    compare_input,
    text="Compare",
    command=compare_countries
).grid(row=0, column=4, padx=8)

make_label(compare_frame, "Example: India and United Arab Emirates", size=11, fg=MUTED, pady=5)

compare_output_frame = tk.Frame(compare_frame, bg=BG)
compare_output_frame.pack(fill="both", expand=True, padx=30, pady=15)

ttk.Button(
    compare_frame,
    text="Main Menu",
    width=16,
    command=lambda: show_frame(menu_frame)
).pack(pady=8)


# ---------------- FAVOURITES PAGE ----------------

make_title(favourites_frame, "Favourite Countries", "Saved countries will appear here while the app is open.")

favourites_list_frame = tk.Frame(favourites_frame, bg=BG)
favourites_list_frame.pack(fill="both", expand=True, padx=70, pady=20)

ttk.Button(
    favourites_frame,
    text="Main Menu",
    width=16,
    command=lambda: show_frame(menu_frame)
).pack(pady=10)


# ---------------- HISTORY PAGE ----------------

make_title(history_frame, "Search History", "Your latest 10 searches and comparisons are shown here.")

history_list_frame = tk.Frame(history_frame, bg=BG)
history_list_frame.pack(fill="both", expand=True, padx=70, pady=20)

ttk.Button(
    history_frame,
    text="Main Menu",
    width=16,
    command=lambda: show_frame(menu_frame)
).pack(pady=10)


update_favourites_page()
update_history_page()
show_frame(welcome_frame)

root.mainloop()