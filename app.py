from flask import Flask, render_template, request, redirect, session
import json
import random

app = Flask(__name__)
app.secret_key = "historia-app"

with open("questions.json", encoding="utf-8") as f:
    DATA = json.load(f)

@app.route("/")
def index():
    progress = session["progress"] if "progress" in session else []
    return render_template(
        "index.html",
        stages=DATA["stages"],
        progress=progress
    )

@app.route("/stage/<stage_id>", methods=["GET", "POST"])
def stage(stage_id):
    stage_data = next(s for s in DATA["stages"] if s["id"] == stage_id)

    q_key = f"q_{stage_id}"
    e_key = f"errors_{stage_id}"
    list_key = f"questions_{stage_id}"

    # inicialização da fase (sorteio)
    if list_key not in session:
        total_indexes = list(range(len(stage_data["questions"])))
        session[list_key] = random.sample(total_indexes, 8)
        session[q_key] = 0
        session[e_key] = 0

    error_msg = None

    if request.method == "POST":
        selected = int(request.form["option"])
        current_q = session[q_key]

        real_index = session[list_key][current_q]
        correct = stage_data["questions"][real_index]["answer"]

        if selected == correct:
            session[q_key] += 1
        else:
            session[e_key] += 1
            error_msg = "Resposta incorreta."

            if session[e_key] >= 2:
                session.pop(q_key)
                session.pop(e_key)
                session.pop(list_key)
                return render_template(
                    "popup.html",
                    message="Você errou duas vezes nesta fase."
                )

    # fase concluída (8 perguntas respondidas)
    if session[q_key] >= 8:
        if "progress" not in session:
            session["progress"] = []

        if stage_id not in session["progress"]:
            session["progress"].append(stage_id)

        session.pop(q_key)
        session.pop(e_key)
        session.pop(list_key)

        # REDIRECIONA PARA PÁGINA DE CONFETE (MESMO TEMPLATE DO POPUP, MAS COM FLAG)
        return render_template(
            "popup.html",
            message=f"Parabéns! Você concluiu a fase: {stage_data['title']}",
            celebration=True
        )

    # pergunta atual (a partir do sorteio)
    real_index = session[list_key][session[q_key]]
    question = stage_data["questions"][real_index]
    errors = session[e_key]

    return render_template(
        "stage.html",
        stage=stage_data,
        question=question,
        error=error_msg,
        errors=errors
    )

if __name__ == "__main__":
    app.run(debug=True)
