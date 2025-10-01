import tkinter as tk
import serial
import threading

ser = serial.Serial('COM3', 9600)  # adapte le port à ton système

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Contrôle Servo par HC-SR04")

        self.ecart_label = tk.Label(root, text="Ecart entre les capteurs (cm) :")
        self.ecart_label.pack()

        self.ecart_entry = tk.Entry(root)
        self.ecart_entry.pack()

        self.status_label = tk.Label(root, text="Statut : Attente")
        self.status_label.pack()

        self.engager_btn = tk.Button(root, text="Engager", command=self.engager, state=tk.DISABLED)
        self.engager_btn.pack()

        self.engage = False
        self.ecart = 0
        self.distG = 0
        self.distD = 0

        self.direction_label = tk.Label(root, text="↕", font=("Arial", 40))
        self.direction_label.pack()



        threading.Thread(target=self.lire_serial, daemon=True).start()

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

        if self.distG < self.ecart and self.distD < self.ecart:
            self.engager_btn.config(state=tk.NORMAL)
            if self.engage:
                self.piloter_servo()
        else:
            self.engager_btn.config(state=tk.DISABLED)
            if self.engage:
                self.engage = False
                self.status_label.config(text="Erreur, reprenez le contrôle manuel")

    def engager(self):
        self.engage = True
        self.status_label.config(text="Statut : Engagé")
        self.piloter_servo()

    def piloter_servo(self):
        if self.distG > self.ecart or self.distD > self.ecart:
            self.engage = False
            self.status_label.config(text="Erreur, reprenez le contrôle manuel")
            return

        if self.distG == self.distD:
            ser.write(b'M')
            self.direction_label.config(text="↕")  # Flèche verticale
        elif self.distG < self.distD:
            ser.write(b'D')
            self.direction_label.config(text="➡")  # Flèche droite
        else:
            ser.write(b'C')
            self.direction_label.config(text="⬅")  # Flèche gauche


root = tk.Tk()
app = Interface(root)
root.mainloop()
