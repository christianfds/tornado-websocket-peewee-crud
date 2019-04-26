import os

from peewee import *
from datetime import date

if 'ON_HEROKU' in os.environ:
    db = MySQLDatabase('heroku_f78727b5063a4f1', user='bc6d48778c7305', passwd='827b35f0',
                       host='us-cdbr-iron-east-02.cleardb.net')
else:
    db = MySQLDatabase('my_crud', user='root', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = db


class Produto(BaseModel):
    nome = TextField()
    quantidade = IntegerField()
    preco = DoubleField()
    img_path = TextField()


class ProdutoRef(BaseModel):
    dono = TextField()
    produto = ForeignKeyField(Produto, on_delete='CASCADE')
    quantidade = IntegerField()


def create_tables():
    try:
        with db.atomic():
            if not db.table_exists('produto') and not db.table_exists('produtoref'):
                db.create_tables([Produto, ProdutoRef])
                init_table_produto()
    except IntegrityError as e:
        print(e)


def add_produto_carrinho(userid, produtoid):
    with db.atomic():
        exist = ProdutoRef.update(quantidade=ProdutoRef.quantidade + 1).where(ProdutoRef.dono == str(userid) and
                                                                              ProdutoRef.produto == produtoid)

        if exist.execute() > 0:
            pass
        else:
            prdRef = ProdutoRef(dono=userid, produto=produtoid,
                                quantidade=1)
            prdRef.save()


def count_produto_carrinho(userid):
    with db.atomic():
        return ProdutoRef.select().where(ProdutoRef.dono == userid).count()


def get_produtos_carrinho(userid):
    with db.atomic():
        return ProdutoRef.select(ProdutoRef, Produto).join(Produto, JOIN.LEFT_OUTER).where(ProdutoRef.dono == str(userid))


def init_table_produto():
    for p in Produto.select():
        p.delete_instance()

    prod = Produto(nome="Bateria de carro", quantidade=200,
                   preco=150, img_path="./img_product/01.jpg")
    prod.save()

    prod = Produto(nome="Lamina Gillete", quantidade=200,
                   preco=3.5, img_path="./img_product/02.jpg")
    prod.save()

    prod = Produto(nome="Escova de dentes", quantidade=200,
                   preco=6, img_path="./img_product/03.jpg")
    prod.save()

    prod = Produto(nome="Caderno", quantidade=200,
                   preco=6, img_path="./img_product/04.jpg")
    prod.save()

    prod = Produto(nome="Teclado Logitech", quantidade=200,
                   preco=180, img_path="./img_product/05.jpg")
    prod.save()

    prod = Produto(nome="Mouse Logitech", quantidade=200,
                   preco=160, img_path="./img_product/06.jpg")
    prod.save()
