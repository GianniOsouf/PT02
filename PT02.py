import tkinter as tk
import serial
import threading

ser = serial.Serial('COM3', 9600)  # adapte le port à ton système

class Interface:
    def __init__(self, root):

        self.root = root
        self.root.title("PT02")

        self.ecart = 0
        self.distG = 0
        self.distD = 0
        self.engage = False
        self.manual_angle = 90
        self.manual_active = False
        self.retour_timer = None
        self.mode_auto = tk.BooleanVar(value=True)

        # Zone de saisie
        tk.Label(root, text="Ecart entre les capteurs (cm) :").pack()
        self.ecart_entry = tk.Entry(root)
        self.ecart_entry.pack()

        # Switch auto/manuel
        self.switch = tk.Checkbutton(root, text="Mode automatique", variable=self.mode_auto, command=self.toggle_mode)
        self.switch.pack()

        # Bouton engager
        self.engager_btn = tk.Button(root, text="Engager", command=self.engager, state=tk.DISABLED)
        self.engager_btn.pack()

        # Statut
        self.status_label = tk.Label(root, text="Statut : Attente")
        self.status_label.pack()

        # Barre led
        self.jauge_frame = tk.Frame(root)
        self.jauge_frame.pack(pady=10)

        self.jauge_labels = []
        for i in range(9):
            lbl = tk.Label(self.jauge_frame, width=2, height=1, bg="lightgray", relief="ridge")
            lbl.grid(row=0, column=i, padx=2)
            self.jauge_labels.append(lbl)


        # Boutons manuels
        self.manual_frame = tk.Frame(root)
        self.manual_frame.pack()

        self.btn_gauche = tk.Button(self.manual_frame, text="⬅ Gauche", width=10)
        self.btn_gauche.grid(row=0, column=0, padx=5)

        self.btn_droite = tk.Button(self.manual_frame, text="Droite ➡", width=10)
        self.btn_droite.grid(row=0, column=1, padx=5)

        self.btn_gauche.bind("<ButtonPress>", self.hold_gauche)
        self.btn_gauche.bind("<ButtonRelease>", self.stop_manual)

        self.btn_droite.bind("<ButtonPress>", self.hold_droite)
        self.btn_droite.bind("<ButtonRelease>", self.stop_manual)


        self.root.bind("<ButtonRelease>", self.stop_manual)

        threading.Thread(target=self.lire_serial, daemon=True).start()

        with open("version.txt", "r") as f:
            version = f.read().strip()

        self.version_label = tk.Label(root, text=f"Version : {version}", fg="gray")
        self.version_label.pack()

    def toggle_mode(self):
        if self.mode_auto.get():
            self.status_label.config(text="Mode automatique activé")
        else:
            self.status_label.config(text="Mode manuel activé")
            self.engage = False

    def lire_serial(self):
        while True:
            ligne = ser.readline().decode().strip()
            if ligne.startswith("G:"):
                try:
                    parts = ligne.split(";")
                    self.distG = int(parts[0].split(":")[1])
                    self.distD = int(parts[1].split(":")[1])
                    self.verifier_conditions()
                except:
                    pass

    def verifier_conditions(self):
        try:
            self.ecart = int(self.ecart_entry.get())
        except:
            self.status_label.config(text="Erreur : saisie invalide")
            self.engager_btn.config(state=tk.DISABLED)
            return

        if self.distG < self.ecart and self.distD < self.ecart and self.mode_auto.get():
            self.engager_btn.config(state=tk.NORMAL)
            if self.engage:
                self.piloter_servo()
        else:
            self.engager_btn.config(state=tk.DISABLED)
            if self.engage:
                self.engage = False
                self.engager_btn.config(text="Engager")
                self.status_label.config(text="Erreur, reprenez le contrôle manuel")

    def engager(self):
        self.engage = not self.engage
        if self.engage:
            self.status_label.config(text="Statut : Engagé")
            self.engager_btn.config(text="Désengager")
            self.piloter_servo()
        else:
            self.status_label.config(text="Statut : Désengagé")
            self.engager_btn.config(text="Engager")

    def calculer_position_servo(self):
        try:
            delta = self.distD - self.distG
            position = ((delta / self.ecart) * 90) + 90
            return max(0, min(180, int(position)))
        except ZeroDivisionError:
            return 90

    def piloter_servo(self):
        position = self.calculer_position_servo()
        ser.write(f"{position}\n".encode())

        if position < 90:
            self.update_jauge()
        elif position > 90:
            self.update_jauge()
        else:
            self.update_jauge()

    def update_jauge(self):
        for lbl in self.jauge_labels:
            lbl.config(bg="lightgray")

        if not self.engage:
            return

        position = self.calculer_position_servo()
        index = 4  # centre

        if position < 90:
            index = max(0, 4 - int((90 - position) / 10))
        elif position > 90:
            index = min(8, 4 + int((position - 90) / 10))
        self.jauge_labels[index].config(bg="green")


    def start_gauche(self):
        self.engage = False
        self.manual_active = True
        self.status_label.config(text="Désengagé (manuel gauche)")
        self.manual_angle = max(0, self.manual_angle - 5)
        ser.write(f"{self.manual_angle}\n".encode())
        self.schedule_return()

    def start_droite(self):
        self.engage = False
        self.manual_active = True
        self.status_label.config(text="Désengagé (manuel droite)")
        self.manual_angle = min(180, self.manual_angle + 5)
        ser.write(f"{self.manual_angle}\n".encode())
        self.schedule_return()

    def stop_manual(self, event=None):
        self.manual_active = False
        self.status_label.config(text="Retour automatique vers 90°")
        self.schedule_return()

    def schedule_return(self):
        if self.retour_timer:
            self.root.after_cancel(self.retour_timer)
        self.retour_timer = self.root.after(200, self.retourner_servo)

    def retourner_servo(self):
        if not self.manual_active and self.manual_angle != 90:
            if self.manual_angle > 90:
                self.manual_angle -= 5
            elif self.manual_angle < 90:
                self.manual_angle += 5
            ser.write(f"{self.manual_angle}\n".encode())
            self.schedule_return()

    def hold_gauche(self, event=None):
        self.engage = False
        self.manual_active = True
        self.status_label.config(text="Désengagé (manuel gauche)")
        self.move_servo_continuous(-5)

    def hold_droite(self, event=None):
        self.engage = False
        self.manual_active = True
        self.status_label.config(text="Désengagé (manuel droite)")
        self.move_servo_continuous(5)

    def move_servo_continuous(self, step):
        if not self.manual_active:
            return
        self.manual_angle = max(0, min(180, self.manual_angle + step))
        ser.write(f"{self.manual_angle}\n".encode())
        self.root.after(200, lambda: self.move_servo_continuous(step))


root = tk.Tk()
app = Interface(root)
root.mainloop()
if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()

