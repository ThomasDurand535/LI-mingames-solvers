from selenium import webdriver

from pages.sudoku import SudokuSolver
from pages.zip import ZipSolver

driver = webdriver.Firefox()


zip = ZipSolver(driver)
zipSolution = zip.getZipSolution()
zip.solvePuzzle(zipSolution) if zipSolution else print(
    "no solution for zip has been found"
)

driver.switch_to.new_window("tab")

sudoku = SudokuSolver(driver)
sudokuSolution = sudoku.solve()
sudoku.solvePuzzle(sudokuSolution) if sudokuSolution else print(
    "no solution for sudoku has been found"
)
