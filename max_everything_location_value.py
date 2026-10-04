from odbAccess import openOdb
from abaqusConstants import *
import os
import csv
import math


# ============================================================
# SETTINGS
# ============================================================

# None = automatically use the last step
STEP_NAME = None

# -1 = automatically use the last frame
FRAME_NUMBER = -1

# Output CSV filename
CSV_NAME = "ODB_Post_Processing_Results.csv"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_element(instance, element_label):
    """
    Find an element by label.

    getFromLabel() is intentionally NOT used because
    OdbMeshElementArray in this Abaqus version does not
    provide that method.
    """

    for element in instance.elements:
        if element.label == element_label:
            return element

    return None


def get_node(instance, node_label):
    """
    Find a node by label.

    getFromLabel() is intentionally NOT used because
    OdbMeshNodeArray in this Abaqus version does not
    provide that method.
    """

    for node in instance.nodes:
        if node.label == node_label:
            return node

    return None


def get_element_center(instance, element):
    """
    Calculate the geometric center of an element
    from the coordinates of its connected nodes.

    This is an approximate location of an integration-point
    result.

    For C3D4 elements, the single integration point is at
    the centroid, so this is effectively the exact location.
    """

    x = 0.0
    y = 0.0
    z = 0.0

    number_of_nodes = len(element.connectivity)

    if number_of_nodes == 0:
        return None

    for node_label in element.connectivity:

        node = get_node(instance, node_label)

        if node is None:
            return None

        coordinates = node.coordinates

        x += coordinates[0]
        y += coordinates[1]
        z += coordinates[2]

    x /= number_of_nodes
    y /= number_of_nodes
    z /= number_of_nodes

    return (x, y, z)


def vector_magnitude(vector):
    """
    Calculate magnitude of a vector.
    """

    total = 0.0

    for value in vector:
        total += value * value

    return math.sqrt(total)


def get_value_magnitude(value):
    """
    Return the magnitude of a field value.

    Used mainly for displacement U.
    """

    try:
        return vector_magnitude(value.data)
    except:
        return None


def get_element_type(element):
    """
    Return element type if available.
    """

    try:
        return element.type
    except:
        return "N/A"


def get_integration_point(value):
    """
    Return integration point number if available.
    """

    try:
        return value.integrationPoint
    except:
        return "N/A"


def get_value_position(value):
    """
    Return the position of a field value.
    """

    try:
        return str(value.position)
    except:
        return "N/A"


# ============================================================
# FIND SCRIPT DIRECTORY
# ============================================================

SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIRECTORY = os.path.dirname(SCRIPT_PATH)

CSV_PATH = os.path.join(
    SCRIPT_DIRECTORY,
    CSV_NAME
)


# ============================================================
# FIND ALL ODB FILES
# ============================================================

odb_files = []

for filename in os.listdir(SCRIPT_DIRECTORY):

    if filename.lower().endswith(".odb"):

        full_path = os.path.join(
            SCRIPT_DIRECTORY,
            filename
        )

        if os.path.isfile(full_path):
            odb_files.append(full_path)


odb_files.sort()


# ============================================================
# START
# ============================================================

print("")
print("=" * 60)
print("ABAQUS ODB POST-PROCESSING")
print("=" * 60)

print("")
print("Script folder:")
print(SCRIPT_DIRECTORY)

print("")
print("ODB files found:")

if len(odb_files) == 0:

    print("  No .odb files found.")

    raise SystemExit


for odb_path in odb_files:

    print("  - " + os.path.basename(odb_path))


# ============================================================
# CSV HEADER
# ============================================================

csv_headers = [

    "ODB",

    "Step",
    "Frame",

    "Instance",
    "Element_Count",

    # --------------------------------------------------------
    # MAX MISES
    # --------------------------------------------------------

    "Max_Mises",

    "Max_Mises_Element",
    "Max_Mises_Element_Type",
    "Max_Mises_Position",
    "Max_Mises_Integration_Point",

    "Max_Mises_X",
    "Max_Mises_Y",
    "Max_Mises_Z",

    # --------------------------------------------------------
    # MAX DISPLACEMENT
    # --------------------------------------------------------

    "Max_Displacement",

    "Max_Displacement_Node",

    "Max_Displacement_X",
    "Max_Displacement_Y",
    "Max_Displacement_Z",

    # --------------------------------------------------------
    # STRAIN ENERGY
    # --------------------------------------------------------

    "Strain_Energy_Field",

    "Max_Strain_Energy",

    "Max_Strain_Energy_Element",
    "Max_Strain_Energy_Element_Type",
    "Max_Strain_Energy_Position",
    "Max_Strain_Energy_Integration_Point",

    "Max_Strain_Energy_X",
    "Max_Strain_Energy_Y",
    "Max_Strain_Energy_Z"
]


