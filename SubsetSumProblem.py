import math
import random
import tkinter as tk
from tkinter import *
import time

num_items = 50  
min_value = 10
max_value = 100
target_sum = 500 
max_generations = 100
pop_size = 50
mutation_rate = 0.1
sleep_time = 0.2  

class Item:
    def __init__(self):
        self.value = random.randint(min_value, max_value)

class SubsetSumSolver(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Subset Sum Problem Solver")
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.state("zoomed")
        background_color = "#000000"  
        self.configure(bg=background_color)
        self.title_label = Label(
            self, 
            text="\nLet's check if the set has a subset that exactly adds up to 500\n",
            font=("Ethnocentric", 15),
            bg="#d9d9f3")
        self.title_label.pack(pady=20)
        self.items = [Item() for _ in range(num_items)]
        self.target = target_sum
        self.selected_solver = tk.StringVar(value="GA")
        self.progress_data = []
        self.create_solver_menu()
        self.render_items()
        self.create_control_buttons()
        self.status_label = Label(self, text="     ", font=("Ethnocentric", 25), bg=background_color, fg="#333333")
        self.status_label.place(x=self.width - 1200, y=600)
        self.ga_solver = None
        self.pso_solver = None
        self.running = False

    def create_solver_menu(self):

        menu_bar = Menu(self)
        solver_menu = Menu(menu_bar, tearoff=0)
        solver_menu.add_radiobutton(label="Genetic Algorithm Optimization", variable=self.selected_solver, value="GA")
        solver_menu.add_radiobutton(label="Particle Swarm Optimization", variable=self.selected_solver, value="PSO")
        menu_bar.add_cascade(label="Select Optimizer", menu=solver_menu)
        self.config(menu=menu_bar)

    def render_items(self):

        items_text = "\n".join(
            ", ".join(f"{item.value}" for item in self.items[i:i + 10]) 
            for i in range(0, len(self.items), 10)
        )
        self.items_label = Label(self, text=f"\n                       ITEMS:\n \n{items_text}\n", font=("Ethnocentric", 25),bg="#d9d9f3", fg="#333333", justify=LEFT)
        self.items_label.place(x=300, y=280, width=1000)

    def create_control_buttons(self):

        button_font = ("Ethnocentric", 12)        
        self.start_button = Button(self, text="Start", command=self.start_solver, font=button_font,bg="#d9d9f3", fg="#333333", width=10, height=2)
        self.start_button.place(x=550, y=770)
        self.stop_button = Button(self, text="Stop", command=self.stop_solver, font=button_font,bg="#d9d9f3", fg="#333333", width=10, height=2)
        self.stop_button.place(x=700, y=770)
        self.show_report_button = Button(self, text="Report", command=self.show_report, font=button_font,bg="#d9d9f3", fg="#333333", width=10, height=2)
        self.show_report_button.place(x=850, y=770)

    def start_solver(self):

        solver_type = self.selected_solver.get()
        self.running = True
        self.progress_data.clear()

        if solver_type == "GA":
            self.ga_solver = GeneticAlgorithmSolver(self.items, self.target, self)
            self.ga_solver.run()
        elif solver_type == "PSO":
            self.pso_solver = ParticleSwarmSolver(self.items, self.target, self)
            self.pso_solver.run()

    def stop_solver(self):

        self.running = False
        print("Solver stopped.")

    def show_report(self):
        report_window = tk.Toplevel(self)
        report_window.title("Summary Report")
        report_text = Text(report_window, wrap='word', font=("Arial", 11))
        report_text.pack(expand=True, fill='both')
        report_text.tag_configure("title", font=("Arial", 14, "bold"))
        report_text.insert(END, "                          Optimization Summary Report\n\n", "title")
        report_text.tag_configure("header", font=("Arial", 12, "bold"))
        report_text.insert(END, "Progress Details:\n", "header")
        report_text.insert(END, "-"*50 + "\n", "header") 
        previous_fitness = None
        for generation, fitness in self.progress_data:
            if fitness != previous_fitness:
                report_text.insert(END, f"Generation {generation}:      Fitness = {fitness:.2f}\n")
                previous_fitness = fitness
        report_text.insert(END, "\n" + "-"*50 + "\n", "header")
        report_text.config(state="disabled")

class GeneticAlgorithmSolver:
    def __init__(self, items, target, ui):
        self.items = items
        self.target = target
        self.ui = ui
        self.population = self.initialize_population()
        self.elitism_count = 2  

    def initialize_population(self):

        return [[random.choice([True, False]) for _ in range(len(self.items))] for _ in range(pop_size)]

    def fitness(self, genome):
        total = sum(item.value for item, included in zip(self.items, genome) if included)
        if total > self.target:
            return (total - self.target) * 1.5  
        else:
            return abs(total - self.target)

    def select_parents(self):
        tournament_size = 5
        def tournament():
            candidates = random.sample(self.population, tournament_size)
            return min(candidates, key=self.fitness)
        return tournament(), tournament()

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, len(parent1) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child

    def mutate(self, genome):
        for i in range(len(genome)):
            if random.random() < mutation_rate:
                genome[i] = not genome[i]
        return genome

    def run(self):
        last_fitness = None  

        for generation in range(max_generations):
            if not self.ui.running:
                break
            self.population.sort(key=self.fitness)
            best_genome = self.population[0]
            best_fitness = self.fitness(best_genome)
            best_sum = sum(item.value for item, included in zip(self.items, best_genome) if included)
            if best_fitness != last_fitness:
                self.ui.progress_data.append((generation, best_fitness))
                last_fitness = best_fitness
            subset = [item.value for item, included in zip(self.items, best_genome) if included]
            subset_text = f"Subset: {subset}"
            self.ui.status_label.config(
                text=f" {subset_text}\n"
                    f"Sum: {best_sum}  "
                    f"Gen: {generation}\n",
                    font=("Ethnocentric", 15),bg="#d9d9f3"
            )
            self.ui.update()
            if best_fitness == 0:
                break

            new_population = self.population[:self.elitism_count]
            while len(new_population) < pop_size:
                parent1, parent2 = self.select_parents()
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population
            time.sleep(sleep_time)
      
class ParticleSwarmSolver:
    def __init__(self, items, target, ui):
        self.items = items
        self.target = target
        self.ui = ui
        self.particles = self.initialize_particles()
        self.velocities = [[0.0] * len(self.items) for _ in range(pop_size)]
        self.best_particle_positions = self.particles[:]
        self.best_particle_fitness = [self.fitness(p) for p in self.particles]
        self.global_best_position = min(self.particles, key=self.fitness)
        self.global_best_fitness = self.fitness(self.global_best_position)

    def initialize_particles(self):
        return [[random.choice([True, False]) for _ in range(len(self.items))] for _ in range(pop_size)]

    def fitness(self, particle):
        total = sum(item.value for item, included in zip(self.items, particle) if included)
        if total > 1500:
            return (total - self.target) * 3  
        elif total > self.target:
            return abs(total - self.target) ** 1.2  
        else:
            return abs(total - self.target)

    def update_velocity_and_position(self, particle_idx, inertia_weight):
        cognitive_weight = 1.5
        social_weight = 1.5

        for i in range(len(self.particles[particle_idx])):
            r1, r2 = random.random(), random.random()
            self.velocities[particle_idx][i] = (
                inertia_weight * self.velocities[particle_idx][i] +
                cognitive_weight * r1 * (self.best_particle_positions[particle_idx][i] - self.particles[particle_idx][i]) +
                social_weight * r2 * (self.global_best_position[i] - self.particles[particle_idx][i])
            )
            if random.random() < 1 / (1 + math.exp(-self.velocities[particle_idx][i])):
                self.particles[particle_idx][i] = not self.particles[particle_idx][i]

    def run(self):
        stagnation_limit = 99
        stagnation_counter = 0
        last_best_fitness = float('inf')
        last_fitness = None  

        for iteration in range(max_generations):
            if not self.ui.running:
                break
            inertia_weight = 0.9 - ((0.9 - 0.4) * iteration / max_generations)

            for idx in range(pop_size):
                self.update_velocity_and_position(idx, inertia_weight)
                current_fitness = self.fitness(self.particles[idx])

                if current_fitness < self.best_particle_fitness[idx]:
                    self.best_particle_positions[idx] = self.particles[idx][:]
                    self.best_particle_fitness[idx] = current_fitness

                if current_fitness < self.global_best_fitness:
                    self.global_best_position = self.particles[idx][:]
                    self.global_best_fitness = current_fitness

            if self.global_best_fitness != last_fitness:
                self.ui.progress_data.append((iteration, self.global_best_fitness))
                last_fitness = self.global_best_fitness

            subset = [item.value for item, included in zip(self.items, self.global_best_position) if included]
            subset_sum = sum(subset)
            self.ui.status_label.config(
                text=f" {subset}\n"
                f"Subset Sum: {subset_sum}"
                f"Gen: {iteration}\n",
                font=("Ethnocentric", 15))
            self.ui.update()

            if self.global_best_fitness == last_best_fitness:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
                last_best_fitness = self.global_best_fitness

            if stagnation_counter >= stagnation_limit or self.global_best_fitness == 0:
                print("Stopping due to stagnation or exact match.")
                break

            time.sleep(sleep_time)


if __name__ == '__main__':
    app = SubsetSumSolver()
    app.mainloop()
