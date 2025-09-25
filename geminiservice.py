import os
import google.generativeai as genai
import json
import re # Import the regular expression module

# --- IMPORTANT ---
# Set your Gemini API key as an environment variable named 'GOOGLE_API_KEY'
# For development, you can temporarily set it here, but this is not recommended for production.
# Example: os.environ['GOOGLE_API_KEY'] = 'YOUR_API_KEY_HERE'

try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    raise Exception("GEMINI_API_KEY environment variable not set. Please set it to your Gemini API key.")

# CORRECTED: Configure the model without the unsupported 'response_mime_type'
generation_config = {
    "temperature": 0.2,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
)

def find_hospitals_with_gemini(lat, lon):
    """
    Uses the Gemini API to find real nearby hospitals and returns a list of dictionaries.
    """
    # A more robust prompt asking for raw JSON
    prompt = f"""
    Find up to 5 real hospitals or medical clinics near latitude {lat} and longitude {lon}.
    For each hospital, provide its name, full address, latitude, and longitude.
    Return the result as a raw JSON array of objects. Each object must have the following keys: "name", "address", "lat", "lon".
    Do not add any introductory text, explanations, or markdown formatting like ```json. Only output the raw JSON array.
    """
    
    try:
        response = model.generate_content(prompt)
        
        # --- NEW: Robust JSON Cleaning ---
        text_to_parse = response.text
        
        # Find the JSON block if it's wrapped in markdown backticks
        match = re.search(r'```(json)?\s*([\s\S]*?)\s*```', text_to_parse)
        if match:
            # If found, use only the content inside the backticks
            text_to_parse = match.group(2)
        
        # Strip any remaining whitespace that could break the parser
        text_to_parse = text_to_parse.strip()

        hospitals = json.loads(text_to_parse)
        return hospitals
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error processing Gemini response: {e}")
        # Log the raw response to help with debugging
        print(f"Raw response from Gemini: {response.text if 'response' in locals() else 'No response received'}")
        return [] # Return an empty list to prevent frontend errors