# Spatial Data Quality Check Tool

A professional desktop application for spatial data quality inspection, built with Python and PyQt5.

## Features

- **Data Loading**: Support multiple data formats
  - Raster data: TIF, BMP, PNG, JPG
  - Vector data: SHP, GeoJSON
  - Text data: TXT, CSV

- **Visualization**: 
  - Image display with zoom and pan
  - Text viewer with line numbers

- **Error Marking**:
  - Click to mark error locations
  - Multiple error types (Geometry, Attribute, Topology, Coordinate, Other)
  - Auto-generated error IDs

- **Error Management**:
  - Save/Load error records (JSON)
  - Search and filter errors
  - Export error reports

## Requirements

- Python 3.9+
- PyQt5
- Pillow
- NumPy
- PyYAML

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
SpatialDataQC/
├── main.py              # Entry point
├── config.yaml          # Configuration
├── requirements.txt     # Dependencies
│
├── ui/                  # UI Layer
│   ├── main_window.py
│   ├── map_canvas.py
│   ├── error_panel.py
│   └── ...
│
├── core/                # Business Logic Layer
│   ├── data_loader.py
│   ├── error_manager.py
│   └── query_engine.py
│
├── data/                # Data Access Layer
│   ├── file_reader.py
│   ├── error_store.py
│   └── models/
│
└── utils/               # Utilities
    ├── logger.py
    └── file_utils.py
```

## Architecture

This project uses a **3-Layer Architecture**:

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│              (ui/)                  │
├─────────────────────────────────────┤
│         Business Logic Layer        │
│              (core/)                │
├─────────────────────────────────────┤
│         Data Access Layer           │
│              (data/)                │
└─────────────────────────────────────┘
```

## License

MIT License
