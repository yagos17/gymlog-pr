from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, date
from db import db
from models import Exercicio, SessaoTreino, SerieExercicio
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__) 

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- HOME (LISTA E CADASTRO DE EXERCÍCIOS) ---------------- #

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nome = request.form['nome']
        grupo = request.form['grupo_muscular']

        novo = Exercicio(nome=nome, grupo_muscular=grupo)

        try:
            db.session.add(novo)
            db.session.commit()
        except Exception as e:
            return f"Erro ao adicionar exercício: {e}"

        return redirect(url_for('home'))

    exercicios = Exercicio.query.order_by(Exercicio.nome).all()
    return render_template('exercicios.html', exercicios=exercicios)


# ---------------- REGISTRAR TREINO ---------------- #

@app.route('/registrar_treino', methods=['GET', 'POST'])
def registrar_treino():
    if request.method == 'POST':
        try:
            data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
            sessao = SessaoTreino(data=data)

            db.session.add(sessao)
            db.session.commit()

            return redirect(url_for('adicionar_series', sessao_id=sessao.id))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar sessão: {e}"

    today = date.today().isoformat()
    return render_template('registrar_treino.html', today_date=today)


# ---------------- ADICIONAR SÉRIES ---------------- #

@app.route('/treino/<int:sessao_id>/adicionar_series', methods=['GET', 'POST'])
def adicionar_series(sessao_id):

    sessao = SessaoTreino.query.get_or_404(sessao_id)
    exercicios = Exercicio.query.order_by(Exercicio.nome).all()

    if request.method == 'POST':
        try:
            serie = SerieExercicio(
                sessao_id=sessao_id,
                exercicio_id=request.form['exercicio_id'],
                repeticoes=request.form['repeticoes'],
                carga=request.form.get('carga') or None
            )

            db.session.add(serie)
            db.session.commit()

            return redirect(url_for('adicionar_series', sessao_id=sessao_id))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao adicionar série: {e}"

    series = SerieExercicio.query.filter_by(sessao_id=sessao_id).all()

    return render_template(
        'adicionar_series.html',
        sessao=sessao,
        exercicios=exercicios,
        series=series
    )


# ---------------- API PARA O GRÁFICO ---------------- #

@app.route('/api/exercicio/<int:id>/progresso')
def progresso_exercicio_json(id):
    series = SerieExercicio.query.filter_by(exercicio_id=id).all()

    dados = {}
    for s in series:
        data = s.sessao.data.strftime('%Y-%m-%d')
        carga = s.carga or 0

        if data not in dados or carga > dados[data]:
            dados[data] = carga

    return jsonify({
        'labels': list(dados.keys()),
        'data': list(dados.values())
    })


# ---------------- EDITAR E EXCLUIR EXERCÍCIO ---------------- #

@app.route('/delete/<int:id>')
def delete_exercicio(id):
    exercicio = Exercicio.query.get_or_404(id)
    try:
        db.session.delete(exercicio)
        db.session.commit()
    except Exception as e:
        return f"Erro ao excluir exercício: {e}"

    return redirect(url_for('home'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_exercicio(id):
    exercicio = Exercicio.query.get_or_404(id)

    if request.method == 'POST':
        exercicio.nome = request.form['nome']
        exercicio.grupo_muscular = request.form['grupo_muscular']

        try:
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            return f"Erro ao editar exercício: {e}"

    return render_template('editar_exercicio.html', exercicio=exercicio)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)