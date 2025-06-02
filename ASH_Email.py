import customtkinter as ctk
from tkinter import messagebox,PhotoImage
import threading
import os
import subprocess
import sys
import platform
from dotenv import load_dotenv, set_key
from PIL import Image
import asyncio
from Rapports_trimestriel_ASH import effectuer_rapport_ASH_async_limited

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ENV_FILE = resource_path(".env")

load_dotenv()

class ASHGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Envoi de Rapports ASH")
        self.geometry("400x350")
        self.grid_columnconfigure(0, weight=1)
        system = platform.system()
        if system == "Windows":
            icon_path = resource_path("assets/icon.ico")
            if os.path.exists(icon_path):
                try:
                    self.iconbitmap(icon_path)
                except Exception as e:
                    print(f"Windows icon load failed: {e}")
        else:  # macOS and Linux
            icon_path = resource_path("assets/icon_64x64.png")
            if os.path.exists(icon_path):
                try:
                    self.icon_img = PhotoImage(file=icon_path)
                    self.iconphoto(False, self.icon_img)
                except Exception as e:
                    print(f"Unix icon load failed: {e}")

        try:
            logo_path = resource_path(r"assets\\ASH.png")
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(100, 100))
            ctk.CTkLabel(self, image=logo_img, text="").pack(pady=(10, 0))
        except:
            pass

        ctk.CTkLabel(self, text="Envoi Automatisé des Rapports aide sociale", font=("Helvetica", 18)).pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=5)

        ctk.CTkButton(self, text="Envoyer les Rapports", command=self.threaded_launch_script).pack(pady=10)
        ctk.CTkButton(self, text="Ouvrir le Dossier 'Protégés'", command=self.open_proteges_folder).pack(pady=5)
        ctk.CTkButton(self, text="Paramètres", command=self.open_settings).pack(pady=5)

    def threaded_launch_script(self):
        threading.Thread(target=self.launch_script, daemon=True).start()

    def launch_script(self):
        def update_status(msg):
            self.status_label.configure(text=msg)

        self.status_label.configure(text="Envoi des rapports en cours...")
        try:
            asyncio.run(effectuer_rapport_ASH_async_limited(status_callback=update_status))
            self.status_label.configure(text="Rapports envoyés avec succès !")
            messagebox.showinfo("Succès", "Les rapports ont été envoyés avec succès !")
        except Exception as e:
            self.status_label.configure(text="Une erreur est survenue.")
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de l'envoi des rapports :\n{e}")

    def open_proteges_folder(self):
        folder_path = os.path.abspath("Protégés")
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier :\n{e}")

    def open_settings(self):
        SettingsWindow(self)

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Paramètres")
        self.geometry("400x300")
        self.grid_columnconfigure(1, weight=1)

        # Icon logic (unchanged)
        import platform
        if platform.system() == "Windows":
            self.iconbitmap(resource_path("assets/icon.ico"))
        else:
            self.icon_img = PhotoImage(file=resource_path("assets/icon_64x64.png"))
            self.iconphoto(False, self.icon_img)

        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()

        # --- Fields ---
        self.vars = {
            "email": ctk.StringVar(value=os.getenv("email")),
            "email_pwd": ctk.StringVar(value=os.getenv("email_pwd")),
            "NameSender": ctk.StringVar(value=os.getenv("NameSender")),
            "Role": ctk.StringVar(value=os.getenv("Role")),
        }

        labels = {
            "email": "Email",
            "email_pwd": "Mot de passe Email",
            "NameSender": "Nom de l'expéditeur",
            "Role": "Rôle",
        }

        self.pwd_entry = None  # to store reference
        self.show_pwd = False  # toggle state

        for i, (key, var) in enumerate(self.vars.items()):
            ctk.CTkLabel(self, text=labels[key]).grid(row=i, column=0, padx=10, pady=5, sticky="e")

            if key == "email_pwd":
                self.pwd_entry = ctk.CTkEntry(self, textvariable=var, show="*")
                self.pwd_entry.grid(row=i, column=1, padx=(10, 0), pady=5, sticky="ew")

                toggle_btn = ctk.CTkButton(self, text="👁", width=30, command=self.toggle_password)
                toggle_btn.grid(row=i, column=2, padx=(5, 10), pady=5)
            else:
                ctk.CTkEntry(self, textvariable=var).grid(
                    row=i, column=1, columnspan=2, padx=10, pady=5, sticky="ew"
                )

        ctk.CTkButton(self, text="Enregistrer", command=self.save_settings).grid(
            row=len(self.vars), column=0, columnspan=3, pady=15
        )

    def toggle_password(self):
        if self.pwd_entry:
            self.show_pwd = not self.show_pwd
            self.pwd_entry.configure(show="" if self.show_pwd else "*")

    def save_settings(self):
        for key, var in self.vars.items():
            set_key(ENV_FILE, key, var.get())
        messagebox.showinfo("Enregistré", "Paramètres enregistrés avec succès !")
        self.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ASHGUI()
    app.mainloop()
