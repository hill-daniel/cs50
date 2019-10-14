import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

fieldNames = ['firstName', 'lastName', 'whisky', 'whiskyType', 'verdict']


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    # get form data
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    whisky = request.form['whisky']
    whiskyType = request.form['whiskyType']
    verdict = request.form['verdict']

    # backend check for required fields
    if not firstName or not lastName or not whisky:
        render_template("error.html", message="Unfortunately your form data was missing data. Please check and try again")

    # append form data as new row in csv file
    with open('survey.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        writer.writerow({'firstName': firstName, 'lastName': lastName,
                         'whisky': whisky, 'whiskyType': whiskyType, 'verdict': verdict})
    return render_template("success.html", message="Data has been submitted!")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    # load csv
    rows = []
    with open('survey.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    # render in template
    return render_template("sheet.html", len=len(fieldNames), header=fieldNames, rows=rows)
