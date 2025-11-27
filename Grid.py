import numpy as np
import dearpygui.dearpygui as dpg
from dearpygui.dearpygui import window


class Cell:
    def __init__(self, x, y, passable = True):
        self.x = x
        self.y = y
        self.passable = passable

class Grid:
    def __init__(self, rows: int, cols: int, cell_size: int = 50):
        self.rows = rows
        self.cols = cols
        self.width = cols * cell_size
        self.height = rows * cell_size
        self.cell_size = cell_size
        self.line_thickness = 1.0
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
        if dpg.does_item_exist("grid_canvas"):
            dpg.delete_item("grid_canvas")
        self.display_grid()

    def handle_grid_click(self, type_of_click):
        # SAFETY CHECK:
        # If the grid doesn't exist (was deleted), stop immediately.
        if not dpg.does_item_exist("grid_canvas") or dpg.get_item_state("main_window")['focused'] == False:
            return

        pos = dpg.get_mouse_pos()
        x, y = pos[0], pos[1]

        rect_min = dpg.get_item_rect_min("grid_canvas")
        x = x - rect_min[0]
        y = y - (rect_min[1] - dpg.get_item_height("main_menu_bar"))

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

    def display_grid_old(self):
        # Extra precaution if for some reason the previous grid was not deleted
        if dpg.does_item_exist("grid_canvas"):
            dpg.delete_item("grid_canvas")

        with dpg.drawlist(tag="grid_canvas", width=self.width, height=self.height, parent="main_window", pos=((dpg.get_viewport_width() - self.width) / 2, (dpg.get_viewport_height() - self.height) / 2)) as dl:
            w = self.width
            h = self.height
            centered_start_point = ((dpg.get_viewport_width() - self.width) / 2,
                                    (dpg.get_viewport_height() - self.height) / 2)
            print(centered_start_point)

            # Border
            dpg.draw_rectangle(
                pmin=(0, 0) if self.grid_centered else centered_start_point,
                pmax=(w, h) if self.grid_centered else (w + centered_start_point[0], h + centered_start_point[1]),
                color=self.line_cell_color,
                thickness=self.line_thickness+2,
                fill=self.default_cell_color,
                parent=dl
            )

            # Cells
            for x in range(self.cols):
                for y in range(self.rows):
                    p_min=(x * self.cell_size, y * self.cell_size) if not self.grid_centered else (x * self.cell_size + centered_start_point[0], y * self.cell_size + centered_start_point[1])
                    p_max = ((x * self.cell_size) + self.cell_size, (y * self.cell_size) + self.cell_size) if not self.grid_centered else ((x * self.cell_size) + self.cell_size + centered_start_point[0], (y * self.cell_size) + self.cell_size + centered_start_point[1])
                    dpg.draw_rectangle(
                        tag=f"CELL_{x}_{y}",
                        pmin=p_min,
                        pmax=p_max,
                        color=self.line_cell_color,
                        thickness=self.line_thickness,
                        fill=self.default_cell_color,
                        parent=dl
                    )

    def display_grid(self):
        if dpg.does_item_exist("grid_canvas"):
            dpg.delete_item("grid_canvas")

        # correct content region (not viewport!)
        content_w, content_h = dpg.get_item_rect_size("main_window")

        with dpg.drawlist(tag="grid_canvas", width=content_w, height=content_h, parent="main_window"):
            with dpg.draw_node(tag="grid_node"):
                dpg.draw_rectangle(
                    pmin=(0, 0),
                    pmax=(self.width, self.height),
                    color=self.line_cell_color,
                    thickness=self.line_thickness + 2,
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

        # correct centering
        if self.grid_centered:
            center_x = (content_w - self.width) / 2
            center_y = (content_h - self.height) / 2
            dpg.apply_transform("grid_node", dpg.create_translation_matrix([center_x, center_y]))

    def on_resize(self, sender = None, app_data = None):
        content_w, content_h = dpg.get_item_rect_size("main_window")
        if self.grid_centered:
            center_x = (content_w - self.width) / 2
            center_y = (content_h - self.height) / 2

            # This applies a translation matrix to everything in "grid_node"
            dpg.apply_transform("grid_node", dpg.create_translation_matrix([center_x, center_y]))

        if dpg.does_item_exist("grid_canvas"):
            dpg.configure_item("grid_canvas", width=content_w, height=content_h)

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


