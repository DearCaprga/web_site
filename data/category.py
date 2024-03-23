import sqlalchemy

from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('news', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('news.id')),
                                     sqlalchemy.Column('category', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('category.id')),
                                     sqlalchemy.Column('sleep', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('sleep.id')),
                                     sqlalchemy.Column('like', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('like.id'))
                                     )


class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
