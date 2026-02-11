import flet as ft
import queue

class LogViewer(ft.Column):
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
        self.expand = True
        
        self.log_list = ft.ListView(
            expand=True,
            spacing=2,
            auto_scroll=True,
        )
        
        self.controls = [
            ft.Text("Execution Logs", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.log_list,
                border=ft.border.all(1, ft.Colors.GREY_800),
                border_radius=5,
                padding=10,
                expand=True,
            )
        ]

    def update_logs(self):
        """Reads from queue and updates the list view. Should be called periodically."""
        try:
            if not self.page:
                return
        except Exception:
            return
        while not self.log_queue.empty():
            try:
                record = self.log_queue.get_nowait()
                msg = record.get("message", "")
                level = record.get("level", "INFO")
                
                color = ft.Colors.WHITE
                if level == "WARNING":
                    color = ft.Colors.YELLOW
                elif level == "ERROR":
                    color = ft.Colors.RED
                elif "Finished" in msg or "Success" in msg:
                    color = ft.Colors.GREEN

                self.log_list.controls.append(
                    ft.Text(f"[{level}] {msg}", color=color, font_family="Consolas")
                )
                
                # Limit history to prevent lag
                if len(self.log_list.controls) > 1000:
                    self.log_list.controls.pop(0)
                    
            except queue.Empty:
                break
            except queue.Empty:
                break
        
        try:
            if self.page:
                self.update()
        except Exception:
            pass
