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
    is_synced = BooleanField(default=False)
    reasoning = CharField(null=True)
    rule_source = CharField(null=True) # 'AI', 'Rule', 'Manual'
    size_estimate = IntegerField(default=0)

class LearnedRule(BaseModel):
    pattern = CharField(unique=True)
    category = CharField()
    confidence = FloatField(default=1.0) # 0.0 to 1.0
    hit_count = IntegerField(default=0)
    correction_count = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
    last_hit_at = DateTimeField(null=True)

def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Email, LearnedRule])
    
    # Simple migration: Add columns if they don't exist
    columns = [c.name for c in db.get_columns('email')]
    if 'is_synced' not in columns:
        print("Migrating: Adding 'is_synced' column to Email table...")
        db.execute_sql('ALTER TABLE email ADD COLUMN is_synced BOOLEAN DEFAULT 0')
    
    if 'reasoning' not in columns:
        # While at it, let's add reasoning too as we might want to store it
        print("Migrating: Adding 'reasoning' column to Email table...")
        db.execute_sql('ALTER TABLE email ADD COLUMN reasoning TEXT')
