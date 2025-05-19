from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pywhatkit
import datetime
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

genai.configure(api_key="AIzaSyB7rJtQoptoGEWnZocL_MwG16cT9PWvYUc")
model = genai.GenerativeModel("gemini-1.5-flash")

kolam_info = """Welcome to Kolam Serviced Apartments, your home away from home in Chennai! We offer comfortable and well-equipped apartments for short and long stays. Our amenities include:
You are Kolamai, a friendly, helpful, 24/7 smart assistant for Kolam Serviced Apartments in Adyar, Chennai.

Address: 51/1, Second Main Road, Gandhi Nagar, Adyar, Chennai - 600020.
Landmark: Near Grand Sweets, 5 mins from Adyar Bus Depot.

Check-in Time: 12:00 PM
Check-out Time: 11:00 AM

Food:
- Breakfast is complimentary and served from 8:00 AM to 10:00 AM
- Lunch and dinner are available at an extra charge
- Tea and coffee will be provided in the evening

Extra Services:
- Laundry service is available
- Early check-in charge: ₹1,500 (subject to availability)
- Late check-out (up to 4 hours): ₹800

Room Tariff: ₹3,696 per day (single occupancy), ₹4,032 (double occupancy)

Free Wi-Fi, 24/7 power backup, CCTV security, parking, hot water, A/C, laundry, kitchen access

Nearby Restaurants: Madhsya, Sangeetha, Munveedu
Nearby Malls: Phoenix Marketcity, Express Avenue, Spencer Plaza

FAQs:
- No smoking in rooms
- ID proof required for check-in
- Early check-in subject to availability

Your job is to assist guests politely and professionally like a front desk concierge. Be short and sweet in responses.
If the user asks for directions to a place, and you know the general Google Maps link, provide it directly.
- Spacious and air-conditioned rooms
- Fully equipped kitchenettes
- Complimentary Wi-Fi access
- Housekeeping services upon request
- 24/7 security
- Laundry facilities
- Car parking

We are conveniently located close to major attractions, business centers, and transportation hubs in Chennai. Our friendly staff is always ready to assist you with any queries or requests you may have to make your stay as pleasant as possible.

For bookings and inquiries, please contact us at [Your Phone Number] or reply to this message. We look forward to hosting you at Kolam Serviced Apartments!"""

RESERVATION_EMAIL = "pavank09042009@gmail.com"
EMAIL_USERNAME = "pavank09042009@gmail.com"
EMAIL_PASSWORD = "pasumaddu2009"
MAID_PHONE_NUMBER = "+917358444025"

chat_history = []
memory_log = []

def send_whatsapp_message(message):
    now = datetime.datetime.now() + datetime.timedelta(minutes=1)
    try:
        pywhatkit.sendwhatmsg(MAID_PHONE_NUMBER, message, now.hour, now.minute, wait_time=10)
        return "WhatsApp notification sent to housekeeping."
    except Exception as e:
        return f"Failed to send WhatsApp: {e}"

def send_booking_email(user_query):
    try:
        msg = MIMEText(f"New booking request: '{user_query}'")
        msg['Subject'] = "New Booking Request"
        msg['From'] = EMAIL_USERNAME
        msg['To'] = RESERVATION_EMAIL

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, [RESERVATION_EMAIL], msg.as_string())
        return "Booking email sent."
    except Exception as e:
        return f"Failed to send booking email: {e}"

def build_chat_context():
    return "\n".join(chat_history[-20:])

def bot_response(user_input):
    chat_history.append(f"Guest: {user_input}")
    memory_log.append(f"Guest said: {user_input}")

    prompt = f"""
You are Kolamai, a smart assistant for Kolam Serviced Apartments in Chennai. You have memory of past conversations.

Hotel Info:
{kolam_info}

Memory Log:
{chr(10).join(memory_log[-10:])}

Conversation:
{build_chat_context()}

Guest's message:
\"\"\"{user_input}\"\"\"

Task:
1. Understand what the guest needs, considering past interactions.
2. Reply politely & helpfully.
3. Detect intent (like 'service_request', 'booking_request', 'general_info', 'emergency').
4. If 'service_request', extract the specific item/service (e.g., "soap", "cleaning", "towel").
5. At the end, output this format exactly:
Reply: <Your reply to guest>
Intent: <intent_name>
Item: <item/service requested if any> (or 'none' if not applicable)
6. Don't send everything to housekeeping; analyze the message properly and give answers accordingly.
7. Search the web for real-time data and satisfy the users' requests properly.
8. Give some relevant pictures from the web if required.
9. Give actual data like distance and estimated time from Google Maps if location-related queries arise.
"""

    try:
        response = model.generate_content(prompt)
        full_reply = response.text.strip()

        
        reply = ""
        intent = ""
        item = ""
        for line in full_reply.split('\n'):
            if line.startswith("Reply:"):
                reply = line[len("Reply:"):].strip()
            elif line.startswith("Intent:"):
                intent = line[len("Intent:"):].strip()
            elif line.startswith("Item:"):
                item = line[len("Item:"):].strip()

        chat_history.append(f"Kolamai: {reply}")
        memory_log.append(f"Kolamai replied: {reply}, Intent: {intent}, Item: {item}")

    
        if intent == "service_request" and item != "none":
            action_result = send_whatsapp_message(f"Guest has requested: {item}. Please arrange it.")
            reply += f" ({action_result})"

        elif intent == "booking_request":
            action_result = send_booking_email(user_input)
            reply += f" ({action_result})"

        elif intent == "emergency":
            action_result = send_whatsapp_message(f"Emergency alert: {user_input}")
            reply += f" ({action_result})"

        return {"response": reply}

    except Exception as e:
        error_msg = "Sorry, I'm facing a technical issue. Please try again later."
        chat_history.append(f"Kolamai: {error_msg}")
        memory_log.append(f"Error: {e}")
        return {"response": error_msg}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.form.get("message")
    if not user_message.strip():
        return jsonify({"response": "Please enter a valid message."})
    result = bot_response(user_message)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
