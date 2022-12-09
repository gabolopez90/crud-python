from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key="Develoteca"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema'

mysql.init_app(app)

CARPETA = os.path.join("uploads")
app.config["CARPETA"] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config["CARPETA"],nombreFoto)

@app.route("/")
def index():
    sql = "SELECT * FROM `empleados`"

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    conn.commit()
    
    return render_template("empleados/index.html", empleados = empleados)
    
@app.route('/destroy/<int:id>')
def destroy(id):
    sql = "DELETE FROM `empleados` WHERE id=%s"

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id=%s",id)
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config["CARPETA"],fila[0][0]))

    cursor.execute(sql,id)    
    conn.commit()
    return redirect("/")

@app.route('/edit/<int:id>')
def edit(id):
    sql = "SELECT * FROM `empleados` WHERE id=%s"

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,id)
    empleados = cursor.fetchall()
    conn.commit()

    return render_template("empleados/edit.html",empleados=empleados)

@app.route('/create')
def create():
    return render_template("empleados/create.html")

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    _fecha = request.form['txtFecha']

    if _nombre == "" or _correo == "" or _foto.filename == "" or _fecha == "":
        flash("Recuerda llenar todos los campos")
        return redirect(url_for("create"))

    now = datetime.now()
    tiempo= now.strftime("%Y%H%M%S")

    if _foto.filename!="":
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`, `fecha`) VALUES (NULL, %s, %s, %s,%s);"

    datos = (_nombre,_correo,nuevoNombreFoto,_fecha)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect("/")

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id=request.form['txtID']
    _fecha = request.form['txtFecha']
    
    sql = "UPDATE `empleados` SET nombre=%s, correo=%s, fecha=%s WHERE id=%s;"

    datos = (_nombre,_correo,_fecha,id)
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo= now.strftime("%Y%H%M%S")

    if _foto.filename!="":
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id=%s",id)
        fila = cursor.fetchall()
        os.remove(os.path.join(app.config["CARPETA"],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()


    cursor.execute(sql,datos)
    conn.commit()

    return redirect("/")
        

if __name__ == '__main__':
    app.run(debug=True)