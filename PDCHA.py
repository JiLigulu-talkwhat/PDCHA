from fitness_functions import create_fitness
import numpy as np
import time
from result_logger import ResultLogger, verbose_to_result_file


class DualFitnessOptimizer(ResultLogger):

    def __init__(
        self,
        func_a,
        func_b,
        dim,
        bounds,
        m=3,
        P=2,
        k_percent=0.2,
        verbose=True,
        repulsion_strategy="lightweight",
        sensitivity_region_ratio=2.0,
        importance_threshold=0.8,
        refined_optimization_threshold=1e-05,
        importance_method="sensitivity",
        results_dir="data/log",
        data_dir="data",
        log_mode="detailed",
        language="en",
    ):
        self._set_language(language)
        self.refined_optimization_threshold = refined_optimization_threshold
        self.func_a = func_a
        self.func_b = func_b
        self.dim = dim
        self.bounds = np.array(bounds)
        self.m = m
        self.P = P
        self.k_percent = k_percent
        self.time_a = 0.0
        self.time_b = 0.0
        self.repulsion_strategy = repulsion_strategy
        self.sensitivity_region_ratio = sensitivity_region_ratio
        self.importance_threshold = importance_threshold
        self.importance_method = importance_method
        self.fitness_a_calls = 0
        self.fitness_b_calls = 0
        self._init_output(results_dir, data_dir, verbose, log_mode)
        num_intervals = 2**self.m
        self.min_search_step = np.array([(high - low) / num_intervals for low, high in self.bounds])
        self.precision_unit = 0.01
        self.min_step = np.full(dim, self.precision_unit)
        self.refined_step_size = np.full(dim, self.precision_unit)
        self.debug_data = dict.fromkeys(
            [
                "global_samples",
                "global_fitness",
                "selected_samples",
                "selected_fitness",
                "unique_selected_samples",
                "unique_selected_fitness",
                "local_opts",
                "local_opt_fitness",
                "filtered_local_opts",
                "filtered_fitness",
                "refined_opts",
                "refined_fitness",
            ]
        )
        self.debug_data.update(
            {key: [] for key in ("importance_results", "hill_climb_histories", "refined_history")}
        )
        self.debug_data["result_file"] = (
            str(self.result_file_path) if self.result_file_path else None
        )
        self.debug_data["final_result"] = None
        self.stage_calls = {
            stage: {"a": 0, "b": 0}
            for stage in (
                "global_sampling",
                "hill_climb_initial",
                "local_opt_filtering",
                "importance_analysis",
                "hill_climb_refined",
                "final_validation",
            )
        }

    def _move(self, point, dim, distance, subtract=False):
        if subtract:
            point[dim] -= distance
        else:
            point[dim] += distance
        point[dim] = np.clip(point[dim], *self.bounds[dim])
        return point

    def _candidate(self, point, dim, distance, subtract=False):
        return self._move(point.copy(), dim, distance, subtract)

    @staticmethod
    def _choose_direction(point, fitness, plus, f_plus, minus, f_minus):
        if f_plus < fitness and f_plus <= f_minus:
            return (plus, f_plus, True)
        if f_minus < fitness and f_minus <= f_plus:
            return (minus, f_minus, True)
        return (point, fitness, False)

    @staticmethod
    def _refinement_state(point, fitness, directions, locked):
        return {
            "point": point.copy(),
            "fitness": fitness,
            "directions": directions.copy(),
            "locked": locked.copy(),
        }

    def _point_key(self, vector):
        scaled = np.round(np.asarray(vector, dtype=float) / self.precision_unit).astype(int)
        return tuple((int(value) for value in scaled.tolist()))

    def _deduplicate_candidates(self, samples, fitness):
        unique_samples = []
        unique_fitness = []
        counts = []
        index_map = {}
        original_to_unique = []
        for point, fit_value in zip(samples, fitness):
            key = self._point_key(point)
            if key in index_map:
                idx = index_map[key]
                counts[idx] += 1
                if fit_value < unique_fitness[idx]:
                    unique_samples[idx] = np.array(point, dtype=float).copy()
                    unique_fitness[idx] = float(fit_value)
                original_to_unique.append(idx)
            else:
                index_map[key] = len(unique_samples)
                unique_samples.append(np.array(point, dtype=float).copy())
                unique_fitness.append(float(fit_value))
                counts.append(1)
                original_to_unique.append(index_map[key])
        if unique_samples:
            unique_samples_array = np.array(unique_samples, dtype=float)
            unique_fitness_array = np.array(unique_fitness, dtype=float)
        else:
            unique_samples_array = np.empty((0, self.dim), dtype=float)
            unique_fitness_array = np.empty((0,), dtype=float)
        return (unique_samples_array, unique_fitness_array, counts, original_to_unique)

    def fitness_a(self, x):
        start_time = time.perf_counter()
        result = self.func_a(x)
        end_time = time.perf_counter()
        self.time_a += end_time - start_time
        self.fitness_a_calls += 1
        return result

    def fitness_b(self, x):
        start_time = time.perf_counter()
        result = self.func_b(x)
        end_time = time.perf_counter()
        self.time_b += end_time - start_time
        self.fitness_b_calls += 1
        return result

    @verbose_to_result_file
    def global_grid_sampling(self):
        start_a = self.fitness_a_calls
        num_points = 2**self.m + 1
        seq_list = []
        for d in range(self.dim):
            low, high = self.bounds[d]
            seq = np.linspace(low, high, num_points)
            seq_list.append(seq)
        grids = np.meshgrid(*seq_list, indexing="ij")
        samples = np.stack(grids, axis=-1).reshape(-1, self.dim)
        fitness = np.array([self.fitness_a(x) for x in samples])
        self.debug_data["global_samples"] = samples
        self.debug_data["global_fitness"] = fitness
        self.stage_calls["global_sampling"]["a"] = self.fitness_a_calls - start_a
        return (samples, fitness)

    @verbose_to_result_file
    def global_pre_hill_climb(self, samples, fitness):
        corrected_samples = samples.copy()
        corrected_fitness = fitness.copy()
        improvement_records = []
        start_a = self.fitness_a_calls
        step = self.min_search_step / (self.P + 1)
        for _ in range(self.P):
            for j in range(len(samples)):
                original_x = corrected_samples[j].copy()
                original_fitness = corrected_fitness[j]
                x = corrected_samples[j].copy()
                f_curr = corrected_fitness[j]
                for d in range(self.dim):
                    x_plus = self._candidate(x, d, step[d])
                    f_plus = self.fitness_a(x_plus)
                    x_minus = self._candidate(x, d, step[d], subtract=True)
                    f_minus = self.fitness_a(x_minus)
                    x, f_curr, _ = self._choose_direction(
                        x, f_curr, x_plus, f_plus, x_minus, f_minus
                    )
                corrected_samples[j] = x
                corrected_fitness[j] = f_curr
                if f_curr < original_fitness:
                    improvement_records.append(
                        [
                            j,
                            *self._flatten_vector(original_x),
                            float(original_fitness),
                            *self._flatten_vector(x),
                            float(f_curr),
                        ]
                    )
        self.stage_calls["global_sampling"]["a"] += self.fitness_a_calls - start_a
        self._record_pre_hillclimb(improvement_records)
        return (corrected_samples, corrected_fitness)

    @verbose_to_result_file
    def repulsion_selection(self, samples, fitness):
        if self.repulsion_strategy == "lightweight":
            return self._lightweight_repulsion(samples, fitness)
        elif self.repulsion_strategy == "precise":
            self.debug_data["selected_samples"] = samples
            self.debug_data["selected_fitness"] = fitness
            return (samples, fitness)
        else:
            raise ValueError(f"UNKNOW strategy: {self.repulsion_strategy}")

    @verbose_to_result_file
    def _lightweight_repulsion(self, samples, fitness):
        k_count = max(1, int(len(samples) * self.k_percent))
        sorted_indices = np.argsort(fitness)[:k_count]
        selected = samples[sorted_indices]
        selected_fitness = fitness[sorted_indices]
        self.debug_data["selected_samples"] = selected
        self.debug_data["selected_fitness"] = selected_fitness
        return (selected, selected_fitness)

    @verbose_to_result_file
    def hill_climb(self, start, use_b=False, max_iter=20, initial_fitness=None):
        x = start.copy()
        history = [start.copy()]
        fitness_func = self.fitness_b if use_b else self.fitness_a
        step_size = np.maximum(0.1 * self.min_search_step.copy(), self.min_step.copy())
        start_a = self.fitness_a_calls
        start_b = self.fitness_b_calls
        if initial_fitness is not None:
            current_fitness = initial_fitness
        else:
            current_fitness = fitness_func(x)
        start_fitness = float(current_fitness)
        stop_reason = "Maximum iterations reached"
        for iter_count in range(max_iter):
            improved = False
            if np.any(step_size < self.precision_unit):
                stop_reason = f"Step below minimum threshold {self.min_step.min():.6f}"
                break
            for dim in range(self.dim):
                x_plus = self._candidate(x, dim, step_size[dim])
                x_minus = self._candidate(x, dim, step_size[dim], subtract=True)
                f_plus = fitness_func(x_plus)
                f_minus = fitness_func(x_minus)
                x, current_fitness, changed = self._choose_direction(
                    x, current_fitness, x_plus, f_plus, x_minus, f_minus
                )
                improved = improved or changed
            history.append(x.copy())
            if not improved:
                step_size *= 0.5
                if np.max(step_size) < self.precision_unit:
                    stop_reason = f"Step below minimum threshold {self.min_step.min():.6f}"
                    break
        a_calls = self.fitness_a_calls - start_a
        b_calls = self.fitness_b_calls - start_b
        self.stage_calls["hill_climb_initial"]["a"] += a_calls
        self.stage_calls["hill_climb_initial"]["b"] += b_calls
        summary = {
            "start_x": start.copy(),
            "start_func_a": start_fitness,
            "end_x": x.copy(),
            "end_func_a": float(current_fitness),
            "iteration_count": int(iter_count + 1),
            "func_a_calls": int(a_calls),
            "func_b_calls": int(b_calls),
            "stop_reason": stop_reason,
        }
        return (x, current_fitness, history, summary)

    @verbose_to_result_file
    def refined_optimization(self, start, important_dims, max_iter=20):
        threshold = self.refined_optimization_threshold
        x = start.copy()
        step = np.maximum(0.05 * self.min_search_step.copy(), self.refined_step_size.copy())
        directions = np.zeros(self.dim, dtype=int)
        locked = np.ones(self.dim, dtype=bool)
        locked[important_dims] = False
        start_b = self.fitness_b_calls
        fitness = self.fitness_b(x)
        history = [self._refinement_state(x, fitness, directions, locked)]
        for _ in range(max_iter):
            if all(locked[important_dims]):
                break
            active = [dim for dim in important_dims if not locked[dim]]
            single = len(active) == 1
            if single:
                dim = active[0]
                direction = directions[dim]
                if direction == 0:
                    trial = self._candidate(x, dim, step[dim])
                    trial_fitness = self.fitness_b(trial)
                    direction = 1
                    if not trial_fitness < fitness - threshold:
                        trial = self._candidate(x, dim, 2 * step[dim], subtract=True)
                        trial_fitness = self.fitness_b(trial)
                        direction = -1
                else:
                    trial = self._candidate(x, dim, direction * step[dim])
                    trial_fitness = self.fitness_b(trial)
            else:
                for dim in active:
                    if directions[dim] == 0:
                        plus = self._candidate(x, dim, step[dim])
                        f_plus = self.fitness_b(plus)
                        directions[dim] = 1 if f_plus < fitness - threshold else -1
                trial = x.copy()
                for dim in active:
                    self._move(trial, dim, directions[dim] * step[dim])
                trial_fitness = self.fitness_b(trial)
            improved = bool(trial_fitness < fitness - threshold)
            if improved:
                x, fitness = (trial, trial_fitness)
                if single:
                    directions[dim] = direction
                else:
                    for dim in active:
                        if history[-1]["directions"][dim] != directions[dim]:
                            locked[dim] = True
            else:
                locked[active] = True
            history.append(self._refinement_state(x, fitness, directions, locked))
            if not improved:
                break
        b_calls = self.fitness_b_calls - start_b
        self.stage_calls["hill_climb_refined"]["b"] += b_calls
        self.debug_data["refined_history"].append(history)
        self._record_refinement(history, important_dims, b_calls)
        return (x, fitness)

    @verbose_to_result_file
    def parameter_importance(self, local_opt):
        start_a = self.fitness_a_calls
        start_b = self.fitness_b_calls
        if self.importance_method == "skip":
            important_dims = list(range(self.dim))
            result = {"method": "skip", "local_opt": local_opt, "important_dims": important_dims}
        elif self.importance_method == "sensitivity":
            region_size = self.sensitivity_region_ratio * self.min_search_step
            p_values = np.zeros(self.dim)
            dimension_details = []
            for dim in range(self.dim):
                test_points = []
                offsets = [
                    -region_size[dim],
                    -0.5 * region_size[dim],
                    0,
                    0.5 * region_size[dim],
                    region_size[dim],
                ]
                for offset in offsets:
                    point = local_opt.copy()
                    point[dim] = np.clip(
                        point[dim] + offset, self.bounds[dim][0], self.bounds[dim][1]
                    )
                    test_points.append(point)
                values = [self.fitness_a(p) for p in test_points]
                p_values[dim] = np.std(values)
                dimension_details.append(
                    {
                        "dim": dim,
                        "test_points": [point.copy() for point in test_points],
                        "values": list(values),
                    }
                )
            total_p = np.sum(p_values)
            if total_p > 0:
                importance = p_values / total_p
            else:
                importance = np.ones(self.dim) / self.dim
            sorted_indices = np.argsort(importance)[::-1]
            sorted_importance = importance[sorted_indices]
            cumulative_importance = np.cumsum(sorted_importance)
            total_importance = np.sum(importance)
            threshold_index = np.argmax(
                cumulative_importance >= total_importance * self.importance_threshold
            )
            important_dims = sorted_indices[: threshold_index + 1]
            result = {
                "method": "sensitivity",
                "local_opt": local_opt,
                "dimension_details": dimension_details,
                "p_values": p_values,
                "importance": importance,
                "important_dims": important_dims,
            }
        self.debug_data["importance_results"].append(result)
        a_calls = self.fitness_a_calls - start_a
        b_calls = self.fitness_b_calls - start_b
        self.stage_calls["importance_analysis"]["a"] += a_calls
        self.stage_calls["importance_analysis"]["b"] += b_calls
        return important_dims

    @verbose_to_result_file
    def filter_local_opts(self, local_opts, local_fitness, top_n=5):
        start_a = self.fitness_a_calls
        start_b = self.fitness_b_calls
        if not local_opts:
            return []
        fitness_a_values = np.array(local_fitness)
        sorted_indices = np.argsort(fitness_a_values)
        keep_indices = sorted_indices[:top_n]
        filtered_opts = [local_opts[i] for i in keep_indices]
        filtered_fitness = fitness_a_values[keep_indices]
        self.stage_calls["local_opt_filtering"]["a"] += self.fitness_a_calls - start_a
        self.stage_calls["local_opt_filtering"]["b"] += self.fitness_b_calls - start_b
        self.debug_data["filtered_local_opts"] = (
            np.array(filtered_opts) if filtered_opts else np.array([])
        )
        self.debug_data["filtered_fitness"] = filtered_fitness
        return filtered_opts

    @verbose_to_result_file
    def optimize(self):
        samples, fitness = self.global_grid_sampling()
        samples, fitness = self.global_pre_hill_climb(samples, fitness)
        unique_samples, unique_fitness, duplicate_counts, original_to_unique = (
            self._deduplicate_candidates(samples, fitness)
        )
        self.debug_data["unique_selected_samples"] = unique_samples
        self.debug_data["unique_selected_fitness"] = unique_fitness
        selected, selected_fitness = self.repulsion_selection(unique_samples, unique_fitness)
        self.debug_data["selected_samples"] = selected
        self.debug_data["selected_fitness"] = selected_fitness
        local_opts = []
        local_opt_fitness = []
        for i, (point, fit_val) in enumerate(zip(selected, selected_fitness)):
            opt, opt_fitness, history, hill_summary = self.hill_climb(
                point, initial_fitness=fit_val
            )
            self.debug_data["hill_climb_histories"].append(history)
            self._record_hill_climb(i, hill_summary)
            if not any((np.linalg.norm(opt - ex) < 0.1 for ex in local_opts)):
                local_opts.append(opt)
                local_opt_fitness.append(opt_fitness)
        self.debug_data["local_opts"] = np.array(local_opts) if local_opts else np.array([])
        self.debug_data["local_opt_fitness"] = np.array(local_opt_fitness)
        filtered_local_opts = self.filter_local_opts(local_opts, local_opt_fitness)
        refined_opts = []
        refined_fitness = []
        for opt in filtered_local_opts:
            important_dims = self.parameter_importance(opt)
            refined, refined_fit = self.refined_optimization(opt, important_dims)
            refined_opts.append(refined)
            refined_fitness.append(refined_fit)
        self.debug_data["refined_opts"] = np.array(refined_opts) if refined_opts else np.array([])
        self.debug_data["refined_fitness"] = np.array(refined_fitness)
        start_a = self.fitness_a_calls
        start_b = self.fitness_b_calls
        if refined_opts:
            best_idx = np.argmin(refined_fitness)
            best_solution = refined_opts[best_idx]
            best_fitness = refined_fitness[best_idx]
        else:
            best_solution = selected[0]
            best_fitness = self.fitness_b(best_solution)
        self.stage_calls["final_validation"]["a"] += self.fitness_a_calls - start_a
        self.stage_calls["final_validation"]["b"] += self.fitness_b_calls - start_b
        self.debug_data["final_result"] = {
            "best_solution": np.array(best_solution).copy(),
            "best_fitness": float(best_fitness),
            "call_summary": self._build_call_summary(),
            "result_file": str(self.result_file_path) if self.result_file_path else None,
        }
        return best_solution


