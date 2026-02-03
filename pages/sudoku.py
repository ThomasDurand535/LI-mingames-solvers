import copy
import math
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from common.cookies import cookies
from pages.basepage import BasePage

possibleValues = [1, 2, 3, 4, 5, 6]


class SudokuSolver(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://www.linkedin.com", cookies)
        self.grid = self.createGrid()
        self.sol: list[list[int]] | None = None

    def createGrid(self):
        self.driver.get("https://www.linkedin.com/games/mini-sudoku/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sudoku-grid"))
        )
        grid: list[list[int]] = [[0 for _ in range(6)] for _ in range(6)]
        for i in range(6):
            for j in range(6):
                value = (
                    self.driver.find_element(
                        By.CSS_SELECTOR, f"div[data-cell-idx='{i * 6 + j}']"
                    )
                    .find_element(By.CLASS_NAME, "sudoku-cell-content")
                    .text
                )
                grid[i][j] = int(value) if value else 0
        return grid

    def getPossibleValues(self, grid, x, y):
        vals = possibleValues.copy()
        for i in range(6):
            if grid[i][y] != 0 and grid[i][y] in vals:
                vals.remove(grid[i][y])

        for j in range(6):
            if grid[x][j] != 0 and grid[x][j] in vals:
                vals.remove(grid[x][j])
        subGridX = math.floor(x / 2) * 2
        subGridY = math.floor(y / 3) * 3

        for i in range(2):
            for j in range(3):
                current = grid[subGridX + i][subGridY + j]
                if current != 0 and current in vals:
                    vals.remove(current)
        return vals

    def nextZero(self, grid: list[list[int]]):
        for i in range(6):
            for j in range(6):
                if grid[i][j] == 0:
                    return {"x": i, "y": j}
        return None

    def rcs(self, grid):
        next = self.nextZero(grid)

        if not next:
            self.sol = grid
            return True

        x, y = next["x"], next["y"]
        possibleValues = self.getPossibleValues(grid, x, y)

        if len(possibleValues) == 0:
            return False

        for val in possibleValues:
            gridCopy = copy.deepcopy(grid)
            gridCopy[x][y] = val
            if self.rcs(gridCopy):
                return True

        return False

    def solve(self):
        next = self.nextZero(self.grid)
        if not next:
            return
        self.rcs(self.grid)

        return self.sol

    def solvePuzzle(self, solution):
        time.sleep(2)
        body = self.driver.find_element(By.TAG_NAME, "body")
        for i in range(6):
            for j in range(6):
                cell = self.driver.find_element(
                    By.CSS_SELECTOR, f"div[data-cell-idx='{i * 6 + j}']"
                ).find_element(By.CLASS_NAME, "sudoku-cell-content")
                try:
                    cell.click()
                    body.send_keys(solution[i][j])
                except ():
                    pass
