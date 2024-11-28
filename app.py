from flask import Flask, render_template, request, flash, session, redirect, url_for
import PyPDF2
from transformers import pipeline
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load the pre-trained question-answering model
nlp = pipeline("question-answering")

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    question = None

    if request.method == "POST":
        # Check if a file is uploaded or already exists in the session
        if not session.get("pdf_text") or ("file" in request.files and request.files["file"].filename):
            if "file" not in request.files or not request.files["file"].filename:
                flash("Please upload a PDF before asking a question.", "error")
                return redirect(url_for("index"))

            file = request.files["file"]
            try:
                # Extract text from the uploaded PDF and store in session
                pdf_text = extract_text_from_pdf(file)
                session["pdf_text"] = pdf_text
                flash("PDF uploaded successfully.", "success")
            except Exception as e:
                flash(f"Error processing PDF: {e}", "error")
                return redirect(url_for("index"))

        # Retrieve the PDF text from the session
        pdf_text = session.get("pdf_text")

        # Handle the user's question
        question = request.form.get("question", "").strip()
        if not question:
            flash("Please enter a question.", "error")
            return redirect(url_for("index"))

        try:
            # Generate an answer using the question-answering model
            answer = answer_question(pdf_text, question)
        except Exception as e: 
            flash(f"An error occurred: {e}", "error")

    return render_template("index.html", answer=answer, question=question) 

# @app.route("/process", methods=["POST"])
# def process():
#     # Get the uploaded PDF file
#     file = request.files["file"]
#     pdf_text = extract_text_from_pdf(file)

#     # Preprocess the extracted text
#     preprocessed_text = preprocess_text(pdf_text)

#     # Get the user's question
#     question = request.form["question"]

#     # Generate the answer using the question-answering model
#     answer = answer_question(preprocessed_text, question)

#     return render_template("result.html", answer=answer)  


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def preprocess_text(text):
    # Implement any necessary preprocessing steps here
    return text

def answer_question(text, question):
    result = nlp(question=question, context=text)
    return result["answer"]

if __name__ == "__main__":
    app.run(debug=True)