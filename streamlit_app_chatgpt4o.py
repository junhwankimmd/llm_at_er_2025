import streamlit as st  # Streamlit 임포트 // Import Streamlit
import time  # 실행 시간 측정을 위한 모듈 // For measuring execution time
import os  # 파일 작업 및 환경변수 처리를 위한 모듈 // For file operations and env variables
import random  # API 딜레이 시뮬레이션을 위한 모듈 // For simulating API delays
from git import Repo  # GitHub 커밋/푸시를 위한 GitPython // For GitHub commit/push
from dotenv import load_dotenv  # .env 파일에서 환경변수 로드 // For loading env variables from .env

load_dotenv()  # .env 파일에서 환경변수 로드 // Load environment variables

# -----------------------------
# GitHub 저장소 경로 설정 // Set GitHub repository path
# -----------------------------
REPO_DIR = "github/junhwankimmd/llm_at_er_2025"
if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)

# -----------------------------
# ChatGPT‑4o용 LLM 설정 // LLM configuration for ChatGPT‑4o
# API Key는 .env 파일에서 불러옵니다. // API key is loaded from .env
# -----------------------------
llm_config = {
    "ChatGPT-4o": {
         "api_key": os.getenv("CHATGPT_4O_API_KEY"),
         "model": "gpt-4o"
    }
}

# -----------------------------
# 연속된 채팅 세션용 API 호출 함수 // API call function for continuous chat session
# (실제 API 호출 코드로 대체 필요) // (Replace with actual API call as needed)
# -----------------------------
def call_llm_api_conversation(llm_name, messages, api_key):
    """
    대화 이력을 포함하여 API 호출을 시뮬레이션합니다.
    Simulates an API call using conversation history.
    """
    start_time = time.time()  # 시작 시간 기록 // Record start time
    simulated_delay = random.uniform(1, 3)  # 1~3초 사이 딜레이 시뮬레이션 // Simulate delay between 1 and 3 seconds
    time.sleep(simulated_delay)
    last_user_message = messages[-1]["content"]
    # 모의 응답: 마지막 유저 입력의 앞 50자 일부를 사용 // Simulated response based on last user input
    response = f"[{llm_name} 응답] Last user input: {last_user_message[:50]}..."
    end_time = time.time()  # 종료 시간 기록 // Record end time
    elapsed_time = end_time - start_time  # 경과 시간 계산 // Calculate elapsed time
    cost = 0.01 * simulated_delay  # 임의 비용 산출 (예: 초당 $0.01) // Simulated cost
    return response, elapsed_time, cost

