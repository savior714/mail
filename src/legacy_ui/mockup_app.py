import flet as ft
import time
import random

# --- DUMMY DATA ---
DUMMY_STATS = {
    "total": 12450,
    "classified": 8900,
    "trash": 1205,
    "storage_saved": "4.2 GB"
}

DUMMY_RULES = [
    {"sender": "newsletter@medium.com", "category": "📚 Read", "source": "Manual"},
    {"sender": "service@paypal.com", "category": "💰 Finance", "source": "AI"},
    {"sender": "promo@amazon.com", "category": "🛒 Shopping", "source": "Rule"},
    {"sender": "alert@google.com", "category": "🔒 Security", "source": "Manual"},
    {"sender": "info@twitter.com", "category": "💬 Social", "source": "AI"},
]

DUMMY_LOGS = [
    "[INFO] System initialized.",
    "[INFO] Connected to Gmail API (Mock).",
    "[WARNING] 5 large files detected in Trash.",
    "[INFO] Ready for command."
]

# --- VIEWS ---

class DashboardMockup(ft.Container):
    def __init__(self):
        super().__init__(padding=20, expand=True)
        
        # 1. Hero / Welcome
        welcome_text = ft.Text(
            "Welcome back! Your inbox is 72% cleaner.", 
            size=28, weight=ft.FontWeight.BOLD
        )
        
        # 2. Stats Cards
        stats_row = ft.Row(
            controls=[
                self._build_card("Total Emails", str(DUMMY_STATS["total"]), ft.icons.EMAIL, ft.colors.BLUE_400),
                self._build_card("Classified", str(DUMMY_STATS["classified"]), ft.icons.CHECK_CIRCLE, ft.colors.GREEN_400),
                self._build_card("Trash Found", str(DUMMY_STATS["trash"]), ft.icons.DELETE, ft.colors.RED_400),
                self._build_card("Space Saved", DUMMY_STATS["storage_saved"], ft.icons.SAVE, ft.colors.PURPLE_400),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # 3. Activity Chart (Dummy)
        chart = ft.BarChart(
            bar_groups=[
                ft.BarChartGroup(x=0, bar_rods=[ft.BarChartRod(from_y=0, to_y=40, width=20, color=ft.colors.AMBER, tooltip="Jan", border_radius=5)]),
                ft.BarChartGroup(x=1, bar_rods=[ft.BarChartRod(from_y=0, to_y=80, width=20, color=ft.colors.BLUE, tooltip="Feb", border_radius=5)]),
                ft.BarChartGroup(x=2, bar_rods=[ft.BarChartRod(from_y=0, to_y=30, width=20, color=ft.colors.RED, tooltip="Mar", border_radius=5)]),
                ft.BarChartGroup(x=3, bar_rods=[ft.BarChartRod(from_y=0, to_y=60, width=20, color=ft.colors.GREEN, tooltip="Apr", border_radius=5)]),
                ft.BarChartGroup(x=4, bar_rods=[ft.BarChartRod(from_y=0, to_y=90, width=20, color=ft.colors.PURPLE, tooltip="May", border_radius=5)]),
            ],
            border=ft.border.all(1, ft.colors.GREY_800),
            left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Emails processed")),
            bottom_axis=ft.ChartAxis(labels=[
                ft.ChartAxisLabel(value=0, label=ft.Container(ft.Text("Jan"), padding=10)),
                ft.ChartAxisLabel(value=1, label=ft.Container(ft.Text("Feb"), padding=10)),
                ft.ChartAxisLabel(value=2, label=ft.Container(ft.Text("Mar"), padding=10)),
                ft.ChartAxisLabel(value=3, label=ft.Container(ft.Text("Apr"), padding=10)),
                ft.ChartAxisLabel(value=4, label=ft.Container(ft.Text("May"), padding=10)),
            ]),
            horizontal_grid_lines=ft.ChartGridLines(color=ft.colors.GREY_800, width=1, dash_pattern=[3, 3]),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.GREY_900),
            max_y=110,
            interactive=True,
            expand=True,
        )

        chart_container = ft.Container(
            content=chart,
            height=300,
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
            border_radius=10,
            padding=20,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE)
        )

        self.content = ft.Column(
            controls=[
                welcome_text,
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                stats_row,
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                ft.Text("Monthly Activity", size=20, weight=ft.FontWeight.W_600),
                chart_container
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def _build_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=color),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(title, size=14, color=ft.colors.GREY_400),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=200,
            height=120,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
            border_radius=10,
            padding=15,
            animate=ft.animation.Animation(300, "easeOut"),
            on_hover=lambda e: self._hover_card(e)
        )

    def _hover_card(self, e):
        e.control.bgcolor = ft.colors.with_opacity(0.1, ft.colors.WHITE) if e.data == "true" else ft.colors.with_opacity(0.05, ft.colors.WHITE)
        e.control.update()


