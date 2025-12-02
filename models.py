from db import db

class Exercicio(db.Model):
    __tablename__ = 'exercicios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    grupo_muscular = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Exercicio {self.nome}>'
    
class SessaoTreino(db.Model):
    __tablename__ = 'sessao_treino'

    id = db.Column(db.integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    series = db.relationship('SerieExercicio', backref='sessao', lazy=True)

class SerieExercicio(db.Model):
    __tablename__ = 'series_exercicio'

    id = db.Column(db.Integer, primary_key=True)
    repeticoes = db.Column(db.Integer, nullable=False)
    carga = db.Column(db.Float, nullable=True)
    exercicio_id = db.Column(db.Integer, db.ForeignKey('exercicios.id'), nullable=False)
    exercicio = db.relationship('Exercicio', backref='series')
    sessao_id = db.Column(db.Integer, db.ForeignKey('sessao_treino.id'), nullable=False)
