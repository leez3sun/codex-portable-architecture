import os
import sys

import ansys.fluent.core as pyfluent


def launch(mode):
    session = pyfluent.launch_fluent(
        product_version=os.environ.get("ANSYS_VERSION", "24.1.0"),
        mode=mode,
        precision="double",
        processor_count=2,
        show_gui=False,
        start_timeout=120,
        start_watchdog=False,
    )
    try:
        if mode == "solver":
            value = session.scheme_eval.string_eval("(+ 1 2)")
            print("SOLVER_RPC_OK", value)
        else:
            session.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
            task = session.workflow.TaskObject["Import Geometry"]
            print("MESHING_WORKFLOW_OK", type(task).__name__)
    finally:
        session.exit()


if __name__ == "__main__":
    requested_mode = sys.argv[1] if len(sys.argv) > 1 else "solver"
    if requested_mode not in ("solver", "meshing"):
        raise SystemExit("mode must be solver or meshing")
    print("PYFLUENT_VERSION", pyfluent.__version__)
    launch(requested_mode)
    print("PROBE_OK")
