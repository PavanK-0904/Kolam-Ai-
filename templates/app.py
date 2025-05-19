

from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Replace with your Gemini API key
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

chat_history = []

kolam_info = """
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
"""

def bot_response(user_input):
    chat_history.append(f"Guest: {user_input}")
    prompt = kolam_info + "\n\n" + "\n".join(chat_history) + "\nKolamai:"

    response = model.generate_content(prompt)
    reply = response.text.strip() if response and response.text else "I'm here to help, but I didn’t understand that."

    chat_history.append(f"Kolamai: {reply}")
    return reply

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.form.get("message")
    if user_message.strip() == "":
        return jsonify({"response": "Please enter a valid message."})

    response = bot_response(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)