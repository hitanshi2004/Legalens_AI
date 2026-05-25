import warnings
# Silence all legacy deprecation messages cleanly
warnings.filterwarnings("ignore", category=FutureWarning)

from google import genai
from google.genai import types
import json

# Initializing using your fresh, verified API key
client = genai.Client(api_key="AIzaSyC2Uj70hq6yhS7hPgm0YorY1Us8X0_Gksg")

def analyze_document_with_gemini(document_text):
    try:
        prompt_instruction = f"""
        You are an expert legal AI framework specializing in contract analysis.
        Analyze the text document provided below and output your assessment parameters strictly formatted in JSON matching the schema format keys.
        
        CRITICAL RULES:
        1. All explanations, risks, and remediations MUST be written strictly in plain English.
        2. Respond ONLY with a raw JSON object string matching the layout structure below.
        
        Document Text Content:
        ---
        {document_text}
        ---
        
        Required JSON Output Structure:
        {{
          "summary": "Provide a detailed, deep plain-English summary paragraph here describing the document scope and core purpose.",
          "version_check": {{
            "is_outdated": false,
            "detected_version": "Specify version profile, revision history, or year discovered.",
            "latest_updates": "Provide modern regulatory change alerts matching compliance criteria."
          }},
          "key_details": {{
            "document_type": "The exact classification of the legal instrument identified.",
            "parties": "Identities of legal entities or individuals signing.",
            "critical_dates": "Effective milestones, deadlines, or duration windows.",
            "monetary_values": "Explicit financial values, consideration streams, or processing fines."
          }},
          "red_flags": [
            {{
              "clause": "Exact excerpt text from the layout containing high exposure or lopsided parameters.",
              "risk": "Explain clearly why this provision disadvantages the reader.",
              "remediation": "Provide replacement phrasing showing how to modify this clause to make it fair."
            }}
          ]
        }}
        """

        # Using the clean SDK generation layer with explicit JSON mime enforcement
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_instruction,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        return response.text
        
    except Exception as e:
        print(f"!!! GenAI Processing Exception Detected: {str(e)}")
        fallback = {
            "summary": f"Failed to extract dynamic insights: {str(e)}",
            "version_check": {"is_outdated": False, "detected_version": "Error Pass", "latest_updates": "None"},
            "key_details": {"document_type": "Variance", "parties": "Unresolved", "critical_dates": "Unresolved", "monetary_values": "Unresolved"},
            "red_flags": []
        }
        return json.dumps(fallback)