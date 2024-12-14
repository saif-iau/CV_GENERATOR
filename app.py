from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os

app = Flask(__name__)

class ATSResumePDF(FPDF):
    def footer(self):
        # Add footer on all pages
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_resume(data):
    pdf = ATSResumePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=8)

    # Header Section
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 8, data.get("name", "Your Name"), ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, data.get("job_title", "Job Title"), ln=True)
    pdf.cell(0, 6, data.get("location", "Location"), ln=True)
    pdf.cell(0, 6, f"Email: {data.get('email', 'Not Provided')}", ln=True)
    pdf.cell(0, 6, f"Phone: {data.get('phone', 'Not Provided')}", ln=True)

    # Line break
    pdf.ln(10)

    # Dynamic Sections
    for section, content in data.items():
        if section.lower() in ["name", "job_title", "location", "email", "phone"]:
            continue  # Skip the header fields

        # Add Section Title
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, section.upper(), ln=True)

        # Add Section Content
        pdf.set_font("Arial", size=10)
        if isinstance(content, str):
            # If the content is a simple string
            pdf.multi_cell(0, 6, content)
        elif isinstance(content, list):
            # If the content is a list of items
            for item in content:
                if isinstance(item, dict):
                    for key, value in item.items():
                        pdf.cell(0, 6, f"- {key}: {value}", ln=True)
                else:
                    pdf.cell(0, 6, f"- {item}", ln=True)
        elif isinstance(content, dict):
            # If the content is a dictionary
            for key, value in content.items():
                pdf.cell(0, 6, f"- {key}: {value}", ln=True)

        # Line break after each section
        pdf.ln(5)

    # Save and return PDF path
    pdf_path = "Generated_CV.pdf"
    pdf.output(pdf_path)
    return pdf_path


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get user input from the form
        data = {
            "name": request.form.get("name"),
            "job_title": request.form.get("job_title"),
            "location": request.form.get("location"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "profile": request.form.get("profile"),
            "education": [
                {"Degree": d, "Institution": i, "Year": y}
                for d, i, y in zip(
                    request.form.getlist("degree"),
                    request.form.getlist("institution"),
                    request.form.getlist("edu_year"),
                )
            ],
            "skills": request.form.getlist("skills"),
            "certifications": request.form.getlist("certifications"),
            "experience": [
                {"Company": c, "Role": r, "Duration": d}
                for c, r, d in zip(
                    request.form.getlist("company"),
                    request.form.getlist("role"),
                    request.form.getlist("exp_duration"),
                )
            ],
        }

        # Generate PDF and return it
        pdf_path = generate_resume(data)
        return send_file(pdf_path, as_attachment=True)

    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)
