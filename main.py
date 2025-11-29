import dearpygui.dearpygui as dpg

from Grid import Grid

#DEARPYGUI SPECIFIC
WINDOW_NAME = "Minotaur Engine"
WINDOW_SIZE = (1000, 800)

REG_FONT_PATH = "extra/Roboto-Light.ttf"
ICO_PATH = "extra/minotaur-icon.ico"

#GRID SPECIFIC
GRID = Grid(10, 10, 25)
MIN_GRID_AXIS_SIZE = 5
MAX_GRID_AXIS_SIZE = 100
MIN_CELL_SIZE = 5
MAX_CELL_SIZE = 100
MIN_LINE_THICKNESS = 1.0
MAX_LINE_THICKNESS = 5.0

# list of global values tied in the DearPyGui Value Registry that we can you so synchronize all values in the fields on the visual side
INITIAL_GLOBAL_VALUES_LIST = {
    "grid_size": (GRID.cols, GRID.rows),
    "cell_size": GRID.cell_size,
    "line_thickness": GRID.line_thickness,
    "line_color": GRID.line_cell_color,
    "cell_color": GRID.default_cell_color,
    "impassable_color": GRID.impassable_color,
    "center_grid": False,
}

def show_modal(modal):
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    modal_width = 300
    modal_height = 150

    pos_x = (viewport_width // 2) - (modal_width // 2)
    pos_y = (viewport_height // 2) - (modal_height // 2)

    dpg.configure_item(modal, pos=(pos_x, pos_y), show=True)

# Initialize the viewport to start adding windows and content
dpg.create_context()
dpg.create_viewport(title=WINDOW_NAME, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1], small_icon="extra/minotaur-icon.ico")

# Create a font registry
with dpg.font_registry():
    default_font = dpg.add_font(REG_FONT_PATH, 14)

dpg.bind_font(default_font)

with dpg.theme() as no_padding_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)

# Create a Value Registry to hold the INITIAL_GLOBAL_VALUES_LIST variables
with dpg.value_registry():
    for key, item in INITIAL_GLOBAL_VALUES_LIST.items():
        if type(item) == tuple:
            if type(item[0]) == int:
                dpg.add_int4_value(tag=key, default_value=item)
            elif type(item[0]) == float:
                dpg.add_color_value(tag=key, default_value=item)
        elif type(item) == int:
            dpg.add_int_value(tag=key, default_value=item)
        elif type(item) == float:
            dpg.add_float_value(tag=key, default_value=item)
        elif type(item) == bool:
            dpg.add_bool_value(tag=key, default_value=item)

# The main window where everything will be based
with dpg.window(tag="main_window", menubar=False, no_collapse=True, no_close=True, no_scrollbar=True, no_scroll_with_mouse=True):
    with dpg.handler_registry():
        dpg.add_mouse_down_handler(button=dpg.mvMouseButton_Left, callback=lambda e: GRID.handle_grid_click("left"))
        dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=GRID.reset_drag_state)
        dpg.add_mouse_down_handler(button=dpg.mvMouseButton_Right, callback=lambda e: GRID.handle_grid_click("right"))
        dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Right, callback=GRID.reset_drag_state)

    with dpg.menu_bar(tag="main_menu_bar"):
        with dpg.menu(label = "Grid"):
            with dpg.menu(label = "Grid Size"):
                dpg.add_menu_item(label = "10 x 10", callback=lambda e: GRID.reset_grid(10, 10))
                dpg.add_menu_item(label = "15 x 15", callback=lambda e: GRID.reset_grid(15, 15))
                dpg.add_menu_item(label = "25 x 25", callback=lambda e: GRID.reset_grid(25, 25))
                dpg.add_menu_item(label = "50 x 50", callback=lambda e: GRID.reset_grid(50, 50))
            with dpg.menu(label = "Cell Size"):
                dpg.add_menu_item(label="25", callback=lambda e: GRID.update_grid(cell_size=25))
                dpg.add_menu_item(label="30", callback=lambda e: GRID.update_grid(cell_size=30))
                dpg.add_menu_item(label="35", callback=lambda e: GRID.update_grid(cell_size=35))
                dpg.add_menu_item(label="40", callback=lambda e: GRID.update_grid(cell_size=40))
                dpg.add_menu_item(label="45", callback=lambda e: GRID.update_grid(cell_size=45))
                dpg.add_menu_item(label="50", callback=lambda e: GRID.update_grid(cell_size=50))

            dpg.add_menu_item(label = "Advanced...", callback=lambda e: show_modal("advanced_grid_settings"))
        with dpg.menu(label = "Pathfinding"):
            dpg.add_menu_item(label = "Set Start Cell")
            dpg.add_menu_item(label = "Set End Cell")

# The Advanced Grid Settings window where you can go more in-depth with customizing the grid
with dpg.window(label="Advanced Grid Settings", modal=True, show=False, no_resize=True, tag="advanced_grid_settings", no_close=True):
    with dpg.table(header_row=False):
        dpg.add_table_column(width_fixed=True)
        dpg.add_table_column()

        with dpg.table_row():
            dpg.add_text("Cell Size:")
            dpg.add_drag_int(width=-1, min_value=MIN_CELL_SIZE, max_value=MAX_CELL_SIZE,
                             clamped=True, label="", source="cell_size", speed=0.1)

        with dpg.table_row():
            dpg.add_text("Grid Size:")
            dpg.add_drag_intx(label="", size=2, width=-1, source="grid_size",
                              min_value=MIN_GRID_AXIS_SIZE, max_value=MAX_GRID_AXIS_SIZE, clamped = True, speed=0.1)

        with dpg.table_row():
            dpg.add_text("Line Thickness:")
            dpg.add_drag_float(width=-1, min_value=MIN_LINE_THICKNESS, max_value=MAX_LINE_THICKNESS,
                             clamped=True, label="", source="line_thickness", speed=0.1)

        with dpg.table_row():
            dpg.add_text("Cell Color:")
            dpg.add_color_edit(label="", width=-1, no_drag_drop=True, source="cell_color")

        with dpg.table_row():
            dpg.add_text("Line Color:")
            dpg.add_color_edit(label="", width=-1, no_drag_drop=True, source="line_color")

        with dpg.table_row():
            dpg.add_text("Block Color:")
            dpg.add_color_edit(label="", width=-1, no_drag_drop=True, source="impassable_color")

        with dpg.table_row():
            dpg.add_text("Center Grid:")
            dpg.add_checkbox(label="", source="center_grid")

    dpg.add_separator()

    with dpg.group(horizontal=True):
        dpg.add_button(label="Cancel", width=130, callback=lambda e: GRID.close_advanced_window(True))
        dpg.add_button(label="Apply", width=130, callback=lambda e: GRID.close_advanced_window(False))

# Set the primary window (ties it to the viewport) to the main window
dpg.set_primary_window("main_window", True)
dpg.set_viewport_resize_callback(GRID.update_grid_position)

# THE 4 LINES BELOW MUST BE RUN FOR THE APPLICATION TO BE DISPLAYED!
dpg.setup_dearpygui()
dpg.show_viewport()

# Display the current grid
GRID.display_grid()

dpg.start_dearpygui()
dpg.destroy_context()