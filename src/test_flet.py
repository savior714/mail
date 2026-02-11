
import flet as ft

def main(page: ft.Page):
    print("Testing flet attributes for animation/border/dropdown...")
    
    # Animation
    try:
        print(f"ft.animation: {ft.animation}")
    except AttributeError:
        print("ft.animation not found")
        try:
            print(f"ft.Animation: {ft.Animation}")
        except AttributeError:
            print("ft.Animation not found")

    # Border
    try:
        print(f"ft.border: {ft.border}")
        try:
            print(f"ft.border.all: {ft.border.all}")
        except AttributeError:
            print("ft.border.all not found")
    except AttributeError:
        print("ft.border not found")

    try:
        print(f"ft.Border: {ft.Border}") 
    except AttributeError: 
        print("ft.Border not found")

    # Dropdown
    try:
        print(f"ft.dropdown: {ft.dropdown}")
        try:
            print(f"ft.dropdown.Option: {ft.dropdown.Option}")
        except AttributeError:
            print("ft.dropdown.Option not found")
    except AttributeError:
        print("ft.dropdown not found")

    try:
        print(f"ft.Dropdown: {ft.Dropdown}")
        try:
            print(f"ft.dropdown_option: {ft.dropdown_option}") # sometimes moved here?
        except AttributeError:
            pass
    except AttributeError:
        print("ft.Dropdown not found")

if __name__ == "__main__":
    ft.app(main)
