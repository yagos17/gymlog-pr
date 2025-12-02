from flask import Flask, render_template, request, redirect, url_for, jsonify
from db import db
from models import Exercicio, SessaoTreino, SerieExercicio
from datetime import date, datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gymlog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        nome_exercicio = request.form['nome']
        grupo_muscular_exercicio = request.form['grupo_muscular']

        novo_exercicio = Exercicio(nome=nome_exercicio, grupo_muscular=grupo_muscular_exercicio)

        try:
            db.session.add(novo_exercicio)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            return f"Erro ao adicionar exercício: {e}"

    else:
        exercicios = Exercicio.query.order_by(Exercicio.nome).all()
        return render_template('exercicios.html', exercicios=exercicios)

@app.route('/registrar_treino', methods=['GET', 'POST'])
def registrar_treino():
    if request.method == 'POST':
        try:
            data_str = request.form['data']
            data_sessao = datetime.strptime(data_str, '%Y-%m-%d').date()

            nova_sessao = SessaoTreino(data=data_sessao)
            db.session.add(nova_sessao)
            db.session.commit()

            return redirect(url_for('adicionar_series', sessao_id=nova_sessao.id)) 

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar sessão: {e}"
        
    today_date = date.today().isoformat()
    return render_template('registrar_treino.html', today_date=today_date)

@app.route('/treino/<int:sessao_id>/adicionar_series', methods=['GET', 'POST'])
def adicionar_series(sessao_id):

    sessao = SessaoTreino.query.get_or_404(sessao_id)
    exercicios_disponiveis = Exercicio.query.order_by(Exercicio.nome).all()
    
    if request.method == 'POST':
        exercicio_id = request.form['exercicio_id']
        repeticoes = request.form['repeticoes']
        carga = request.form.get('carga') 

        try:
            nova_serie = SerieExercicio(
                sessao_id=sessao_id,
                exercicio_id=exercicio_id,
                repeticoes=repeticoes,
                carga=carga if carga else None 
            )
            
            db.session.add(nova_serie)
            db.session.commit()
            
            return redirect(url_for('adicionar_series', sessao_id=sessao_id))
            
        except Exception as e:
            db.session.rollback()
            return f"Erro ao adicionar série: {e}"

    series_da_sessao = SerieExercicio.query.filter_by(sessao_id=sessao_id).order_by(SerieExercicio.id).all()
    
    return render_template('adicionar_series.html', 
                           sessao=sessao, 
                           exercicios=exercicios_disponiveis,
                           series=series_da_sessao)

@app.route('/api/exercicio/<int:exercicio_id>/progresso')
def progresso_exercicio_json(exercicio_id):

    series = SerieExercicio.query.filter_by(exercicio_id=exercicio_id).all()

    dados_grafico = {}

    for serie in series:
        data_str = serie.sessao.data.strftime('%Y-%m-%d')
        carga = serie.carga if serie.carga is not None else 0.0

        if data_str not in dados_grafico or carga > dados_grafico[data_str]:
            dados_grafico[data_str] = carga

    datas = sorted(dados_grafico.keys())
    cargas = [dados_grafico[data] for data in datas]

    return jsonify({
        'labels': datas,
        'data': cargas
    })

@app.route('/delete/<int:id>')
def delete_exercicio(id):
    exercicio = Exercicio.query.get_or_404(id)
    try:
        db.session.delete(exercicio)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Erro ao excluir exercício: {e}"
    
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
    
    else:
        return render_template('editar_exercicio.html', exercicio=exercicio)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)