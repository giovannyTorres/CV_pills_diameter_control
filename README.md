# Capsule Diameter Measurement

This project analyzes cross-sectional images of capsules to compute the ratio
between inner and outer diameters. The code follows a class-based architecture
with PEP 8 compliant naming and documentation in English.

## Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the command-line interface:

```bash
python main.py -i path/to/image.png
```

The script processes the image, saves an annotated copy in `img_output`, and
stores the average ratio in a MySQL database named `CapsuleDB`.

## Modules

- `capsule_processor.py`: Provides the `CapsuleProcessor` class for image
  processing and ratio calculation.
- `database_manager.py`: Provides the `CapsuleDatabase` class for database
  operations.
- `main.py`: Entry point that ties everything together.

## Notes

Proper results require clear, well-lit images where the capsule is centered and
background noise is minimal.
