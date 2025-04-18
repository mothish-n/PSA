import streamlit as st
from transformers import pipeline

# Set Streamlit page configuration
st.set_page_config(page_title="📘 Study Notes Generator", layout="centered")

# Load the model pipeline
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-large")

pipe = load_model()

# Function to generate study notes
def generate_notes(topic):
    prompt = f"""Generate detailed study notes about the topic "{topic}". 
Include:
- Key concepts
- Definitions
- Examples
- Clear headings and bullet points."""
    
    result = pipe(prompt, max_length=512, do_sample=True)[0]["generated_text"]
    return result.strip()

# Function to generate a multiple-choice quiz
def generate_quiz(topic):
    prompt = f"""Create one multiple-choice question about "{topic}" in this exact format:
Question: ...
A. ...
B. ...
C. ...
D. ...
Answer: ...
"""

    result = pipe(prompt, max_length=256, do_sample=True)[0]["generated_text"]
    print("[DEBUG RAW OUTPUT]", result)

    try:
        lines = result.strip().split("\n")
        question = next(line for line in lines if line.startswith("Question:")).split(":", 1)[1].strip()
        options = {
            "A": next(line for line in lines if line.startswith("A.")).split("A.")[1].strip(),
            "B": next(line for line in lines if line.startswith("B.")).split("B.")[1].strip(),
            "C": next(line for line in lines if line.startswith("C.")).split("C.")[1].strip(),
            "D": next(line for line in lines if line.startswith("D.")).split("D.")[1].strip(),
        }
        answer = next(line for line in lines if line.startswith("Answer:")).split(":", 1)[1].strip().upper()
        return {
            "question": question,
            "options": options,
            "correct": answer
        }
    except Exception as e:
        print("[Quiz Parsing Error]", e)
        return None

# Streamlit UI
st.title("🎓 Personalized Study Assistant")

menu = st.sidebar.radio("Navigate", ["Home", "📄 Generate Notes", "🧠 Take Quiz", "⚙️ Settings"])

if menu == "Home":
    st.header("📚 Welcome!")
    st.write("Boost your learning with auto-generated notes and quizzes based on any topic!")

elif menu == "📄 Generate Notes":
    st.header("📝 Study Notes Generator")
    topic = st.text_input("Enter a topic for notes:")
    if st.button("Generate Notes"):
        if topic:
            with st.spinner("Generating your notes..."):
                notes = generate_notes(topic)
                st.markdown("### 📖 Your Notes:")
                st.markdown(notes)
        else:
            st.warning("⚠️ Please enter a topic to generate notes.")

elif menu == "🧠 Take Quiz":
    st.header("🎯 Topic-Based Quiz")
    quiz_topic = st.text_input("Enter a topic for quiz:")
    if st.button("Generate Quiz"):
        if quiz_topic:
            with st.spinner("Generating your quiz..."):
                quiz_data = generate_quiz(quiz_topic)
                if quiz_data:
                    st.session_state.quiz = quiz_data
                    st.session_state.score_shown = False
                else:
                    st.error("❌ Could not generate quiz. Try another topic or rephrase.")
        else:
            st.warning("⚠️ Please enter a topic.")

    if "quiz" in st.session_state:
        q = st.session_state.quiz
        st.markdown(f"**Question:** {q['question']}")
        user_answer = st.radio("Choose your answer:", [
            f"A. {q['options']['A']}",
            f"B. {q['options']['B']}",
            f"C. {q['options']['C']}",
            f"D. {q['options']['D']}"
        ])

        if st.button("Submit Answer") and not st.session_state.get("score_shown", False):
            selected_option = user_answer[0]  # A/B/C/D
            correct_option = q["correct"]
            if selected_option == correct_option:
                st.success("✅ Correct Answer!")
            else:
                st.error(f"❌ Incorrect. Correct answer is {correct_option}: {q['options'][correct_option]}")
            st.session_state.score_shown = True

elif menu == "⚙️ Settings":
    st.header("⚙️ Learning Preferences")
    subject = st.selectbox("Preferred Subject", ["Math", "Science", "History", "Computer Science", "English"])
    style = st.radio("Learning Style", ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"])
    goal = st.slider("Daily Study Goal (minutes):", 10, 180, 30)

    if st.button("Save Preferences"):
        st.success("✅ Preferences saved!")
