# AI-Driven Public Health Chatbot for Disease Awareness

This project is a prototype of an **AI-driven chatbot** designed to educate rural and semi-urban populations about:
- Preventive healthcare
- Common disease symptoms
- Vaccination schedules

The chatbot is built as a **Flask** backend and is connected to **WhatsApp using Twilio**. Users can send a WhatsApp message and receive automated health information responses.

---

## Features (Prototype)

- Receives user messages from WhatsApp via a **Twilio webhook**
- Processes the text and matches it to predefined health information
- Sends back responses about:
  - Preventive measures
  - Symptoms of common diseases
  - General vaccination info
- Designed as an academic prototype for public–health awareness

> **Note:** This is a learning/academic project and **not** a real medical tool.  
> It should **not** be used for professional medical advice.

---

## Tech Stack

- **Backend:** Python, Flask  
- **Messaging Integration:** Twilio WhatsApp API  
- **Data:** Static / hard-coded health information (e.g., dictionaries, lists, or files)

---

## How to Run (Backend)

1. Install dependencies:

   ```bash
   pip install flask twilio
2. Set your Twilio credentials as environment variables or in a config file (not committed to GitHub):

   ```text
   TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID
   TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

Run the Flask app:

python app.py


In the Twilio console, configure the WhatsApp sandbox to send incoming messages to your Flask endpoint (for example /whatsapp).

---

Current Status & Limitations:

Responses are rule-based and may not always be accurate or complete.

No real government health database integration yet (static information only).

Prototype level; meant for experimentation and learning with Flask + Twilio.