class PipelineMockup(ft.Container):
    def __init__(self):
        super().__init__(padding=20, expand=True)

        self.log_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)
        for log in DUMMY_LOGS:
            self._add_log(log)

        self.progress_ring = ft.ProgressRing(width=30, height=30, stroke_width=4, visible=False)
        self.status_text = ft.Text("Ready to archive.", color=ft.colors.GREY_400)

        self.btn_sync = ft.ElevatedButton("Start Sync (2024)", icon=ft.icons.SYNC, on_click=lambda e: self._run_simulation("Syncing...", 3))
        self.btn_auto = ft.ElevatedButton("Full Auto Mode", icon=ft.icons.AUTO_MODE, bgcolor=ft.colors.AMBER_800, color=ft.colors.WHITE, on_click=lambda e: self._run_simulation("Running Auto Pipeline...", 5))

        self.content = ft.Column([
            ft.Text("Pipeline Execution", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Manual and automated triggers for archiving tasks.", color=ft.colors.GREY_400),
            ft.Divider(),
            ft.Row([self.btn_sync, self.btn_auto, self.progress_ring, self.status_text], spacing=20, alignment=ft.MainAxisAlignment.START),
            ft.Divider(),
            ft.Container(
                content=self.log_list,
                bgcolor="#1e1e1e",
                border_radius=5,
                padding=15,
                expand=True,
                border=ft.border.all(1, "#333333")
            )
        ])

    def _add_log(self, message):
        color = ft.colors.WHITE
        if "[INFO]" in message: color = ft.colors.CYAN_200
        if "[WARNING]" in message: color = ft.colors.YELLOW_200
        if "[ERROR]" in message: color = ft.colors.RED_200
        
        self.log_list.controls.append(ft.Text(message, color=color, font_family="Consolas"))

    def _run_simulation(self, status_msg, duration):
        self.btn_sync.disabled = True
        self.btn_auto.disabled = True
        self.progress_ring.visible = True
        self.status_text.value = status_msg
        self.update()

        # Simulate logs
        self._add_log(f"[INFO] Started: {status_msg}")
        self.update()
        
        # We can't actually sleep in the main thread in a real app, but for mockup it's fine 
        # or we use a timer. Let's just create a quick visual effect.
        # Ideally, use page.run_task or simlar, but here we just update UI to show state.
        self._add_log(f"[INFO] (Simulated) Task running for {duration} seconds...")
        
        # Reset visual state after a delay (conceptually)
        # For mockup, we'll just leave it "Running" to show the state, 
        # or use a threading Timer to reset it for effect.
        import threading
        def reset():
            time.sleep(duration)
            self.btn_sync.disabled = False
            self.btn_auto.disabled = False
            self.progress_ring.visible = False
            self.status_text.value = "Task Complete."
            self._add_log("[INFO] Task Finished Successfully.")
            self.update()
        
        threading.Thread(target=reset, daemon=True).start()


class RulesMockup(ft.Container):
    def __init__(self):
        super().__init__(padding=20, expand=True)
        
        self.dt = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sender")),
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Source")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[self._build_row(r) for r in DUMMY_RULES],
            column_spacing=20,
            heading_row_color=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        )

        self.content = ft.Column([
            ft.Row([
                ft.Text("Rules Editor", size=28, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.icons.ADD, tooltip="Add Rule", icon_color=ft.colors.GREEN),
                ft.IconButton(ft.icons.REFRESH, tooltip="Reload Rules", icon_color=ft.colors.BLUE),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Manage auto-classification rules manually.", color=ft.colors.GREY_400),
            ft.Divider(),
            ft.Column([self.dt], scroll=ft.ScrollMode.AUTO, expand=True)
        ])

    def _build_row(self, rule):
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(rule["sender"], weight=ft.FontWeight.BOLD)),
            ft.DataCell(ft.Container(
                content=ft.Text(rule["category"], color=ft.colors.BLACK, size=12),
                bgcolor=ft.colors.AMBER_200 if "Shopping" in rule["category"] else ft.colors.BLUE_200,
                padding=5,
                border_radius=5
            )),
            ft.DataCell(ft.Text(rule["source"], italic=True, size=12)),
            ft.DataCell(ft.Row([
                ft.IconButton(ft.icons.EDIT, icon_size=18, tooltip="Edit"),
                ft.IconButton(ft.icons.DELETE, icon_size=18, icon_color=ft.colors.RED, tooltip="Delete"),
            ]))
        ])

class SettingsMockup(ft.Container):
    def __init__(self):
        super().__init__(padding=20, expand=True)
        
        self.api_key_field = ft.TextField(label="Google API Key", password=True, can_reveal_password=True, value="AIzaSy...MockKey")
        self.theme_switch = ft.Switch(label="Dark Mode", value=True)
        self.safe_mode_switch = ft.Switch(label="Safe Mode (Confirm before delete)", value=True)

        self.content = ft.Column([
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("API Configuration", size=18, weight=ft.FontWeight.BOLD),
            self.api_key_field,
            ft.Divider(),
            ft.Text("Preferences", size=18, weight=ft.FontWeight.BOLD),
            self.theme_switch,
            self.safe_mode_switch,
            ft.Divider(),
            ft.ElevatedButton("Save Changes", icon=ft.icons.SAVE, bgcolor=ft.colors.BLUE)
        ])


def main(page: ft.Page):
    page.title = "Gmail AI Archivist - Mockup"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    
    # Views
    dashboard_view = DashboardMockup()
    rules_view = RulesMockup()
    pipeline_view = PipelineMockup()
    settings_view = SettingsMockup()

    # Layout Area
    content_area = ft.Container(content=dashboard_view, expand=True)

    def change_view(e):
        idx = e.control.selected_index
        if idx == 0: content_area.content = dashboard_view
        elif idx == 1: content_area.content = rules_view
        elif idx == 2: content_area.content = pipeline_view
        elif idx == 3: content_area.content = settings_view
        content_area.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.icons.RULE, label="Rules"),
            ft.NavigationRailDestination(icon=ft.icons.PLAY_CIRCLE, label="Pipeline"),
            ft.NavigationRailDestination(icon=ft.icons.SETTINGS, label="Settings"),
        ],
        on_change=change_view
    )

    page.add(ft.Row([rail, ft.VerticalDivider(width=1), content_area], expand=True))

if __name__ == "__main__":
    ft.app(target=main)
