from datetime import datetime
from logger import logger
from bronze import bronze_process
from silver import silver_process

# PIPELINE MAIN FUNCTION ====================================


def main():

    # ==============================
    # LOGGER
    # ==============================
    logger.info(
        "==========PROCESS: Pipeline start | STATUS: Success==========")
    start_datetime = datetime.now()

    # ==============================
    # PIPELINE ORCHESTRATOR
    # ==============================
    bronze_process()
    silver_process()

    # ==============================
    # CALCULATE TIME
    # ==============================
    end_datetime = datetime.now()
    duration = (end_datetime - start_datetime).total_seconds()

    # ==============================
    # LOGGER
    # ==============================
    logger.info(
        f"==========Start time: {start_datetime} | End time: {end_datetime} | Duration: {duration}==========")
    logger.info(
        "==========PROCESS: Pipeline Completion | STATUS: COMPLETED==========")


if __name__ == "__main__":
    main()
