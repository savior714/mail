import flet as ft
import queue
import logging
import sys
import os
import pathlib

# Add project root to path
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from src.ui.views.dashboard_view import DashboardView
from src.ui.views.pipeline_view import PipelineView
from src.ui.views.rules_view import RulesView
from src.ui.views.settings_view import SettingsView
from src.utils.gui_logger import GuiLoggerHandler
from src.models import init_db

# Configure Root Logger
def setup_logging(log_queue: queue.Queue):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to avoid duplication
    if not logger.handlers:
        # 1. Console Handler (for debug)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

        # 2. GUI Handler
        gui_handler = GuiLoggerHandler(log_queue)
        gui_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(gui_handler)

def main(page: ft.Page):
    # 1. Init DB
    init_db()

    # 2. Setup Logging
    log_queue = queue.Queue()
    setup_logging(log_queue)

    # 3. Window Setup
    page.title = "Gmail AI Archivist"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0

    # 4. Views
    print("Initializing DashboardView...")
    try:
        dashboard_view = DashboardView(page)
        print("DashboardView initialized.")
    except Exception as e:
        print(f"Failed to init DashboardView: {e}")
        dashboard_view = ft.Text(f"Dashboard Failed: {e}", color=ft.Colors.RED)

    print("Initializing PipelineView...")
    try:
        pipeline_view = PipelineView(page, log_queue)
        print("PipelineView initialized.")
    except Exception as e:
        print(f"Failed to init PipelineView: {e}")
        pipeline_view = ft.Text(f"Pipeline Failed: {e}")

    print("Initializing RulesView...")
    try:
        rules_view = RulesView(page)
        print("RulesView initialized.")
    except Exception as e:
        print(f"Failed to init RulesView: {e}")
        rules_view = ft.Text(f"Rules Failed: {e}")

    print("Initializing SettingsView...")
    try:
        settings_view = SettingsView(page)
        print("SettingsView initialized.")
    except Exception as e:
        print(f"Failed to init SettingsView: {e}")
        settings_view = ft.Text(f"Settings Failed: {e}")

    # 5. Navigation Handling
    def change_view(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            content_area.content = dashboard_view
            dashboard_view.refresh_data()
        elif selected_index == 1:
            content_area.content = rules_view
        elif selected_index == 2:
            content_area.content = pipeline_view
        elif selected_index == 3:
            content_area.content = settings_view
        page.update()

    # 6. UI Layout
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        leading=ft.Icon("mail", size=30),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon="dashboard_outlined",
                selected_icon="dashboard",
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon="rule", # rule_outlined is not standard, falling back to rule or description
                selected_icon="rule",
                label="Rules",
            ),
            ft.NavigationRailDestination(
                icon="play_circle_outline",
                selected_icon="play_circle_filled",
                label="Pipeline",
            ),
            ft.NavigationRailDestination(
                icon="settings_outlined",
                selected_icon="settings",
                label="Settings",
            ),
        ],
        on_change=change_view,
    )

    content_area = ft.Container(
        content=dashboard_view,
        expand=True,
        padding=0, # Let views handle padding
    )

    print("Adding controls to page...")
    try:
        page.add(
            ft.Row(
                [
                    rail,
                    ft.VerticalDivider(width=1),
                    content_area,
                ],
                expand=True,
            )
        )
        print("Page.add completed.")
    except Exception as e:
        print(f"Failed to add to page: {e}")

if __name__ == "__main__":
    ft.app(main)
