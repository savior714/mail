
import flet as ft

def main(page: ft.Page):
    print("Searching for BarChart...")
    for attr in dir(ft):
        if "Chart" in attr:
            print(f"Found: {attr}")

if __name__ == "__main__":
    ft.app(main)
