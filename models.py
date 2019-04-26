from peewee import *
from datetime import date

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
        exist = ProdutoRef.select().where(ProdutoRef.dono == userid &
                                          ProdutoRef.produto == produtoid)

        quant = 1
        if exist:
            print('já existe')
            # quant = exist.get().quantidade

        prdRef = ProdutoRef(dono=userid, produto=produtoid,
                            quantidade=quant, preco=3)

        prdRef.save()


def count_produto_carrinho(userid):
    with db.atomic():
        return ProdutoRef.select().where(ProdutoRef.dono == userid).count()


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
