import flet as ft
from src.models import Email, fn
import calendar

class DashboardView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(padding=20, expand=True)
        self.main_page = page
        
        # 1. Hero
        self.welcome_text = ft.Text(
            "Welcome back! Loading stats...", 
            size=28, weight=ft.FontWeight.BOLD
        )
        
        # 2. Stats Row
        self.stats_row = ft.Row(
            controls=[
                self._build_card("Total Emails", "-", "inbox", ft.Colors.BLUE_400),
                self._build_card("Classified", "-", "check_circle", ft.Colors.GREEN_400),
                self._build_card("Trash Found", "-", "delete", ft.Colors.RED_400),
                self._build_card("Avg Size", "-", "save", ft.Colors.PURPLE_400),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # 3. Chart Container (Empty initially)
        # self.chart = ft.BarChart(...) # Deprecated/Removed in 0.80.5
        self.chart = ft.Text("Chart temporarily disabled due to Flet 0.80+ API changes", color=ft.Colors.RED)
        
        chart_container = ft.Container(
            content=self.chart,
            height=300,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            border_radius=10,
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        )

        self.content = ft.Column(
            controls=[
                self.welcome_text,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.stats_row,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Text("Activity Trends", size=20, weight=ft.FontWeight.W_600),
                chart_container
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def _build_card(self, title, value, icon, color):
        content = ft.Column(
            [
                ft.Icon(icon, size=30, color=color),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=14, color=ft.Colors.GREY_400),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        return ft.Container(
            content=content,
            width=200,
            height=120,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=10,
            padding=15,
            animate=ft.Animation(300, "easeOut"),
            on_hover=lambda e: self._hover_card(e)
        )

    def _hover_card(self, e):
        e.control.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.WHITE) if e.data == "true" else ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        e.control.update()

    def refresh_data(self):
        """Fetch real data from DB."""
        try:
            # 1. Stats
            total = Email.select().count()
            classified = Email.select().where(Email.is_classified == True).count()
            # Approximation for trash: emails with 'Promo' or 'Shopping' > 1MB (just an example logic or use rules)
            trash_count = Email.select().where(Email.size_estimate > 1000000).count() 
            avg_size = Email.select(fn.AVG(Email.size_estimate)).scalar() or 0
            
            # Update Cards
            cards = self.stats_row.controls
            cards[0].content.controls[1].value = f"{total:,}"
            cards[1].content.controls[1].value = f"{classified:,}"
            cards[2].content.controls[1].value = f"{trash_count:,}"
            cards[3].content.controls[1].value = f"{int(avg_size/1024):,} KB"
            
            percent = int((classified / total * 100)) if total > 0 else 0
            self.welcome_text.value = f"Welcome back! Your archive is {percent}% classified."

            # 2. Chart Data (Group by Month)
            # SQLite strftime format: %Y-%m
            monthly_data = (Email
                            .select(fn.strftime('%Y-%m', Email.date).alias('month'), fn.COUNT(Email.id).alias('count'))
                            .group_by(fn.strftime('%Y-%m', Email.date))
                            .order_by(fn.strftime('%Y-%m', Email.date).desc())
                            .limit(6)) # Last 6 months
            
            data_map = {row.month: row.count for row in monthly_data}
            sorted_months = sorted(data_map.keys())

            bar_groups = []
            labels = []
            max_y = 0

            # for i, month in enumerate(sorted_months):
            #     count = data_map[month]
            #     max_y = max(max_y, count)
            #     bar_groups.append(
            #         ft.BarChartGroup(
            #             x=i, 
            #             bar_rods=[ft.BarChartRod(from_y=0, to_y=count, width=20, color=ft.Colors.BLUE, border_radius=5, tooltip=f"{month}: {count}")]
            #         )
            #     )
            #     labels.append(ft.ChartAxisLabel(value=i, label=ft.Container(ft.Text(month), padding=10)))

            # Chart update disabled
            # self.chart.bar_groups = bar_groups
            # self.chart.bottom_axis.labels = labels
            # self.chart.max_y = max_y * 1.2
            
            self.update()
            
        except Exception as e:
            print(f"DB Error: {e}")
