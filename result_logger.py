import csv
import numpy as np
from datetime import datetime
from functools import wraps
from pathlib import Path


def verbose_to_result_file(method):

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "_logging_redirect_depth", 0) > 0:
            return method(self, *args, **kwargs)
        original_verbose = self.verbose
        before_calls = (self.fitness_a_calls, self.fitness_b_calls)
        self._logging_redirect_depth += 1
        try:
            with self.result_file_path.open("a", encoding="utf-8") as fh:
                self._result_file_handle = fh
                self.verbose = True
                result = method(self, *args, **kwargs)
                self._report_completion(method.__name__, before_calls)
                return result
        finally:
            self.verbose = original_verbose
            self._result_file_handle = None
            self._logging_redirect_depth -= 1

    return wrapper


class ResultLogger:
    messages = {
        "call_statistics_title": "Function evaluation statistics",
        "stage_calls_title": "\nCalls by stage:",
        "stage_calls_header": "Stage                     | Function a calls | Function b calls | Total calls",
        "stage_calls_total": "Total                     | {0:<10} | {1:<10} | {2:<10}",
        "total_calls_title": "\nTotal calls:",
        "total_calls_a": "Function a total calls: {0}",
        "total_calls_b": "Function b total calls: {0}",
        "total_calls": "Total function calls: {0}",
        "compact_statistics_title": "Function evaluation statistics",
        "compact_calls_a": "Function a total calls: {0}",
        "compact_calls_b": "Function b total calls: {0}",
        "compact_calls_total": "Total function calls: {0}",
        "stage_calls_row": "{0:<25} | {1:<10} | {2:<10} | {3:<10}",
        "call_proportions_title": "\nCall proportions:",
        "call_proportion_a": "Function a call proportion: {0:.2%}",
        "call_proportion_b": "Function b call proportion: {0:.2%}",
        "elapsed_time_a": "Function a elapsed time: {0:.1f} ({1:.2%})",
        "elapsed_time_b": "Function b elapsed time: {0:.1f} ({1:.2%})",
        "elapsed_time_total": "Total evaluation time: {0:.2f} seconds",
        "compact_call_proportion_a": "Function a call proportion: {0:.2%}",
        "compact_call_proportion_b": "Function b call proportion: {0:.2%}",
        "compact_time_cost_a": "Function a time cost: {0:.1f} ({1:.2%})",
        "compact_time_cost_b": "Function b time cost: {0:.1f} ({1:.2%})",
        "invalid_geometry": "  [PENALTY] Invalid geometry.",
        "geometry_generation_failed": "  [PENALTY] Error during geometry generation: {0}",
        "geometry_write_failed": "  [PENALTY] Failed to write temp file: {0}",
        "physics_timeout": "  [PENALTY] MATLAB did not respond in time.",
        "geometry_cleanup_failed": "  Warning: Could not delete temp file {0}: {1}",
        "timing_report": "\n==================================================\nComplete optimization timing\nFunction a accumulated time: {0:.6f} seconds\nFunction b accumulated time: {1:.6f} seconds\nAccumulated evaluation time: {2:.6f} seconds\nOther optimization overhead: {3:.6f} seconds\nExternally measured total time: {4:.6f} seconds\nExternally measured total time: {5:.6f} minutes\n==================================================\n",
        "optimization_summary": "\n==================================================\nOptimization results\nGlobal samples: {0}\nUnique samples after pre-hillclimb: {1}\nSelected candidates: {2}\nLocal optima: {3}\nRetained local optima: {4}\nRefined solutions: {5}\nBest solution found: {6}\nBest fitness: {7:.6f}\n==================================================\n",
        "stage_completed": "{0} completed: function a calls={1}, function b calls={2}",
    }
    translations = {}

    def _translate_log(self, text):
        for original, translated in self.translations.items():
            text = text.replace(original, translated)
        return text

    def _message(self, key, *values):
        values = tuple(
            (self._translate_log(value) if isinstance(value, str) else value for value in values)
        )
        return self.messages[key].format(*values)

    def _log_message(self, key, *values, summary=False):
        self._log(self._message(key, *values), summary=summary)

    def _log(self, *args, sep=" ", end="\n", summary=False):
        if (self.log_mode == "compact") != summary:
            return
        text = sep.join((str(arg) for arg in args)) + end
        text = self._translate_log(text)
        if self._result_file_handle is not None:
            self._result_file_handle.write(text)
        else:
            with self.result_file_path.open("a", encoding="utf-8") as fh:
                fh.write(text)

    def _summary_print(self, *args, **kwargs):
        self._log(*args, summary=True, **kwargs)

    def _append_csv_row(self, filename, columns, row):
        path = self._allocate_csv_output_path(self.data_dir / filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            if needs_header:
                fh.write(self._build_csv_metadata_line() + "\n")
                writer.writerow(columns)
            writer.writerow(row)

    def _create_result_file(self):
        self.results_dir.mkdir(parents=True, exist_ok=True)
        date_prefix = datetime.now().strftime("%Y%m%d")
        existing_indices = []
        for path in self.results_dir.glob(f"{date_prefix}_*_result.txt"):
            parts = path.stem.split("_")
            if len(parts) >= 3 and parts[1].isdigit():
                existing_indices.append(int(parts[1]))
        next_index = max(existing_indices, default=0) + 1
        file_path = self.results_dir / f"{date_prefix}_{next_index:03d}_result.txt"
        file_path.touch()
        return file_path.resolve()

    def _build_csv_metadata_line(self):
        bounds_text = ";".join((f"[{float(low)},{float(high)}]" for low, high in self.bounds))
        return f"dim={self.dim},m={self.m},P={self.P},k_percent={self.k_percent},repulsion_strategy={self.repulsion_strategy},importance_method={self.importance_method},log_mode={self.log_mode},bounds={bounds_text},run_id={self.run_id}"

    def _write_csv_with_metadata(self, path, columns, rows):
        output_path = self._allocate_csv_output_path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as fh:
            fh.write(self._build_csv_metadata_line() + "\n")
            writer = csv.writer(fh)
            writer.writerow(columns)
            writer.writerows(rows)
        return output_path

    def _allocate_csv_output_path(self, base_path):
        base_path = Path(base_path)
        cache_key = str(base_path.resolve())
        cached_path = self._csv_output_paths.get(cache_key)
        if cached_path is not None:
            return cached_path
        candidate = base_path
        if candidate.exists():
            suffix_index = 1
            while True:
                candidate = base_path.with_name(
                    f"{base_path.stem}_{suffix_index:03d}{base_path.suffix}"
                )
                if not candidate.exists():
                    break
                suffix_index += 1
        self._csv_output_paths[cache_key] = candidate
        return candidate

    def _flatten_vector(self, vector):
        array = np.asarray(vector, dtype=float).reshape(-1)
        return [float(value) for value in array]

    def _format_vector(self, vector):
        return "[" + ", ".join((str(value) for value in self._flatten_vector(vector))) + "]"

    def _export_hill_climb_csv(self, row):
        hill_columns = (
            ["candidate_index"]
            + [f"original_x_{idx}" for idx in range(self.dim)]
            + ["original_func_a"]
            + [f"improved_x_{idx}" for idx in range(self.dim)]
            + ["improved_func_a", "iteration_count", "func_a_calls", "func_b_calls", "stop_reason"]
        )
        self._append_csv_row(f"{self.run_id}_hill_climb_improvements.csv", hill_columns, row)

    def _export_refined_history_csv(self, row):
        refined_columns = [
            "history_index",
            "refined_iterations",
            "func_b_calls",
            "important_dims",
            "start_x",
            "start_func_b",
            "end_x",
            "end_func_b",
            "best_x",
            "best_func_b",
        ]
        self._append_csv_row(f"{self.run_id}_refined_history.csv", refined_columns, row)

    @verbose_to_result_file
    def print_call_summary(self):
        self._log("\n" + "=" * 50)
        self._log_message("call_statistics_title")
        self._log("=" * 50)
        self._log_message("stage_calls_title")
        self._log_message("stage_calls_header")
        self._log("-" * 60)
        total_a = 0
        total_b = 0
        for stage, calls in self.stage_calls.items():
            a_calls = calls["a"]
            b_calls = calls["b"]
            total_a += a_calls
            total_b += b_calls
            stage_name = {
                "global_sampling": "Global grid sampling",
                "hill_climb_initial": "Initial hill climb",
                "local_opt_filtering": "Local optimum filtering",
                "importance_analysis": "Parameter importance analysis",
                "hill_climb_refined": "Refinement",
                "final_validation": "Final validation",
            }.get(stage, stage)
            self._log_message("stage_calls_row", stage_name, a_calls, b_calls, a_calls + b_calls)
        self._log("-" * 60)
        self._log_message("stage_calls_total", total_a, total_b, total_a + total_b)
        self._log_message("total_calls_title")
        self._log_message("total_calls_a", self.fitness_a_calls)
        self._log_message("total_calls_b", self.fitness_b_calls)
        self._log_message("total_calls", self.fitness_a_calls + self.fitness_b_calls)
        if self.fitness_a_calls > 0 or self.fitness_b_calls > 0:
            self._log_message("call_proportions_title")
            total_calls = self.fitness_a_calls + self.fitness_b_calls
            self._log_message("call_proportion_a", self.fitness_a_calls / total_calls)
            self._log_message("call_proportion_b", self.fitness_b_calls / total_calls)
            a_time = self.time_a
            b_time = self.time_b
            total_time = a_time + b_time
            self._log_message("elapsed_time_a", a_time, a_time / total_time)
            self._log_message("elapsed_time_b", b_time, b_time / total_time)
            self._log_message("elapsed_time_total", total_time)
        self._log("=" * 50)
        self._summary_print("=" * 50)
        self._log_message("compact_statistics_title", summary=True)
        self._summary_print("=" * 50)
        self._log_message("compact_calls_a", self.fitness_a_calls, summary=True)
        self._log_message("compact_calls_b", self.fitness_b_calls, summary=True)
        self._log_message(
            "compact_calls_total", self.fitness_a_calls + self.fitness_b_calls, summary=True
        )
        if self.fitness_a_calls > 0 or self.fitness_b_calls > 0:
            total_calls = self.fitness_a_calls + self.fitness_b_calls
            a_time = self.fitness_a_calls * self.time_a
            b_time = self.fitness_b_calls * self.time_b
            total_time = a_time + b_time
            self._log_message(
                "compact_call_proportion_a", self.fitness_a_calls / total_calls, summary=True
            )
            self._log_message(
                "compact_call_proportion_b", self.fitness_b_calls / total_calls, summary=True
            )
            self._log_message("compact_time_cost_a", a_time, a_time / total_time, summary=True)
            self._log_message("compact_time_cost_b", b_time, b_time / total_time, summary=True)
        self._summary_print("=" * 50)

    def _report_completion(self, method_name, before_calls):
        if method_name == "print_call_summary":
            return
        summary = self.log_mode == "compact"
        if method_name != "optimize":
            self._log_message(
                "stage_completed",
                method_name,
                self.fitness_a_calls - before_calls[0],
                self.fitness_b_calls - before_calls[1],
                summary=summary,
            )
            return
        data = self.debug_data
        result = data["final_result"]
        self._log_message(
            "optimization_summary",
            len(data["global_samples"]),
            len(data["unique_selected_samples"]),
            len(data["selected_samples"]),
            len(data["local_opts"]),
            len(data["filtered_local_opts"]),
            len(data["refined_opts"]),
            result["best_solution"],
            result["best_fitness"],
            summary=summary,
        )

    def _build_call_summary(self):
        total_a = sum((calls["a"] for calls in self.stage_calls.values()))
        total_b = sum((calls["b"] for calls in self.stage_calls.values()))
        total_calls = self.fitness_a_calls + self.fitness_b_calls
        a_time = self.fitness_a_calls * self.time_a
        b_time = self.fitness_b_calls * self.time_b
        return {
            "stage_calls": {stage: calls.copy() for stage, calls in self.stage_calls.items()},
            "stage_totals": {"a": total_a, "b": total_b},
            "fitness_a_calls": self.fitness_a_calls,
            "fitness_b_calls": self.fitness_b_calls,
            "total_calls": total_calls,
            "virtual_time": self.time_a + self.time_b,
            "time_cost": {"a": a_time, "b": b_time, "total": a_time + b_time},
        }

    def _set_language(self, language):
        if language != "en":
            raise ValueError("Only English logging is supported")
        self.language = "en"
        self.messages = ResultLogger.messages
        self.translations = {}

    def _init_output(self, results_dir, data_dir, verbose, log_mode):
        self.verbose = verbose
        self._logging_redirect_depth = 0
        self.log_mode = log_mode
        self.results_dir = Path(results_dir)
        if not self.results_dir.is_absolute():
            self.results_dir = Path(__file__).resolve().parent / self.results_dir
        self.data_dir = Path(data_dir)
        if not self.data_dir.is_absolute():
            self.data_dir = Path(__file__).resolve().parent / self.data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.result_file_path = self._create_result_file()
        self._result_file_handle = None
        self.run_id = self.result_file_path.stem.replace("_result", "")
        self._csv_output_paths = {}

    def _record_pre_hillclimb(self, improvement_records):
        global_columns = (
            ["sample_index"]
            + [f"original_x_{idx}" for idx in range(self.dim)]
            + ["original_func_a"]
            + [f"improved_x_{idx}" for idx in range(self.dim)]
            + ["improved_func_a"]
        )
        global_csv_path = self.data_dir / f"{self.run_id}_global_pre_hill_improvements.csv"
        self._write_csv_with_metadata(global_csv_path, global_columns, improvement_records)

    def _record_refinement(self, history, important_dims, b_calls):
        history_index = len(self.debug_data["refined_history"]) - 1
        best_step = min(history, key=lambda item: item["fitness"])
        refined_csv_row = [
            history_index,
            len(history) - 1,
            b_calls,
            str(list(np.asarray(important_dims, dtype=int).tolist())),
            self._format_vector(history[0]["point"]),
            float(history[0]["fitness"]),
            self._format_vector(history[-1]["point"]),
            float(history[-1]["fitness"]),
            self._format_vector(best_step["point"]),
            float(best_step["fitness"]),
        ]
        self._export_refined_history_csv(refined_csv_row)

    def _record_hill_climb(self, i, hill_summary):
        hill_row = (
            [i]
            + self._flatten_vector(hill_summary["start_x"])
            + [hill_summary["start_func_a"]]
            + self._flatten_vector(hill_summary["end_x"])
            + [
                hill_summary["end_func_a"],
                hill_summary["iteration_count"],
                hill_summary["func_a_calls"],
                hill_summary["func_b_calls"],
                hill_summary["stop_reason"],
            ]
        )
        self._export_hill_climb_csv(hill_row)
