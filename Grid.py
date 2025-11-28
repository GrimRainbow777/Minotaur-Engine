import numpy as np
import dearpygui.dearpygui as dpg

class Cell:
    def __init__(self, x, y, passable = True):
        self.x = x
        self.y = y
        self.passable = passable

class Grid:
    def __init__(self, rows: int, cols: int, cell_size: int = 50):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.line_thickness = 1.0
        self.border_thickness = self.line_thickness + 2
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self.default_cell_color = (0.0, 0.0, 0.0, 0.0)
        self.impassable_color = (21.0, 22.0, 28.0, 255.0)
        self.line_cell_color = (0.0, 0.0, 0.0, 255.0)

        self.cells = np.empty((cols, rows), dtype=object)
        self.grid_centered = False

        self.last_painted_cell = None

        for x in range(cols):
            for y in range(rows):
                # Create a cell object with coordinates
                self.cells[x][y] = Cell(x, y)

    def reset_grid(self, rows: int = None, cols: int = None, cell_size: int = None):
        self.rows = rows if rows is not None else self.rows
        self.cols = cols if cols is not None else self.cols

        dpg.set_value("grid_size", (cols if cols is not None else self.cols, rows if rows is not None else self.rows))

        self.cell_size = cell_size if cell_size is not None else self.cell_size
        dpg.set_value("cell_size", cell_size if cell_size is not None else self.cell_size)
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self.cells = np.empty((self.cols, self.rows), dtype=object)

        self.last_painted_cell = None

        for x in range(self.cols):
            for y in range(self.rows):
                # Create a cell object with coordinates
                self.cells[x][y] = Cell(x, y)

        # 1. Delete the existing canvas if it exists
        if dpg.does_item_exist("grid_wrapper"):
            dpg.delete_item("grid_wrapper")
        self.display_grid()

    def handle_grid_click(self, type_of_click):
        # SAFETY CHECK:
        # If the grid doesn't exist (was deleted), stop immediately.
        if not dpg.does_item_exist("grid_wrapper"):
            return
        elif not dpg.get_item_state("grid_wrapper")['focused']:
            return

        pos = dpg.get_mouse_pos()
        x, y = pos[0], pos[1]

        rect_min = dpg.get_item_pos("grid_canvas")
        x = x - rect_min[0]
        y = y - rect_min[1]

        col = int(x // self.cell_size)
        row = int(y // self.cell_size)

        cell_tag = f"CELL_{col}_{row}"
        if 0 <= col < self.cols and 0 <= row < self.rows and cell_tag != self.last_painted_cell:
            # print(f"Clicked Cell: Row={row}, Col={col} (Tag: {cell_tag}")
            if self.cells[col][row].passable and type_of_click == "left":
                self.cells[col][row].passable = False
                dpg.configure_item(cell_tag, fill=self.impassable_color)
            elif type_of_click == "right":
                self.cells[col][row].passable = True
                dpg.configure_item(cell_tag, fill=self.default_cell_color)

            self.last_painted_cell = cell_tag

    def reset_drag_state(self):
        self.last_painted_cell = None

    def display_grid(self, no_padding_theme = None):
        if dpg.does_item_exist("grid_wrapper"):
            dpg.delete_item("grid_wrapper")

        # correct content region (not viewport!)
        content_w, content_h = dpg.get_item_width("main_window"), dpg.get_item_height("main_window")

        with dpg.child_window(tag="grid_wrapper", parent="main_window", horizontal_scrollbar=True, border=False, autosize_x=True, autosize_y=True):
            with dpg.drawlist(tag="grid_canvas", width=self.width, height=self.height):
                with dpg.draw_node(tag="grid_node"):
                    dpg.draw_rectangle(
                        pmin=(0, 0),
                        pmax=(self.width, self.height),
                        color=self.line_cell_color,
                        thickness=self.border_thickness,
                        fill=self.default_cell_color
                    )

                    for x in range(self.cols):
                        for y in range(self.rows):
                            xp = x * self.cell_size
                            yp = y * self.cell_size
                            dpg.draw_rectangle(
                                tag=f"CELL_{x}_{y}",
                                pmin=(xp, yp),
                                pmax=(xp + self.cell_size, yp + self.cell_size),
                                color=self.line_cell_color,
                                thickness=self.line_thickness,
                                fill=self.default_cell_color
                            )

        dpg.bind_item_theme("grid_wrapper", no_padding_theme)

        # correct centering
        if self.grid_centered:
            center_x = (content_w - self.width) // 2
            center_y = (content_h - self.height) // 2
            dpg.set_item_pos("grid_wrapper", (center_x, center_y))

    def on_resize(self, sender = None, app_data = None):
        content_w, content_h = dpg.get_item_width("main_window"), dpg.get_item_height("main_window")
        if self.grid_centered:
            center_x = (content_w - self.width) // 2
            center_y = (content_h - self.height) // 2

            dpg.set_item_pos("grid_wrapper", (center_x, center_y))

    def close_advanced_window(self, canceled: bool):
        dpg.configure_item("advanced_grid_settings", show=False)

        if not canceled:
            new_grid_size = dpg.get_value("grid_size")

            self.cols = new_grid_size[0]
            self.rows = new_grid_size[1]
            self.cell_size = dpg.get_value("cell_size")
            self.line_thickness = dpg.get_value("line_thickness")
            self.default_cell_color = dpg.get_value("cell_color")
            self.line_cell_color = dpg.get_value("line_color")
            self.impassable_color = dpg.get_value("impassable_color")
            self.grid_centered = dpg.get_value("center_grid")

            self.reset_grid()
        else:
            dpg.set_value("grid_size", (self.cols, self.rows))
            dpg.set_value("cell_size", self.cell_size)
            dpg.set_value("line_thickness", self.line_thickness)
            dpg.set_value("cell_color", self.default_cell_color)
            dpg.set_value("line_color", self.line_cell_color)
            dpg.set_value("impassable_color", self.impassable_color)
            dpg.set_value("center_grid", self.grid_centered)


