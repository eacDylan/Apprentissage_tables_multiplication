import streamlit as st
import pandas as pd
import random
from pathlib import Path
    

# --- Génération du DataFrame ---
def generate_dataframe():
    data = []
    for i in range(1, 11):
        for j in range(1, 11):
            data.append({
                "a": i,
                "b": j,
                "result": i * j,
                "score": 1,
                "time_factor": 1,
                "success": 0,
                "fail": 0
            })
    return pd.DataFrame(data)

# --- Import du fichier csv ---
file_path = Path("tables.csv") # Création d'un objet Path avec le chemin du fichier contenant les tables

# --- Initialisation ---
if file_path.is_file():
    st.session_state.df = pd.read_csv(file_path, sep=";")
else:
    if "df" not in st.session_state:
        st.session_state.df = generate_dataframe()

if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "message" not in st.session_state:
    st.session_state.message = ""
if "user_answer" not in st.session_state:
    st.session_state.user_answer = 0
if "question_replied" not in st.session_state:
    st.session_state.question_replied = False

# --- Sélection aléatoire d’une question ---
def new_question():
    weights = st.session_state.df["score"] * st.session_state.df["time_factor"]
    row = st.session_state.df.sample(
        n=1,
        weights=weights
        ).iloc[0]
    st.session_state.current_question = row
    st.session_state.question_replied = False
    st.session_state.pop("user_answer", None) # commande nécessaire pour remettre à zéro le champ réponse

# --- Vérification de la réponse ---
def check_answer(user_answer):
    row = st.session_state.current_question
    correct = row["result"]
    idx = st.session_state.df[
        (st.session_state.df["a"] == row["a"]) & (st.session_state.df["b"] == row["b"])
    ].index[0]

    if user_answer == correct:
        st.session_state.df.at[idx, "success"] += 1
        st.session_state.df.at[idx, "score"] = st.session_state.df.at[idx, "score"] / 2
        st.session_state.df["time_factor"] += 0.1
        st.session_state.df.at[idx, "time_factor"] = 0.1
        st.session_state.message = f"✅ Correct ! {int(row['a'])} × {int(row['b'])} = {int(correct)}"
    else:
        st.session_state.df.at[idx, "fail"] += 1
        st.session_state.df.at[idx, "score"] = st.session_state.df.at[idx, "score"] * 10
        #st.session_state.df["time_factor"] += 0.1
        st.session_state.message = f"❌ Faux ! {int(row['a'])} × {int(row['b'])} = {int(correct)}"
    
    st.session_state.question_replied = True
    st.session_state.df.to_csv(file_path, index=False, sep=";")


# --- Interface Streamlit ---
st.title("🎯 Entraîne-toi aux tables de multiplication (1 à 10)")

if st.session_state.current_question is None:
    new_question()

row = st.session_state.current_question

st.subheader(f"Combien fait {int(row['a'])} × {int(row['b'])} ?")

user_answer = st.number_input("Ta réponse :", min_value=0, step=1, key="user_answer")

if st.button("Valider"):
    if st.session_state.question_replied == False and user_answer != 0:
        check_answer(user_answer)
    elif user_answer == 0:
        st.session_state.message = "Veuillez répondre à la question avant de valider !"
    else:
        st.session_state.message = "Question déjà traitée, cliquez sur Question suivante !"

st.write(st.session_state.message)

if st.button("Question suivante"):
    if st.session_state.question_replied == True:
        new_question()
        st.session_state.message = ""
        st.rerun()
    else:
        st.session_state.message = "Vous devez répondre à la question !"

#st.write(st.session_state.question_replied)
#st.write(st.session_state.user_answer)
#st.write(st.session_state.df.at[idx,"score"] * st.session_state.df.at[idx,"time_factor"])

# --- Stats ---
with st.expander("📊 Voir mes stats"):
    st.dataframe(st.session_state.df)
