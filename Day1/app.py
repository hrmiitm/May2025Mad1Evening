from flask import Flask, render_template, request # class


app = Flask(__name__) # instance/object

# /
# /?id=123
# /?id=123&name=hrithik
@app.route('/', methods=['GET'])
def home():
    x = request.args.get('id')
    return render_template('home.html', name=request.args.get('name'), x=x)



# /login/24/hritik
# /login/2451/anthing
@app.route('/login/<int:id>/<string:name>')
def login(id, name):
    return f"<h1>Login Page {id} - {name}</h1>"

app.run(debug=True)