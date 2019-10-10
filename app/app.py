from flask import Flask, render_template,flash, redirect,url_for,session,logging,request    
from pymongo import MongoClient
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = "secret"

try:
    conn = MongoClient('localhost', 27017)
    print("Db Connected")
except:
    print("Could not connect to DB") 


db = conn.task
if db:
    studentCollection = db.students
    resultCollection = db.results
    

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        userName = request.form["username"]
        password = request.form["password"]
        user_data = studentCollection.find_one({'email' : userName})
        if user_data and sha256_crypt.verify(password, user_data['password']):
            session['user_id'] = str(user_data["_id"])
            del user_data['password']
            return render_template("show.html", student_id = str(user_data["_id"]))
        else:
        	return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        roll_no = request.form['roll_no']
        password = sha256_crypt.encrypt(request.form['password'])
        standard = request.form['standard']


        student_id = studentCollection.insert(
            {'username' : username,
        	'email' : email,
        	'roll_no' : roll_no,
        	'password' : password,
        	'standard' : standard,
        	}) 
        print("Data inserted with student id",student_id) 
        return redirect(url_for("results",standard = standard, st_id = str(student_id)))
    return render_template("register.html")

@app.route("/results/<int:standard>/<st_id>", methods=['GET', 'POST'])
def results(standard,st_id):
    if request.method == "POST":
        result = []
        for i in range(1,standard):
            data = {}
            data['standard'] = request.form['Standard'+str(i)]
            data['grade'] = request.form['grade'+str(i)]
            data['remark'] = request.form['remark'+str(i)]
            data['percentage'] = request.form['percentage'+str(i)]
            result.append(data)
    
        response = resultCollection.update_one(
            {
                "student_id" : st_id
            },
            {
                  "$set": { 
                      "student_id" : st_id,
                      "result": result
                      }
            },
            upsert=True
            )
        return redirect(url_for("show"), student_id= str(st_id))
    return render_template("result.html",standard = standard)

@app.route("/show/<student_id>")
def show(student_id):
    if student_id:
        user_data = resultCollection.find({"student_id": student_id})
    else:
        student_id = request.args.get('student_id', None)
        user_data = resultCollection.find({"student_id": student_id})
        
    return render_template("show.html", user_data = user_data)     
if __name__ == '__main__':
	app.run(debug = True)