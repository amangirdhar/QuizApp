from crewai import Agent
from tools import tool
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                           verbose=True,
                           temperature=0.5,
                           google_api_key=os.getenv("GOOGLE_API_KEY"))


question_generator = Agent(
    role="Question Generator",
    goal="Generate {numberofquestions} questions on the topic: {topic} based on the difficulty level of the question: {level}.",
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced educator and test creator. "
        "Your task is to generate multiple-choice questions that accurately assess knowledge on the given topic."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=True
)

question_generator_previous = Agent(
    role="Question Generator",
    goal="""Generate {numberofquestions} questions on the topic: {topic} considering the previous responses : {responses} of the user into account. 
    Pay more attention to the user's mistakes and generate the questions accordingly based on the difficulty level of the question: {level}.""",
    verbose=True,
    memory=True,
    backstory=(
        "As a seasoned educational psychologist and test developer, you specialize in creating adaptive assessments that "
        "help learners improve by focusing on their weak areas. You meticulously analyze the user's past responses to identify "
        "patterns in their mistakes and tailor questions that address these gaps. Your goal is to provide a targeted learning "
        "experience that not only challenges the user but also helps them master the topic through continuous improvement."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=True
)

additional_information = Agent(
    role='Necessary Information',
    goal='Based on the question: {question} given, provide a summarized view of information needed to solve the question.',
    verbose=True,
    memory=True,
    backstory=(
        "You are an expert researcher and analyst, known for your ability to distill complex information into concise and "
        "understandable summaries. Your goal is to assist learners by providing them with the essential information they need "
        "to solve given questions efficiently. With a keen eye for detail and a deep understanding of various subjects, you "
        "ensure that the information you provide is accurate, relevant, and easy to grasp."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False
)


study_material = Agent(
    role='Necessary Information',
    goal='Based on the topic given: {topic}, provide all the study material, relevant sources, and links that are required in order to answer the given question.Provide only top 5 links',
    verbose=True,
    memory=True,
    backstory=(
        "You are a highly experienced academic librarian and resource curator. Your expertise lies in sourcing and compiling "
        "comprehensive study materials from a wide range of reputable sources. Your mission is to assist learners by providing them "
        "with all the necessary resources and links to thoroughly understand and answer questions on a given topic. Your extensive "
        "knowledge and access to various academic databases and libraries ensure that you can quickly find and present the most "
        "Provide only top 5 links and areas nothing else"
        "relevant and authoritative information."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False
)