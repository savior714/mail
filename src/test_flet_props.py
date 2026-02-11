
import flet as ft
import inspect

def main(page: ft.Page):
    print("Inspecting flet module...")
    attributes = dir(ft)
    
    print(f"Has 'animation'? {'animation' in attributes}")
    print(f"Has 'Animation'? {'Animation' in attributes}")
    
    print(f"Has 'border'? {'border' in attributes}")
    print(f"Has 'Border'? {'Border' in attributes}")
    
    print(f"Has 'dropdown'? {'dropdown' in attributes}")
    print(f"Has 'Dropdown'? {'Dropdown' in attributes}")
    
    print(f"Has 'alignment'? {'alignment' in attributes}")
    print(f"Has 'Alignment'? {'Alignment' in attributes}")

    # Check for Option
    print(f"Has 'Option'? {'Option' in attributes}")
    print(f"Has 'dropdown_option'? {'dropdown_option' in attributes}")

if __name__ == "__main__":
    ft.app(main)
