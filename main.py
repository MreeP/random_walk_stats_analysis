import csv
import os
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Particle:
    def __init__(self, probability_of_moving_up, number_of_steps):
        self.probability_of_moving_up = probability_of_moving_up
        self.number_of_steps = number_of_steps
        self.position = 0
        self.moves = []

    def run_simulation(self):
        for i in range(self.number_of_steps):
            self.move()

    def move(self):
        if self.random() < self.probability_of_moving_up:
            self.position += 1
            self.moves.append(1)
        else:
            self.position -= 1
            self.moves.append(-1)

    @staticmethod
    def random():
        return random.random()


class Experiment:
    number_of_trajectories_to_plot = 10

    def __init__(self, probability_of_moving_up, number_of_steps, number_of_simulations_per_experiment):
        self.probability_of_moving_up = probability_of_moving_up
        self.number_of_steps = number_of_steps
        self.number_of_simulations_per_experiment = number_of_simulations_per_experiment
        self.results = []
        self.final_positions = np.array([])
        self.positions = []
        self.mean_after_k_steps = np.array([])
        self.stddev_after_k_steps = np.array([])

    def run_experiment(self):
        for i in range(self.number_of_simulations_per_experiment):
            final_position, moves = self.run_test_case()
            self.results.append([i, final_position, ''.join(['+' if x == 1 else '-' for x in moves])])
            self.positions.append(np.cumsum(moves))

        self.final_positions = np.array([x[1] for x in self.results])
        self.mean_after_k_steps = np.mean(self.positions, axis=0)
        self.stddev_after_k_steps = np.std(self.positions, axis=0, ddof=1)

    def run_test_case(self):
        particle = Particle(self.probability_of_moving_up, self.number_of_steps)
        particle.run_simulation()
        return particle.position, particle.moves

    def save_results(self):
        os.makedirs('rawdata', exist_ok=True)

        with open(self.get_file_name('rawdata/results', 'csv'), 'w') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['id', 'final_position', 'steps'])
            csv_writer.writerows(self.results)

    def save_histogram_of_final_positions(self):
        os.makedirs('charts/histograms', exist_ok=True)

        plt.hist(self.final_positions, bins=25, color='pink', edgecolor='black', alpha=0.7)
        plt.title(f'Histogram of final positions\n{self.number_of_simulations_per_experiment} simulations {self.number_of_steps} steps each\n{self.probability_of_moving_up} probability of moving up', )
        plt.xlabel('Final position')
        plt.ylabel('Frequency')
        plt.minorticks_on()
        plt.grid(which='major', linestyle='-', linewidth='0.25', color='gray', alpha=0.4)
        plt.grid(which='minor', linestyle='-', linewidth='0.15', color='gray', alpha=0.3)
        plt.savefig(self.get_file_name('charts/histograms/histogram', 'png'), bbox_inches='tight')
        plt.close()

    def nth_positions(self, n):
        return np.cumsum([0] + [int(x + '1') for x in self.results[n][2]])

    def save_sample_walk_trajectories(self):
        os.makedirs('charts/trajectories', exist_ok=True)

        data_set_indexes = sorted(np.random.choice(len(self.results), self.number_of_trajectories_to_plot, replace=False))

        random_walk_positions_set = [
            self.nth_positions(x)
            for x
            in data_set_indexes
        ]

        figure, axes = plt.subplots(self.number_of_trajectories_to_plot, 1, figsize=(10, 20))

        for ind, (positions, ax) in enumerate(zip(random_walk_positions_set, axes)):
            ax.step(np.arange(len(positions)), positions)
            ax.set_title(f'Trajectory {data_set_indexes[ind]}')
            ax.set_xlabel('Step')
            ax.set_ylabel('Position')
            ax.grid(which='major', linestyle='-', linewidth='0.25', color='gray', alpha=0.4)

        plt.tight_layout()

        plt.savefig(self.get_file_name('charts/trajectories/trajectories_random', 'png'), bbox_inches='tight')

        plt.close()

        figure2, summary_ax = plt.subplots(figsize=(8, 6))

        for ind, positions in enumerate(random_walk_positions_set):
            summary_ax.step(np.arange(len(positions)), positions, where='post', label=f'Trajectory {data_set_indexes[ind]}')

        summary_ax.set_title('Trajectories summary')
        summary_ax.set_xlabel('Step')
        summary_ax.set_ylabel('Position')
        summary_ax.legend(bbox_to_anchor=(0, -0.35, 1.0, 0.102), loc='lower center', ncol=4, mode='expand')
        summary_ax.grid(True)

        figure2.tight_layout()

        plt.savefig(self.get_file_name('charts/trajectories/trajectories_summary', 'png'), bbox_inches='tight')

        plt.close()

    def save_mean_after_k_steps_with_confidence_interval(self):
        os.makedirs('charts/mean', exist_ok=True)

        # Wartość z tablicy rozkładu normalnego dla 95% przedziału ufności wzięta z tablicy https://naukowiec.org/tablice/statystyka/rozklad-t-studenta_248.html
        z = 1.96

        lower_bound = self.mean_after_k_steps - z * (self.stddev_after_k_steps / len(self.stddev_after_k_steps))
        upper_bound = self.mean_after_k_steps + z * (self.stddev_after_k_steps / len(self.stddev_after_k_steps))

        plt.figure(figsize=(8, 5))
        plt.plot(range(1, self.number_of_steps + 1), self.mean_after_k_steps, label='mean position')
        plt.fill_between(range(1, self.number_of_steps + 1), lower_bound, upper_bound, color='pink', alpha=0.3, label='95% confidence interval')
        plt.xlabel('Step')
        plt.ylabel('Position')
        plt.title('mean position after k steps with 95% confidence interval')
        plt.grid(which='major', linestyle='-', linewidth='0.25', color='gray', alpha=0.4)
        plt.legend()
        plt.savefig(self.get_file_name('charts/mean/mean_95_percent_confidence_interval', 'png'), bbox_inches='tight')
        plt.close()

    def get_cumulative_results(self):
        return np.mean(self.final_positions), np.std(self.final_positions), np.min(self.final_positions), np.max(self.final_positions), np.max(self.final_positions) - np.min(self.final_positions), np.median(self.final_positions)

    def get_file_name(self, prefix, extension):
        return f'{prefix}_{int(self.probability_of_moving_up * 100)}_{self.number_of_steps}.{extension}'


