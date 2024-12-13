from send_mess import send_message
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import re
import firebase_admin
from firebase_admin import credentials, firestore
from fpdf import FPDF

app = FastAPI()
from crewai import Crew,Process
from tasks import question_generator_task , question_generator_previous_task , additional_information_task ,study_material_task
from agents import question_generator , question_generator_previous , additional_information , study_material

crew=Crew(
    agents=[question_generator],
    tasks=[question_generator_task],

)

crew_previous = Crew(
    agents= [question_generator_previous],
    tasks= [question_generator_previous_task]
)

crew_study_material = Crew(
    agents= [study_material],
    tasks=[study_material_task]
)

crew_neccessary_information = Crew(
    agents= [additional_information],
    tasks= [additional_information_task]
)

cred = credentials.Certificate("C:/PROJECTS/Quiz App/quizapp-7bc35-firebase-adminsdk-4denh-cb7f1c9dab.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://quizapp-7bc35-default-rtdb.firebaseio.com/"})

db = firestore.client()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def generate_questions(topic, number_of_questions, level):
    result = crew.kickoff(inputs={'topic': topic, 'numberofquestions': number_of_questions, 'level': level})
    if hasattr(result, 'text'):
        result_text = result.text
    elif hasattr(result, 'get'):
        result_text = result.get('text', '')
    else:
        result_text = str(result)
    return result_text

def from_previous_question(topic, number_of_questions, previous, level):
    result = crew_previous.kickoff(inputs={'topic': topic, 'numberofquestions': number_of_questions, 'level': level, 'responses': previous})
    if hasattr(result, 'text'):
        result_text = result.text
    elif hasattr(result, 'get'):
        result_text = result.get('text', '')
    else:
        result_text = str(result)
    return result_text


def create_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for line in content:
        pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln()
    
    pdf.output(filename)

def parse_questions(questions_text):
    if isinstance(questions_text, str):
        question_pattern = re.compile(r"\*\*Question \d+:\*\*\n\n(.+?)\n\n\(A\) (.+?)\n\(B\) (.+?)\n\(C\) (.+?)\n\(D\) (.+?)\n\nResult: (.+)")
        matches = question_pattern.findall(questions_text)
        questions = []
        for match in matches:
            questions.append({
                "question": match[0],
                "option_a": match[1],
                "option_b": match[2],
                "option_c": match[3],
                "option_d": match[4],
                "result": match[5]
            })
        return questions
    else:
        print("Unexpected format for questions_text")
        return []


def provide_question(question):
    result = crew_neccessary_information.kickoff(inputs= {'question' : question})
    if hasattr(result, 'text'):
        result_text = result.text
    elif hasattr(result, 'get'):
        result_text = result.get('text', '')
    else:
        result_text = str(result)
    return result_text


def scholar_section(topic):
    result = crew_study_material.kickoff(inputs= {'topic' : topic})
    if hasattr(result, 'text'):
        result_text = result.text
    elif hasattr(result, 'get'):
        result_text = result.get('text', '')
    else:
        result_text = str(result)
    return result_text

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

db = firestore.client()


@app.get("/leaderboard", response_class=HTMLResponse)
async def get_leaderboard(request: Request):
    try:
        collection_ref = db.collection('user_responses')
        docs = collection_ref.stream()
        documents = []
        for doc in docs:
            data = doc.to_dict()
            print(f'Document Data: {data}') 
            documents.append({
                'id': doc.id,
                'name': data.get('name', 'N/A'),
                'score': data.get('score', 0),
                'topic': data.get('topic', 'N/A')  
            })
        
        documents.sort(key=lambda x: x['score'], reverse=True)
    
        return templates.TemplateResponse("leaderboard.html", {"request": request, "leaderboard": documents})
    
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})

