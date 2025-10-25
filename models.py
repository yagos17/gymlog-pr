from db import db

class Exercicio(db.model):
    __tablename__ = 'exercicios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True,nullable=False)
    grupo_muscular = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Exercicio {self.nome}>"