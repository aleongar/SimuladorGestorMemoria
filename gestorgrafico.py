import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import platform
import gestormemoria as gm #modulo gestor

class MemoryManagerGUI:
    """Clase que gestiona la interfaz gráfica del programa gestor de memoria
    """
    def __init__(self, root):
        """Constructor de la clase, añade el widget base.

        Args:
            root (Tk): Widget base de la interfaz
        """
        self.root = root
        self.root.title("Gestor de Memoria")
        self.process_line = None
        self.process_queue = []
        self.simulation_running = False
        self.sleep_seconds = 1  # Default sleep time

        # Widgets principales
        self.createWidgets()

    def createWidgets(self):
        """Método que crea los widgets de la interfaz y le aplica estilos.
        """
        self.root.call("source", "theme/equilux/equilux.tcl")
        style = ttk.Style().theme_use('equilux')
        self.root.configure(bg="#464646")
        # Panel superior
        frame_top = ttk.Frame(self.root, padding=10)
        frame_top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frame_top, text="Método de Asignación:").pack(side=tk.LEFT, padx=5)

        self.method_var = tk.StringVar(value="Mejor Hueco")
        self.method_dropdown = ttk.Combobox(frame_top, textvariable=self.method_var, state="readonly")
        self.method_dropdown["values"] = ["Mejor Hueco", "Peor Hueco"]
        self.method_dropdown.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(frame_top, text="Cargar Procesos", command=self.loadProcesses)
        self.load_button.pack(side=tk.LEFT, padx=5)

        ttk.Label(frame_top, text="Espera:").pack(side=tk.LEFT, padx=5)

        self.sleep_entry = ttk.Entry(frame_top, width=5)
        self.sleep_entry.insert(0, "1")  # Default value
        self.sleep_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = ttk.Button(frame_top, text="Iniciar Simulación", command=self.startSimulation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.start_button["state"] = "disabled"

        self.stop_button = ttk.Button(frame_top, text="Detener Simulación", command=self.stopSimulation)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button["state"] = "disabled"

        # Tabla de procesos
        self.tree = ttk.Treeview(self.root, columns=("ID", "Memoria", "Posición", "Duración"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Memoria", text="Memoria")
        self.tree.heading("Posición", text="Posición Inicial - Posición Final")
        self.tree.heading("Duración", text="Duración")
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Botón de salida
        self.exit_button = ttk.Button(self.root, text="Salir", command=self.root.quit)
        self.exit_button.pack(side=tk.BOTTOM, pady=10)

    def loadProcesses(self):
        """Carga los procesos que se cargan desde el sistema de archivos.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if not file_path:
            return
        try:
            self.resetSimulation()  # Limpia cualquier dato previo
            self.process_queue = gm.generateProcessFromFile(file_path)
            messagebox.showinfo("Carga Exitosa", f"Se cargaron {len(self.process_queue)} procesos.")
            self.start_button["state"] = "normal"
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

    def startSimulation(self):
        """Inicia la simulación. Crea la linea de procesos según los procesos cargados y establece el método de gestión de fragmentos

        Raises:
            ValueError: Cuando lee el valor para hacer el sleep, en caso de ser negativo este dará un error
        """
        if self.simulation_running:
            messagebox.showerror("Error", "La simulación ya está en curso.")
            return

        if not self.process_queue:
            messagebox.showerror("Error", "Primero carga los procesos.")
            return

        if self.process_line is None:
            # Inicializar según el método seleccionado
            method = self.method_var.get()
            if method == "Mejor Hueco":
                self.process_line = gm.ProcessLine(gm.BestFitSorting())
            elif method == "Peor Hueco":
                self.process_line = gm.ProcessLine(gm.WorstFitSorting())
            else:
                messagebox.showerror("Error", "Método de asignación no válido.")
                return
        try:
            self.sleep_seconds = float(self.sleep_entry.get())
            if self.sleep_seconds < 0:
                raise ValueError("El tiempo debe ser positivo.")
        except ValueError:
            messagebox.showerror("Error", "El tiempo de sleep debe ser un número positivo.")
            return

        self.simulation_running = True
        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"

        self.simulation_thread = threading.Thread(target=self.runSimulation, daemon=True)
        self.simulation_thread.start()

    def stopSimulation(self):
        """Detiene la simulación y establece los parámetros necesarios para su detención
        """
        self.simulation_running = False
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"

    def runSimulation(self):
        """Metodo que controla la actualización de la línea de procesos en cada intervalo de tiempo.
        Cuando termina anuncia con un mensaje, su finalización.
        En caso de error finaliza la simulación y anuncia el error
        """
        try:
            while (len(self.process_queue) > 0 or len(self.process_line.__buff__.processList) > 0 or not all(ps.process is None for ps in self.process_line.processList)) and self.simulation_running:
                ready_processes = gm.getProcessesToAdd(self.process_queue, self.process_line.__time__)
                self.process_line.update(processes=ready_processes)
                self.updateTree()
                if not self.simulation_running:
                    break
                threading.Event().wait(self.sleep_seconds)

            if self.simulation_running:
                messagebox.showinfo("Simulación Completa", "Todos los procesos se han ejecutado correctamente.")
                self.resetSimulation()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.simulation_running = False
            self.start_button["state"] = "normal"
            self.stop_button["state"] = "disabled"

    def updateTree(self):
        """Gestiona los elementos de la tabla
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        for page in self.process_line.processList:
            process = page.process
            if process:
                self.tree.insert("", tk.END, values=(
                    process.name,
                    process.memory,
                    f"{page.start_position} - {page.end_position}",
                    process.execTime
                ))

    def resetSimulation(self):
        """Reinicia la simulación, establece la linea de procesos y la cola de procesos a nulo y elimina todos los elementos visibles de la tabla
        """
        self.process_line = None #elimina la cola de procesos
        self.process_queue = []
        for item in self.tree.get_children():
            self.tree.delete(item) #Elimina cualquier dato en la tabla


if __name__ == "__main__":
    root = tk.Tk()
    gui = MemoryManagerGUI(root)
    root.mainloop()
