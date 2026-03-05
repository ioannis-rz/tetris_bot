import time
import pyautogui
from pynput.keyboard import Controller

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

keyboard = Controller()

N = 50000

print("Testing pyautogui...")

start = time.perf_counter()

for _ in range(N):
    pyautogui.press("a")

end = time.perf_counter()

print(f"pyautogui: {end - start:.4f} seconds")
print("pyautogui actions/sec:", N / (end - start))


print("\nTesting pynput...")

start = time.perf_counter()

for _ in range(N):
    keyboard.press("a")
    keyboard.release("a")

end = time.perf_counter()

print("pynput time:", end - start)
print("pynput actions/sec:", N / (end - start))