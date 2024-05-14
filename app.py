from tkinter import ttk
from tkinter import *
import sqlite3


class Product:
    db_name = "database.db"

    def __init__(self, window):
        self.window = window
        self.window.title("Aplicación de Productos")
        frame = LabelFrame(self.window, text="Registrar Producto")
        frame.grid(row=0, column=0, columnspan=3, pady=10)

        Label(frame, text="Producto: ").grid(row=1, column=0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        Label(frame, text="Precio: ").grid(row=2, column=0)
        self.price = Entry(frame)
        self.price.grid(row=2, column=1)

        ttk.Button(frame, text="Guardar Producto", command=self.add_products).grid(
            row=3, columnspan=2, sticky=W + E)

        self.message = Label(text="", fg="red")
        self.message.grid(row=3, column=0, columnspan=2, sticky=W + E)

        self.tree = ttk.Treeview(height=10, columns=2)
        self.tree.grid(row=4, column=0, columnspan=2)
        self.tree.heading("#0", text="Nombre", anchor=CENTER)
        self.tree.heading("#1", text="Precio", anchor=CENTER)

        ttk.Button(text="BORRAR", command=self.delete_products).grid(
            row=5, column=0, sticky=W + E)
        ttk.Button(text="EDITAR", command=self.edit_products).grid(
            row=5, column=1, sticky=W + E)

        self.get_products()

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def get_products(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = "SELECT * FROM producto ORDER BY nombre DESC"
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert("", 0, text=row[1], values=row[2])

    def validate(self):
        return len(self.name.get()) != 0 and len(self.price.get()) != 0

    def add_products(self):
        if self.validate():
            query = "INSERT INTO producto VALUES(NULL, ?, ?)"
            parameters = (self.name.get(), self.price.get())
            self.run_query(query, parameters)
            self.message["text"] = f"El producto {self.name.get()} fue agregado"
            self.name.delete(0, END)
            self.price.delete(0, END)
        else:
            self.message["text"] = "Nombre y precio requeridos"
        self.get_products()

    def delete_products(self):
        self.message["text"] = ""
        try:
            self.tree.item(self.tree.selection())["text"][0]
        except IndexError as error:
            self.message["text"] = "Por favor selecciona un producto"
            return
        self.message["text"] = ""
        name = self.tree.item(self.tree.selection())["text"]
        query = "DELETE FROM producto WHERE nombre = ?"
        self.run_query(query, (name, ))
        self.message["text"] = f"Producto {name} borrado con éxito"
        self.get_products()

    def edit_products(self):
        self.message["text"] = ""
        try:
            self.tree.item(self.tree.selection())["text"][0]
        except IndexError as error:
            self.message["text"] = "Por favor selecciona un producto"
            return
        name = self.tree.item(self.tree.selection())["text"]
        self.old_price = self.tree.item(self.tree.selection())["values"][0]
        self.edit_window = Toplevel()
        self.edit_window.title = "Editar Producto"

        Label(self.edit_window, text="Nombre antiguo"). grid(row=0, column=1)
        Entry(self.edit_window, textvariable=StringVar(self.edit_window,
                                                       value=name), state="readonly").grid(row=0, column=2)
        Label(self.edit_window, text="Nombre nuevo").grid(row=1, column=1)
        self.new_name = Entry(self.edit_window)
        self.new_name.grid(row=1, column=2)

        Label(self.edit_window, text="Precio antiguo").grid(row=2, column=1)
        Entry(self.edit_window, textvariable=StringVar(self.edit_window,
                                                       value=self.old_price), state="readonly").grid(row=2, column=2)
        Label(self.edit_window, text="Nuevo precio").grid(row=3, column=1)
        self.new_price = Entry(self.edit_window)
        self.new_price.grid(row=3, column=2)

        Button(self.edit_window, text="Actualizar", command=lambda: self.edit_records(
            self.new_name.get(), name, self.new_price.get(), self.old_price)).grid(row=4, columnspan=4, sticky=W + E)

        self.edit_wind_message = Label(self.edit_window, text="", fg="red")
        self.edit_wind_message.grid(row=5, columnspan=4, sticky=W + E)

    def validate_edit(self):
        return len(self.new_name.get()) != 0 and len(self.new_price.get()) != 0

    def edit_records(self, new_name, name, new_price, old_price):
        if self.validate_edit():
            query = "UPDATE producto SET nombre = ?, precio = ? WHERE nombre = ? AND precio = ?;"
            parameters = (new_name, new_price, name, old_price)
            self.run_query(query, parameters)
            self.edit_window.destroy()
            self.message["text"] = f"El producto {name} fue actualizado"
        else:
            self.edit_wind_message["text"] = f"Por favor llena los campos"

        self.get_products()


if __name__ == "__main__":
    window = Tk()
    app = Product(window)
    window.mainloop()
