import math

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from common.cookies import cookies
from pages.basepage import BasePage

# Directions and movement deltas for navigating the grid
DIRS = [Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_LEFT, Keys.ARROW_UP]
dx = [0, 1, 0, -1]  # Change in x-coordinate for each direction
dy = [1, 0, -1, 0]  # Change in y-coordinate for each direction


class ZipSolver(BasePage):
    def __init__(self):
        # Initialize the BasePage with LinkedIn URL and cookies
        super().__init__("https://www.linkedin.com", cookies)

        # Create the game grid by scraping the webpage
        self.grid = self.createGrid()
        self.n = len(self.grid)  # Grid size (assume square)

        # Keep track of visited cells during DFS
        self.visited = [[False] * self.n for _ in range(self.n)]

        # The largest number on the grid
        self.total_numbers = max(max(row) for row in self.grid)

    def createGrid(self):
        """
        Navigate to the LinkedIn Zip game page and scrape the grid numbers.
        Returns a 2D list representing the grid.
        """
        self.driver.get("https://www.linkedin.com/games/zip/")

        # Wait until the interactive grid element is present
        htmlGrid = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-testid='interactive-grid']")
            )
        )

        # Calculate the grid's edge length assuming it's square
        edge = int(math.sqrt(len(htmlGrid.find_elements(By.XPATH, "./*"))))

        # Initialize empty grid
        grid: list[list[int]] = [[0 for _ in range(edge)] for _ in range(edge)]

        # Fill the grid with numbers from the webpage
        for i in range(edge):
            for j in range(edge):
                value = self.driver.find_element(
                    By.CSS_SELECTOR, f"div[data-cell-idx='{i * edge + j}']"
                ).text
                # Convert string to int; empty cells become 0
                grid[i][j] = int(value) if value else 0

        return grid

    def printGrid(self):
        """Print the current grid to the console (useful for debugging)."""
        for row in self.grid:
            print(row)

    def in_bounds(self, x, y):
        """Check if (x, y) is inside the grid boundaries."""
        return 0 <= x < self.n and 0 <= y < self.n

    def dfs(self, x, y, path_dirs, next_number):
        """
        Depth-First Search to traverse the grid according to the game's rules:
        - Can move to a cell if it is zero or the next number in sequence
        - Keep track of visited cells and move directions

        Args:
            x, y: current cell coordinates
            path_dirs: list of movement directions so far
            next_number: the next number we need to visit
        """
        # If all numbers are visited and all cells are filled
        if next_number > self.total_numbers and all(all(row) for row in self.visited):
            return True

        # Explore all four directions
        for d in range(4):
            nx, ny = x + dx[d], y + dy[d]

            # Skip if out of bounds or already visited
            if not self.in_bounds(nx, ny) or self.visited[nx][ny]:
                continue

            val = self.grid[nx][ny]

            # Move if cell is 0 or the next number
            if val == 0 or val == next_number:
                self.visited[nx][ny] = True
                path_dirs.append(DIRS[d])  # Record the move

                # Save next_number for backtracking
                original_next = next_number
                if val == next_number:
                    next_number += 1

                # Continue DFS recursively
                if self.dfs(nx, ny, path_dirs, next_number):
                    return True

                # Backtrack: undo move and mark as unvisited
                self.visited[nx][ny] = False
                path_dirs.pop()
                next_number = original_next

        return False

    def getZipSolution(self):
        """
        Solve the puzzle:
        - Find the starting cell containing 1
        - Use DFS to find the sequence of moves to complete the game
        Returns a list of movement keys (arrow keys).
        """
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 1:
                    self.visited[i][j] = True
                    path_dirs = []
                    if self.dfs(i, j, path_dirs, 2):
                        return path_dirs
        return []

    def solvePuzzle(self, iteration: list[str]):
        """
        Send the computed sequence of arrow key movements to the game
        Args:
            iteration: list of arrow keys representing the solution path
        """
        body = self.driver.find_element(By.TAG_NAME, "body")
        for key in iteration:
            # Send each key with a short delay
            self.driver.implicitly_wait(0.05)
            body.send_keys(key)
