# Abaqus ODB Batch Post-Processing — Maximum Values and Locations

A Python-based post-processing tool for Abaqus `.odb` files that automatically processes **all ODB files located in the same folder as the Python script** and extracts the maximum values and corresponding locations of several important analysis results.

The script is designed to work with the **Abaqus Python environment** and cannot be executed using a standard Python installation.

The main results extracted for each Abaqus instance/part are:

* Maximum von Mises stress
* Location of maximum von Mises stress
* Maximum displacement magnitude
* Location of maximum displacement
* Spatial strain energy, when available
* Location of maximum strain energy, when available

All results are automatically saved into a single CSV file, making the script particularly useful for **mesh-convergence studies, model comparisons, and batch post-processing of multiple Abaqus analyses**.

---

# Features

* Automatically searches the Python script's folder for all `.odb` files.
* Processes multiple ODB files in a single run.
* Opens each Abaqus `.odb` file in read-only mode.
* Automatically selects the last analysis step by default.
* Automatically selects the last frame of the selected step by default.
* Processes every assembly instance/part in each ODB.
* Extracts stress (`S`) at integration points.
* Finds the maximum von Mises stress.
* Identifies the element containing the maximum von Mises stress.
* Reports:

  * ODB filename
  * Analysis step
  * Frame number
  * Instance name
  * Element count
  * Element label
  * Element type
  * Stress output position
  * Integration point
  * Maximum von Mises stress
  * Approximate XYZ location of maximum stress
* Extracts displacement (`U`) and calculates its vector magnitude.
* Finds the maximum displacement.
* Identifies the node containing the maximum displacement.
* Reports the exact XYZ coordinates of the maximum-displacement node.
* Searches for spatial strain-energy fields (`ELSE` or `SENER`).
* Reports the maximum spatial strain energy when available.
* Reports the approximate location of maximum strain energy when available.
* Automatically creates a CSV file containing all extracted results.
* Keeps results from different ODB files separated using the ODB filename.
* Does not require ODB paths to be manually entered into the script.
* Uses Abaqus-compatible methods for finding nodes and elements without relying on `getFromLabel()`.

---

# Requirements

## Software

* Abaqus
* Abaqus Python interpreter
* Tested with Abaqus 2024

The script requires Abaqus-specific modules:

```python
from odbAccess import openOdb
from abaqusConstants import *
```

Therefore, running the script using standard Python will result in an error similar to:

```text
ModuleNotFoundError: No module named 'odbAccess'
```

---

# File Name

The script is named:

```text
max_everything_location_value.py
```

---

# Folder Structure

The script is designed to automatically find all `.odb` files in the **same folder as the Python script**.

For example:

```text
Abaqus-F/
│
├── max_everything_location_value.py
│
├── Model-1.odb
├── Model-2.odb
├── Model-3.odb
├── Model-4.odb
│
└── ODB_Post_Processing_Results.csv
```

The CSV file is automatically created after the script finishes.

There is no need to enter the ODB file paths manually.

---

# Analysis Step Selection

The script contains:

```python
STEP_NAME = None
```

When this is set to:

```python
STEP_NAME = None
```

the script automatically selects the **last analysis step** available in each ODB.

For example, if an ODB contains:

```text
Initial
Step-1
Step-2
```

the script will automatically process:

```text
Step-2
```

### Selecting a specific step

If a specific step is required, change:

```python
STEP_NAME = None
```

to, for example:

```python
STEP_NAME = "Step-1"
```

The name must exactly match the step name stored in the ODB.

---

# Frame Selection

The script contains:

```python
FRAME_NUMBER = -1
```

By default, this means:

```text
Use the last frame of the selected analysis step.
```

For example, if the selected step contains:

```text
Frame 0
Frame 1
Frame 2
...
Frame 12
```

the script will automatically use:

```text
Frame 12
```

### Selecting a specific frame

To process a particular frame, change:

```python
FRAME_NUMBER = -1
```

to, for example:

```python
FRAME_NUMBER = 5
```

The script will then use Frame 5.

---

# Important Note About Frames

Different ODB files may contain different numbers of frames.

For example:

```text
Model-1.odb → 9 frames
Model-2.odb → 13 frames
Model-3.odb → 9 frames
```

Using:

```python
FRAME_NUMBER = -1
```

means that the script selects the **final frame of each ODB**.

The number of frames alone does not necessarily mean that the ODBs represent different physical loading states. Different numbers of frames can result from different numbers of solution increments.

For mesh-convergence studies, it is therefore important to verify that the final frames correspond to the same physical analysis state.

---

# Running the Script

Do not run this script using standard Python.

### Incorrect

```powershell
python max_everything_location_value.py
```

### Correct

Run the script using the Abaqus Python interpreter:

```powershell
abaqus python "Path\to\max_everything_location_value.py"
```

For example:

```powershell
abaqus python "C:\Projects\Abaqus\Mesh Study\max_everything_location_value.py"
```

The script will automatically find all `.odb` files located in the same folder.

---

# CSV Output

After processing all ODB files, the script creates:

```text
ODB_Post_Processing_Results.csv
```

in the same folder as the Python script.

The CSV contains one row for each **ODB instance/part**.

For example:

```text
ODB,Step,Frame,Instance,Element_Count,Max_Mises,...
Model-1.odb,Step-1,12,MANDIBLE-1,159778,85.49,...
Model-1.odb,Step-1,12,STAPLE-1,1200,142.31,...
Model-2.odb,Step-1,8,MANDIBLE-1,180000,84.97,...
Model-2.odb,Step-1,8,STAPLE-1,1400,141.82,...
```