def run(language="en", fitness_factory=create_fitness):
    fitness = fitness_factory()
    optimizer = DualFitnessOptimizer(
        func_a=fitness.func_a,
        func_b=fitness.func_b,
        dim=len(fitness.bounds),
        bounds=fitness.bounds,
        m=3,
        P=2,
        k_percent=0.2,
        repulsion_strategy="lightweight",
        refined_optimization_threshold=0.01,
        sensitivity_region_ratio=2,
        importance_threshold=0.9,
        verbose=True,
        importance_method="sensitivity",
        language=language,
    )
    fitness.log = optimizer._log
    fitness.log_message = optimizer._log_message
    start_time = time.perf_counter()
    best_solution = optimizer.optimize()
    compute_time = time.perf_counter() - start_time
    evaluation_time = optimizer.time_a + optimizer.time_b
    other_time = compute_time - evaluation_time
    timing_report = optimizer._message(
        "timing_report",
        optimizer.time_a,
        optimizer.time_b,
        evaluation_time,
        other_time,
        compute_time,
        compute_time / 60,
    )
    if optimizer.result_file_path is not None:
        with open(optimizer.result_file_path, "a", encoding="utf-8") as f:
            f.write(timing_report)
    optimizer.print_call_summary()
    fitness.close()
    return (
        optimizer,
        best_solution,
        {
            "compute_time": compute_time,
            "evaluation_time": evaluation_time,
            "other_time": other_time,
        },
    )


if __name__ == "__main__":
    run(language="en")
