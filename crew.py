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
