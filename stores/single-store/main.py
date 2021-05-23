from flask import Flask, render_template

app = Flask(__name__,
	template_folder='../templates',
	static_folder='../static')


@app.route("/")
def home():
	return render_template(
		'single-store/home.djhtml'
		)

@app.route("/single")
def single_product():
	return render_template(
		'single-store/single-product-page.djhtml'
		)

if __name__=="__main__":
	app.run(debug=True)