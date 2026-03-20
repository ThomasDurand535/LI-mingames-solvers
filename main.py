from selenium import webdriver

from pages.queens import QueensSolver
from pages.sudoku import SudokuSolver
from pages.tango import TangoSolver
from pages.zip import ZipSolver

driver = webdriver.Firefox()


zip = ZipSolver(driver)
zip.getSolution()
zip.solvePuzzle()

driver.switch_to.new_window("tab")

sudoku = SudokuSolver(driver)
sudoku.getSolution()
sudoku.solvePuzzle()

driver.switch_to.new_window("tab")

queens = QueensSolver(driver)
queens.getSolution()
queens.solvePuzzle()

driver.switch_to.new_window("tab")

tango = TangoSolver(driver)
tango.getSolution()
tango.solvePuzzle()
