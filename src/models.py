from peewee import *
import datetime

db = SqliteDatabase('emails.db')

class BaseModel(Model):
    class Meta:
        database = db

class Email(BaseModel):
    id = CharField(primary_key=True)
    sender = CharField(null=True)
    subject = CharField(null=True)
    snippet = TextField(null=True)
    date = DateTimeField(default=datetime.datetime.now)
    category = CharField(default='Unclassified')
    is_classified = BooleanField(default=False)
    rule_source = CharField(null=True) # 'AI', 'Rule', 'Manual'
    size_estimate = IntegerField(default=0)

def init_db():
    db.connect()
    db.create_tables([Email])
