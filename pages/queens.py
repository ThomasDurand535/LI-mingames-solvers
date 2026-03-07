import math
import time
from collections import Counter

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from common.cookies import cookies
from pages.basepage import BasePage

directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


class QueensSolver(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://www.linkedin.com", cookies)
        self.grid = self.createGrid()

        self.sortedAreas = []
        self.usedCols = []
        self.usedRows = []

        self.solution = []

    def createGrid(self):
        self.driver.get("https://www.linkedin.com/games/queens/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-testid='interactive-grid']")
            )
        )

        gameGridHtml = self.driver.find_element(
            By.CSS_SELECTOR, "div[data-testid='interactive-grid']"
        ).find_elements(By.CSS_SELECTOR, "div[data-cell-idx]")
        nbCells = len(gameGridHtml)
        edge = int(math.sqrt(nbCells))
        grid: list[list[str]] = [["" for _ in range(edge)] for _ in range(edge)]

        for i in range(edge):
            for j in range(edge):
                cellIndex = i * edge + j
                grid[i][j] = gameGridHtml[cellIndex].value_of_css_property(
                    "background-color"
                )

        return grid

    def isThereAnAdjacentCrown(self, gridRes, x, y):
        for di, dj in directions:
            dx, dy = x + di, y + dj
            if len(gridRes) > dx >= 0 and len(gridRes) > dy >= 0:
                if gridRes[dx][dy]:
                    return True
        return False

    def isSolutionValid(self, gridRes):
        colWithCrown = []
        rowWithCrown = []
        for i in range(len(gridRes)):
            for j in range(len(gridRes)):
                if gridRes[i][j]:
                    if self.isThereAnAdjacentCrown(gridRes, i, j):
                        return False
                    colWithCrown.append(i)
                    rowWithCrown.append(j)
        colCounter = Counter(colWithCrown)
        rowCounter = Counter(rowWithCrown)
        return not (
            any(countCol > 1 for countCol in colCounter.values())
            or any(countRow > 1 for countRow in rowCounter.values())
        )

    def browseGrid(self, gridRes, colorIndex):
        if colorIndex == len(self.sortedAreas):
            result = self.isSolutionValid(gridRes)
            if result:
                self.solution = gridRes
            return result

        for i in range(len(gridRes)):
            for j in range(len(gridRes)):
                if self.grid[i][j] == self.sortedAreas[colorIndex]:
                    if self.isThereAnAdjacentCrown(gridRes, i, j):
                        continue
                    if j in self.usedCols or i in self.usedRows:
                        continue

                    gridRes[i][j] = True
                    self.usedCols.append(j)
                    self.usedRows.append(i)
                    if self.browseGrid(gridRes, colorIndex + 1):
                        return True

                    self.usedRows.pop()
                    self.usedCols.pop()
                    gridRes[i][j] = False
        return False

    def getAreasCounterSorted(self):
        flat_list = [item for sublist in self.grid for item in sublist]
        areaCounter = Counter(flat_list)
        sorted_strings = [
            item for item, _ in sorted(areaCounter.items(), key=lambda x: x[1])
        ]
        return sorted_strings

    def getSolution(self):
        gridLength = len(self.grid)
        gridRes: list[list[bool]] = [
            [False for _ in range(gridLength)] for _ in range(gridLength)
        ]

        self.sortedAreas = self.getAreasCounterSorted()
        self.browseGrid(gridRes, 0)
        print(self.solution)

    def solvePuzzle(self):
        time.sleep(1)
        if len(self.solution) == 0:
            self.notSolved()
            return
        edge = len(self.solution)
        for i in range(edge):
            for j in range(edge):
                if self.solution[i][j]:
                    cellIndex = i * edge + j
                    element = self.driver.find_element(
                        By.CSS_SELECTOR, f"div[data-cell-idx='{cellIndex}']"
                    )
                    element.click()
                    element.click()
