"""Command-line entry point for capsule measurement."""
import argparse
from capsule_processor import CapsuleProcessor
from database_manager import CapsuleDatabase


def main() -> None:
    """Measure capsule ratios and store them in the database."""
    parser = argparse.ArgumentParser(
        description="Measure capsule thickness ratio and store the result."
    )
    parser.add_argument(
        "-i", "--image", required=True, help="Path to the input capsule image."
    )
    args = parser.parse_args()

    processor = CapsuleProcessor(args.image)
    ratios = processor.measure_pill()
    parameter = CapsuleProcessor.check_parameter(ratios)

    db = CapsuleDatabase(host="localhost", user="root", password="")
    db.setup_database()
    db.insert_capsule(ratios["ratio_average"], parameter)


if __name__ == "__main__":
    main()