def max_minus_min_by_probability(df: pd.DataFrame):
    groups = df.groupby('number_of_steps')

    for name, group in groups:
        plt.scatter(group['probability'], group['max_minus_min'], label=f"{name} steps")

    plt.xlabel('Probability')
    plt.ylabel('Max - Min')
    plt.title('Max - Min by probability')
    plt.legend()
    plt.savefig('charts/max_minus_min_by_probability.png', bbox_inches='tight')
    plt.close()


def max_minus_min_by_step_count(df: pd.DataFrame):
    groups = df.groupby('probability')

    for name, group in groups:
        plt.scatter(group['number_of_steps'], group['max_minus_min'], label=f"{name}%")

    plt.xlabel('Number of steps')
    plt.ylabel('Max - Min')
    plt.title('Max - Min by number of steps')
    plt.legend()
    plt.savefig('charts/max_minus_min_by_number_of_steps.png', bbox_inches='tight')
    plt.close()


def mean_final_position_by_probability(df: pd.DataFrame):
    groups = df.groupby('number_of_steps')

    for name, group in groups:
        plt.plot(group['probability'], group['mean'], linestyle='-', color='gray', alpha=0.1)
        plt.scatter(group['probability'], group['mean'], label=f"{name} steps")

    plt.xlabel('Probability')
    plt.ylabel('Mean')
    plt.title('Mean final position by probability')
    plt.grid(which='major', linestyle='-', linewidth='0.25', color='gray', alpha=0.2)
    plt.legend()
    plt.savefig('charts/mean_final_position_by_probability.png', bbox_inches='tight')
    plt.close()


def mean_final_position_by_number_of_steps(df: pd.DataFrame):
    groups = df.groupby('probability')

    for name, group in groups:
        plt.plot(group['number_of_steps'], group['mean'], linestyle='-', color='gray', alpha=0.1)
        plt.scatter(group['number_of_steps'], group['mean'], label=f"{name}%")

    plt.xlabel('Number of steps')
    plt.ylabel('Mean')
    plt.title('Mean final position by number of steps')
    plt.grid(which='major', linestyle='-', linewidth='0.25', color='gray', alpha=0.2)
    plt.legend()
    plt.savefig('charts/mean_final_position_by_number_of_steps.png', bbox_inches='tight')
    plt.close()


def main():
    cumulative_results_df = pd.read_csv('cumulative_results.csv')

    # probabilities = [0.5 + x * 0.05 for x in range(10)]
    # numbers_of_steps_per_simulation = [100, 200, 300, 400, 500]
    # number_of_simulations_per_experiment = 1000
    # cumulative_results_df = pd.DataFrame(columns=['probability', 'number_of_steps', 'mean', 'std', 'min', 'max', 'max_minus_min', 'median'])
    #
    # for number_of_steps_per_simulation in numbers_of_steps_per_simulation:
    #     for probability in probabilities:
    #         experiment = Experiment(probability, number_of_steps_per_simulation, number_of_simulations_per_experiment)
    #         experiment.run_experiment()
    #         experiment.save_histogram_of_final_positions()
    #         experiment.save_sample_walk_trajectories()
    #         experiment.save_mean_after_k_steps_with_confidence_interval()
    #         experiment.save_results()
    #         mean, std, min_final, max_final, max_minus_min_final, median = experiment.get_cumulative_results()
    #         cumulative_results_df.loc[len(cumulative_results_df)] = {'probability': int(probability * 100), 'number_of_steps': number_of_steps_per_simulation, 'mean': mean, 'std': std, 'min': min_final, 'max': max_final, 'max_minus_min': max_minus_min_final, 'median': median}
    #
    # cumulative_results_df.to_csv('cumulative_results.csv', index=False)
    #
    max_minus_min_by_probability(cumulative_results_df)
    max_minus_min_by_step_count(cumulative_results_df)
    mean_final_position_by_probability(cumulative_results_df)
    mean_final_position_by_number_of_steps(cumulative_results_df)


if __name__ == '__main__':
    main()
