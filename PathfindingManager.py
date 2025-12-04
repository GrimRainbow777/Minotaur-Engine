import dearpygui.dearpygui as dpg

from Grid import Grid, get_cell_tag


class PathfindingManager:
    def __init__(self, grid: Grid = None):
        self.grid = grid
        self.setting_start = False
        self.setting_goal = False
        self.last_highlighted_cell = None

        self.start_color = (79, 225, 46, 255)
        self.goal_color = (255, 0, 0, 255)

        self.start = None
        self.goal = None
        self.path = None

    def set_start_cell(self, x: int, y: int):
        new_start = self.grid.get_cell_from_pos(x, y)
        if new_start is None: return False
        if self.start:
            self.start.is_start = False
            dpg.configure_item(item=get_cell_tag(self.start.x, self.start.y),
                               fill=self.grid.default_cell_color)
        dpg.hide_item("pathfinding_registry")
        self.setting_start = False
        if not new_start.is_start and not new_start.is_goal:
            self.start = new_start
            new_start.is_start = True
            new_start.passable = True
            dpg.configure_item(item=get_cell_tag(new_start.x, new_start.y),
                               color=self.grid.line_cell_color,
                               thickness=self.grid.line_thickness,
                               fill=self.start_color)
            return True
        return False

    def set_goal_cell(self, x: int, y: int):
        new_goal = self.grid.get_cell_from_pos(x, y)
        if new_goal is None: return False
        # dpg.configure_item(item=get_cell_tag(new_goal.x, new_goal.y),
        #                    thickness=self.grid.line_thickness,)
        if self.goal:
            self.goal.is_goal = False
            dpg.configure_item(item=get_cell_tag(self.goal.x, self.goal.y),
                               fill=self.grid.default_cell_color)
        dpg.hide_item("pathfinding_registry")
        self.setting_goal = False
        if not new_goal.is_start and not new_goal.is_goal:
            self.start = new_goal
            new_goal.is_start = True
            new_goal.passable = True
            dpg.configure_item(item=get_cell_tag(new_goal.x, new_goal.y),
                               color=self.grid.line_cell_color,
                               thickness=self.grid.line_thickness,
                               fill=self.goal_color)
            return True
        return False

    def on_setting_start(self):
        self.setting_start = True
        self.setting_goal = False
        self.last_highlighted_cell = None
        dpg.show_item("pathfinding_registry")

    def on_setting_goal(self):
        self.setting_goal = True
        self.setting_start = False
        self.last_highlighted_cell = None
        dpg.show_item("pathfinding_registry")

    def mouse_visual_movement(self):
        if self.setting_start or self.setting_goal:
            if self.last_highlighted_cell:
                dpg.configure_item(item=get_cell_tag(self.last_highlighted_cell.x, self.last_highlighted_cell.y),
                                   color=self.grid.line_cell_color,
                                   thickness=self.grid.line_thickness)
                self.last_highlighted_cell = None
            if dpg.get_item_state("grid_canvas")['hovered']:
                x, y = dpg.get_drawing_mouse_pos()
                hovered_cell = self.grid.get_cell_from_pos(x, y)
                if hovered_cell:
                    self.last_highlighted_cell = hovered_cell
                    dpg.configure_item(item=get_cell_tag(hovered_cell.x, hovered_cell.y),
                                       color=self.start_color if self.setting_start else self.goal_color,
                                       thickness=self.grid.border_thickness)
