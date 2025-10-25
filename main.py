from flask import Flask, render_template, request, redirect, url_for
from db import db
from models import Exercicio

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///gymlog.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nome_exercicio = request.form[home]
        grupo_muscular_exercicio = request.form['grupo_muscular']
        novo_exercicio = Exercicio(nome=nome_exercicio, grupo_muscular=grupo_muscular_exercicio)

    try:
        db.session.add(novo_exercicio)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Erro ao adicionar exercício: {e}"
    else:
        exercicios = Exercicio.query.order_by(Exercicios.nome).all()
        return render_template('exercicios.html', exercicios=exercicios)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)