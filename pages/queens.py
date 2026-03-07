import math
from collections import Counter

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from common.cookies import cookies
from pages.basepage import BasePage


class QueensSolver(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://www.linkedin.com", cookies)
        self.grid = self.createGrid()
        self.sortedAreas = []
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

    def isSolutionValid(self, gridRes):
        colorsWithCrown = []
        colWithCrown = []
        rowWithCrown = []
        for i in range(len(gridRes)):
            for j in range(len(gridRes)):
                if gridRes[i][j]:
                    colorsWithCrown.append(self.grid[i][j])
                    colWithCrown.append(i)
                    rowWithCrown.append(j)
        colorCounter = Counter(colorsWithCrown)
        colCounter = Counter(colWithCrown)
        rowCounter = Counter(rowWithCrown)
        return not (
            any(count > 1 for count in colorCounter.values())
            or any(countCol > 1 for countCol in colCounter.values())
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
                    gridRes[i][j] = True
                    if self.browseGrid(gridRes, colorIndex + 1):
                        return True
                    gridRes[i][j] = False
                    continue
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
        return self.solution

    def solvePuzzle(self):
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
