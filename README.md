# Abaqus ODB Batch Post-Processing — Maximum Values and Locations

A Python-based post-processing tool for Abaqus `.odb` files. The script automatically processes **all ODB files in the same folder as the Python script** and extracts maximum result values and their corresponding locations.

It is designed for **batch processing, model comparison, and mesh-convergence studies**.

---

## Features

For each ODB and each assembly instance/part, the script extracts:

* Maximum von Mises stress
* Element and integration point of maximum stress
* Approximate XYZ location of maximum stress
* Maximum displacement magnitude
* Node and exact XYZ location of maximum displacement
* Maximum spatial strain energy, when `ELSE` or `SENER` is available
* Approximate location of maximum strain energy
* ODB filename, step, frame, instance, and element count

All results are saved to a single CSV file.

---

## Requirements

* Abaqus
* Abaqus Python interpreter
* Tested with Abaqus 2024

The script uses Abaqus-specific modules such as:

```python
from odbAccess import openOdb
from abaqusConstants import *
```

Therefore, it must be run using the Abaqus Python interpreter rather than standard Python.

---

## Folder Structure

Place the script and the ODB files in the same folder:

```text
Abaqus-F/
│
├── max_everything_location_value.py
├── Model-1.odb
├── Model-2.odb
├── Model-3.odb
└── ...
```

The script automatically detects all `.odb` files in this folder.

No ODB paths need to be entered manually.

---

## Settings

By default:

```python
STEP_NAME = None
FRAME_NUMBER = -1
```

This means:

* The **last analysis step** is selected automatically.
* The **last frame** of that step is selected automatically.

A specific step or frame can be selected by changing these values, for example:

```python
STEP_NAME = "Step-1"
FRAME_NUMBER = 5
```

For mesh-convergence studies, make sure that the selected final frames represent the same physical loading state, even if different ODBs contain different numbers of frames.

---

## Running the Script

Run it using Abaqus Python:

```powershell
abaqus python "Path\to\max_everything_location_value.py"
```

For example:

```powershell
abaqus python "C:\Projects\Abaqus\Mesh Study\max_everything_location_value.py"
```

---

## Output

The script creates:

```text
ODB_Post_Processing_Results.csv
```

in the same folder.

The CSV contains separate results for each ODB and each assembly instance.

---

## Stress and Displacement Locations

Von Mises stress is extracted from the `S` field at integration points.

The stress location is calculated from the geometric center of the element's nodes. For `C3D4` elements, this corresponds to the single integration point at the element centroid.

Displacement is extracted from the `U` field and its magnitude is calculated as:

$$
|U|=\sqrt{U_x^2+U_y^2+U_z^2}
$$

Since displacement is a nodal result, its reported coordinates are the exact coordinates of the corresponding node.

---

## Strain Energy

The script searches for spatial strain-energy output in the following order:

```text
ELSE
SENER
```

If neither field is available, strain energy is reported as:

```text
N/A
```

`ALLSE` is not used for the strain-energy location because it represents total strain energy rather than a spatial field with an XYZ location.

---

## Notes

* The script processes **all `.odb` files in its own folder**.
* Existing `ODB_Post_Processing_Results.csv` files are overwritten when the script is run again.
* Stress locations are approximate for element types where the integration point does not coincide with the element centroid.
* The script is intended primarily for Abaqus solid-element post-processing.

---

## Author

**Sepehr Sohrabi**

Abaqus Python Post-Processing Utility
Enjoy!