# -----------------------------
# 단일 케이스 처리 함수 (연속 대화 세션) // Main process function for one case (continuous chat session)
# -----------------------------
def run_case(case_no, step1_query, step2_query):
    # 고정 쿼리 (모든 케이스에서 동일) // Fixed queries for steps that remain the same
    fixed_que_prompt ="""
I want you to think and respond as if you are a doctor with over 10 years of experience in primary care of gynecologic oncology emergency patients when a female cancer patient visits the emergency room with specific symptoms. I would like you to provide guidance on what differential diagnoses should be considered, what tests are necessary, and what subsequent treatments are needed.

I will provide you with a single example case, and for each example, I will ask four sets of questions:

    1. I will provide the basic information of the patient at the time of the ER visit and a brief history before the visit. Based on this, I will ask what tests are necessary for differential diagnosis.
    2. After performing the tests in step 1 (some tests may have been conducted, and some may not have been), I will summarize the results of the tests that were conducted. I will then ask for the most likely presumptive diagnosis (only one final diagnosis) and treatment plans. 
    3. In step 3, I will ask for the actual full order of prescriptions that match the treatment plan suggested in step 2. (For example, V/S check q4hr, I/O check q4hr, NPO, normal saline IV 80cc/hr, 10% dextrose IV 40cc/hr, famotidine IV q12hr, prn ketoprofen IVS q8hr when pain NRS>4, etc.) 
    4. In Step 4, at a level understandable for the patient, I will ask you to provide education on the reasons for the tests performed in Step 1 and how the results have contributed to determining the presumptive diagnosis and treatment plan in Step 2. 

*If there are any additional questions regarding the information I provide or if you feel that a crucial element for your decision-making is missing, please ask additional questions.
""" 
    fixed_step3 = """"Make an actual full detailed example order of prescriptions that match the treatment plan, line by line (from V/S, diet, ambulation or 
    bed rest, I/O (if needed), body weight, BST, fluid (considering volume and nutrition if NPO), H2 blocker or PPI, medications including prn order, etc). 
    Add explanation at the end of the order, not in the middle of the order. """     
    fixed_step4 = """At a level understandable for the patient, provide education on the reasons for the tests performed in Step 1 and how the results have 
    contributed to determining the presumptive diagnosis and treatment plan in Step 2. Summarize the information clearly and in simple terms to ensure the 
    patient can fully understand the purpose and findings of each step in the process. """ 

    # 사용자가 입력한 쿼리와 고정 쿼리를 딕셔너리로 구성 // Assemble queries dictionary
    queries = {
        "Que prompt": fixed_que_prompt,
        "Step 1": step1_query,
        "Step 2": step2_query,
        "Step 3": fixed_step3,
        "Step 4": fixed_step4
    }

    # 시스템 메세지로 사용될 고정 user prompt // Fixed user prompt as system message
    fixed_user_prompt = (
        "You are a professional gynecologic oncologist assistant and coding engineer. "
        "Also, be nice and kind. Think at least three times before answering. Always be logical, mathematical, scientific. "
        "You always answer back with relevant reference you reviewed when you are asked with scientific questions "
        "(for medical questions, you look for PubMed before answering). You are good at visualizing data into graphs and tables. "
        "You are native in Korean and English. Always answer in language which I asked in."
    )

    session_count = 3  # 각 LLM당 세션 수 // Number of sessions per case
    steps = ["Que prompt", "Step 1", "Step 2", "Step 3", "Step 4"]

    # 시간 및 비용 요약을 위한 딕셔너리 // Dictionaries for summarizing time and cost
    time_summary = {}
    cost_summary = {}

    st.write(f"### Processing Case {case_no} with ChatGPT-4o...")  # 케이스 처리 메시지

    for session_no in range(1, session_count + 1):
        st.write(f"**Session {session_no} starting...**")
        # 대화 이력 초기화 (시스템 메세지 포함) // Initialize conversation with system message
        conversation = [{"role": "system", "content": fixed_user_prompt}]
        session_times = {}
        session_costs = {}
        # 각 단계별로 순차적으로 진행 (대화 이력 포함) // Process each step sequentially with conversation history
        for step in steps:
            # 현재 단계의 유저 메세지 추가 // Append user message for current step
            conversation.append({"role": "user", "content": queries[step]})
            response, elapsed, cost = call_llm_api_conversation("ChatGPT-4o", conversation, llm_config["ChatGPT-4o"]["api_key"])
            # 어시스턴트의 응답을 대화 이력에 추가 // Append assistant response to conversation history
            conversation.append({"role": "assistant", "content": response})
            session_times[step] = elapsed
            session_costs[step] = cost
            st.write(f"{step} done - Elapsed time: {elapsed:.2f} sec, Cost: ${cost:.4f}")

        # 개별 세션 대화 내용을 텍스트 파일로 저장 // Save conversation history of the session to a file
        filename = f"case{case_no}_ChatGPT-4o_try{session_no}.txt"
        filepath = os.path.join(REPO_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"Case {case_no} - ChatGPT-4o - Session {session_no}\n")
            for msg in conversation:
                file.write(f"{msg['role']}: {msg['content']}\n")
        st.write(f"File saved: {filename}")

        time_summary[f"session{session_no}"] = session_times
        cost_summary[f"session{session_no}"] = sum(session_costs.values())

    # 시간 요약 파일 저장 // Save time summary file
    time_summary_filename = f"time_case{case_no}_ChatGPT-4o_summary.txt"
    time_summary_filepath = os.path.join(REPO_DIR, time_summary_filename)
    with open(time_summary_filepath, "w", encoding="utf-8") as ts_file:
        ts_file.write("Session, Que prompt time, Step 1 time, Step 2 time, Step 3 time, Step 4 time\n")
        for session_key, times in time_summary.items():
            ts_file.write(
                f"{session_key}, {times['Que prompt']:.2f}, {times['Step 1']:.2f}, "
                f"{times['Step 2']:.2f}, {times['Step 3']:.2f}, {times['Step 4']:.2f}\n"
            )
    st.write(f"Time summary file saved: {time_summary_filename}")

    # 비용 요약 파일 저장 // Save cost summary file
    cost_summary_filename = f"cost_case{case_no}_ChatGPT-4o_summary.txt"
    cost_summary_filepath = os.path.join(REPO_DIR, cost_summary_filename)
    with open(cost_summary_filepath, "w", encoding="utf-8") as cs_file:
        cs_file.write("Session, Total Cost\n")
        for session_key, total_cost in cost_summary.items():
            cs_file.write(f"{session_key}, ${total_cost:.4f}\n")
    st.write(f"Cost summary file saved: {cost_summary_filename}")

    # GitHub에 결과 커밋 및 푸시 // Commit and push results to GitHub
    try:
        repo = Repo(REPO_DIR)
        repo.git.add(A=True)
        commit_message = f"Case {case_no} results update (ChatGPT-4o)"
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push()
        st.success(f"Case {case_no} results committed and pushed to GitHub (ChatGPT-4o).")
    except Exception as e:
        st.error("Error during GitHub commit/push: " + str(e))

# -----------------------------
# Streamlit UI // Streamlit User Interface
# -----------------------------
st.title("LLM Query Executor for Gynecologic Oncology Cases - ChatGPT-4o")
st.write(
    "This app executes queries for gynecologic oncology cases using ChatGPT-4o in a continuous chat session. "
    "Enter the Case Number, Step 1 query, and Step 2 query. Other queries (Que prompt, Step 3, Step 4) are hardcoded. "
    "Press Submit to execute and save results to GitHub. "
    "이 앱은 ChatGPT-4o를 사용하여 부인종양 케이스에 대해 연속된 채팅 세션으로 쿼리를 실행합니다."
)
with st.form(key="chatgpt4o_case_form"):
    case_number = st.number_input("Case Number (케이스 번호)", min_value=1, max_value=15, value=1, step=1)
    step1_query = st.text_area("Step 1 Query (단계 1 질의)", height=100)
    step2_query = st.text_area("Step 2 Query (단계 2 질의)", height=100)
    submit_button = st.form_submit_button("Submit (제출)")
if submit_button:
    run_case(case_number, step1_query, step2_query)
    st.success("Processing completed for ChatGPT-4o.")