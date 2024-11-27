from flask import Flask, render_template, request, flash, session
import PyPDF2
from transformers import pipeline
import os

app = Flask(__name__)

# Load the pre-trained question-answering model
nlp = pipeline("question-answering")

UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Check if a file is uploaded
            if "file" not in request.files:
                flash("No file uploaded", "error")
                return render_template("index.html")

            file = request.files["file"]
            filename = file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            file.save(file_path)

            # Ensure the file is a PDF
            if not file.filename.endswith(".pdf"):
                flash("Only PDF files are allowed", "error")
                return render_template("index.html")

            # Extract text from PDF
            pdf_text = extract_text_from_pdf(file)
            if not pdf_text.strip():
                flash("Failed to extract text from the PDF", "error")
                return render_template("index.html")
            
            # session["pdf_text"] = pdf_text  # Save extracted text
            # session["file_path"] = file_path  # Save file path for reference
            # flash("PDF uploaded successfully! You can now ask questions.", "success")

            # Preprocess the extracted text
            preprocessed_text = preprocess_text(pdf_text)

            # Get the user's question
            question = request.form.get("question", "").strip()
            if not question:
                flash("Please enter a question", "error")
                return render_template("index.html")

            # Generate the answer using the question-answering model
            answer = answer_question(preprocessed_text, question)

            return render_template("index.html", question=question, answer=answer)

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("index.html")

    # GET request
    return render_template("index.html")

    # return render_template("index.html")

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
#     # return render_template("index.html", answer=answer)

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text
    # with open(file_path, 'rb') as file:
    #     pdf_reader = PyPDF2.PdfReader(file)
    #     text = ""
    #     for page in pdf_reader.pages:
    #         text += page.extract_text()
    # return text


def preprocess_text(text):
    # Implement any necessary preprocessing steps here
    return text

def answer_question(text, question):
    result = nlp(question=question, context=text)
    return result["answer"]

if __name__ == "__main__":
    app.run(debug=True)