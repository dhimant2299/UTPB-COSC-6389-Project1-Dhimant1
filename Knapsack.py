import math
import random
import tkinter as tk
from tkinter import *

num_items = 100
frac_target = 0.7
min_value = 128
max_value = 2048
screen_padding = 25
item_padding = 5
stroke_width = 5
num_generations = 1000
pop_size = 50
elitism_count = 2
mutation_rate = 0.1
sleep_time = 0.1

def random_rgb_color():
    red = random.randint(0x10, 0xff)
    green = random.randint(0x10, 0xff)
    blue = random.randint(0x10, 0xff)
    return f'#{red:02x}{green:02x}{blue:02x}'

class Item:
    def __init__(self):
        self.value = random.randint(min_value, max_value)
        self.color = random_rgb_color()
        self.x = self.y = self.w = self.h = 0

    def place(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def draw(self, canvas, active=False):
        canvas.create_text(self.x + self.w + item_padding + stroke_width * 2, self.y + self.h / 2, text=f'{self.value}')
        fill_color = self.color if active else ""
        outline_color = self.color if active else ""
        canvas.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h, fill=fill_color, outline=outline_color, width=stroke_width)

class GeneticAlgorithm:
    def __init__(self, pop_size, num_generations, elitism_count, mutation_rate, items_list, target):
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.elitism_count = elitism_count
        self.mutation_rate = mutation_rate
        self.items_list = items_list
        self.target = target
        self.population = []

    def initialize_population(self):
        self.population = [
            [random.random() < frac_target for _ in range(len(self.items_list))]
            for _ in range(self.pop_size)
        ]

    def gene_sum(self, genome):
        return sum(item.value for item, included in zip(self.items_list, genome) if included)

    def fitness(self, genome, penalty_factor=2):
        total_value = self.gene_sum(genome)
        if total_value > self.target:
            return (total_value - self.target) * penalty_factor
        else:
            return abs(total_value - self.target)
    
    def select_parents(self, tournament_size=5):
        if len(self.population) < tournament_size:
            tournament_size = len(self.population)

        def tournament():
            group = random.sample(self.population, tournament_size)
            return min(group, key=self.fitness)

        return tournament(), tournament()

    def crossover(self, parent1, parent2):
        length = len(parent1)
        point1, point2 = sorted([random.randint(0, length - 1) for _ in range(2)])
        return parent1[:point1] + parent2[point1:point2] + parent1[point2:]

    def mutate(self, genome):
        num_bits_to_flip = max(1, int(len(genome) * self.mutation_rate))
        for _ in range(num_bits_to_flip):
            index = random.randint(0, len(genome) - 1)
            genome[index] = not genome[index]
        return genome
    
    def evolve_generation(self):
        new_population = sorted(self.population, key=self.fitness)[:self.elitism_count]
        while len(new_population) < self.pop_size:
            parent1, parent2 = self.select_parents()
            child = self.crossover(parent1, parent2)
            if random.random() < self.mutation_rate:
                child = self.mutate(child)
            new_population.append(child)
        self.population = new_population
        return min(self.population, key=self.fitness)

