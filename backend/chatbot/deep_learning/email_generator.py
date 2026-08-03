from datetime import datetime
import json

class EmailGenerator:
    def __init__(self):
        # Municipal corporation email templates
        self.templates = {
            'pothole': {
                'subject': 'URGENT: Pothole Issue at {location} - Immediate Action Required',
                'body': """
Dear Municipal Corporation Team,

I am writing to bring to your immediate attention a serious pothole issue at the following location:

📍 Location: {location}
📅 Date Reported: {date}
⚠️ Severity Level: {severity}

Details of the Issue:
A significant pothole has been observed at the above-mentioned location. This poses a serious safety hazard to:
- Vehicles passing through the area
- Pedestrians, especially during nighttime
- Two-wheeler riders

The condition of the road is deteriorating rapidly and requires immediate intervention to prevent:
• Vehicle damage
• Traffic accidents
• Injury to pedestrians

Request for Action:
1. Immediate site inspection
2. Installation of warning signs/barricades
3. Prompt repair of the pothole
4. Follow-up maintenance to prevent recurrence

Please find attached an image of the pothole for your reference.

I request you to kindly look into this matter on an urgent basis and take necessary action.

For any further details, please contact me.

Regards,
{user_name}
Contact: {user_contact}
Email: {user_email}
"""
            },
            'garbage': {
                'subject': 'URGENT: Waste Accumulation at {location} - Health Hazard Alert',
                'body': """
Dear Municipal Corporation Team,

I am writing to report a serious waste accumulation issue that poses significant health and environmental hazards at:

📍 Location: {location}
📅 Date Reported: {date}
⚠️ Severity Level: {severity}

Issue Description:
There is an alarming accumulation of garbage/waste at the above-mentioned location. The situation is critical due to:

Health Hazards:
• Breeding ground for disease-carrying vectors
• Risk of waterborne diseases
• Air pollution from decomposing waste
• Potential for rodent infestation

Environmental Impact:
• Visual pollution affecting the area
• Soil contamination
• Water source pollution
• Odor nuisance

Request for Immediate Action:
1. Emergency cleanup of the accumulated waste
2. Installation of adequate waste bins
3. Regular waste collection schedule
4. Public awareness about waste disposal

Please find attached an image showing the current condition of the site.

I urge you to take immediate action to resolve this issue and prevent further environmental degradation.

Regards,
{user_name}
Contact: {user_contact}
Email: {user_email}
"""
            },
            'water_logging': {
                'subject': 'URGENT: Water Logging Issue at {location} - Flood Risk Alert',
                'body': """
Dear Municipal Corporation Team,

I am writing to urgently report severe water logging at the following location:

📍 Location: {location}
📅 Date Reported: {date}
⚠️ Severity Level: {severity}

Critical Situation:
The area is experiencing severe water logging due to:
• Blocked drainage systems
• Insufficient drainage capacity
• Recent rainfall accumulation

Consequences:
• Disruption of daily life and commute
• Risk of waterborne diseases
• Property damage
• Traffic congestion
• Safety hazard for pedestrians

Request for Immediate Intervention:
1. Emergency drainage clearance
2. Inspection of drainage infrastructure
3. Installation of additional drainage facilities
4. Regular maintenance of drainage systems

Please find attached an image showing the current water logging situation.

I request your urgent intervention to prevent this situation from escalating and causing widespread disruption.

Regards,
{user_name}
Contact: {user_contact}
Email: {user_email}
"""
            },
            'other': {
                'subject': 'Infrastructure Issue Report at {location}',
                'body': """
Dear Municipal Corporation Team,

I am writing to report an infrastructure issue that requires your attention at:

📍 Location: {location}
📅 Date Reported: {date}

Issue Description:
An infrastructure issue has been observed at the above location that needs to be addressed.

Request for Action:
1. Site inspection
2. Assessment of the issue
3. Necessary repairs/action
4. Follow-up

Please find attached an image of the issue for your reference.

I request you to kindly look into this matter and take appropriate action.

Regards,
{user_name}
Contact: {user_contact}
Email: {user_email}
"""
            }
        }
    
    def generate_email(self, prediction_result, user_data, location, custom_prompt=None):
        """Generate a professional email based on prediction and user data"""
        
        # Determine the issue type
        issue_type = prediction_result.get('class', 'other')
        
        # Get the appropriate template
        template_data = self.templates.get(issue_type, self.templates['other'])
        
        # Calculate severity level
        severity_score = prediction_result.get('severity', 0.5)
        if severity_score > 0.7:
            severity = 'HIGH (Immediate Action Required)'
        elif severity_score > 0.4:
            severity = 'MEDIUM (Urgent Action Required)'
        else:
            severity = 'LOW (Action Required Soon)'
        
        # Format the email
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
        
        # If custom prompt is provided, incorporate it
        if custom_prompt:
            email_data['custom_notes'] = custom_prompt
        
        return email_data
    
    def generate_response(self, email_data):
        """Generate a JSON response for the API"""
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