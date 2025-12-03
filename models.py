from db import db

class Exercicio(db.Model):
    __tablename__ = 'exercicios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    grupo_muscular = db.Column(db.String(50))

    # Agora as séries serão apagadas quando excluir o exercício
    series = db.relationship(
        'SerieExercicio',
        backref='exercicio',
        cascade='all, delete-orphan',
        passive_deletes=True
    )


class SessaoTreino(db.Model):
    __tablename__ = 'sessao_treino'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)

    series = db.relationship(
        'SerieExercicio',
        backref='sessao',
        cascade='all, delete-orphan',
        passive_deletes=True
    )


class SerieExercicio(db.Model):
    __tablename__ = 'series_exercicio'

    id = db.Column(db.Integer, primary_key=True)
    repeticoes = db.Column(db.Integer, nullable=False)
    carga = db.Column(db.Float)

    exercicio_id = db.Column(
        db.Integer,
        db.ForeignKey('exercicios.id', ondelete='CASCADE'),
        nullable=False
    )

    sessao_id = db.Column(
        db.Integer,
        db.ForeignKey('sessao_treino.id', ondelete='CASCADE'),
        nullable=False
    )
