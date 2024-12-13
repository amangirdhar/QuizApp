from crewai import Task
from tools import tool
from agents import question_generator,question_generator_previous ,additional_information , study_material

question_generator_task = Task(
    description=(
        "Generate a specified number of multiple-choice questions (MCQs) based on a given topic and difficulty level. "
        "Each question should have 4 options, with only one correct answer."
    ),
    expected_output=(
        "A list of multiple-choice questions (MCQs) related to the topic, formatted as follows:\n"
        "**Question X:**\n\nQuestion?\n\n(A) OptionA\n(B) OptionB\n(C) OptionC\n(D) OptionD\n\nResult: A/B/C/D"
    ),
    tools=[tool],
    agent=question_generator,
    verbose=True
)


question_generator_previous_task = Task(
    description=(
        "Generate a specified number of multiple-choice questions (MCQs) based on a given topic, difficulty level, and the user's previous responses. "
        "Each question should address areas where the user has shown difficulty, with 4 options and only one correct answer."
    ),
    expected_output=(
        "A list of multiple-choice questions (MCQs) related to the topic, focusing on the user's weak areas, formatted as follows:\n"
        "**Question X:**\n\nQuestion?\n\n(A) OptionA\n(B) OptionB\n(C) OptionC\n(D) OptionD\n\nResult: A/B/C/D"
    ),
    tools=[tool],
    agent=question_generator_previous,
    verbose = True  
)

additional_information_task = Task(
    description=(
        "Provide necessary background information for answering specific questions related to a given question. "
        "The information should be summarized and directly relevant to the question at hand."
    ),
    expected_output=(
        "A summarized view of relevant information needed to answer the question, formatted as follows:\n"
        "**Question:** {question}\n\n**Information:**\n\n[Summarized information here]"
    ),
    tools=[tool],
    agent=additional_information,
    verbose=True  
)

study_material_task = Task(
    description=(
        "Gather and provide all relevant study material related to a specific topic. "
        "This includes links, snippets, research papers, and any other valuable resources."
        "Provide top 5 links only"
    ),
    expected_output=(
        "A top 5 list of study materials related to the topic, formatted as follows:\n"
        "**Topic:** {topic}\n\n**Study Materials:**\n\n[Links, snippets, research papers, etc.]"
    ),
    tools=[tool],
    agent=study_material,
    verbose=True  
)