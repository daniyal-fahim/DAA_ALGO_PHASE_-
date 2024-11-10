import random

# Generate 10 files with random points for closest pair algorithm
for i in range(10):
    with open(f"points_input_{i+1}.txt", "w") as file:
        points = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(100)]
        for x, y in points:
            file.write(f"{x} {y}\n")

# Generate 10 files with random integers for integer multiplication (Karatsuba)
for i in range(10):
    with open(f"integers_input_{i+1}.txt", "w") as file:
        x = random.randint(10**50, 10**51)
        y = random.randint(10**50, 10**51)
        file.write(f"{x}\n{y}\n")
