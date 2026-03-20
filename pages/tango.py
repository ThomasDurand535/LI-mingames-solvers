import copy
import time
from collections import Counter
from pydoc import html
from xxlimited import new

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

from common.cookies import cookies
from common.types.tango import TangoCell, TangoCellSignEnum, TangoCellValEnum
from pages.basepage import BasePage


class TangoSolver(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver, "https://www.linkedin.com", cookies)
        self.grid: list[list[TangoCell]] = self.createGrid()
        self.solution = []

    def getCellValue(self, cell: list[WebElement]) -> TangoCellValEnum:
        try:
            return TangoCellValEnum(
                cell[0].find_element(By.CSS_SELECTOR, "g[id]").get_attribute("id")
            )
        except (ValueError, NoSuchElementException):
            return TangoCellValEnum.EMPTY

    def getCellSign(self, cell: WebElement) -> TangoCellSignEnum:
        try:
            return TangoCellSignEnum(
                cell.find_element(By.CSS_SELECTOR, "svg[data-testid]").get_attribute(
                    "aria-label"
                )
            )
        except (ValueError, NoSuchElementException):
            return TangoCellSignEnum.NONE

    def createCell(self, cell: list[WebElement]) -> TangoCell:
        try:
            value = self.getCellValue(cell)
            match len(cell):
                # 2 and not 3 cause we search "div" elements
                case 3:
                    right = self.getCellSign(cell[1])
                    bottom = self.getCellSign(cell[2])
                    return TangoCell(value=value, right=right, bottom=bottom)
                case 2:
                    sign = self.getCellSign(cell[1])
                    isRight = cell[1].value_of_css_property("right") == "0px"
                    return TangoCell(
                        value=value,
                        right=sign if isRight else TangoCellSignEnum.NONE,
                        bottom=sign if not isRight else TangoCellSignEnum.NONE,
                    )
                case _:
                    return TangoCell(
                        value=value,
                        right=TangoCellSignEnum.NONE,
                        bottom=TangoCellSignEnum.NONE,
                    )

        except (ValueError, NoSuchElementException):
            return TangoCell(
                value=TangoCellValEnum.EMPTY,
                right=TangoCellSignEnum.NONE,
                bottom=TangoCellSignEnum.NONE,
            )

    def createGrid(self):
        self.driver.get("https://www.linkedin.com/games/tango/")
        htmlGrid = (
            WebDriverWait(self.driver, 10)
            .until(
                presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-testid='interactive-grid']")
                )
            )
            .find_elements(By.CSS_SELECTOR, "div[data-cell-idx]")
        )

        # grid is set to 6 but might change in the future (I'm lazy)
        gridEdge = 6
        baseCell = TangoCell(
            value=TangoCellValEnum.EMPTY,
            right=TangoCellSignEnum.NONE,
            bottom=TangoCellSignEnum.NONE,
        )
        grid: list[list[TangoCell]] = [
            [baseCell for _ in range(gridEdge)] for _ in range(gridEdge)
        ]
        for i in range(gridEdge):
            for j in range(gridEdge):
                cellIndex = i * gridEdge + j
                cell = self.createCell(
                    htmlGrid[cellIndex].find_elements(By.TAG_NAME, "div")
                )
                grid[i][j] = cell
        return grid

    def canUseSign(
        self,
        values: list[TangoCellValEnum],
        sign: TangoCellValEnum,
        hasEqual: bool,
        pos: int,
    ) -> bool:
        filled = [v for v in values if v != TangoCellValEnum.EMPTY]
        if filled.count(sign) >= 3:
            return False
        n = len(values)

        if pos >= 1 and hasEqual and values[pos - 1] == sign:
            return False

        if pos >= 2 and values[pos - 1] == sign and values[pos - 2] == sign:
            return False

        if (
            pos >= 1
            and pos < n - 1
            and values[pos - 1] == sign
            and values[pos + 1] == sign
        ):
            return False

        if pos < n - 2 and values[pos + 1] == sign and values[pos + 2] == sign:
            return False

        return True

    def getValByValueAndSign(self, val: TangoCellValEnum, sign: TangoCellSignEnum):
        if sign == TangoCellSignEnum.EQUAL:
            return (
                TangoCellValEnum.SUN
                if val == TangoCellValEnum.SUN
                else TangoCellValEnum.MOON
            )
        return (
            TangoCellValEnum.MOON
            if val == TangoCellValEnum.SUN
            else TangoCellValEnum.SUN
        )

    def setSigns(self, grid: list[list[TangoCell]], x, y, edge):
        cell: TangoCell = grid[x][y]
        right, bottom, value = cell["right"], cell["bottom"], cell["value"]

        if right != TangoCellSignEnum.NONE:
            grid[x][y + 1]["value"] = (
                self.getValByValueAndSign(value, right)
                if value != TangoCellValEnum.EMPTY
                else TangoCellValEnum.EMPTY
            )

        if bottom != TangoCellSignEnum.NONE:
            grid[x + 1][y]["value"] = (
                self.getValByValueAndSign(value, bottom)
                if value != TangoCellValEnum.EMPTY
                else TangoCellValEnum.EMPTY
            )

    def fillGrid(self, newGrid: list[list[TangoCell]], edge) -> bool:

        for i in range(edge):
            for j in range(edge):
                if newGrid[i][j]["value"] != TangoCellValEnum.EMPTY:
                    continue
                row = [cell["value"] for cell in newGrid[i]]
                col = [newGrid[k][j]["value"] for k in range(edge)]

                canUseSunRow = self.canUseSign(
                    row,
                    TangoCellValEnum.SUN,
                    newGrid[i][j]["right"] == TangoCellSignEnum.EQUAL,
                    j,
                )
                canUseMoonRow = self.canUseSign(
                    row,
                    TangoCellValEnum.MOON,
                    newGrid[i][j]["right"] == TangoCellSignEnum.EQUAL,
                    j,
                )

                if (
                    self.canUseSign(
                        col,
                        TangoCellValEnum.SUN,
                        newGrid[i][j]["bottom"] == TangoCellSignEnum.EQUAL,
                        i,
                    )
                    and canUseSunRow
                ):
                    newGrid[i][j]["value"] = TangoCellValEnum.SUN
                    self.setSigns(newGrid, i, j, edge)
                    if self.fillGrid(copy.deepcopy(newGrid), edge):
                        return True

                if (
                    self.canUseSign(
                        col,
                        TangoCellValEnum.MOON,
                        newGrid[i][j]["bottom"] == TangoCellSignEnum.EQUAL,
                        i,
                    )
                    and canUseMoonRow
                ):
                    newGrid[i][j]["value"] = TangoCellValEnum.MOON
                    self.setSigns(newGrid, i, j, edge)
                    if self.fillGrid(copy.deepcopy(newGrid), edge):
                        return True

                return False
        self.solution = newGrid
        return True

    def getSolution(self):
        grid = self.grid.copy()
        edge = len(grid)
        self.fillGrid(grid, edge)

    def printGrid(self, grid, prop):
        for row in grid:
            print([cell[prop] for cell in row])

    def solvePuzzle(self):
        if len(self.solution) == 0:
            self.notSolved()
            return
        body = self.driver.find_element(By.TAG_NAME, "body")
        edge = len(self.solution)
        time.sleep(1)
        body.click()
        for i in range(edge):
            for j in range(edge):
                if self.grid[i][j]["value"] != TangoCellValEnum.EMPTY:
                    continue
                cellIndex = i * edge + j
                element = self.driver.find_element(
                    By.CSS_SELECTOR, f"div[data-cell-idx='{cellIndex}']"
                )
                if self.solution[i][j]["value"] == TangoCellValEnum.SUN:
                    element.click()
                    continue
                element.click()
                element.click()
