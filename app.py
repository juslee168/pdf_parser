from flask import Flask, render_template, request, flash, session
import PyPDF2
from transformers import pipeline
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Ensure to use a secure secret key

# Load the pre-trained question-answering model
nlp = pipeline("question-answering")

UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_saved_pdf():
    # Check for a saved PDF in the upload folder
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".pdf"):
            return filename
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    saved_pdf = get_saved_pdf()
    pdf_text = None

    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            if file.filename.endswith(".pdf"):
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                pdf_text = extract_text_from_pdf(file_path)
                saved_pdf = file.filename
                session["qa_history"] = []  # Reset the history on new file upload
                flash("PDF uploaded successfully!", "success")
            else:
                flash("Only PDF files are allowed", "error")

        question = request.form.get("question", "").strip()
        if question:
            if not saved_pdf:
                flash("No PDF file uploaded. Please upload a PDF file first.", "error")
            else:
                if not pdf_text:
                    pdf_text = extract_text_from_pdf(os.path.join(UPLOAD_FOLDER, saved_pdf))
                if pdf_text:
                    preprocessed_text = preprocess_text(pdf_text)
                    answer = answer_question(preprocessed_text, question)

                    # Save question and answer to session
                    if "qa_history" not in session:
                        session["qa_history"] = []
                    session["qa_history"].append({"question": question, "answer": answer})

                    return render_template("index.html", saved_pdf=saved_pdf, qa_history=session["qa_history"])
                else:
                    flash("Failed to extract text from the PDF", "error")

    return render_template("index.html", saved_pdf=saved_pdf, qa_history=session.get("qa_history", []))

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
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
