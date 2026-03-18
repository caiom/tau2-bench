"""Load saved tau2-bench result files and log metrics to a single wandb run.

Usage:
    python -m tau2.scripts.log_wandb results1.json results2.json ...

Each file's domain is extracted from the results and used as a metric prefix,
e.g. airline/avg_reward, retail/pass_hat_1.

Wandb project/entity/key are read from environment variables
(WANDB_PROJECT, WANDB_ENTITY, WANDB_API_KEY).
"""

import argparse
import sys
from pathlib import Path

from tau2.data_model.simulation import Results
from tau2.metrics.agent_metrics import compute_metrics
from tau2.utils.wandb_logger import finish_wandb_run, init_wandb_run, log_metrics


def main():
    parser = argparse.ArgumentParser(
        description="Log saved tau2-bench results to wandb"
    )
    parser.add_argument(
        "result_files",
        nargs="+",
        type=str,
        help="Paths to result JSON files",
    )
    args = parser.parse_args()

    # Collect per-domain metrics
    all_metrics: dict[str, dict] = {}
    config_for_wandb: dict = {}

    for path_str in args.result_files:
        path = Path(path_str)
        if not path.exists():
            print(f"WARNING: {path} does not exist, skipping")
            continue

        results = Results.load(path)
        domain = results.info.environment_info.domain_name
        metrics = compute_metrics(results)
        all_metrics[domain] = metrics.as_dict()

        # Use first file's info as wandb config
        if not config_for_wandb:
            config_for_wandb = {
                "agent_llm": results.info.agent_info.llm,
                "user_llm": results.info.user_info.llm,
                "num_trials": results.info.num_trials,
                "max_steps": results.info.max_steps,
                "domains": list(all_metrics.keys()),
            }

    if not all_metrics:
        print("No valid result files found")
        sys.exit(1)

    # Update domains list with all domains found
    config_for_wandb["domains"] = list(all_metrics.keys())

    init_wandb_run(config=config_for_wandb)
    for domain, metrics_dict in all_metrics.items():
        log_metrics(metrics_dict, prefix=domain)
    finish_wandb_run()

    print(f"Logged metrics for {list(all_metrics.keys())} to wandb")


if __name__ == "__main__":
    main()
