import time
import pyautogui
import pynput

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

keyboard = Controller()

N = 500

print("Testing pyautogui...")

start = time.perf_counter()

for _ in range(N):
    pyautogui.press("space")

end = time.perf_counter()

print(f"pyautogui: {end - start:.4f} seconds")
print("pyautogui actions/sec:", N / (end - start))


print("\nTesting pynput...")

start = time.perf_counter()

for _ in range(N):
    keyboard.press("space")
    keyboard.release("space")

end = time.perf_counter()

print("pynput time:", end - start)
print("pynput actions/sec:", N / (end - start))