from datetime import datetime
import json

class EmailGenerator:
    def __init__(self):
        self.templates = {
            "pothole": {
                "subject": "URGENT: Pothole Issue at {location} - Immediate Action Required",
                "body": """
# Pothole Complaint Report

Dear Municipal Corporation Team,

I hope this message finds you well.

I would like to report a pothole that requires immediate attention as it poses a risk to public safety.

---

## Complaint Details

| Field | Information |
|-------|-------------|
| **Location** | {location} |
| **Date Reported** | {date} |
| **Severity Level** | {severity} |

---

## Issue Description

A significant pothole has been observed at the above-mentioned location. The damaged road surface has become hazardous for commuters and may lead to accidents if not repaired promptly.

---

## Safety Concerns

- Risk of accidents for two-wheelers and four-wheelers.
- Danger to pedestrians, especially during nighttime.
- Increased traffic congestion due to vehicles avoiding the damaged section.
- Possibility of further road deterioration if left unattended.

---

## Requested Action

Kindly take the following actions at the earliest:

1. Conduct an immediate site inspection.
2. Install temporary warning signs or barricades.
3. Repair and restore the damaged road surface.
4. Ensure the repaired section is safe for public use.

---

## Attachment

An image of the pothole has been attached to assist in identifying the exact issue and location.

---

Thank you for your prompt attention to this matter. I look forward to your timely response and necessary action.
"""
            },

            "garbage": {
                "subject": "URGENT: Waste Accumulation at {location} - Health Hazard Alert",
                "body": """
# Waste Accumulation Complaint

Dear Municipal Corporation Team,

I hope you are doing well.

I wish to report a serious waste accumulation issue that requires urgent intervention due to its impact on public health and sanitation.

---

## Complaint Details

| Field | Information |
|-------|-------------|
| **Location** | {location} |
| **Date Reported** | {date} |
| **Severity Level** | {severity} |

---

## Issue Description

A large amount of garbage has accumulated at the above-mentioned location. The waste has remained unattended for an extended period, creating an unhygienic environment for nearby residents and commuters.

---

## Health & Environmental Concerns

- Increased risk of mosquito and insect breeding.
- Possibility of waterborne and vector-borne diseases.
- Foul odor affecting nearby residential and commercial areas.
- Environmental pollution and reduced public cleanliness.

---

## Requested Action

Kindly arrange for the following actions as soon as possible:

1. Immediate removal of the accumulated waste.
2. Cleaning and sanitization of the affected area.
3. Installation of adequate waste collection bins.
4. Regular monitoring and scheduled waste collection.

---

## Attachment

An image of the affected location has been attached for your reference.

---

Thank you for your attention to this matter. I would appreciate prompt action to resolve this issue in the interest of public health and safety.
"""
            }
        }
    
    def generate_email(self, prediction_result, user_data, location, custom_prompt=None):
        issue_type = prediction_result.get('class', 'garbage')
        # If prediction is not pothole or garbage, default to garbage
        if issue_type not in self.templates:
            issue_type = 'garbage'
        
        template_data = self.templates.get(issue_type, self.templates['garbage'])
        
        severity_score = prediction_result.get('severity', 0.5)
        if severity_score > 0.7:
            severity = 'HIGH (Immediate Action Required)'
        elif severity_score > 0.4:
            severity = 'MEDIUM (Urgent Action Required)'
        else:
            severity = 'LOW (Action Required Soon)'
        
        email_data = {
            'subject': template_data['subject'].format(
                location=location,
                date=datetime.now().strftime('%B %d, %Y'),
                severity=severity
            ),
            'body': template_data['body'].format(
                location=location,
                date=datetime.now().strftime('%B %d, %Y'),
                severity=severity,
                user_name=user_data.get('name', 'Citizen'),
                user_contact=user_data.get('contact', 'N/A'),
                user_email=user_data.get('email', 'N/A')
            ),
            'issue_type': issue_type,
            'severity': severity,
            'severity_score': severity_score,
            'confidence': prediction_result.get('confidence', 0.0)
        }
        
        if custom_prompt:
            email_data['custom_notes'] = custom_prompt
        
        return email_data
    
    def generate_response(self, email_data):
        return {
            'success': True,
            'email': {
                'subject': email_data['subject'],
                'body': email_data['body'],
                'issue_type': email_data['issue_type'],
                'severity': email_data['severity'],
                'severity_score': email_data['severity_score'],
                'confidence': email_data['confidence']
            },
            'message': f"Professional email generated for {email_data['issue_type']} issue.",
            'action_required': email_data['severity_score'] > 0.6
        }