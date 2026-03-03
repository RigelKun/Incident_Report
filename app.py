from datetime import datetime
from io import BytesIO

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from openpyxl import Workbook


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///disaster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

ALLOWED_EMERGENCY_TYPES = {"OBGYN", "Trauma", "Medical"}


class Incident(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	emergency_type = db.Column(db.String(120), nullable=False)
	incident_name = db.Column(db.String(200), nullable=False)
	incident_date = db.Column(db.Date, nullable=False)
	incident_time = db.Column(db.Time, nullable=False)
	place = db.Column(db.String(200), nullable=False)
	driver = db.Column(db.String(120), nullable=False)
	ptv_number = db.Column(db.String(50), nullable=False)
	responders = db.Column(db.String(250), nullable=False)
	remarks = db.Column(db.Text, nullable=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == "POST":
		emergency_type = request.form.get("emergency_type", "").strip()
		incident_name = request.form.get("incident_name", "").strip()
		incident_date_raw = request.form.get("incident_date", "").strip()
		incident_time_raw = request.form.get("incident_time", "").strip()
		place = request.form.get("place", "").strip()
		driver = request.form.get("driver", "").strip()
		ptv_number = request.form.get("ptv_number", "").strip()
		responders = request.form.get("responders", "").strip()
		remarks = request.form.get("remarks", "").strip()

		if not all(
			[
				emergency_type,
				incident_name,
				incident_date_raw,
				incident_time_raw,
				place,
				driver,
				ptv_number,
				responders,
			]
		):
			flash("Please fill in all required fields.", "error")
			return redirect(url_for("home"))

		if emergency_type not in ALLOWED_EMERGENCY_TYPES:
			flash("Emergency type must be OBGYN, Trauma, or Medical.", "error")
			return redirect(url_for("home"))

		try:
			incident_date = datetime.strptime(incident_date_raw, "%Y-%m-%d").date()
			incident_time = datetime.strptime(incident_time_raw, "%H:%M").time()
		except ValueError:
			flash("Invalid date/time format.", "error")
			return redirect(url_for("home"))

		new_incident = Incident(
			emergency_type=emergency_type,
			incident_name=incident_name,
			incident_date=incident_date,
			incident_time=incident_time,
			place=place,
			driver=driver,
			ptv_number=ptv_number,
			responders=responders,
			remarks=remarks,
		)
		db.session.add(new_incident)
		db.session.commit()
		flash("Incident saved successfully.", "success")
		return redirect(url_for("home"))

	return render_template("app.html")


@app.route("/database", methods=["GET"])
def database():
	incidents = Incident.query.order_by(Incident.id.desc()).all()
	return render_template("database.html", incidents=incidents)


@app.route("/incident/<int:incident_id>/edit", methods=["GET", "POST"])
def edit_incident(incident_id):
	incident = Incident.query.get_or_404(incident_id)

	if request.method == "POST":
		emergency_type = request.form.get("emergency_type", "").strip()
		incident_name = request.form.get("incident_name", "").strip()
		incident_date_raw = request.form.get("incident_date", "").strip()
		incident_time_raw = request.form.get("incident_time", "").strip()
		place = request.form.get("place", "").strip()
		driver = request.form.get("driver", "").strip()
		ptv_number = request.form.get("ptv_number", "").strip()
		responders = request.form.get("responders", "").strip()
		remarks = request.form.get("remarks", "").strip()

		if not all(
			[
				emergency_type,
				incident_name,
				incident_date_raw,
				incident_time_raw,
				place,
				driver,
				ptv_number,
				responders,
			]
		):
			flash("Please fill in all required fields.", "error")
			return redirect(url_for("edit_incident", incident_id=incident.id))

		if emergency_type not in ALLOWED_EMERGENCY_TYPES:
			flash("Emergency type must be OBGYN, Trauma, or Medical.", "error")
			return redirect(url_for("edit_incident", incident_id=incident.id))

		try:
			incident_date = datetime.strptime(incident_date_raw, "%Y-%m-%d").date()
			incident_time = datetime.strptime(incident_time_raw, "%H:%M").time()
		except ValueError:
			flash("Invalid date/time format.", "error")
			return redirect(url_for("edit_incident", incident_id=incident.id))

		incident.emergency_type = emergency_type
		incident.incident_name = incident_name
		incident.incident_date = incident_date
		incident.incident_time = incident_time
		incident.place = place
		incident.driver = driver
		incident.ptv_number = ptv_number
		incident.responders = responders
		incident.remarks = remarks

		db.session.commit()
		flash("Incident updated successfully.", "success")
		return redirect(url_for("database"))

	return render_template("edit_incident.html", incident=incident)


@app.route("/incidents/remove-all", methods=["POST"])
def remove_all_incidents():
	deleted_count = db.session.query(Incident).delete()
	db.session.commit()
	flash(f"{deleted_count} incident(s) deleted.", "success")
	return redirect(url_for("database"))


@app.route("/export")
def export_excel():
	incidents = Incident.query.order_by(Incident.id.asc()).all()

	workbook = Workbook()
	worksheet = workbook.active
	worksheet.title = "Incidents"

	headers = [
		"No.",
		"Emergency Type",
		"Incident Name",
		"Date of Incident",
		"Time of Incident",
		"Place of Incident",
		"Driver",
		"PTV Number",
		"Responders",
		"Remarks",
	]
	worksheet.append(headers)

	for incident in incidents:
		worksheet.append(
			[
				incident.id,
				incident.emergency_type,
				incident.incident_name,
				incident.incident_date.strftime("%Y-%m-%d"),
				incident.incident_time.strftime("%H:%M"),
				incident.place,
				incident.driver,
				incident.ptv_number,
				incident.responders,
				incident.remarks or "",
			]
		)

	output = BytesIO()
	workbook.save(output)
	output.seek(0)

	filename = f"incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
	return send_file(
		output,
		as_attachment=True,
		download_name=filename,
		mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	)


with app.app_context():
	db.create_all()


if __name__ == "__main__":
	app.run(debug=True)