@app.post("/generate_quiz", response_class=HTMLResponse)
async def generate_quiz(request: Request, name: str = Form(...), email: str = Form(...), topic: str = Form(...), num_questions: int = Form(...), level: str = Form(...)):
    try:
        print(f"Received topic: {topic}, level: {level}")
        
        existing_user = db.collection("user_responses").where("email", "==", email).get()
        
        if existing_user:
            previous_responses = []
            for user in existing_user:
                user_data = user.to_dict()
                if "responses" in user_data:
                    previous_responses.extend(user_data["responses"])
            previous_responses_str = ', '.join([f"{response['question']}: {response['user_answer']}" for response in previous_responses])
            questions_text = from_previous_question(topic, num_questions, previous_responses_str, level)
        else:
            questions_text = generate_questions(topic, num_questions, level)
        
        questions = parse_questions(questions_text)
        
        return templates.TemplateResponse("quiz.html", {
            "request": request,
            "name": name,
            "email": email,
            "topic": topic,
            "num_questions": num_questions,
            "questions": questions
        })
    except Exception as e:
        print(f"Error generating quiz: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})

@app.post("/submit_quiz", response_class=HTMLResponse)
async def submit_quiz(request: Request):
    try:
        form = await request.form()
        
        name = form.get("name", "").strip()
        email = form.get("email", "").strip()
        topic = form.get("topic", "").strip()
        print(f"Topic is: {topic}")
        
        question_keys = [key for key in form.keys() if key.startswith("question_")]
        total_questions = len(question_keys)
        score = 0
        
        questions = []
        
        for i in range(total_questions):
            question_key = f"question_{i}"
            user_answer = form.get(question_key, "").strip()
            
            if not user_answer:
                continue
            
            correct_answer = form.get(f"correct_answer_{i}", "").strip()
            question_text = form.get(f"question_text_{i}", "").strip()
            option_a = form.get(f"option_a_{i}", "").strip()
            option_b = form.get(f"option_b_{i}", "").strip()
            option_c = form.get(f"option_c_{i}", "").strip()
            option_d = form.get(f"option_d_{i}", "").strip()
            
            correct_answer = correct_answer.split(":")[0].strip()  
            correct_answer = correct_answer[0]
            
            if question_text:
                questions.append({
                    "question": question_text,
                    "option_a": option_a,
                    "option_b": option_b,
                    "option_c": option_c,
                    "option_d": option_d,
                    "user_answer": user_answer,
                    "result": correct_answer,
                    "additional_info": provide_question(question_text) if question_text else ""
                })
            
                if user_answer == correct_answer:
                    score += 10
        
        max_score = len(questions) * 10
        
        user_data = {
            "name": name,
            "email": email,
            "responses": [{
                "question": q["question"],
                "user_answer": q["user_answer"],
                "correct_answer": q["result"]
            } for q in questions],
            "score": score
        }
        db.collection("user_responses").add(user_data)

        study_material = []
        if topic:
            study_material = scholar_section(topic)
            if not study_material or "No results found." in study_material:
                study_material = ["No study material found for this topic."]
            else:
                print(f"Study material for topic '{topic}' fetched successfully.")
        else:
            print("No valid topic provided, skipping study material retrieval.")
            study_material = ["No topic was provided, so no study material could be retrieved."]
        
        create_pdf(study_material, "study_material.pdf")
        create_pdf([f"Your score: {score}/{max_score}"] + [
            f"Question: {q['question']}\nOptions:\n(A) {q['option_a']}\n(B) {q['option_b']}\n(C) {q['option_c']}\n(D) {q['option_d']}\nYour Answer: {q['user_answer']}\nCorrect Answer: {q['result']}\nAdditional Info: {q['additional_info']}"
            for q in questions], "quiz_result.pdf")

        send_message(name, email, "quiz_result.pdf", "study_material.pdf")
        
        return templates.TemplateResponse("quiz_result.html", {
            "request": request,
            "name": name,
            "email": email,
            "questions": questions,
            "score": score,
            "total_questions": len(questions),
            "max_score": max_score
        })
    except Exception as e:
        print(f"Error submitting quiz: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
