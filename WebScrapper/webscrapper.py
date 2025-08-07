import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk
import csv
import threading

def fetch_headlines():
    def task():
        url = url_entry.get().strip()
        if not url:
            status_label.config(text="Please enter a valid URL.", fg="red")
            return

        fetch_btn.config(state=tk.DISABLED)
        status_label.config(text="Fetching headlines...", fg="blue")
        display_box.delete("1.0", tk.END)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            headlines = []
            for tag in soup.find_all(['h1', 'h2', 'title']):
                text = tag.get_text(strip=True)
                if text and text not in headlines:
                    headlines.append(text)

            if headlines:
                for idx, headline in enumerate(headlines, start=1):
                    display_box.insert(tk.END, f"{idx}. {headline}\n")
                save_btn.config(state=tk.NORMAL)
                status_label.config(text=f"Found {len(headlines)} headlines!", fg="green")
            else:
                display_box.insert(tk.END, "No headlines found.")
                status_label.config(text="No headlines found.", fg="orange")
                save_btn.config(state=tk.DISABLED)

            global last_headlines
            last_headlines = headlines

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data:\n{str(e)}")
            status_label.config(text="Failed to fetch data.", fg="red")

        finally:
            fetch_btn.config(state=tk.NORMAL)

    threading.Thread(target=task).start()


def save_to_csv():
    if not last_headlines:
        messagebox.showinfo("Info", "No headlines to save.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                             filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Headline"])
            for headline in last_headlines:
                writer.writerow([headline])
        messagebox.showinfo("Saved", f"Headlines saved to {file_path}")

def change_theme(event):
    theme = theme_var.get()
    if theme == "Light":
        app.configure(bg="white")
        for widget in app.winfo_children():
            widget.configure(bg="white", fg="black")
        display_box.configure(bg="white", fg="black", insertbackground="black")
    else:
        app.configure(bg="#2e2e2e")
        for widget in app.winfo_children():
            if isinstance(widget, (tk.Label, tk.Entry, tk.Button, ttk.Combobox)):
                widget.configure(bg="#2e2e2e", fg="white")
        display_box.configure(bg="#1e1e1e", fg="white", insertbackground="white")

app = tk.Tk()
app.title("📰 News Headline Scraper")
app.geometry("700x600")
app.configure(bg="white")

top_frame = tk.Frame(app, bg="white")
top_frame.pack(pady=15)

tk.Label(top_frame, text="🔗 Enter News Website URL:", font=("Arial", 12), bg="white").grid(row=0, column=0, padx=5)
url_entry = tk.Entry(top_frame, width=50, font=("Arial", 12))
url_entry.grid(row=0, column=1, padx=5)

theme_var = tk.StringVar(value="Light")
theme_dropdown = ttk.Combobox(top_frame, textvariable=theme_var, values=["Light", "Dark"], width=10, state="readonly")
theme_dropdown.grid(row=0, column=2, padx=10)
theme_dropdown.bind("<<ComboboxSelected>>", change_theme)

fetch_btn = tk.Button(app, text="📡 Fetch Headlines", command=fetch_headlines, bg="#4CAF50", fg="white", font=("Arial", 11), width=20)
fetch_btn.pack(pady=10)

save_btn = tk.Button(app, text="💾 Save to CSV", command=save_to_csv, state=tk.DISABLED, bg="#2196F3", fg="white", font=("Arial", 11), width=20)
save_btn.pack()

display_box = scrolledtext.ScrolledText(app, width=80, height=20, font=("Arial", 10), wrap=tk.WORD)
display_box.pack(pady=10)

status_label = tk.Label(app, text="", font=("Arial", 10), bg="white")
status_label.pack()

last_headlines = []

app.mainloop()
