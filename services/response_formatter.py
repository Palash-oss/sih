import re
import html

class ResponseFormatter:
    """
    Format chatbot responses with proper HTML styling for better frontend display.
    Acts as a middleware between the chatbot response and the frontend.
    """
    
    @staticmethod
    def format_for_html(response_text):
        """
        Transform the plaintext response into HTML with proper styling
        """
        if not response_text:
            return ""
        
        # Sanitize the input
        response_text = html.escape(response_text)
        
        # Apply formatting
        formatted_html = []
        
        # Parse sections
        sections = re.split(r'(─+)\s*', response_text)
        conditions = []
        
        current_section = []
        for i, section in enumerate(sections):
            # If this is a separator line, start a new condition
            if re.match(r'─+', section) and current_section:
                conditions.append(''.join(current_section))
                current_section = []
                continue
            
            current_section.append(section)
            
        # Don't forget the last section
        if current_section:
            conditions.append(''.join(current_section))
        
        # Create the header
        header_match = re.search(r'📋\s+(.+?)(?=\s*🔍|\s*$)', conditions[0] if conditions else response_text)
        if header_match:
            formatted_html.append(f'<div class="health-response-header">{header_match.group(1)}</div>')
            
        # Format each condition card
        for condition in conditions:
            if not condition.strip():
                continue
                
            card_html = ['<div class="health-condition-card">']
            
            # Extract condition name and description
            title_match = re.search(r'🔍\s+([A-Z\s]+)([^🤒]+)', condition)
            if title_match:
                condition_name = title_match.group(1).strip()
                description = title_match.group(2).strip()
                card_html.append(f'<h3 class="condition-title">{condition_name}</h3>')
                card_html.append(f'<p class="condition-desc">{description}</p>')
            
            # Extract symptoms
            symptoms_match = re.search(r'🤒\s+SYMPTOMS(.*?)(?=🛡️|\⚠️|$)', condition, re.DOTALL)
            if symptoms_match:
                symptoms_text = symptoms_match.group(1).strip()
                symptoms_list = re.findall(r'•\s+(.*?)(?=$|\s+•\s+)', symptoms_text + ' •')
                
                if symptoms_list:
                    card_html.append('<div class="symptom-section">')
                    card_html.append('<h4>Symptoms</h4>')
                    card_html.append('<ul class="symptom-list">')
                    for symptom in symptoms_list:
                        card_html.append(f'<li>{symptom.strip()}</li>')
                    card_html.append('</ul>')
                    card_html.append('</div>')
            
            # Extract prevention
            prevention_match = re.search(r'🛡️\s+PREVENTION(.*?)(?=⚠️|$)', condition, re.DOTALL)
            if prevention_match:
                prevention_text = prevention_match.group(1).strip()
                prevention_list = re.findall(r'•\s+(.*?)(?=$|\s+•\s+)', prevention_text + ' •')
                
                if prevention_list:
                    card_html.append('<div class="prevention-section">')
                    card_html.append('<h4>Prevention</h4>')
                    card_html.append('<ul class="prevention-list">')
                    for item in prevention_list:
                        card_html.append(f'<li>{item.strip()}</li>')
                    card_html.append('</ul>')
                    card_html.append('</div>')
            
            # Extract warning signs
            warning_match = re.search(r'⚠️\s+SEEK MEDICAL HELP IF:(.*?)(?=$)', condition, re.DOTALL)
            if warning_match:
                warning_text = warning_match.group(1).strip()
                warning_list = re.findall(r'•\s+(.*?)(?=$|\s+•\s+)', warning_text + ' •')
                
                if warning_list:
                    card_html.append('<div class="warning-section">')
                    card_html.append('<h4>Seek Medical Help If</h4>')
                    card_html.append('<ul class="warning-list">')
                    for item in warning_list:
                        card_html.append(f'<li>{item.strip()}</li>')
                    card_html.append('</ul>')
                    card_html.append('</div>')
            
            card_html.append('</div>')
            formatted_html.append(''.join(card_html))
        
        # Add disclaimer if present
        disclaimer_match = re.search(r'⚠️\s+Disclaimer:(.*?)(?=$)', response_text, re.DOTALL)
        if disclaimer_match:
            disclaimer_text = disclaimer_match.group(1).strip()
            formatted_html.append(f'<div class="health-disclaimer"><strong>Disclaimer:</strong> {disclaimer_text}</div>')
        
        # Add CSS styles
        css = """
        <style>
        .health-response-header {
            font-size: 1.2em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }
        .health-condition-card {
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .condition-title {
            color: #2980b9;
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 1.4em;
        }
        .condition-desc {
            color: #34495e;
            margin-bottom: 15px;
        }
        h4 {
            color: #2c3e50;
            margin-top: 15px;
            margin-bottom: 10px;
            font-size: 1.1em;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .symptom-section h4 {
            color: #e74c3c;
        }
        .prevention-section h4 {
            color: #27ae60;
        }
        .warning-section h4 {
            color: #f39c12;
        }
        .symptom-list, .prevention-list, .warning-list {
            padding-left: 20px;
            margin-top: 10px;
            margin-bottom: 15px;
            list-style-type: none;
        }
        .symptom-list li, .prevention-list li, .warning-list li {
            position: relative;
            padding-left: 20px;
            margin-bottom: 5px;
            line-height: 1.5;
        }
        .symptom-list li:before {
            content: "•";
            color: #e74c3c;
            font-size: 18px;
            position: absolute;
            left: 0;
            top: -2px;
        }
        .prevention-list li:before {
            content: "•";
            color: #27ae60;
            font-size: 18px;
            position: absolute;
            left: 0;
            top: -2px;
        }
        .warning-list li:before {
            content: "•";
            color: #f39c12;
            font-size: 18px;
            position: absolute;
            left: 0;
            top: -2px;
        }
        .health-disclaimer {
            font-size: 0.9em;
            color: #7f8c8d;
            padding: 10px;
            margin-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
        }
        </style>
        """
        
        final_html = css + '\n'.join(formatted_html)
        return final_html