import sys
import os
import argparse

# Add project root to path
import pathlib
ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress
from rich.logging import RichHandler
import logging

from src.models import init_db, Email, fn
from src.services.syncer import EmailSyncer
from src.services.rule_generator import RuleGenerator
from src.services.gmail_applier import GmailApplier
from dotenv import load_dotenv

load_dotenv()

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Gmail AI Archivist - Production Scale-up")
    parser.add_argument("--year", type=int, help="Limit operations to a specific year")
    args = parser.parse_args()

    init_db()
    
    # Setup logging for CLI
    logging.basicConfig(
        level=logging.INFO,  # Use constant instead of string
        format="%(message)s", 
        datefmt="[%X]", 
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    
    logger = logging.getLogger(__name__)
    
    def month_iterator(start_date, end_date=None):
        """월 단위로 날짜 범위를 생성하는 제너레이터"""
        current = start_date
        
        while True:
            # Calculate next month
            if current.month == 12:
                next_month = current.replace(year=current.year + 1, month=1, day=1)
            else:
                next_month = current.replace(month=current.month + 1, day=1)
            
            # Check if we've reached the end
            if end_date and current >= end_date:
                break
            
            yield (
                current.strftime("%Y/%m/%d"),
                next_month.strftime("%Y/%m/%d"),
                next_month
            )
            
            current = next_month

    syncer = EmailSyncer()
    
    if args.year:
        console.print(f"[bold green]Mode: Yearly Batch Processing ({args.year})[/]")
        limit = int(Prompt.ask("How many emails for this year?", default="500"))
        syncer.sync(limit=limit, year=args.year)
        console.print("[yellow]Batch Sync Complete. Please generate/apply rules normally.[/]")
        Prompt.ask("Press Enter to enter Interactive Mode")

    while True:
        console.clear()
        console.rule("[bold blue]Gmail AI Archivist (Phase 2: Production Scale-up)[/]")
        
        # Show Stats
        try:
            total = Email.select().count()
            classified = Email.select().where(Email.is_classified == True).count()
            console.print(f"📊 Total Emails: [bold]{total}[/] | Classified: [green]{classified}[/]")
        except Exception as e:
            logger.error(f"DB error when fetching stats: {e}")
            console.print("[red]DB error. See logs for details.[/]")

        console.print("\n[1] 📥 Sync Emails (Fetch from Gmail)")
        console.print("[w] 📅 Weekly Sync (2024 Batch Mode)")
        console.print("[a] 🤖 Full Auto (Sync + AI + Cloud Apply)")
        console.print("[2] 🧠 Generate Rules (AI Audit Mode)")
        console.print("[3] 🚀 Apply Rules (Local DB)")
        console.print("[4] ☁️  Cloud Sync (Push to Gmail Server)")
        console.print("[5] 📈 Show Report")
        console.print("[q] Quit")
        
        choice = Prompt.ask("Select an option", choices=["1", "w", "a", "2", "3", "4", "5", "q"])
        
        if choice == "1":
            limit = int(Prompt.ask("How many emails?", default="200"))
            year_input = Prompt.ask("Year (Optional, e.g. 2024)", default="")
            
            # Enhanced year validation
            year = None
            if year_input and year_input.isdigit():
                year = int(year_input)
                if not (1900 <= year <= 2100):
                    console.print("[red]Year must be between 1900 and 2100[/]")
                    Prompt.ask("Press Enter to continue")
                    continue
            elif year_input:
                console.print("[red]Invalid year format. Please enter a valid year.[/]")
                Prompt.ask("Press Enter to continue")
                continue
                
            syncer.sync(limit=limit, year=year)
            Prompt.ask("Press Enter to continue")
            
        elif choice == "w":
            import datetime
            start_date_str = Prompt.ask("Start Date (YYYY-MM-DD)", default="2024-01-01")
            try:
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError as e:
                console.print(f"[bold red]Invalid date format: {e}[/]")
                console.print("[yellow]Please use YYYY-MM-DD format (e.g., 2024-01-01)[/]")
                Prompt.ask("Press Enter to return")
                continue

            # Use month_iterator for batch processing
            for after, before, next_date in month_iterator(start_date):
                syncer.sync(limit=None, after=after, before=before)
                
                console.print(f"\n[bold green]Finished month {after} - {before}[/]")
                cont = Prompt.ask("Continue to next month?", choices=["y", "n"], default="y")
                if cont == "n":
                    break

        elif choice == "a":
            import datetime
            start_date_str = Prompt.ask("Start Date (Full Auto)", default="2024-01-01")
            try:
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError as e:
                console.print(f"[bold red]Invalid date format: {e}[/]")
                console.print("[yellow]Please use YYYY-MM-DD format (e.g., 2024-01-01)[/]")
                Prompt.ask("Press Enter to return")
                continue

            # Use month_iterator for full auto pipeline
            for after, before, next_date in month_iterator(start_date):
                console.rule(f"[bold yellow]Full Auto Pipeline: {after} - {before}[/]")
                
                # 1. Sync
                syncer.sync(limit=None, after=after, before=before)
                
                # 2. Generate (AI)
                generator = RuleGenerator()
                generator.generate_rules(top_n=None)
                
                # 3. Apply Local
                generator.apply_rules()
                
                # 4. Push to Gmail
                applier = GmailApplier()
                applier.apply_to_gmail(archive_inbox=True)

                console.print(f"\n[bold green]Successfully processed & uploaded: {after} to {before}[/]")
                
                cont = Prompt.ask("Proceed to next month?", choices=["y", "n"], default="y")
                if cont == "n":
                    break
            
        elif choice == "2":
            gen = RuleGenerator()
            # Analyze ALL unique senders in DB
            gen.generate_rules(top_n=None)
            console.print("[bold yellow]Rule Audit suggested![/] Open rules.json and check classifications.")
            Prompt.ask("Press Enter to continue")
            
        elif choice == "3":
            gen = RuleGenerator()
            gen.apply_rules()
            Prompt.ask("Press Enter to continue")

        elif choice == "4":
            applier = GmailApplier()
            archive = Prompt.ask("Archive from Inbox after labeling?", choices=["y", "n"], default="y") == "y"
            applier.apply_to_gmail(archive_inbox=archive)
            Prompt.ask("Press Enter to continue")
            
        elif choice == "5":
            show_report()
            Prompt.ask("Press Enter to continue")
            
        elif choice == "q":
            break

def show_report():
    query = (Email
             .select(Email.category, fn.COUNT(Email.id).alias('count'))
             .group_by(Email.category)
             .order_by(fn.COUNT(Email.id).desc()))
    
    table = Table(title="Classification Report")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="magenta")
    
    for row in query:
        table.add_row(row.category, str(row.count))
        
    console.print(table)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold red]Interrupted by user. Exiting...[/]")
        sys.exit(0)
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        console.print(f"\n[bold red]Unexpected error:[/] {e}")
        console.print("[dim]See logs for full traceback.[/]")
        sys.exit(1)
