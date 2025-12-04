import dearpygui.dearpygui as dpg
import numpy as np


class Cell:
    def __init__(self, x, y, passable=True, is_start=False, is_goal=False):
        self.x = x
        self.y = y
        self.is_start = is_start
        self.is_goal = is_goal
        self.passable = passable


def get_cell_tag(x, y):
    return f"CELL_{x}_{y}"


class Grid:
    def __init__(self, rows: int, cols: int, cell_size: int = 50):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.line_thickness = 1.0
        self.border_thickness = self.line_thickness * 2
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self.default_cell_color = (0.0, 0.0, 0.0, 0.0)
        self.impassable_color = (255.0, 155.0, 28.0, 255.0)
        self.line_cell_color = (255.0, 255.0, 255.0, 125.0)

        self.grid_original_pos = None

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

        self.cell_size = cell_size if cell_size is not None else self.cell_size
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

    def get_cell_from_pos(self, x, y):
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)

        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.cells[col][row]
        return None

    def handle_grid_click(self, type_of_click):
        # SAFETY CHECK:
        # If the grid doesn't exist (was deleted), stop immediately.
        if not dpg.does_item_exist("grid_wrapper"):
            return
        elif not dpg.get_item_state("grid_canvas")['hovered']:
            return

        pos = dpg.get_drawing_mouse_pos()
        cell = self.get_cell_from_pos(pos[0], pos[1])

        cell_tag = get_cell_tag(cell.x, cell.y)
        if cell and cell_tag != self.last_painted_cell:
            # print(f"Clicked Cell: Row={row}, Col={col} (Tag: {cell_tag}")
            if cell.is_start or cell.is_goal: return
            if cell.passable and type_of_click == "left":
                cell.passable = False
                dpg.configure_item(cell_tag, fill=self.impassable_color)
            elif type_of_click == "right":
                cell.passable = True
                dpg.configure_item(cell_tag, fill=self.default_cell_color)

            self.last_painted_cell = cell_tag

    def reset_drag_state(self):
        self.last_painted_cell = None

    def display_grid(self):
        if self.grid_original_pos is None:
            self.grid_original_pos = (dpg.get_value("main_window_padding"),
                                      dpg.get_value("main_window_padding") + dpg.get_item_height("main_menu_bar"))

        if dpg.does_item_exist("grid_wrapper"):
            dpg.delete_item("grid_wrapper")

        # correct content region (not viewport!)
        content_w, content_h = dpg.get_item_width("main_window"), dpg.get_item_height(
            "main_window") + dpg.get_item_height("main_menu_bar")

        with dpg.child_window(tag="grid_wrapper", parent="main_window", horizontal_scrollbar=True, border=False,
                              pos=self.grid_original_pos):
            with dpg.drawlist(tag="grid_canvas", width=self.width, height=self.height):
                with dpg.draw_node(tag="grid_node"):
                    dpg.draw_rectangle(
                        tag="grid_border",
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
                                tag=get_cell_tag(x, y),
                                pmin=(xp, yp),
                                pmax=(xp + self.cell_size, yp + self.cell_size),
                                color=self.line_cell_color,
                                thickness=self.line_thickness,
                                fill=self.default_cell_color
                            )

        # correct centering
        if self.grid_centered and not self.width >= content_w and not self.height >= content_h:
            center_x = (content_w - self.width) // 2
            center_y = (content_h - self.height) // 2

            if center_x >= 0 and center_y >= 0:
                dpg.set_item_pos("grid_wrapper", (center_x, center_y))
            elif center_x >= 0 and not center_y >= 0:
                dpg.set_item_pos("grid_wrapper", (center_x, self.grid_original_pos[1]))
            elif not center_x >= 0 and center_y >= 0:
                dpg.set_item_pos("grid_wrapper", (self.grid_original_pos[0], center_y))
            else:
                dpg.set_item_pos("grid_wrapper", self.grid_original_pos)

    def update_grid(self, grid_size=None, cell_size=None, line_thickness=None, default_cell_color=None,
                    line_cell_color=None, impassable_color=None, grid_centered=None, clear=False):
        if not dpg.does_item_exist("grid_wrapper"):
            return

        redraw_grid = ((grid_size[0], grid_size[1]) != (self.cols, self.rows)) if grid_size is not None else False
        self.cols = grid_size[0] if grid_size is not None else self.cols
        self.rows = grid_size[1] if grid_size is not None else self.rows
        self.cell_size = cell_size if cell_size is not None else self.cell_size
        self.line_thickness = line_thickness if line_thickness is not None else self.line_thickness
        self.default_cell_color = default_cell_color if default_cell_color is not None else self.default_cell_color
        self.line_cell_color = line_cell_color if line_cell_color is not None else self.line_cell_color
        self.impassable_color = impassable_color if impassable_color is not None else self.impassable_color
        self.grid_centered = grid_centered if grid_centered is not None else self.grid_centered
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self.border_thickness = self.line_thickness * 2

        dpg.set_value("grid_size", (self.cols, self.rows))
        dpg.set_value("cell_size", self.cell_size)
        dpg.set_value("line_thickness", self.line_thickness)

        if redraw_grid:
            self.reset_grid()
            return

        dpg.configure_item("grid_canvas", width=self.width, height=self.height)
        dpg.configure_item("grid_border", pmax=(self.width, self.height), color=self.line_cell_color,
                           thickness=self.border_thickness, fill=self.default_cell_color)

        for row in self.cells:
            for cell in row:
                xp = cell.x * self.cell_size
                yp = cell.y * self.cell_size
                cell.passable = True if clear else cell.passable
                dpg.configure_item(
                    get_cell_tag(cell.x, cell.y),
                    pmin=(xp, yp),
                    pmax=(xp + self.cell_size, yp + self.cell_size),
                    color=self.line_cell_color,
                    thickness=self.line_thickness,
                    fill=self.default_cell_color if cell.passable else self.impassable_color
                )

        self.update_grid_position()

    def update_grid_position(self, sender=None, app_data=None):
        content_w, content_h = dpg.get_item_width("main_window"), dpg.get_item_height(
            "main_window") + dpg.get_item_height("main_menu_bar")
        if self.grid_centered:
            center_x = (content_w - self.width) // 2
            center_y = (content_h - self.height) // 2

            if center_x >= 0 and center_y >= 0:
                dpg.set_item_pos("grid_wrapper", (center_x, center_y))
            elif center_x >= 0 and not center_y >= 0:
                dpg.set_item_pos("grid_wrapper", (center_x, self.grid_original_pos[1]))
            elif not center_x >= 0 and center_y >= 0:
                dpg.set_item_pos("grid_wrapper", (self.grid_original_pos[0], center_y))
            else:
                dpg.set_item_pos("grid_wrapper", self.grid_original_pos)
        else:
            dpg.set_item_pos("grid_wrapper", self.grid_original_pos)

    def close_advanced_window(self, canceled: bool):
        dpg.configure_item("advanced_grid_settings", show=False)

        if not canceled:
            self.update_grid(grid_size=dpg.get_value("grid_size"),
                             cell_size=dpg.get_value("cell_size"),
                             line_thickness=dpg.get_value("line_thickness"),
                             default_cell_color=dpg.get_value("cell_color"),
                             line_cell_color=dpg.get_value("line_color"),
                             impassable_color=dpg.get_value("impassable_color"),
                             grid_centered=dpg.get_value("center_grid"))
        else:
            dpg.set_value("grid_size", (self.cols, self.rows))
            dpg.set_value("cell_size", self.cell_size)
            dpg.set_value("line_thickness", self.line_thickness)
            dpg.set_value("cell_color", self.default_cell_color)
            dpg.set_value("line_color", self.line_cell_color)
            dpg.set_value("impassable_color", self.impassable_color)
            dpg.set_value("center_grid", self.grid_centered)