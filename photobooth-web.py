from flask import Flask, render_template, request, jsonify 

app = Flask(__name__)
app.debug = False

count = 0
change = 1
a = "initialisation"

@app.route("/") 
def hello():
	templateData = {
		'title' : 'PhotoBooth - A&F'
	}
	return render_template('main.html', **templateData)


@app.route('/_refresh')
def resfresh():
	global a
	with open('./infos_photobooth','r') as f:
		a = f.read()
	return jsonify(result=a)

if __name__ == "__main__":
	app.run(threaded=True, host='0.0.0.0', port=80, debug=False)


