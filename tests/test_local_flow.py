from src.models import init_db, Email
from src.services.syncer import EmailSyncer
from src.services.rule_generator import RuleGenerator
import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

def test():
    print("Initializing DB...")
    init_db()
    
    print("Syncing emails (limit=10)...")
    syncer = EmailSyncer()
    syncer.sync(limit=10)
    
    count = Email.select().count()
    print(f"Emails in DB: {count}")
    
    print("Generating rules (top 5)...")
    gen = RuleGenerator()
    gen.generate_rules(top_n=5)
    
    if os.path.exists("rules.json"):
        with open("rules.json", "r", encoding="utf-8") as f:
            print(f"Rules content sample: {f.read()[:100]}...")
        
    print("Applying rules...")
    gen.apply_rules()
    
    classified = Email.select().where(Email.is_classified == True).count()
    print(f"Classified emails: {classified}")
    print("Verification complete!")

if __name__ == "__main__":
    test()
