import flet as ft
import json
import os

class RulesView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(padding=20, expand=True)
        self.main_page = page
        self.rules_file = "rules.json"
        self.rules_data = {}

        # Table
        self.dt = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sender")),
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Source")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            column_spacing=20,
            heading_row_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        )

        # Dialogs
        self.add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Rule"),
            content=ft.Column([
                ft.TextField(label="Sender Email", hint_text="e.g. news@site.com"),
                ft.Dropdown(
                    label="Category",
                    options=[
                        ft.DropdownOption("📚_Read"),
                        ft.DropdownOption("💰_Finance"),
                        ft.DropdownOption("🛒_Shopping"),
                        ft.DropdownOption("💬_Social"),
                        ft.DropdownOption("🔒_Security"),
                        ft.DropdownOption("✈️_Travel"),
                    ]
                )
            ], height=150),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(self.add_dialog)),
                ft.TextButton("Save", on_click=self.save_new_rule),
            ],
        )

        self.content = ft.Column([
            ft.Row([
                ft.Text("Rules Editor", size=28, weight=ft.FontWeight.BOLD),
                ft.IconButton("add", tooltip="Add Rule", icon_color=ft.Colors.GREEN, on_click=self.open_add_dialog),
                ft.IconButton("refresh", tooltip="Reload Rules", icon_color=ft.Colors.BLUE, on_click=lambda e: self.load_rules()),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Manage auto-classification rules manually.", color=ft.Colors.GREY_400),
            ft.Divider(),
            ft.Column([self.dt], scroll=ft.ScrollMode.AUTO, expand=True)
        ])

        self.load_rules()

    def load_rules(self):
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    self.rules_data = json.load(f)
            else:
                self.rules_data = {}
            
            self._refresh_table()
        except Exception as e:
            print(f"Error loading rules: {e}")

    def _refresh_table(self):
        self.dt.rows = []
        # sort by sender
        for sender in sorted(self.rules_data.keys()):
            rule = self.rules_data[sender]
            # Handle migration (str vs dict)
            if isinstance(rule, str):
                category = rule
                source = "Legacy"
            else:
                category = rule.get("category", "Unknown")
                source = rule.get("source", "Manual")

            self.dt.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(sender, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(category, color=ft.Colors.BLACK, size=12),
                        bgcolor=ft.Colors.AMBER_200 if "Shopping" in category else ft.Colors.BLUE_200,
                        padding=5,
                        border_radius=5
                    )),
                    ft.DataCell(ft.Text(source, italic=True, size=12)),
                    ft.DataCell(ft.IconButton(
                        "delete", 
                        icon_size=18, 
                        icon_color=ft.Colors.RED, 
                        tooltip="Delete",
                        data=sender,
                        on_click=self.delete_rule
                    ))
                ])
            )
        self.update()

    def open_add_dialog(self, e):
        self.main_page.dialog = self.add_dialog
        self.add_dialog.open = True
        self.main_page.update()

    def close_dialog(self, dialog):
        dialog.open = False
        self.main_page.update()

    def save_new_rule(self, e):
        sender = self.add_dialog.content.controls[0].value
        category = self.add_dialog.content.controls[1].value
        
        if sender and category:
            self.rules_data[sender] = {
                "category": category,
                "source": "Manual_UI",
                "last_date": "N/A"
            }
            self._save_to_file()
            self._refresh_table()
            self.close_dialog(self.add_dialog)
            # Clear inputs
            self.add_dialog.content.controls[0].value = ""

    def delete_rule(self, e):
        sender = e.control.data
        if sender in self.rules_data:
            del self.rules_data[sender]
            self._save_to_file()
            self._refresh_table()

    def _save_to_file(self):
        with open(self.rules_file, "w", encoding="utf-8") as f:
            json.dump(self.rules_data, f, indent=4, ensure_ascii=False)
