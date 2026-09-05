import argparse
import logging
import sys
from pathlib import Path
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AvalancheVision")

def run_step(command: list[str], description: str):
    logger.info(f"--- Starting: {description} ---")
    result = subprocess.run([sys.executable] + command)
    if result.returncode != 0:
        logger.error(f"Failed during: {description}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="AvalancheVision: Deep Learning Pipeline")
    parser.add_argument("--skip-train", action="store_true", help="Skip model training and run inference only")
    parser.add_argument("--threshold", type=float, default=0.5, help="Probability threshold for hazard vectorization")
    args = parser.parse_args()

    logger.info("Initializing AvalancheVision Processing Engine...")

    # Step 1: ERA5 Weather Integration
    run_step(["ml/preprocessing/add_weather_features.py"], "ERA5 Atmospheric Stacking")

    # Step 2: Model Training (Optional)
    if not args.skip_train:
        run_step(["ml/models/train_unet.py"], "U-Net 10-Band Retraining")

    # Step 3: Sliding Window Inference
    run_step(["-m", "ml.models.inference"], "Full-Tile Risk Map Inference")

    # Step 4: Vectorization & Evaluation
    run_step(["ml/postprocessing/evaluate_and_vectorize.py"], "Risk Map Vectorization")

    # Step 5: Web Map Generation
    run_step(["visualization/generate_map.py"], "Folium Interactive Map Generation")

    logger.info("Pipeline execution complete! Deliverables generated in data/processed/")

if __name__ == "__main__":
    main()