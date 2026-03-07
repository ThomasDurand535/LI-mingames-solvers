import math
import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from common.cookies import cookies
from pages.basepage import BasePage

DIRS = [Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_LEFT, Keys.ARROW_UP]
dx = [0, 1, 0, -1]
dy = [1, 0, -1, 0]


class ZipSolver(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://www.linkedin.com", cookies)
        self.grid = self.createGrid()
        self.n = len(self.grid)
        self.visited = [[False] * self.n for _ in range(self.n)]
        self.total_numbers = max(max(row) for row in self.grid)
        self.solution = []

    def createGrid(self):
        self.driver.get("https://www.linkedin.com/games/zip/")
        htmlGrid = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-testid='interactive-grid']")
            )
        )
        edge = int(math.sqrt(len(htmlGrid.find_elements(By.XPATH, "./*"))))
        grid: list[list[int]] = [[0 for _ in range(edge)] for _ in range(edge)]
        for i in range(edge):
            for j in range(edge):
                value = self.driver.find_element(
                    By.CSS_SELECTOR, f"div[data-cell-idx='{i * edge + j}']"
                ).text
                grid[i][j] = int(value) if value else 0
        return grid

    def printGrid(self):
        for row in self.grid:
            print(row)

    def in_bounds(self, x, y):
        return 0 <= x < self.n and 0 <= y < self.n

    def dfs(self, x, y, path_dirs, next_number):
        if next_number > self.total_numbers and all(all(row) for row in self.visited):
            return True
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]
            if not self.in_bounds(nx, ny) or self.visited[nx][ny]:
                continue
            val = self.grid[nx][ny]
            if val == 0 or val == next_number:
                self.visited[nx][ny] = True
                path_dirs.append(DIRS[d])
                original_next = next_number
                if val == next_number:
                    next_number += 1
                if self.dfs(nx, ny, path_dirs, next_number):
                    return True
                self.visited[nx][ny] = False
                path_dirs.pop()
                next_number = original_next
        return False

    def getZipSolution(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 1:
                    self.visited[i][j] = True
                    path_dirs = []
                    if self.dfs(i, j, path_dirs, 2):
                        self.solution = path_dirs
                        return
        self.solution = []

    def solvePuzzle(self):
        if len(self.solution) == 0:
            self.notSolved()
            return
        body = self.driver.find_element(By.TAG_NAME, "body")
        time.sleep(1)
        for key in self.solution:
            body.send_keys(key)