This allows results from multiple models and mesh sizes to be compared directly.

---

# Extracted Results

The CSV contains the following main groups of information.

## ODB and Analysis Information

* `ODB`
* `Step`
* `Frame`
* `Instance`
* `Element_Count`

---

## Maximum von Mises Stress

The following information is extracted:

* `Max_Mises`
* `Max_Mises_Element`
* `Max_Mises_Element_Type`
* `Max_Mises_Position`
* `Max_Mises_Integration_Point`
* `Max_Mises_X`
* `Max_Mises_Y`
* `Max_Mises_Z`

The stress field is obtained from:

```python
frame.fieldOutputs["S"]
```

and the values are requested at:

```python
INTEGRATION_POINT
```

The script then searches through the integration-point values belonging to each instance and identifies the largest:

```text
S.Mises
```

value.

---

# Maximum Displacement

The script obtains displacement from:

```python
frame.fieldOutputs["U"]
```

For every nodal displacement value, the magnitude is calculated as:

$$
|U|=\sqrt{U_x^2+U_y^2+U_z^2}
$$

The maximum displacement magnitude is then identified for each instance.

The CSV reports:

* `Max_Displacement`
* `Max_Displacement_Node`
* `Max_Displacement_X`
* `Max_Displacement_Y`
* `Max_Displacement_Z`

Because displacement is a nodal result, the reported coordinates correspond directly to the node containing the maximum displacement.

---

# Strain Energy

The script searches for spatial strain-energy output in the following order:

```text
ELSE
SENER
```

If `ELSE` is available, it is used.

If `ELSE` is unavailable but `SENER` exists, `SENER` is used.

The CSV reports:

* `Strain_Energy_Field`
* `Max_Strain_Energy`
* `Max_Strain_Energy_Element`
* `Max_Strain_Energy_Element_Type`
* `Max_Strain_Energy_Position`
* `Max_Strain_Energy_Integration_Point`
* `Max_Strain_Energy_X`
* `Max_Strain_Energy_Y`
* `Max_Strain_Energy_Z`

If neither `ELSE` nor `SENER` exists in the selected frame, the script reports:

```text
Spatial strain energy: N/A
```

This does **not** indicate an error in the script. It means that a spatial strain-energy field was not written to the ODB.

---

# Important Note About ALLSE

The script intentionally does not use `ALLSE` to determine the location of maximum strain energy.

`ALLSE` represents the **total strain energy** of the model/region and is generally a history output rather than a spatial field containing an XYZ location.

Therefore, `ALLSE` cannot directly provide:

```text
X
Y
Z
```

coordinates for a maximum-energy location.

For a spatial location, the ODB must contain a suitable element-level energy field such as `ELSE` or `SENER`.

---

# Location of Maximum Stress

The stress values are obtained at integration points.

The script does not use the `COORD` field. Instead, it calculates an approximate spatial location from the coordinates of the element's connected nodes.

For an element with `n` nodes:

$$
X_c=\frac{\sum_{i=1}^{n}X_i}{n}
$$

$$
Y_c=\frac{\sum_{i=1}^{n}Y_i}{n}
$$

$$
Z_c=\frac{\sum_{i=1}^{n}Z_i}{n}
$$

The resulting point is the geometric center of the element.

---

# Accuracy of the Stress Location

For a linear tetrahedral element such as:

```text
C3D4
```

there is one integration point located at the element centroid.

Therefore, for C3D4 elements, the calculated element center corresponds to the integration-point location.

For other element types with multiple integration points, the geometric center is an **approximate location** of the reported integration-point result.

The maximum stress value itself is taken directly from the Abaqus integration-point field output; only the reported XYZ location is approximate for general element types.

---

# Example Terminal Output

A typical run may look like:

```text
============================================================
ABAQUS ODB POST-PROCESSING
============================================================

Script folder:
C:\Projects\Abaqus\Mesh Study

ODB files found:
  - Model-1.odb
  - Model-2.odb
  - Model-3.odb

============================================================
PROCESSING ODB
============================================================
ODB: Model-1.odb

Step : Step-1
Frame: 12

Available field outputs:
  S
  U
  LE
  RF
  UR

------------------------------------------------------------
INSTANCE / PART
------------------------------------------------------------
Instance: MANDIBLEA_COPY-1#PART-1-1
Elements: 159778

Maximum Mises stress: 85.495857
Max Mises element: 12
Max Mises element type: C3D4
Max Mises integration point: 1
Max Mises location: -22.003788, -185.956532, -220.786194

Maximum displacement: 0.163973
Max displacement node: 310
Max displacement location: -22.380726, -185.219772, -220.329910

Spatial strain energy: N/A

Finished: Model-1.odb

============================================================
ALL ODB FILES PROCESSED
============================================================

CSV file created:
C:\Projects\Abaqus\Mesh Study\ODB_Post_Processing_Results.csv

Done.
```

---

# Batch Processing

One of the main purposes of this script is to process several Abaqus analyses automatically.

For example, a mesh-convergence folder could contain:

```text
Mesh_2.5mm.odb
Mesh_1.5mm.odb
Mesh_1.0mm.odb
Mesh_0.75mm.odb
Mesh_0.5mm.odb
```

The script processes all of them automatically.

This makes it possible to create a single table containing results s
