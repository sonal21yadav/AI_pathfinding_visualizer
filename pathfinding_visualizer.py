import random
import sys
import time
from collections import deque

import pygame

#  CONSTANTS
ROWS = 20
COLS = 30
CELL = 28
PANEL_WIDTH   = 330
HEADER_HEIGHT = 72
FOOTER_HEIGHT = 86
GRID_WIDTH    = COLS * CELL
GRID_HEIGHT   = ROWS * CELL
WINDOW_WIDTH  = GRID_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = HEADER_HEIGHT + GRID_HEIGHT + FOOTER_HEIGHT

#  COLORS & METADATA
COLORS = {
    "bg": (245, 241, 230),
    "bg_alt": (233, 242, 239),
    "panel": (250, 247, 240),
    "panel_soft": (240, 235, 225),
    "card": (255, 255, 252),
    "border": (182, 172, 155),
    "border_soft": (210, 201, 187),
    "text": (28,  35,  44 ),
    "muted": (96,  104, 112),
    "chip_text": (67,  75,  83 ),
    "empty": (247, 245, 238),
    "wall": (44,  44,  42 ),
    "start": (29,  158, 117),
    "end": (216, 90,  48 ),
    "visited": (181, 212, 244),
    "best_path": (239, 159, 39 ),
    "avg_path": (127, 119, 221),
    "worst_path": (226, 75,  74 ),
}

CASE_COLORS = {
    "Best Case":    COLORS["start"],
    "Average Case": COLORS["avg_path"],
    "Worst Case":   COLORS["worst_path"],
}

ALGO_BLURB = {
    "BFS":           "Explores level-by-level and guarantees shortest path on unweighted grids.",
    "DFS":           "Dives deep into one branch first and backtracks when blocked.",
    "A*":            "Balances known cost and estimated distance for efficient optimal paths.",
    "Hill Climbing": "Greedy local search moving to better immediate neighbors.",
    "Best First":    "Expands the most promising node according to heuristic only.",
    "MiniMax":       "Adversarial-style exploration with alternating maximize/minimize choices.",
}

TIME_COMPLEXITY = {
    "BFS":           ("O(1)",   "O(V+E)",   "O(V+E)"),
    "DFS":           ("O(1)",   "O(V+E)",   "O(V+E)"),
    "A*":            ("O(b^d)", "O(b^d)",   "O(b^d)"),
    "Hill Climbing": ("O(b*m)", "O(b*m)",   "O(b*m)"),
    "Best First":    ("O(b^m)", "O(b^m)",   "O(b^m)"),
    "MiniMax":       ("O(b^m)", "O(b^m)",   "O(b^m)"),
}

ALGORITHMS = ["BFS", "DFS", "A*", "Hill Climbing", "Best First", "MiniMax"]
MODES      = ["Best Case", "Average Case", "Worst Case"]
TOOL_WALL  = "wall"
TOOL_START = "start"
TOOL_END   = "end"



#  GRID UTILITIES
def make_grid():
    return [["empty" for _ in range(COLS)] for _ in range(ROWS)]


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(grid, node):
    r, c = node
    out = []
    for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != "wall":
            out.append((nr, nc))
    return out


def reconstruct_path(parent, end):
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()
    return path if len(path) > 1 else []

#  ALGORITHMS
def bfs(grid, start, end):
    q = deque([start])
    seen = {start}
    parent = {start: None}
    visited = []
    while q:
        curr = q.popleft()
        visited.append(curr)
        if curr == end:
            return visited, reconstruct_path(parent, end)
        for nb in neighbors(grid, curr):
            if nb not in seen:
                seen.add(nb)
                parent[nb] = curr
                q.append(nb)
    return visited, []


def dfs(grid, start, end):
    stack = [start]
    seen = set()
    parent = {start: None}
    visited = []
    while stack:
        curr = stack.pop()
        if curr in seen:
            continue
        seen.add(curr)
        visited.append(curr)
        if curr == end:
            return visited, reconstruct_path(parent, end)
        for nb in neighbors(grid, curr):
            if nb not in seen:
                parent[nb] = curr
                stack.append(nb)
    return visited, []


