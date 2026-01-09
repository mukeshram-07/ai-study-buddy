AI-Powered Study Buddy

AI-Powered Study Buddy is a web-based academic assistant designed to help students **learn, revise, and prepare for exams efficiently**.  
The application combines large language models with visual learning aids to provide explanations, summaries, quizzes, flashcards, flowcharts, and exam-focused key points.

Features

 Explain Topic
- Clear, student-friendly explanations
- Automatically displays **related images** for better visual understanding

 Summarize Notes
- Converts long notes into **concise bullet-point summaries**
- Ideal for quick revision

 Generate Quiz
- Creates **topic-specific quiz questions with answers**
- Helps in self-assessment and practice

 Generate Flashcards
- Produces flashcards in **structured card format**
- Uses JSON-based generation to ensure consistent formatting

 Generate Flowchart
- Automatically creates:
  - Mermaid-based visual flowcharts
  - Step-by-step vertical process timeline
  - Simple beginner-friendly explanation
- Includes **related diagrams/images**

 Exam Quick Revision (Key Feature)
- Generates **high-yield exam key points**
- Short, crisp, memory-oriented points
- Perfect for last-minute exam preparation
- 
 History
- View and revisit previously generated content



Tech Stack

- **Frontend & UI:** Streamlit  
- **Backend / AI:** Groq LLM (LLaMA 3.1)  
- **Image API:** Pexels API  
- **Language:** Python  

Project Structure

ai-study-buddy/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── LICENSE
│
├── docs/
│ ├── architecture.md
│ └── features.md
│
└── screenshots/
├── home.png
├── flashcards.png
└── flowchart.png