class UI(tk.Tk):
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("KNAPSACK")
        self.option_add("*tearOff", FALSE)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}+0+0")
        self.state("zoomed")
        self.canvas = Canvas(self)
        self.canvas.place(x=0, y=0, width=self.width, height=self.height)
        self.items_list = []
        self.target = 0  
        self.algorithm = None   
        self.generation = 0
        self.running = True
        self.progress_data = []
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_bar = Menu(self)
        self['menu'] = menu_bar
        menu_K = Menu(menu_bar, tearoff=0)  # Removes the dotted line for cleaner appearance
        menu_bar.add_cascade(menu=menu_K, label='Knapsack Options', underline=0)
        menu_K.add_command(label="Generate Items", command=self.generate_knapsack, underline=0)
        menu_K.add_command(label="Set Target Value", command=self.set_target, underline=0)
        menu_K.add_separator()  # Adds a separator line to organize sections
        menu_K.add_command(label="Run Genetic Algorithm", command=self.run, underline=0)
        stop_button = Button(self, text="<--- Stop", command=self.stop_generations, font=("Arial Black", 14))
        stop_button.place(x=1400, y=770) 
        self.mainloop()

    def generate_knapsack(self):
        self.items_list.clear()
        for _ in range(num_items):
            item = Item()
            while any(existing_item.value == item.value for existing_item in self.items_list):
                item = Item()
            self.items_list.append(item)
        item_max = max(item.value for item in self.items_list)
        w, h = self.width - screen_padding, self.height - screen_padding
        num_rows = math.ceil(num_items / 6)
        row_w, row_h = w / 8 - item_padding, (h - 200) / num_rows
        for x in range(0, 6):
            for y in range(0, num_rows):
                if x * num_rows + y >= num_items:
                    break
                item = self.items_list[x * num_rows + y]
                item.place(screen_padding + x * row_w + x * item_padding,
                           screen_padding + y * row_h + y * item_padding,
                           row_w / 2,
                           max(item.value / item_max * row_h, 1))
        self.draw_items()

    def set_target(self):
        self.after_cancel(self.evolve_generation)
        target_set = random.sample(self.items_list, int(num_items * frac_target))
        self.target = sum(item.value for item in target_set)
        self.algorithm = GeneticAlgorithm(pop_size, num_generations, elitism_count, mutation_rate, self.items_list, self.target)
        self.algorithm.initialize_population()
        self.draw_target()

    def run(self):
        if not self.algorithm:
            return
        self.running = True
        self.progress_data = []
        self.algorithm.initialize_population()
        self.evolve_generation(0)

    def evolve_generation(self, generation):
        if self.running and generation < num_generations:
            best_genome = self.algorithm.evolve_generation()
            best_fitness = self.algorithm.fitness(best_genome)
            if not self.progress_data or self.progress_data[-1][1] != best_fitness:
                self.progress_data.append((generation, best_fitness))
            self.update_ui(best_genome, generation)
            self.after(int(sleep_time * 1000), self.evolve_generation, generation + 1)
        elif not self.running:
            self.show_report()

    def stop_generations(self):
        self.running = False

    def show_report(self):
        report_window = tk.Toplevel(self)
        report_window.title("        ____KNAPSACK SUMMARY REPORT____")
        report_text = Text(report_window, wrap='word', font=("Arial", 12))
        report_text.pack(expand=True, fill='both')
        report_text.insert(END, "                              ***************** Optimization Summary Report *****************\n\n")
        if self.progress_data:
            report_text.insert(END, f" || Initial Proximity to Target: {self.progress_data[0][1]:.2f}\n\n ||")
        report_text.insert(END, "   Progress:\n")
        report_text.insert(END, "   ────────────────────────────────────────────────────────────\n")
        report_text.insert(END, "   Generation            Proximity to Target\n")
        report_text.insert(END, "   ────────────────────────────────────────────────────────────\n")
        for gen, fitness in self.progress_data:
            report_text.insert(END, f"   {gen:<12}          |       {fitness:.2f}\n")
        report_text.insert(END, "   ────────────────────────────────────────────────────────────\n\n")
        report_text.insert(END, "                     *************** Thank You for Using the Optimizer ***************\n")
        report_text.config(state=DISABLED)

    def update_ui(self, best_genome, generation):
        self.clear_canvas()
        self.draw_target()
        self.draw_sum(self.algorithm.gene_sum(best_genome), self.target)
        self.draw_genome(best_genome, generation)

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_items(self):
        for item in self.items_list:
            item.draw(self.canvas)

    def draw_target(self):
        x, y = (self.width - screen_padding) / 8 * 7, screen_padding
        w, h = (self.width - screen_padding) / 8 - screen_padding, self.height / 2 - screen_padding
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(x + w // 2, y + h + screen_padding, text=f'{self.target}', font=('Arial', 18))

    def draw_sum(self, item_sum, target):
        x, y = (self.width - screen_padding) / 8 * 6, screen_padding
        w, h = (self.width - screen_padding) / 8 - screen_padding, self.height / 2 - screen_padding
        h *= (item_sum / target)
        self.canvas.create_rectangle(x, y, x + w, y + h, fill='black')
        self.canvas.create_text(x + w // 2, y + h + screen_padding, text=f'{item_sum} ({"+" if item_sum > target else "-"}{abs(item_sum - target)})', font=('Arial', 18))

    def draw_genome(self, genome, gen_num):
        for i, active in enumerate(genome):
            self.items_list[i].draw(self.canvas, active)
        x, y = (self.width - screen_padding) / 8 * 6, screen_padding
        w, h = (self.width - screen_padding) / 8 - screen_padding, self.height / 4 * 3
        self.canvas.create_text(x + w, y + h + screen_padding * 2, text=f'Generation No:{gen_num}', font=('Arial', 16))

if __name__ == '__main__':
    UI()