def astar(grid, start, end):
    open_set = [(heuristic(start, end), 0, start)]
    seen = set()
    parent = {start: None}
    g_score = {start: 0}
    visited = []
    while open_set:
        open_set.sort(key=lambda x: x[0])
        _, g_curr, curr = open_set.pop(0)
        if curr in seen:
            continue
        seen.add(curr)
        visited.append(curr)
        if curr == end:
            return visited, reconstruct_path(parent, end)
        for nb in neighbors(grid, curr):
            tentative = g_curr + 1
            if tentative < g_score.get(nb, float("inf")):
                g_score[nb] = tentative
                parent[nb] = curr
                h = heuristic(nb, end)
                open_set.append((tentative + h, tentative, nb))
    return visited, []


def hill_climbing(grid, start, end):
    curr = start
    seen = set()
    parent = {start: None}
    visited = []
    while curr is not None:
        if curr in seen:
            break
        seen.add(curr)
        visited.append(curr)
        if curr == end:
            return visited, reconstruct_path(parent, end)
        nbs = [n for n in neighbors(grid, curr) if n not in seen]
        nbs.sort(key=lambda n: heuristic(n, end))
        if nbs and heuristic(nbs[0], end) < heuristic(curr, end):
            nxt = nbs[0]
            parent[nxt] = curr
            curr = nxt
        else:
            break
    return visited, []


def best_first(grid, start, end):
    open_set = [(heuristic(start, end), start)]
    seen = set()
    parent = {start: None}
    visited = []
    while open_set:
        open_set.sort(key=lambda x: x[0])
        _, curr = open_set.pop(0)
        if curr in seen:
            continue
        seen.add(curr)
        visited.append(curr)
        if curr == end:
            return visited, reconstruct_path(parent, end)
        for nb in neighbors(grid, curr):
            if nb not in seen:
                parent[nb] = curr
                open_set.append((heuristic(nb, end), nb))
    return visited, []


def minimax(grid, start, end, depth=5):
    seen = set()
    parent = {start: None}
    visited = []
    def mm(node, d, is_max):
        if node in seen or d == 0:
            return heuristic(node, end)
        seen.add(node)
        visited.append(node)
        if node == end:
            return 0
        nbs = [n for n in neighbors(grid, node) if n not in seen]
        if not nbs:
            return heuristic(node, end)
        if is_max:
            best_val = -float("inf")
            for nb in nbs:
                val = mm(nb, d - 1, False)
                if val > best_val:
                    best_val = val
                    parent[nb] = node
            return best_val
        best_val = float("inf")
        for nb in nbs:
            val = mm(nb, d - 1, True)
            if val < best_val:
                best_val = val
                parent[nb] = node
        return best_val
    mm(start, depth, True)
    return visited, reconstruct_path(parent, end)


def run_algorithm(name, grid, start, end):
    if name == "BFS":           return bfs(grid, start, end)
    if name == "DFS":           return dfs(grid, start, end)
    if name == "A*":            return astar(grid, start, end)
    if name == "Hill Climbing": return hill_climbing(grid, start, end)
    if name == "Best First":    return best_first(grid, start, end)
    if name == "MiniMax":       return minimax(grid, start, end)
    return [], []


def apply_case_mode(base_grid, mode, start, end):
    grid = [row[:] for row in base_grid]
    if mode == "Best Case":
        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c] == "wall":
                    grid[r][c] = "empty"
    if mode == "Worst Case":
        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) == start or (r, c) == end:
                    continue
                if random.random() < 0.35:
                    grid[r][c] = "wall"
    return grid


