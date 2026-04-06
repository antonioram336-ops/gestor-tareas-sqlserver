from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

server = r'LAPTOP-LU46FNHV\MSSQLSERVER02'
database = 'GestorTareasDB'

connection_string = (
    'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;'
)

def get_connection():
    return pyodbc.connect(connection_string)

@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, titulo, descripcion, completada FROM tareas ORDER BY id DESC")
    tareas = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM tareas")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tareas WHERE completada = 1")
    completadas = cursor.fetchone()[0]

    pendientes = total - completadas

    conn.close()

    return render_template(
        "index.html",
        tareas=tareas,
        total=total,
        completadas=completadas,
        pendientes=pendientes
    )

@app.route("/agregar", methods=["POST"])
def agregar():
    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tareas (titulo, descripcion) VALUES (?, ?)",
        (titulo, descripcion)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/completar/<int:id>")
def completar(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tareas SET completada = 1 WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/editar/<int:id>")
def editar(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, descripcion, completada FROM tareas WHERE id = ?",
        (id,)
    )
    tarea = cursor.fetchone()
    conn.close()

    if not tarea:
        return redirect(url_for("index"))

    return render_template("editar.html", tarea=tarea)

@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tareas SET titulo = ?, descripcion = ? WHERE id = ?",
        (titulo, descripcion, id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)