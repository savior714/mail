import flet as ft
import os

class SettingsView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(padding=20, expand=True)
        self.main_page = page
        
        # Load Env
        self.env_path = ".env"
        current_api_key = os.getenv("GOOGLE_API_KEY", "")

        self.api_key_field = ft.TextField(
            label="Google API Key", 
            password=True, 
            can_reveal_password=True, 
            value=current_api_key
        )
        self.theme_switch = ft.Switch(
            label="Dark Mode", 
            value=(page.theme_mode == ft.ThemeMode.DARK),
            on_change=self.toggle_theme
        )

        self.content = ft.Column([
            ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("API Configuration", size=18, weight=ft.FontWeight.BOLD),
            self.api_key_field,
            ft.Text("Changes to API Key require restart to take effect.", size=12, color=ft.Colors.RED_400),
            ft.Divider(),
            ft.Text("Preferences", size=18, weight=ft.FontWeight.BOLD),
            self.theme_switch,
            ft.Divider(),
            ft.ElevatedButton("Save Changes", icon="save", bgcolor=ft.Colors.BLUE, on_click=self.save_settings)
        ])

    def toggle_theme(self, e):
        self.main_page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        self.main_page.update()

    def save_settings(self, e):
        new_key = self.api_key_field.value
        
        # Update .env
        try:
            lines = []
            if os.path.exists(self.env_path):
                with open(self.env_path, "r") as f:
                    lines = f.readlines()
            
            key_found = False
            new_lines = []
            for line in lines:
                if line.startswith("GOOGLE_API_KEY="):
                    new_lines.append(f"GOOGLE_API_KEY={new_key}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            
            if not key_found:
                new_lines.append(f"\nGOOGLE_API_KEY={new_key}\n")
                
            with open(self.env_path, "w") as f:
                f.writelines(new_lines)

            # Update Runtime Env (Optional, for rules gen)
            os.environ["GOOGLE_API_KEY"] = new_key
            
            snack = ft.SnackBar(ft.Text("Settings saved!"))
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()
            
        except Exception as ex:
            print(f"Error saving settings: {ex}")