#  VISUALIZER CLASS
class Visualizer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("AI Path Finding Visualizer - Python")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock  = pygame.time.Clock()
        self.title  = pygame.font.SysFont("Avenir Next", 22, bold=True)
        self.font   = pygame.font.SysFont("Avenir Next", 18, bold=True)
        self.small  = pygame.font.SysFont("Segoe UI",    14)
        self.tiny   = pygame.font.SysFont("Consolas",    13)
        self.badge  = pygame.font.SysFont("Segoe UI",    12, bold=True)

        self.grid        = make_grid()
        self.start       = (5, 3)
        self.end         = (14, 26)
        self.tool        = TOOL_WALL
        self.algorithm   = "A*"
        self.case_mode   = "Average Case"
        self.speed       = 18
        self.show_values = True
        self.mouse_down  = False
        self.running     = False
        self.visited_order = []
        self.path          = []
        self.visited_index = 0
        self.path_index    = 0
        self.path_started  = False
        self.last_tick     = 0
        self.path_start_at = 0
        self.stats         = None
        self.cell_states   = {}
        self.ui_buttons    = []

    # State management
    def clear_visualization(self):
        self.running = False
        self.visited_order = []
        self.path = []
        self.visited_index = self.path_index = 0
        self.path_started = False
        self.last_tick = self.path_start_at = 0
        self.stats = None
        self.cell_states = {}

    def reset_grid(self):
        self.clear_visualization()
        self.grid = make_grid()

    def speed_delay(self):
        return max(1, 21 - self.speed)

    def toggle_cell(self, r, c):
        if self.tool == TOOL_START:
            self.start = (r, c); self.clear_visualization(); return
        if self.tool == TOOL_END:
            self.end = (r, c); self.clear_visualization(); return
        if (r, c) == self.start or (r, c) == self.end:
            return
        self.grid[r][c] = "wall" if self.grid[r][c] != "wall" else "empty"
        self.clear_visualization()

    def erase_cell(self, r, c):
        if (r, c) in (self.start, self.end): return
        self.grid[r][c] = "empty"
        self.clear_visualization()

    def cell_at_mouse(self, pos):
        x, y = pos
        y -= HEADER_HEIGHT
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT: return None
        return (y // CELL, x // CELL)

    # Core run
    def visualize(self):
        self.clear_visualization()
        case_grid = apply_case_mode(self.grid, self.case_mode, self.start, self.end)
        self.grid = case_grid
        t0 = time.perf_counter()
        self.visited_order, self.path = run_algorithm(self.algorithm, case_grid, self.start, self.end)
        t1 = time.perf_counter()
        self.running = True
        self.last_tick = pygame.time.get_ticks()
        self.path_start_at = self.last_tick + len(self.visited_order) * self.speed_delay() + 50
        path_color = {"Best Case": "best_path", "Worst Case": "worst_path"}.get(self.case_mode, "avg_path")
        self.stats = {
            "algo": self.algorithm, "visited": len(self.visited_order),
            "path_len": len(self.path), "found": len(self.path) > 0,
            "time_ms": f"{(t1-t0)*1000:.2f}", "case_mode": self.case_mode,
            "path_color": path_color,
        }

    def animate(self):
        if not self.running: return
        now, delay = pygame.time.get_ticks(), self.speed_delay()
        if self.visited_index < len(self.visited_order):
            if now - self.last_tick >= delay:
                self.cell_states[self.visited_order[self.visited_index]] = "visited"
                self.visited_index += 1
                self.last_tick = now
            return
        if not self.path_started and now >= self.path_start_at:
            self.path_started = True
            self.last_tick = now
        if self.path_started and self.path_index < len(self.path):
            if now - self.last_tick >= delay * 2:
                self.cell_states[self.path[self.path_index]] = self.stats["path_color"]
                self.path_index += 1
                self.last_tick = now
            return
        self.running = False

    # UI button system
    def add_button(self, rect, action, value=None):
        self.ui_buttons.append({"rect": rect, "action": action, "value": value})

    def handle_ui_click(self, pos):
        for btn in reversed(self.ui_buttons):
            if btn["rect"].collidepoint(pos):
                a, v = btn["action"], btn["value"]
                if a == "algo":          self.algorithm = v
                elif a == "mode":        self.case_mode = v
                elif a == "tool":        self.tool = v
                elif a == "visualize" and not self.running: self.visualize()
                elif a == "clear":       self.clear_visualization()
                elif a == "reset":       self.reset_grid()
                elif a == "speed_inc":   self.speed = min(20, self.speed + 1)
                elif a == "speed_dec":   self.speed = max(1,  self.speed - 1)
                elif a == "toggle_values": self.show_values = not self.show_values
                return True
        return False

    # Events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE: pygame.quit(); sys.exit(0)
                if k == pygame.K_SPACE and not self.running: self.visualize()
                if k == pygame.K_c: self.clear_visualization()
                if k == pygame.K_r: self.reset_grid()
                if k == pygame.K_v: self.show_values = not self.show_values
                if k == pygame.K_s: self.tool = TOOL_START
                if k == pygame.K_e: self.tool = TOOL_END
                if k == pygame.K_d: self.tool = TOOL_WALL
                if k == pygame.K_b: self.case_mode = "Best Case"
                if k == pygame.K_a: self.case_mode = "Average Case"
                if k == pygame.K_w: self.case_mode = "Worst Case"
                if k == pygame.K_UP:   self.speed = min(20, self.speed + 1)
                if k == pygame.K_DOWN: self.speed = max(1,  self.speed - 1)
                if pygame.K_1 <= k <= pygame.K_6:
                    self.algorithm = ALGORITHMS[k - pygame.K_1]
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.handle_ui_click(event.pos): continue
                rc = self.cell_at_mouse(event.pos)
                if rc is None: continue
                self.mouse_down = True
                r, c = rc
                if event.button == 1: self.toggle_cell(r, c)
                if event.button == 3: self.erase_cell(r, c)
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
            if event.type == pygame.MOUSEMOTION and self.mouse_down:
                rc = self.cell_at_mouse(event.pos)
                if rc is None: continue
                r, c = rc
                if pygame.mouse.get_pressed()[0] and self.tool == TOOL_WALL:
                    if (r, c) not in (self.start, self.end):
                        self.grid[r][c] = "wall"; self.clear_visualization()
                if pygame.mouse.get_pressed()[2]:
                    self.erase_cell(r, c)

    # Drawing helpers
    def cell_color(self, r, c):
        if (r, c) == self.start: return COLORS["start"]
        if (r, c) == self.end:   return COLORS["end"]
        if (r, c) in self.cell_states: return COLORS[self.cell_states[(r, c)]]
        if self.grid[r][c] == "wall": return COLORS["wall"]
        return COLORS["empty"]

    def draw_chip(self, x, y, w, h, text, active=False, accent=(43, 52, 64)):
        bg     = COLORS["card"] if not active else accent
        fg     = COLORS["chip_text"] if not active else (255, 255, 255)
        border = COLORS["border_soft"] if not active else accent
        rect   = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, bg,     rect, border_radius=999)
        pygame.draw.rect(self.screen, border, rect, width=1, border_radius=999)
        label  = self.badge.render(text, True, fg)
        self.screen.blit(label, (x + (w - label.get_width()) // 2,
                                 y + (h - label.get_height()) // 2))

    def draw_click_button(self, x, y, w, h, text, action, value=None, active=False, accent=(43, 52, 64)):
        self.draw_chip(x, y, w, h, text, active=active, accent=accent)
        self.add_button(pygame.Rect(x, y, w, h), action, value)

    def draw_stat_card(self, x, y, w, h, label, value, value_color=None):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, COLORS["card"],        rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS["border_soft"], rect, width=1, border_radius=12)
        self.screen.blit(self.badge.render(label, True, COLORS["muted"]), (x + 10, y + 7))
        self.screen.blit(self.small.render(value, True, value_color or COLORS["text"]), (x + 10, y + 26))

    def draw_wrapped_text(self, text, x, y, max_width, color):
        words, line, line_h = text.split(" "), "", self.small.get_linesize()
        for word in words:
            candidate = (line + " " + word).strip()
            if self.small.size(candidate)[0] <= max_width:
                line = candidate; continue
            self.screen.blit(self.small.render(line, True, color), (x, y))
            y += line_h + 2; line = word
        if line: self.screen.blit(self.small.render(line, True, color), (x, y))

    # Draw sections
    def draw_background(self):
        self.screen.fill(COLORS["bg"])
        halo_a = pygame.Surface((420, 420), pygame.SRCALPHA)
        pygame.draw.circle(halo_a, (127, 119, 221, 28), (210, 210), 205)
        self.screen.blit(halo_a, (-100, -70))
        halo_b = pygame.Surface((500, 500), pygame.SRCALPHA)
        pygame.draw.circle(halo_b, (29, 158, 117, 22), (250, 250), 230)
        self.screen.blit(halo_b, (WINDOW_WIDTH - 430, -150))

    def draw_header(self):
        self.ui_buttons = []
        pygame.draw.rect(self.screen, COLORS["panel"], (0, 0, WINDOW_WIDTH, HEADER_HEIGHT))
        pygame.draw.line(self.screen, COLORS["border"],
                         (0, HEADER_HEIGHT - 1), (WINDOW_WIDTH, HEADER_HEIGHT - 1), 1)
        self.screen.blit(self.title.render("AI Pathfinding Visualizer", True, COLORS["text"]), (14, 10))
        self.screen.blit(self.badge.render("PYTHON EDITION � 6 ALGORITHMS", True, COLORS["muted"]), (16, 40))
        row1_y, x = 10, 350
        for algo in ALGORITHMS:
            w = max(66, 14 + self.badge.size(algo)[0] + 14)
            self.draw_click_button(x, row1_y, w, 24, algo, "algo", value=algo,
                                   active=(self.algorithm == algo), accent=(43, 52, 64))
            x += w + 6
        row2_y, x = 40, 350
        for mode in MODES:
            w = max(94, 14 + self.badge.size(mode)[0] + 14)
            self.draw_click_button(x, row2_y, w, 24, mode, "mode", value=mode,
                                   active=(self.case_mode == mode), accent=CASE_COLORS[mode])
            x += w + 6
        for tool_id, label in ((TOOL_WALL, "Wall"), (TOOL_START, "Start"), (TOOL_END, "End")):
            self.draw_click_button(x, row2_y, 68, 24, label, "tool", value=tool_id,
                                   active=(self.tool == tool_id), accent=(64, 72, 84))
            x += 74
        self.draw_click_button(x, row2_y, 86, 24, "Visualize", "visualize",
                               active=not self.running, accent=(29, 158, 117))
        x += 92
        self.draw_click_button(x, row2_y, 60, 24, "Clear", "clear")
        x += 66
        self.draw_click_button(x, row2_y, 60, 24, "Reset", "reset")

    def draw_grid(self):
        grid_bg = pygame.Rect(8, HEADER_HEIGHT + 8, GRID_WIDTH - 16, GRID_HEIGHT - 16)
        pygame.draw.rect(self.screen, COLORS["panel"],       grid_bg, border_radius=16)
        pygame.draw.rect(self.screen, COLORS["border_soft"], grid_bg, width=1, border_radius=16)
        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, HEADER_HEIGHT + r * CELL
                rect  = pygame.Rect(x, y, CELL, CELL)
                pygame.draw.rect(self.screen, self.cell_color(r, c), rect)
                pygame.draw.rect(self.screen, COLORS["border_soft"], rect, 1)
                if (r, c) == self.start:
                    self.screen.blit(self.small.render("S", True, (255,255,255)), (x+10, y+6))
                elif (r, c) == self.end:
                    self.screen.blit(self.small.render("E", True, (255,255,255)), (x+10, y+6))
                elif self.show_values and self.grid[r][c] != "wall":
                    v   = str(heuristic((r, c), self.end))
                    txt = self.tiny.render(v, True, (94, 104, 116))
                    self.screen.blit(txt, txt.get_rect(center=(x + CELL//2, y + CELL//2)))

    def draw_side_panel(self):
        px = GRID_WIDTH
        pygame.draw.rect(self.screen, COLORS["panel_soft"], (px, HEADER_HEIGHT, PANEL_WIDTH, GRID_HEIGHT))
        pygame.draw.line(self.screen, COLORS["border"], (px, HEADER_HEIGHT), (px, HEADER_HEIGHT + GRID_HEIGHT), 1)
        card = pygame.Rect(px + 12, HEADER_HEIGHT + 12, PANEL_WIDTH - 24, GRID_HEIGHT - 24)
        pygame.draw.rect(self.screen, COLORS["panel"],       card, border_radius=16)
        pygame.draw.rect(self.screen, COLORS["border_soft"], card, width=1, border_radius=16)
        y = HEADER_HEIGHT + 26
        self.screen.blit(self.font.render("Algorithm Insight", True, COLORS["text"]), (px + 24, y))
        y += 30
        self.draw_wrapped_text(ALGO_BLURB[self.algorithm], px + 24, y, PANEL_WIDTH - 48, COLORS["muted"])
        y += 74
        self.screen.blit(self.font.render("Results", True, COLORS["text"]), (px + 24, y))
        y += 28
        if self.stats:
            status_value = "Path Found" if self.stats["found"] else "No Path"
            status_color = COLORS["start"] if self.stats["found"] else COLORS["worst_path"]
            self.draw_stat_card(px + 24,  y, 136, 58, "STATUS", status_value, value_color=status_color)
            self.draw_stat_card(px + 170, y, 136, 58, "NODES",  str(self.stats["visited"]))
            y += 66
            self.draw_stat_card(px + 24,  y, 136, 58, "PATH",   str(self.stats["path_len"]))
            self.draw_stat_card(px + 170, y, 136, 58, "TIME",   f"{self.stats['time_ms']}ms")
            y += 76
            self.screen.blit(self.small.render("Time Complexity", True, COLORS["text"]), (px + 24, y))
            y += 22
            best, avg, worst = TIME_COMPLEXITY[self.stats["algo"]]
            self.draw_chip(px + 24, y, 282, 25, f"Best: {best}",    active=True, accent=COLORS["start"])
            y += 30
            self.draw_chip(px + 24, y, 282, 25, f"Average: {avg}",  active=True, accent=COLORS["avg_path"])
            y += 30
            self.draw_chip(px + 24, y, 282, 25, f"Worst: {worst}",  active=True, accent=COLORS["worst_path"])
        else:
            hint_box = pygame.Rect(px + 24, y, 282, 80)
            pygame.draw.rect(self.screen, COLORS["card"],        hint_box, border_radius=12)
            pygame.draw.rect(self.screen, COLORS["border_soft"], hint_box, width=1, border_radius=12)
            self.screen.blit(self.small.render("Press SPACE to run visualization", True, COLORS["muted"]), (px+34, y+22))
            self.screen.blit(self.small.render("Metrics will appear after run.",   True, COLORS["muted"]), (px+34, y+44))

    def draw_footer(self):
        y0 = HEADER_HEIGHT + GRID_HEIGHT
        pygame.draw.rect(self.screen, COLORS["panel"], (0, y0, WINDOW_WIDTH, FOOTER_HEIGHT))
        pygame.draw.line(self.screen, COLORS["border"], (0, y0), (WINDOW_WIDTH, y0), 1)
        self.screen.blit(self.tiny.render(
            "Tip: You can click all controls above. Keyboard shortcuts still work.",
            True, COLORS["muted"]), (14, y0 + 10))
        self.draw_click_button(WINDOW_WIDTH - 260, y0+8, 26, 24, "-", "speed_dec")
        self.draw_chip(        WINDOW_WIDTH - 230, y0+8, 74, 24, f"Speed {self.speed}")
        self.draw_click_button(WINDOW_WIDTH - 152, y0+8, 26, 24, "+", "speed_inc")
        self.draw_click_button(WINDOW_WIDTH - 122, y0+8, 108, 24,
            "Values: ON" if self.show_values else "Values: OFF",
            "toggle_values", active=self.show_values, accent=(127, 119, 221))
        legend = [("Start",   COLORS["start"]),     ("End",     COLORS["end"]),
                  ("Wall",    COLORS["wall"]),       ("Visited", COLORS["visited"]),
                  ("Best",    COLORS["best_path"]),  ("Average", COLORS["avg_path"]),
                  ("Worst",   COLORS["worst_path"])]
        x, y = 14, y0 + 36
        for label, color in legend:
            pill = pygame.Rect(x, y, 98, 28)
            pygame.draw.rect(self.screen, COLORS["card"],        pill, border_radius=999)
            pygame.draw.rect(self.screen, COLORS["border_soft"], pill, width=1, border_radius=999)
            pygame.draw.rect(self.screen, color, (x+8, y+8, 12, 12), border_radius=3)
            self.screen.blit(self.badge.render(label, True, COLORS["muted"]), (x+27, y+7))
            x += 103

    # Main loop
    def run(self):
        while True:
            self.handle_events()
            self.animate()
            self.draw_background()
            self.draw_header()
            self.draw_grid()
            self.draw_side_panel()
            self.draw_footer()
            pygame.display.flip()   # Show the rendered frame
            self.clock.tick(60)     # Cap at 60 FPS


if __name__ == "__main__":
    Visualizer().run()