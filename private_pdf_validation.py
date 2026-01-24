# coding: utf-8
import os
import argparse
import sys
import io
import pathlib
import yaml
from registry.registry import EVAL_TASK_REGISTRY, DATASET_REGISTRY, METRIC_REGISTRY
import dataset
import task
import metrics

def process_args(args):
    parser = argparse.ArgumentParser(description='Render latex formulas for comparison.')
    parser.add_argument('--config', '-c', type=str, default='./configs/private.yaml')
    parameters = parser.parse_args(args)
    return parameters

if __name__ == '__main__':
    parameters = process_args(sys.argv[1:])
    config_path = parameters.config
    
    if isinstance(config_path, (str, pathlib.Path)):
        with io.open(os.path.abspath(config_path), "r", encoding="utf-8") as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
    else:
        raise TypeError("Unexpected file type")

    if cfg is not None and not isinstance(cfg, (list, dict, str)):
        raise IOError(f"Invalid loaded object type: {type(cfg).__name__}")

    for task_name in cfg.keys():
        if not cfg.get(task_name):
            print(f'No config for task {task_name}')
            continue
            
        dataset_name = cfg[task_name]['dataset']['dataset_name']
        metrics_list = cfg[task_name]['metrics']
        val_dataset = DATASET_REGISTRY.get(dataset_name)(cfg[task_name])
        val_task = EVAL_TASK_REGISTRY.get(task_name)

        # --- Dynamic Path Logic ---
        prediction_path = cfg[task_name]['dataset']['prediction'].get('data_path', '')
        # Extracts 'sr' from 'output/sr'
        mode_name = os.path.basename(prediction_path) if prediction_path else "default"
        
        # Define and create output directory: result/{mode}/
        output_dir = os.path.join("result", mode_name)
        os.makedirs(output_dir, exist_ok=True)

        if prediction_path:
            base_name = os.path.basename(prediction_path) + '_' + cfg[task_name]['dataset'].get('match_method', 'quick_match')
        else:
            base_name = os.path.basename(cfg[task_name]['dataset']['ground_truth']['data_path']).split('.')[0]
        
        # Final save path: result/{mode}/{filename}
        save_path = os.path.join(mode_name, base_name)
        
        print(f'###### Processing Task: {task_name}')
        print(f'###### Saving to: {save_path}')
        
        if cfg[task_name]['dataset']['ground_truth'].get('page_info'):
            val_task(val_dataset, metrics_list, cfg[task_name]['dataset']['ground_truth']['page_info'], save_path)
        else:
            val_task(val_dataset, metrics_list, cfg[task_name]['dataset']['ground_truth']['data_path'], save_path)