from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import json
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage

load_dotenv()


# Load your CV into JSON (extracted from your PDF)
cv_data = {
  "name": "Kavya G.A.C.",
  "contact": {
    "email": "ckchamindukavya@gmail.com",
    "linkedin": "https://www.linkedin.com/in/chamindu-kavya/",
   
  },
  "summary": "A passionate Computer Science and Engineering undergraduate with a strong focus on web development and a growing interest in LLM engineering. Skilled in building full-stack web applications using technologies like Next.js, React, Tailwind CSS, MongoDB, and Spring Boot. Enthusiastic about exploring AI applications in web platforms, including chatbots and LLM-powered tools. Also experienced in 2D game development with Unity. Interested in learning and collaborating on challenging projects in software development.",
  "education": [
    {
      "university": "University of Moratuwa",
      "date": "March 2023",
      "degree": "B.Sc. Undergraduate in Computer Science and Engineering"
    }
  ],
  "projects": [
    {
      "name": "MSRA - Medical exam prep platform",
      "link": "acemsra.com",
      "description": [
        "Developed a web application for MSRA exam preparation featuring user and admin interfaces.",
        "Users can register, make payments via Stripe, access and attempt quizzes, review their past attempts, and leave comments on individual questions. The admin panel enables efficient management of quizzes and user-related data"
      ],
      "tools": "MongoDB, NextJs, Tailwind CSS, TypeScript"
    },
    {
      "name": "Air Plane Reservation System",
      "link": "GitHub",
      "description": [
        "Worked as part of a team on an airplane reservation system as semester 3 database project.",
        "In this project, I contribute to both the front-end and back-end, designing user interfaces for flight search, seat selection, and booking confirmation, ensuring an intuitive user experience."
      ],
      "tools": "MySQL, NextJs, Tailwind CSS, TypeScript"
    },
    {
      "name": "Online Tutor Platform (on-going)",
      "link": "GitHub",
      "description": [
        "A web-based learning platform that allows students to connect with tutors, access study materials, take quizzes, and track their progress, while tutors can manage content and interact with students in real time."
      ],
      "tools": "PostgreSQL, NextJs, Tailwind CSS, TypeScript, SpringBoot"
    },
    {
      "name": "Candle Night",
      "link": "celestia.uomleos.org",
      "description": [
        "Worked as part of a team on web development project for book tickets and order foods for a event that oraganized by leo club."
      ],
      "tools": "MongoDB, NextJs, Tailwind CSS, TypeScript"
    },
    {
      "name": "CSE 40 website",
      "link": "cse40.cse.uom.lk",
      "description": [
        "Worked as part of a team on web development project for 40th anniversary of department of computer science university of moratuwa."
      ],
      "tools": "MongoDB, NextJs, Tailwind CSS, TypeScript"
    },
    {
      "name": "Shilpa - Educational Resource and Quiz Platform",
      "link": "shilpa.org",
      "description": [
        "Contributed to the development of Shilpa, a web-based educational platform for A/L and O/L exam preparation.",
        "Developed core backend features including resource downloads, teacher advertisements, interactive quizzes with instant feedback, and an admin panel for managing content and users."
      ],
      "tools": "TypeScript, Tailwind CSS, Next.js, MongoDB"
    },
    {
      "name": "MERCON website",
      "link": "mercon.uom.lk",
      "description": [
        "Collaborated with a team to develop a professional website for an international research conference organized by the University of Moratuwa.",
        "Implemented core features to showcase conference schedules, speaker profiles, paper submissions, and registration processes."
      ],
      "tools": "JavaScript, css, html"
    },
    {
      "name": "Desert Monster",
      "link": "GitHub",
      "description": [
        "Developed an engaging Android game using Unity. This project was a creative hobby, allowing me to explore game development in Unity and experiment with C# scripting."
      ],
      "tools": "C#, Unity"
    },
    {
      "name": "3D Shooting Game",
      "link": "GitHub",
      "description": [
        "Developed a real-time 3D multiplayer game using Unity, featuring networked player interactions, character animations, and immersive environments for engaging gameplay."
      ],
      "tools": "C, unity"
    }
  ],
  "volunteeringExperience": [
    {
      "role": "CSE40 2025 - Web Team Member",
      "description": "Volunteered as part of the web committee for the CSE 40 event, celebrating 40 years of the CSE department."
    },
    {
      "role": "Celestia 2025 - Web Team Member",
      "description": "Volunteered as part of the web committee for the celesta event oraganized by Leo club of university Moratuwa."
    },
    {
      "role": "MERCON 2025 - Web Team Member",
      "description": "Volunteered as part of the web committee for the MERCON - Moratuwa Engineering Research Conference."
    },
    {
      "role": "SLIOT - 2025",
      "description": "Volunteered as part of the Delegate Handling committee"
    }
  ],
  "technologies": {
    "languages": "Python, C++, C, Java, C#, SQL, JavaScript, SQL, HTML, CSS",
    "technologies": "NextJS, React Native(Expo), Spring Boot, NestJs",
    "gameDevelopment": "Unity Engine",
    "databases": "MongoDB, MySQL, PostgreSQL",
    "llmEngineering": "RAG, LangChain, OpenAI API, Vector Search with MongoDB"
  },
  "certificates": [
    {
      "name": "LLM Engineering",
      "link": "Certificate"
    }
  ],
  "references": [
    {
      "name": "Prof. Dulani Meedeniya",
      "position": "Professor, Department of Computer Science and Engineering, University of Moratuwa",
      "email": "dulanim@cse.mrt.ac.lk"
    },
    {
      "name": "Dr. Adeesha Wijayasiri",
      "position": "Senior Lecturer, Department of Computer Science and Engineering, University of Moratuwa",
      "email": "adeeshaw@cse.mrt.ac.lk"
    }
  ],
  "declaration": "I hereby declare that the information provided above is true and correct to the best of my knowledge and that I assume full responsibility for its accuracy."
}

app = FastAPI()

llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)

class ChatRequest(BaseModel):
    messages: List[str]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print("Received request:****************", request)
    system_prompt = f"""
    You are a chatbot that answers only based on the following CV data:
    {json.dumps(cv_data, indent=2)}
    Be concise and friendly.
    """

    conversation = [AIMessage(content=system_prompt)]
    for msg in request.messages:
        conversation.append(HumanMessage(content=msg))

    def generate():
        for chunk in llm.stream(conversation):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")
