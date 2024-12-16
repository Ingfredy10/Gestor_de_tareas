import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Configuración de la base de datos (SQLite) ---
DATABASE_FILE = 'tareas.db' #Nombre del archivo de la base de datos
engine = create_engine(f'sqlite:///{DATABASE_FILE}')

Base = declarative_base()

class Tarea(Base):
    __tablename__ = 'tareas'

    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    descripcion = Column(String)
    estado = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# --- Funciones para la interfaz gráfica ---
def actualizar_lista_tareas():
    listbox_tareas.delete(0, tk.END)
    tareas = session.query(Tarea).all()
    for tarea in tareas:
        listbox_tareas.insert(tk.END, f"{tarea.titulo} ({tarea.estado})")

def agregar_tarea_gui():
    def agregar():
        titulo = entry_titulo.get()
        descripcion = entry_descripcion.get("1.0", tk.END).strip()
        if titulo and descripcion:
            nueva_tarea = Tarea(titulo=titulo, descripcion=descripcion, estado="pendiente")
            session.add(nueva_tarea)
            try:
                session.commit()
                actualizar_lista_tareas()
                ventana_agregar.destroy()
            except Exception as e: #Capturar cualquier error de base de datos
                session.rollback() #Revertir la transacción en caso de error.
                messagebox.showerror("Error", f"Error al agregar la tarea: {e}")
        else:
            messagebox.showwarning("Error", "Por favor ingresa un título y una descripción.")

    ventana_agregar = tk.Toplevel(ventana)
    ventana_agregar.title("Agregar Tarea")

    label_titulo = tk.Label(ventana_agregar, text="Título:")
    label_titulo.grid(row=0, column=0, padx=5, pady=5)
    entry_titulo = tk.Entry(ventana_agregar)
    entry_titulo.grid(row=0, column=1, padx=5, pady=5)

    label_descripcion = tk.Label(ventana_agregar, text="Descripción:")
    label_descripcion.grid(row=1, column=0, padx=5, pady=5)
    entry_descripcion = tk.Text(ventana_agregar, height=5)
    entry_descripcion.grid(row=1, column=1, padx=5, pady=5)

    boton_agregar = tk.Button(ventana_agregar, text="Agregar", command=agregar)
    boton_agregar.grid(row=2, column=1, pady=5)

def mostrar_detalles(indice, listbox):
    try:
        tarea = session.query(Tarea).all()[indice]
        messagebox.showinfo(
            tarea.titulo,
            f"Descripción: {tarea.descripcion}\nEstado: {tarea.estado}"
        )
    except IndexError:
        messagebox.showerror("Error", "No se ha seleccionado ninguna tarea.")

def crear_ventana_lista(titulo, comando):
    ventana_lista = tk.Toplevel(ventana)
    ventana_lista.title(titulo)

    listbox_tareas_lista = tk.Listbox(ventana_lista, width=50)
    listbox_tareas_lista.pack(padx=10, pady=10)
    
    tareas = session.query(Tarea).all()
    for tarea in tareas:
        listbox_tareas_lista.insert(tk.END, f"{tarea.titulo} ({tarea.estado})")

    if comando == "detalles":
        listbox_tareas_lista.bind("<Double-Button-1>", lambda event: mostrar_detalles(listbox_tareas_lista.curselection()[0],listbox_tareas_lista) if listbox_tareas_lista.curselection() else None)
    elif comando == "marcar" or comando == "eliminar":
        def ejecutar_accion():
            seleccion = listbox_tareas_lista.curselection()
            if seleccion:
                indice = seleccion[0]
                try:
                    tarea = session.query(Tarea).all()[indice]
                    if comando == "marcar":
                        tarea.estado = "completada"
                    elif comando == "eliminar":
                        session.delete(tarea)
                    session.commit()
                    actualizar_lista_tareas()
                    ventana_lista.destroy()
                except Exception as e:
                    session.rollback()
                    messagebox.showerror("Error", f"Error al realizar la acción: {e}")
            else:
                messagebox.showwarning("Error", "Selecciona una tarea de la lista.")
        boton_accion = tk.Button(ventana_lista, text=titulo, command=ejecutar_accion)
        boton_accion.pack()

    return ventana_lista

def listar_tareas_gui():
    crear_ventana_lista("Listar Tareas","detalles")
    
def marcar_completada_gui():
    crear_ventana_lista("Marcar como Completada","marcar")

def eliminar_tarea_gui():
    crear_ventana_lista("Eliminar Tarea","eliminar")

# --- Ventana principal ---
ventana = tk.Tk()
ventana.title("Gestor de Tareas")

# --- Frame para la lista de tareas ---
frame_lista = tk.Frame(ventana)
frame_lista.pack(pady=10)

listbox_tareas = tk.Listbox(frame_lista, width=50)
listbox_tareas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_lista)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox_tareas.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox_tareas.yview)

# --- Botones ---
boton_agregar = tk.Button(ventana, text="Agregar Tarea", command=agregar_tarea_gui)
boton_agregar.pack(pady=5)

boton_listar = tk.Button(ventana, text="Listar Tareas", command=listar_tareas_gui)
boton_listar.pack(pady=5)

boton_marcar = tk.Button(ventana, text="Marcar Completada", command=marcar_completada_gui)
boton_marcar.pack(pady=5)

boton_eliminar = tk.Button(ventana, text="Eliminar Tarea", command=eliminar_tarea_gui)
boton_eliminar.pack(pady=5)

actualizar_lista_tareas() #Cargar las tareas al inicio.
ventana.mainloop()