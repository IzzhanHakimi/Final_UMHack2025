![image](https://github.com/user-attachments/assets/10e7b05a-343f-4073-b124-9ae3d429b4af)

# Final_UMHack2025!
Brought to you by Group Ctrl C, Ctrl V !

## Technical Documentation
https://docs.google.com/document/d/1cXjXFpVgq6qbZicm1CYq4AiodvkLz44zRLexPidmNf4/edit?usp=sharing

## Presentation Link
https://www.canva.com/design/DAGkPyNxdnk/phOQBOu-WcV5wduhDWe9FQ/edit?utm_content=DAGkPyNxdnk&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

## Figma Prototype (for Mobile App)
https://www.figma.com/design/L7TvvRBIr4VUq02b4eq0d5/Untitled?node-id=0-1&t=0CX2ag1VvLqJjVvO-1

## About Our Product
### 📌 Overview
MEX Assistant is a real-time, chat-based analytics tool built for food delivery merchants. It uses OpenAI’s GPT-4o to convert natural language questions into insights — like revenue trends, peak hours, or late deliveries — with charts, summaries, and downloadable reports. It’s built for small-to-mid-sized F&B businesses who want data-driven decisions without technical complexity.

### 🧱 System Architecture
#### 1. Frontend (Streamlit UI):
Chat-based dashboard with dynamic visual feedback
Merchant login and session tracking

#### 2. Backend Logic:
Handles natural language input → Python code via GPT-4o
Generates graphs and exports (PDF, PPTX)
Maintains session state for context-aware interaction

#### 3. Analytics Engine:
Converts queries to code (NLP-to-Code prompting)
Simulates live order activity using CSV manipulation
Visualizes metrics with Matplotlib & Seaborn

#### 4. Data Layer:
Works with CSVs (e.g., Bagel Bros & Noodle Nest)
Merges and filters by merchant/date

#### 5. External Integrations:
OpenAI API: Chat understanding & code generation
Twilio API: SMS alerts for delays
ReportLab & python-pptx: Export reports

### 🔁 Workflow
Question → GPT-4o interprets → Python code runs → Graphs/insights returned → Optional alerts/reports generated

### 💡 Features
1. Natural language queries → auto-generated insights
2. Real-time simulation of orders
3. Exportable reports (PDF/PPTX)
4. Multi-merchant support
5. Mobile-friendly UI with custom CSS

### 🚀 Deployment Ready
1. Works on Streamlit Cloud
2. Easily extendable with Firebase/PostgreSQL
3. .env for secure API key handling
4. Scalable design with modular components

### ✅ Testing & Validation
1. Tested with various merchant queries
2. Validated graphs across time filters
3. Export features tested with different chat histories

### 🏁 Conclusion
MEX Assistant is a plug-and-play AI analytics tool tailored for food delivery businesses. With real-time data simulation, chat-based insights, and intuitive exports — it empowers merchants to make smarter decisions without needing a data team.



