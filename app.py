import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pypdf
import json
import traceback

app = Flask(__name__)
CORS(app)

cached_document_text = ""

@app.route('/analyze', methods=['POST'])
def analyze_document():
    global cached_document_text
    print("\n--- [INCOMING TRANSACTION]: Analyzing Document File Payload ---")
    
    if 'document' not in request.files:
        return jsonify({"error": "Missing valid document stream key."}), 400
        
    uploaded_file = request.files['document']

    try:
        from ai_handler import analyze_document_with_gemini
        
        compiled_text_chunks = []
        if uploaded_file.filename.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted_page_text = page.extract_text()
                if extracted_page_text:
                    compiled_text_chunks.append(extracted_page_text)
            raw_document_text = "\n".join(compiled_text_chunks)
        else:
            raw_document_text = uploaded_file.read().decode('utf-8', errors='ignore')

        if not raw_document_text.strip():
            raw_document_text = f"Document Profile: {uploaded_file.filename}."

        cached_document_text = raw_document_text
        ai_response_text = analyze_document_with_gemini(raw_document_text)
        
        clean_json_text = ai_response_text.strip()
        if clean_json_text.startswith("```json"):
            clean_json_text = clean_json_text.split("```json")[1].split("```")[0].strip()
        elif clean_json_text.startswith("```"):
            clean_json_text = clean_json_text.split("```")[1].split("```")[0].strip()

        return jsonify(json.loads(clean_json_text))

    except Exception as internal_pipeline_error:
        print(traceback.format_exc())
        return jsonify({
            "summary": "The document structure failed deep parsing rules.",
            "version_check": {"is_outdated": False, "detected_version": "Unreadable", "latest_updates": "None"},
            "key_details": {"document_type": "Unreadable", "parties": "Unreadable", "critical_dates": "Unreadable", "monetary_values": "Unreadable"},
            "red_flags": []
        })

@app.route('/chat', methods=['POST'])
def handle_chat_inquiry():
    global cached_document_text
    client_payload = request.get_json()
    user_query = client_payload.get('message', '')
    
    if not user_query:
        return jsonify({"reply": "Input query parameters evaluate to an empty block."}), 400

    try:
        from google import genai
        chat_client = genai.Client(api_key="AIzaSyC2Uj70hq6yhS7hPgm0YorY1Us8X0_Gksg")
        
        system_context_prompt = f"""
        You are an expert legal assistant inside LegaLens AI.
        Answer user questions about legal terms or the uploaded document in clear, simple English.
        
        Document Context:
        {cached_document_text if cached_document_text else "No document uploaded yet."}
        
        User Query: "{user_query}"
        """
        
        response = chat_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_context_prompt
        )
        return jsonify({"reply": response.text.strip()})
        
    except Exception as e:
        return jsonify({"reply": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)