# ============================================================
# OPEN CSV
# ============================================================

with open(
    CSV_PATH,
    "w",
    newline=""
) as csv_file:

    writer = csv.writer(csv_file)

    writer.writerow(csv_headers)


    # ========================================================
    # PROCESS EACH ODB
    # ========================================================

    for odb_path in odb_files:

        odb_filename = os.path.basename(odb_path)

        print("")
        print("")
        print("=" * 60)
        print("PROCESSING ODB")
        print("=" * 60)

        print("ODB: " + odb_filename)


        # ----------------------------------------------------
        # OPEN ODB
        # ----------------------------------------------------

        try:

            odb = openOdb(
                path=odb_path,
                readOnly=True
            )

        except Exception as error:

            print("")
            print("ERROR opening ODB:")
            print(str(error))

            continue


        # ----------------------------------------------------
        # STEP
        # ----------------------------------------------------

        step_names = list(odb.steps.keys())

        if len(step_names) == 0:

            print("")
            print("No steps found.")

            odb.close()

            continue


        if STEP_NAME is None:

            step_name = step_names[-1]

        else:

            step_name = STEP_NAME


        if step_name not in odb.steps:

            print("")
            print("ERROR:")
            print("Step not found: " + step_name)

            odb.close()

            continue


        step = odb.steps[step_name]


        # ----------------------------------------------------
        # FRAME
        # ----------------------------------------------------

        if len(step.frames) == 0:

            print("")
            print("No frames found.")

            odb.close()

            continue


        if FRAME_NUMBER == -1:

            frame_index = len(step.frames) - 1

        else:

            frame_index = FRAME_NUMBER


        if frame_index >= len(step.frames):

            print("")
            print("ERROR:")
            print("Requested frame does not exist.")

            odb.close()

            continue


        frame = step.frames[frame_index]


        print("")
        print("Step : " + step_name)
        print("Frame: " + str(frame_index))


        # ----------------------------------------------------
        # AVAILABLE FIELD OUTPUTS
        # ----------------------------------------------------

        print("")
        print("Available field outputs:")

        field_output_names = list(
            frame.fieldOutputs.keys()
        )

        for field_name in field_output_names:

            print("  " + field_name)


        # ====================================================
        # GET STRESS FIELD
        # ====================================================

        stress_field = None

        if "S" in frame.fieldOutputs:

            stress_field = frame.fieldOutputs["S"]

            try:

                stress_field_ip = stress_field.getSubset(
                    position=INTEGRATION_POINT
                )

            except:

                stress_field_ip = stress_field

        else:

            stress_field_ip = None


        # ====================================================
        # GET DISPLACEMENT FIELD
        # ====================================================

        displacement_field = None

        if "U" in frame.fieldOutputs:

            displacement_field = frame.fieldOutputs["U"]


        # ====================================================
        # GET STRAIN ENERGY FIELD
        # ====================================================
        #
        # IMPORTANT:
        #
        # ALLSE is normally a whole-model/history quantity
        # and therefore does NOT provide a physical XYZ
        # location.
        #
        # For a spatial strain-energy result, we look for
        # ELSE or SENER.
        #
        # ====================================================

        strain_energy_field = None
        strain_energy_field_name = "N/A"

        if "ELSE" in frame.fieldOutputs:

            strain_energy_field = frame.fieldOutputs["ELSE"]
            strain_energy_field_name = "ELSE"

        elif "SENER" in frame.fieldOutputs:

            strain_energy_field = frame.fieldOutputs["SENER"]
            strain_energy_field_name = "SENER"


        # ====================================================
        # PROCESS EVERY INSTANCE
        # ====================================================

        for instance_name in odb.rootAssembly.instances.keys():

            instance = odb.rootAssembly.instances[
                instance_name
            ]


            print("")
            print("-" * 60)
            print("INSTANCE / PART")
            print("-" * 60)

            print(
                "Instance: " +
                instance_name
            )

            print(
                "Elements: " +
                str(len(instance.elements))
            )


            # =================================================
            # MAX MISES INITIALIZATION
            # =================================================

            max_mises = None

            max_mises_element = None
            max_mises_element_type = "N/A"

            max_mises_position = "N/A"
            max_mises_integration_point = "N/A"

            max_mises_x = None
            max_mises_y = None
            max_mises_z = None


            # =================================================
            # FIND MAX MISES
            # =================================================

            if stress_field_ip is not None:

                for value in stress_field_ip.values:

                    # -----------------------------------------
                    # Ignore values belonging to other
                    # instances
                    # -----------------------------------------

                    try:

                        if value.instance.name != instance_name:
                            continue

                    except:

                        continue


                    # -----------------------------------------
                    # Mises
                    # -----------------------------------------

                    try:

                        mises = value.mises

                    except:

                        continue


                    # -----------------------------------------
                    # Check maximum
                    # -----------------------------------------

                    if (
                        max_mises is None
                        or
                        mises > max_mises
                    ):

                        max_mises = mises


                        # -------------------------------------
                        # Element label
                        # -------------------------------------

                        try:

                            element_label = value.elementLabel

                        except:

                            element_label = None


                        max_mises_element = element_label


                        # -------------------------------------
                        # Element information
                        # -------------------------------------

                        if element_label is not None:

                            element = get_element(
                                instance,
                                element_label
                            )

                            if element is not None:

                                max_mises_element_type = (
                                    get_element_type(element)
                                )

                                coordinates = (
                                    get_element_center(
                                        instance,
                                        element
                                    )
                                )

                                if coordinates is not None:

                                    max_mises_x = coordinates[0]
                                    max_mises_y = coordinates[1]
                                    max_mises_z = coordinates[2]


                        # -------------------------------------
                        # Position
                        # -------------------------------------

                        max_mises_position = (
                            get_value_position(value)
                        )

                        max_mises_integration_point = (
                            get_integration_point(value)
                        )


            # =================================================
            # MAX DISPLACEMENT INITIALIZATION
            # =================================================

            max_displacement = None

            max_displacement_node = None

            max_displacement_x = None
            max_displacement_y = None
            max_displacement_z = None


            # =================================================
            # FIND MAX DISPLACEMENT
            # =================================================

            if displacement_field is not None:

                for value in displacement_field.values:

                    # -----------------------------------------
                    # Ignore values belonging to other
                    # instances
                    # -----------------------------------------

                    try:

                        if value.instance.name != instance_name:
                            continue

                    except:

                        continue


                    # -----------------------------------------
                    # Magnitude
                    # -----------------------------------------

                    displacement = (
                        get_value_magnitude(value)
                    )

                    if displacement is None:
                        continue


                    # -----------------------------------------
                    # Check maximum
                    # -----------------------------------------

                    if (
                        max_displacement is None
                        or
                        displacement > max_displacement
                    ):

                        max_displacement = displacement


                        # -------------------------------------
                        # Node label
                        # -------------------------------------

                        try:

                            node_label = value.nodeLabel

                        except:

                            node_label = None


                        max_displacement_node = node_label


                        # -------------------------------------
                        # Node coordinates
                        # -------------------------------------

                        if node_label is not None:

                            node = get_node(
                                instance,
                                node_label
                            )

                            if node is not None:

                                coordinates = node.coordinates

                                max_displacement_x = (
                                    coordinates[0]
                                )

                                max_displacement_y = (
                                    coordinates[1]
                                )

                                max_displacement_z = (
                                    coordinates[2]
                                )


            # =================================================
            # MAX STRAIN ENERGY INITIALIZATION
            # =================================================

            max_strain_energy = None

            max_strain_energy_element = None
            max_strain_energy_element_type = "N/A"

            max_strain_energy_position = "N/A"
            max_strain_energy_integration_point = "N/A"

            max_strain_energy_x = None
            max_strain_energy_y = None
            max_strain_energy_z = None


            # =================================================
            # FIND MAX STRAIN ENERGY
            # =================================================

            if strain_energy_field is not None:

                try:

                    strain_energy_field_ip = (
                        strain_energy_field.getSubset(
                            position=INTEGRATION_POINT
                        )
                    )

                except:

                    strain_energy_field_ip = (
                        strain_energy_field
                    )


                for value in strain_energy_field_ip.values:

                    # -----------------------------------------
                    # Ignore other instances
                    # -----------------------------------------

                    try:

                        if value.instance.name != instance_name:
                            continue

                    except:

                        continue


                    # -----------------------------------------
                    # Get energy value
                    # -----------------------------------------

                    try:

                        energy = value.data

                        # Some Abaqus field values can be
                        # returned as a tuple.
                        if isinstance(
                            energy,
                            tuple
                        ):

                            if len(energy) > 0:
                                energy = energy[0]
                            else:
                                continue

                    except:

                        continue


                    # -----------------------------------------
                    # Check maximum
                    # -----------------------------------------

                    if (
                        max_strain_energy is None
                        or
                        energy > max_strain_energy
                    ):

                        max_strain_energy = energy


                        # -------------------------------------
                        # Element label
                        # -------------------------------------

                        try:

                            element_label = (
                                value.elementLabel
                            )

                        except:

                            element_label = None


                        max_strain_energy_element = (
                            element_label
                        )


                        # -------------------------------------
                        # Element information
                        # -------------------------------------

                        if element_label is not None:

                            element = get_element(
                                instance,
                                element_label
                            )

                            if element is not None:

                                max_strain_energy_element_type = (
                                    get_element_type(
                                        element
                                    )
                                )

                                coordinates = (
                                    get_element_center(
                                        instance,
                                        element
                                    )
                                )

                                if coordinates is not None:

                                    max_strain_energy_x = (
                                        coordinates[0]
                                    )

                                    max_strain_energy_y = (
                                        coordinates[1]
                                    )

                                    max_strain_energy_z = (
                                        coordinates[2]
                                    )


                        # -------------------------------------
                        # Position
                        # -------------------------------------

                        max_strain_energy_position = (
                            get_value_position(value)
                        )

                        max_strain_energy_integration_point = (
                            get_integration_point(value)
                        )


            # =================================================
            # PRINT RESULTS
            # =================================================

            print("")

            if max_mises is not None:

                print(
                    "Maximum Mises stress: " +
                    str(max_mises)
                )

                print(
                    "Max Mises element: " +
                    str(max_mises_element)
                )

                print(
                    "Max Mises element type: " +
                    str(max_mises_element_type)
                )

                print(
                    "Max Mises integration point: " +
                    str(max_mises_integration_point)
                )

                print(
                    "Max Mises location: " +
                    str(max_mises_x) +
                    ", " +
                    str(max_mises_y) +
                    ", " +
                    str(max_mises_z)
                )

            else:

                print(
                    "Maximum Mises stress: N/A"
                )


            print("")

            if max_displacement is not None:

                print(
                    "Maximum displacement: " +
                    str(max_displacement)
                )

                print(
                    "Max displacement node: " +
                    str(max_displacement_node)
                )

                print(
                    "Max displacement location: " +
                    str(max_displacement_x) +
                    ", " +
                    str(max_displacement_y) +
                    ", " +
                    str(max_displacement_z)
                )

            else:

                print(
                    "Maximum displacement: N/A"
                )


            print("")

            if max_strain_energy is not None:

                print(
                    "Strain energy field: " +
                    strain_energy_field_name
                )

                print(
                    "Maximum strain energy: " +
                    str(max_strain_energy)
                )

                print(
                    "Max strain energy element: " +
                    str(max_strain_energy_element)
                )

                print(
                    "Max strain energy location: " +
                    str(max_strain_energy_x) +
                    ", " +
                    str(max_strain_energy_y) +
                    ", " +
                    str(max_strain_energy_z)
                )

            else:

                print(
                    "Spatial strain energy: N/A"
                )


            # =================================================
            # WRITE CSV ROW
            # =================================================

            writer.writerow([

                # ---------------------------------------------
                # ODB
                # ---------------------------------------------

                odb_filename,

                # ---------------------------------------------
                # STEP / FRAME
                # ---------------------------------------------

                step_name,
                frame_index,

                # ---------------------------------------------
                # INSTANCE
                # ---------------------------------------------

                instance_name,
                len(instance.elements),

                # ---------------------------------------------
                # MAX MISES
                # ---------------------------------------------

                max_mises,

                max_mises_element,
                max_mises_element_type,
                max_mises_position,
                max_mises_integration_point,

                max_mises_x,
                max_mises_y,
                max_mises_z,

                # ---------------------------------------------
                # MAX DISPLACEMENT
                # ---------------------------------------------

                max_displacement,

                max_displacement_node,

                max_displacement_x,
                max_displacement_y,
                max_displacement_z,

                # ---------------------------------------------
                # STRAIN ENERGY
                # ---------------------------------------------

                strain_energy_field_name,

                max_strain_energy,

                max_strain_energy_element,
                max_strain_energy_element_type,
                max_strain_energy_position,
                max_strain_energy_integration_point,

                max_strain_energy_x,
                max_strain_energy_y,
                max_strain_energy_z

            ])


        # ====================================================
        # CLOSE ODB
        # ====================================================

        odb.close()

        print("")
        print(
            "Finished: " +
            odb_filename
        )


# ============================================================
# FINISHED
# ============================================================

print("")
print("")
print("=" * 60)
print("ALL ODB FILES PROCESSED")
print("=" * 60)

print("")
print("CSV file created:")

print(CSV_PATH)

print("")
print("Done.")

# abaqus python "Path of this Python File/same as the folder your .odb file exists in"  
# run the line above in powershell. the ressults will be availabe in a .csv file that get's created in the folder. enjoy! S.S.