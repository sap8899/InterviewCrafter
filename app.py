from flask import Flask, render_template, request, make_response, jsonify
from bardapi import Bard, BardCookies
import re
import os
app = Flask(__name__)

open_prompt = """You are part of an app that teaches people about security.
The application works by providing questions in a certain area, after that,
it receives the customer's answer,and gives it a score according to the level of accuracy.
Also, the application will provide the costumer with the correct answer at the end.

App capabilities:
    1. Creating questions in the field of security
    2. Checking the customer's answers
    3. Scoring the customer's answers between 1 to 10
    4. Provide the correct answer
    5. If the customer does not know the answer and asks for hint, supply a hint

Your output format for each question will be:
question: <your question here>
hint: <hint for question here>
answer: <answer for question here>

The client will give you his or her name, 
Make sure you are:
 1. Simulating a job interview
 2. Using the client name 
Please answer this information 'yes' so that i can continue.
"""

prompt_ad_sec_questions_basic = """
The name of the client is: [NAME]
Your domain is : [FIELD]
Please write 5 questions in this field, so that each question is on a different topic in the field of [FIELD].
Make sure to concentrate on the main topics in this field.
"""


prompt_ad_sec_questions_deep = """
The name of the client is: [NAME]
Your domain is : [FIELD]
Please write 5 deep questions in this field, so that each question is on a different topic in the field of [FIELD].
Make sure to concentrate on the main topics in this field.
These questions need to match advanced level

"""

prompt_get_q = "Please send me only question number X. do not send the hint and do not send the answer"
prompt_get_h = "Please send me the hint for question number X and nothing else"
prompt_get_a = "Please send me the answer for question number X and nothing else"

prompt_get_a_info = """
This is the user's answer:
{here}
 Make sure you answer follows these guidelines:
 1. Simulating a job interview
 2. Using the client name 
  
be very strict when judging the user's answer.

please return the following:
 1. Score between 1 to 10 for the user's answer
 2. explain why you chose this score
 3. the correct answer

"""

prompt_final = """
 Make sure you answer follows these guidelines:
 1. Simulating a job interview
 2. Using the client name 
 
Please give an overall summery for the user:
- Score between 1 to 10
- Why you chose this score
- Recommendations for the user, how to improve his answers
- Suggestions for learning to job interviews in this field
- Add 5 more example questions so the user will be able to keep learning this field

"""
prompt_improve = """
Make sure your response follows these guidelines:
1. simulate job interview , talking to the client and using his name
2. your answers are technically correct
3. your questions are technically correct 

Your response was:
{R}
"""
def create_bard():
    global bard
    cookie_dict = {
        "__Secure-1PSID": "ZghV4ENS-ZZ5R2rTW3h8seGTmh6o-CJaXBDXIco8GrtTheMp3CvbHH2H_TSzcg9-dGZWTw.",
        "__Secure-1PSIDTS": "sidts-CjIBSAxbGRG5T85gPI7MvwjIJCnlKGwOQkgeuifs62-MCxmh6t-uCY1sDz0HNAEU9VWTdRAA",
    }
    bard = BardCookies(cookie_dict=cookie_dict)
    ans = bard.get_answer(open_prompt)['content']
    return ans

def return_string(output_string):
    return output_string


@app.route('/', methods=['GET'])
def index():
    global question_number
    question_number = 1
    return render_template('index.html')


@app.route('/run_function', methods=['POST'])
def run_function():
    global user_name
    data = request.get_json()
    user_name = data['user_name']
    #basic_q = prompt_ad_sec_questions_basic.replace("[NAME]", user_name)
    #deep_q = prompt_ad_sec_questions_deep.replace("[NAME]", user_name)
    print(user_name)
    ans = create_bard()
    #print(ans)
    response = make_response("ok", 200)
    return response

@app.route('/choose_field', methods=['POST'])
def choose_field():
    global field
    data = request.get_json()
    field = data['selected_field']
    response = make_response("ok", 200)
    return response


@app.route('/choose_option', methods=['POST'])
def choose_option():
    global selected_option

    data = request.get_json()
    selected_option = data['selected_option']
    print(selected_option)
    ans = ""
    if selected_option == "easy":
        basic_q = prompt_ad_sec_questions_basic.replace("[NAME]", user_name).replace("[FIELD]", field)
        ans = bard.get_answer(basic_q)['content']
        #print(basic_q)
    if selected_option == "hard":
        deep_q = prompt_ad_sec_questions_deep.replace("[NAME]", user_name).replace("[FIELD]", field)
        ans = bard.get_answer(deep_q)['content']
        #print(deep_q)


    out_string = f"Great! let's start"
    return jsonify(result=return_string(out_string))

@app.route('/start_chat', methods=['POST'])
def start_chat():
    global question_number
    if question_number == 6:
        return jsonify(result=return_string("DONE")),201
    bard_prompt = prompt_get_q.replace("X", str(question_number))
    q = bard.get_answer(bard_prompt)['content']

    double_check_prompt = f"""
    make sure that this text only contains the question and not the answer or parts of it.
     if this text contains the answer, return the question without the answer.
     also, make sure the question is technically correct.
     
    text:
    {q}
    """

    only_q = bard.get_answer(double_check_prompt)['content']
    #tripple_check  = bard.get_answer(prompt_improve.replace("{R}", only_q))['content']
    #print(q)
    print(question_number)
    question_number = question_number + 1
    return jsonify(result=return_string(only_q))

@app.route('/get_ans', methods=['POST'])
def get_ans():
    global question_number
    data = request.get_json()
    user_ans = data['user_ans']
    bard_prompt = prompt_get_a_info.replace("{here}", user_ans)
    a = bard.get_answer(bard_prompt)['content']
    #improved =  bard.get_answer(prompt_improve.replace("{R}", a))['content']
    #print(q)
    return jsonify(result=return_string(a))

@app.route('/final_info', methods=['POST'])
def final_info():
    final_out = bard.get_answer(prompt_final)['content']
    #improved = bard.get_answer(prompt_improve.replace("{R}", final_out))['content']
    return jsonify(result=return_string(final_out))


if __name__ == '__main__':
    app.run(debug=True)
