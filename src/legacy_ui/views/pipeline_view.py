import flet as ft
import queue
import threading
import time
from src.ui.components.log_viewer import LogViewer
from src.services.syncer import EmailSyncer
from src.services.rule_generator import RuleGenerator
from src.services.gmail_applier import GmailApplier

class PipelineView(ft.Column):
    def __init__(self, page: ft.Page, log_queue: queue.Queue):
        super().__init__()
        self.main_page = page
        self.log_queue = log_queue
        self.expand = True
        
        # 1. Log Viewer
        self.log_viewer = LogViewer(log_queue)

        # 2. Controls
        self.progress_ring = ft.ProgressRing(width=30, height=30, stroke_width=4, visible=False)
        self.status_text = ft.Text("Ready to archive.", color=ft.Colors.GREY_400)

        self.btn_sync = ft.ElevatedButton("Start Sync (2024)", icon="sync", on_click=self.on_sync_click)
        self.btn_auto = ft.ElevatedButton("Full Auto Mode", icon="smart_toy", bgcolor=ft.Colors.AMBER_800, color=ft.Colors.WHITE, on_click=self.on_auto_click)
        self.btn_rules = ft.ElevatedButton("Generate Rules", icon="rule", on_click=self.on_rules_click)

        # 3. Layout
        self.controls = [
            ft.Text("Pipeline Execution", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Real backend services connected.", color=ft.Colors.GREY_400),
            ft.Divider(),
            ft.Row([self.btn_sync, self.btn_auto, self.btn_rules, self.progress_ring, self.status_text], spacing=20, alignment=ft.MainAxisAlignment.START),
            ft.Divider(),
            self.log_viewer
        ]
        
        self.polling = True
        threading.Thread(target=self._log_poller, daemon=True).start()

    def _log_poller(self):
        while self.polling:
            self.log_viewer.update_logs()
            time.sleep(0.1)

    def set_loading(self, loading: bool, message: str = ""):
        self.btn_sync.disabled = loading
        self.btn_auto.disabled = loading
        self.btn_rules.disabled = loading
        self.progress_ring.visible = loading
        self.status_text.value = message if loading else "Ready"
        self.update()

    def run_task(self, target, *args):
        self.set_loading(True, "Running Task...")
        threading.Thread(target=target, args=args, daemon=True).start()

    # --- Event Handlers ---
    def on_sync_click(self, e):
        self.run_task(self._run_sync)

    def on_auto_click(self, e):
        self.run_task(self._run_auto)

    def on_rules_click(self, e):
        self.run_task(self._run_rules)

    # --- Workers ---
    def _run_sync(self):
        try:
            syncer = EmailSyncer()
            # Hardcoded small batch for safety/demo
            syncer.sync(limit=50, year=2024)
            self.log_queue.put({"level": "INFO", "message": "Sync Job Completed."})
        except Exception as e:
            self.log_queue.put({"level": "ERROR", "message": f"Sync Failed: {e}"})
        finally:
            self.set_loading(False)

    def _run_auto(self):
        try:
            # Full Auto: Sync -> Gen -> Apply -> Cloud
            # Limited range for safety
            self.log_queue.put({"level": "INFO", "message": "Starting Auto Cycle for Jan 2024..."})
            
            syncer = EmailSyncer()
            syncer.sync(limit=None, after="2024/01/01", before="2024/02/01")
            
            gen = RuleGenerator()
            gen.generate_rules()
            gen.apply_rules()
            
            applier = GmailApplier()
            applier.apply_to_gmail(archive_inbox=True)
            
            self.log_queue.put({"level": "INFO", "message": "Full Auto Pipeline Successful."})
        except Exception as e:
            self.log_queue.put({"level": "ERROR", "message": f"Auto Pipeline Failed: {e}"})
        finally:
            self.set_loading(False)

    def _run_rules(self):
        try:
            gen = RuleGenerator()
            gen.generate_rules()
            self.log_queue.put({"level": "INFO", "message": "Rule Generation Complete."})
        except Exception as e:
            self.log_queue.put({"level": "ERROR", "message": f"Rule Gen Failed: {e}"})
        finally:
            self.set_loading(False)
