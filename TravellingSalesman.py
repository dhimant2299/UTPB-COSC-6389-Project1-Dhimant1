import math
import random
import tkinter as tk
from tkinter import *

num_cities = 30
num_generations = 500
pop_size = 100
mutation_rate = 0.1
tournament_size = 5
city_scale = 5
road_width = 4
padding = 100

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas, color='blue'):
        canvas.create_oval(self.x - city_scale, self.y - city_scale, self.x + city_scale, self.y + city_scale, fill=color)

class Edge:
    def __init__(self, a, b):
        self.city_a = a
        self.city_b = b
        self.length = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

    def draw(self, canvas, color='grey', style=(2, 4)):
        canvas.create_line(self.city_a.x, self.city_a.y, self.city_b.x, self.city_b.y, fill=color, width=road_width, dash=style)

class GeneticAlgorithm:
    def __init__(self, cities):
        self.cities = cities
        self.population = self.initialize_population()
        self.elitism_count = 5  
        self.initial_mutation_rate = mutation_rate  
    def initialize_population(self):
        population = []
        nearest_neighbor_count = int(0.2 * pop_size) 
        for _ in range(nearest_neighbor_count):
            genome = self.nearest_neighbor_tour()
            population.append(genome)
        population += [random.sample(range(len(self.cities)), len(self.cities)) for _ in range(pop_size - nearest_neighbor_count)]
        return population

    def nearest_neighbor_tour(self):
        start_city = random.choice(range(len(self.cities)))
        unvisited = set(range(len(self.cities)))
        unvisited.remove(start_city)
        tour = [start_city]
        current_city = start_city
        while unvisited:
            next_city = min(unvisited, key=lambda city: self.distance(self.cities[current_city], self.cities[city]))
            tour.append(next_city)
            unvisited.remove(next_city)
            current_city = next_city
        return tour

    def fitness(self, genome):
        if len(set(genome)) != len(self.cities):  
            return float('inf')  
        total_distance = 0
        for i in range(len(genome) - 1):
            city_a = self.cities[genome[i]]
            city_b = self.cities[genome[i + 1]]
            total_distance += self.distance(city_a, city_b)
        city_start = self.cities[genome[0]]
        city_end = self.cities[genome[-1]]
        total_distance += self.distance(city_start, city_end)
        return total_distance

    def distance(self, city_a, city_b):
        return math.sqrt((city_a.x - city_b.x) ** 2 + (city_a.y - city_b.y) ** 2)
    def select_parents(self, generation, max_generations):
        adaptive_tournament_size = min(tournament_size + generation // 50, len(self.population) // 2)
        def tournament():
            group = random.sample(self.population, adaptive_tournament_size)
            return min(group, key=self.fitness)
        return tournament(), tournament()

    def crossover(self, parent1, parent2):
        length = len(parent1)
        start, end = sorted(random.sample(range(length), 2))
        child = [-1] * length
        child[start:end] = parent1[start:end]
        pos = end
        for city in parent2:
            if city not in child:
                if pos >= length:
                    pos = 0
                child[pos] = city
                pos += 1
        return child

    def mutate(self, genome, generation, max_generations):
        current_mutation_rate = self.initial_mutation_rate * (1 - generation / max_generations)
        
        if random.random() < current_mutation_rate:
            i, j = random.sample(range(len(genome)), 2)
            genome[i], genome[j] = genome[j], genome[i]
        if random.random() < current_mutation_rate / 5:
            start, end = sorted(random.sample(range(len(genome)), 2))
            genome[start:end] = reversed(genome[start:end])
        return genome

    def evolve_population(self, generation, max_generations):
        new_population = sorted(self.population, key=self.fitness)[:self.elitism_count]
        while len(new_population) < pop_size:
            parent1, parent2 = self.select_parents(generation, max_generations)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child, generation, max_generations)
            new_population.append(child)
        self.population = new_population
        return min(self.population, key=self.fitness)

class UI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Traveling Salesman")
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)
        self.generation_label = Label(self, text="Generation: 0", font=("Arial", 16))
        self.generation_label.place(x=10, y=10)
        self.distance_label = Label(self, text="Total Distance: 0", font=("Arial", 16))
        self.distance_label.place(x=10, y=40)
        self.cities = [Node(random.randint(padding, self.width - padding), random.randint(padding, self.height - padding)) for _ in range(num_cities)]
        self.algorithm = GeneticAlgorithm(self.cities)
        self.generation = 0
        self.max_generations = num_generations
        self.running = True  
        self.progress_data = [] 
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_TS = Menu(menu_bar, tearoff=0)  
        menu_bar.add_cascade(menu=menu_TS, label='Traveling Salesman Options', underline=0)
        menu_TS.add_command(label="Generate Cities and Paths", command=self.generate, underline=0)
        stop_button = Button(self, text="|| Stop ||", command=self.stop_generations, font=("Arial", 12, "bold"), bg="#d9534f", fg="white")
        stop_button.place(x=10, y=70) 
        self.mainloop()

    def generate(self):
        """Start the evolutionary process for real-time updates."""
        self.generation = 0
        self.running = True  
        self.progress_data = []  
        self.run_evolution()

    def run_evolution(self):
        if self.running and self.generation < self.max_generations:
            best_genome = self.algorithm.evolve_population(self.generation, self.max_generations)
            best_distance = self.algorithm.fitness(best_genome)  
            if not self.progress_data or self.progress_data[-1][1] != best_distance:
                self.progress_data.append((self.generation, best_distance))
            self.update_ui(best_genome, best_distance)
            self.generation += 1
            self.after(100, self.run_evolution)  
        elif not self.running:
            self.show_report()

    def stop_generations(self):
        self.running = False

    def show_report(self):
        report_window = tk.Toplevel(self)
        report_window.title("        ____TRAVELLING SALESMAN SUMMARY REPORT____")
        report_text = Text(report_window, wrap='word', font=("Arial", 12))
        report_text.pack(expand=True, fill='both')
        report_text.insert(END, "                                     ***************** Optimization Summary Report *****************\n\n")
        if self.progress_data:
            report_text.insert(END, f"   Initial Distance is {self.progress_data[0][1]:.2f} units\n\n")
        report_text.insert(END, "   PROGRESS REPORT:\n")
        report_text.insert(END, "   ────────────────────────────────────────────────────────────\n")
        report_text.insert(END, "      Generation           Distance (units)\n")
        report_text.insert(END, "   ────────────────────────────────────────────────────────────\n")
        for gen, dist in self.progress_data:
            report_text.insert(END, f"           {gen:<12}             |             {dist:.2f}\n")
        report_text.insert(END, "   ────────────────────────────────────────────────────────────\n\n")
        report_text.insert(END, "                                     *************** Thank You for Using the Optimizer ***************\n")

        report_text.config(state=DISABLED)

    def update_ui(self, best_genome, best_distance):
        self.canvas.delete("all")
        for i in range(len(best_genome) - 1):
            Edge(self.cities[best_genome[i]], self.cities[best_genome[i + 1]]).draw(self.canvas, color="red")
        Edge(self.cities[best_genome[0]], self.cities[best_genome[-1]]).draw(self.canvas, color="red") 
        for city in self.cities:
            city.draw(self.canvas)
        self.generation_label.config(text=f"Generation: {self.generation}")
        self.distance_label.config(text=f"Total Distance: {best_distance:.2f}")

if __name__ == '__main__':
    UI()
