import os
import sys

# Wrappers for async:
# Wrapper for setup_mysql_connection
import signal

import traceback
import additionals.logger

signal_dict = {
    signal.SIGHUP: "Hangup detected on controlling terminal or death of controlling process. Used to report that the user's terminal is disconnected and usually to terminate the program.",
    signal.SIGINT: "Interrupt from keyboard (usually Ctrl+C). Allows for graceful termination of the process.",
    signal.SIGQUIT: "Quit from keyboard (usually Ctrl+\\). Causes the process to terminate and dump core.",
    signal.SIGILL: "Illegal Instruction. Generally indicates a corrupted program or an attempt to execute data.",
    signal.SIGTRAP: "Trace/breakpoint trap. Used by debuggers.",
    signal.SIGABRT: "Abort signal from abort() system call. Indicates an abnormal termination.",
    signal.SIGBUS: "Bus error. Generally indicates a programming error that results in an unaligned memory access.",
    signal.SIGFPE: "Floating point exception. Indicates an erroneous arithmetic operation, such as division by zero.",
    signal.SIGKILL: "Kill signal. Forces the process to terminate immediately.",
    signal.SIGUSR1: "User-defined signal 1. Can be used for any purpose by the application.",
    signal.SIGSEGV: "Segmentation fault. Indicates an invalid access to storage, often a symptom of a programming bug.",
    signal.SIGUSR2: "User-defined signal 2. Can be used for any purpose by the application.",
    signal.SIGPIPE: "Broken pipe. Indicates an attempt to write to a pipe without a process connected to the other end.",
    signal.SIGALRM: "Timer signal from alarm(). Used for timeouts and alarms.",
    signal.SIGTERM: "Termination signal. Allows for graceful termination of the process, and can be handled or ignored.",
    signal.SIGCHLD: "Child stopped or terminated. Sent to a parent process whenever one of its child processes terminates or stops.",
    signal.SIGCONT: "Continue executing, if stopped. Sent to a process to make it continue after a stop.",
    signal.SIGSTOP: "Stop executing (cannot be caught or ignored). Used to stop a process for job control purposes.",
    signal.SIGTSTP: "Stop typed at terminal (usually Ctrl+Z). Used by the shell to implement job control.",
    signal.SIGTTIN: "Terminal input for background process. Sent to a background process attempting to read input from the terminal.",
    signal.SIGTTOU: "Terminal output for background process. Sent to a background process attempting to write output to the terminal.",
    signal.SIGURG: "Urgent condition on socket. Indicates out-of-band data received on a socket.",
    signal.SIGXCPU: "CPU time limit exceeded. Sent when a process exceeds its CPU time limit.",
    signal.SIGXFSZ: "File size limit exceeded. Sent when a process attempts to grow a file larger than the maximum allowed size.",
    signal.SIGVTALRM: "Virtual alarm clock. Delivered when a virtual timer expires.",
    signal.SIGPROF: "Profiling alarm clock. Delivered when a system’s profiling timer expires.",
    signal.SIGWINCH: "Window resize signal. Sent to a process when its controlling terminal changes its size.",
    signal.SIGIO: "I/O now possible. Indicates a file descriptor is ready for I/O.",
    signal.SIGPWR: "Power failure. Indicates the system experienced a power failure.",
    signal.SIGSYS: "Bad system call. Indicates a system call that is not valid.",
}


def write_log(message):
    print(message)
    loggerKill = additionals.funcs.setup_logger("Crash.log")
    loggerKill.error(message)


# old not so detailed
# def kill(signal_number, frame):
#     signal_name = signal.Signals(signal_number).name  # Retrieve the name of the signal
#     explanation = signal_dict.get(signal_number, "No description available")
#     file_name = frame.f_code.co_filename
#     line_number = frame.f_lineno
#     function_name = frame.f_code.co_name
#     write_log(f"Process terminated with signal {signal_name} ({signal_number}) - {explanation}, at {file_name} in function {function_name} on line {line_number} all frame "+str(frame))
#     sys.exit(5)


# Extra detail kill
def kill(signal_number, frame):
    signal_name = signal.Signals(signal_number).name
    explanation = signal_dict.get(signal_number, "No description available")
    stack_trace = "".join(traceback.format_stack(frame))
    write_log(
        f"Process terminated with signal {signal_name} ({signal_number}) - {explanation}. Current stack trace:\n{stack_trace}"
    )
    sys.exit(5)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Get the last traceback object and extract filename, line number and function name
    tb = traceback.extract_tb(exc_traceback)[-1]
    file_name = tb.filename
    line_number = tb.lineno
    function_name = tb.name

    write_log(
        f"Error Happened Process Killed {traceback.format_exception(exc_type, exc_value, exc_traceback)} from {file_name} in {function_name} on line {line_number}"
    )
    sys.exit(555)


# Register signal handlers
signal.signal(signal.SIGINT, kill)
signal.signal(signal.SIGTERM, kill)
signal.signal(signal.SIGQUIT, kill)

# Set up exception handling
sys.excepthook = handle_exception


def setup_mysql_connection(env_dict, logger):
    return additionals.mysql_functions.setup_mysql_connection(env_dict, logger)


async def async_setup_mysql_connection(env_dict, logger):
    return await asyncio.to_thread(setup_mysql_connection, env_dict, logger)


# Wrapper for execute_query
def execute_query(connection, query, logger):
    return additionals.mysql_functions.execute_query(connection, query, logger)


async def async_execute_query(connection, query, logger):
    return await asyncio.to_thread(execute_query, connection, query, logger)


# Wrapper for run_server_artifact
def run_server_artifact(artifact_name, logger):
    modules.Velociraptor.VelociraptorScript.run_server_artifact(artifact_name, logger)


async def async_run_server_artifact(artifact_name, logger):
    await asyncio.to_thread(run_server_artifact, artifact_name, logger)


def get_clients(logger):
    modules.Velociraptor.VelociraptorScript.get_clients(logger)


async def async_get_clients(logger):
    # Run the get_clients function asynchronously in a separate thread
    return await asyncio.to_thread(get_clients, logger)


# Wrapper for connect_timesketch_api
def connect_timesketch_api(config_json, logger):
    return modules.Velociraptor.AddToTimeSketch.connect_timesketch_api(
        config_json, logger
    )


async def async_connect_timesketch_api(config_json, logger):
    return await asyncio.to_thread(connect_timesketch_api, config_json, logger)


# Wrapper for collect_hunt_data
def collect_hunt_data(request, logger):
    return modules.Velociraptor.VelociraptorScript.collect_hunt_data(request, logger)


async def async_collect_hunt_data(request, logger):
    return await asyncio.to_thread(collect_hunt_data, request, logger)


# Wrapper for run_generic_vql
def run_generic_vql(query, logger):
    return modules.Velociraptor.VelociraptorScript.run_generic_vql(query, logger)


async def async_run_generic_vql(query, logger):
    return await asyncio.to_thread(run_generic_vql, query, logger)


# Wrapper for update_json
def update_json(connection, config_json, previous_config_date, flag, logger):
    additionals.funcs.update_json(
        connection, config_json, previous_config_date, flag, logger
    )


async def async_update_json(
    connection, config_json, previous_config_date, flag, logger
):
    await asyncio.to_thread(
        update_json, connection, config_json, previous_config_date, flag, logger
    )


# Wrapper for get_timeline_status
def get_timeline_status(timesketch_api, sketch_id, timeline_id, logger):
    return modules.Velociraptor.AddToTimeSketch.get_timeline_status(
        timesketch_api, sketch_id, timeline_id, logger
    )


async def async_get_timeline_status(timesketch_api, sketch_id, timeline_id, logger):
    return await asyncio.to_thread(
        get_timeline_status, timesketch_api, sketch_id, timeline_id, logger
    )


# Set the script directory and parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(script_dir, "../../"))
os.chdir(script_dir)

# Add parent directory to Python path
if script_dir not in sys.path:
    sys.path.append(script_dir)

print(f"Current working directory: {os.getcwd()}")
import logging
import json
import traceback
import time
import modules.Velociraptor.VelociraptorScript
import modules.Velociraptor.AddToTimeSketch
import modules.Dashboard.Dashboards
import modules.Nuclei.NucleiScript
import additionals.mysql_functions
import additionals.funcs
import threading
import pandas as pd
import random
import psutil
from datetime import datetime
import asyncio


def terminate_duplicate_scripts(script_name, logger):
    current_pid = os.getpid()
    found_duplicates = False

    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # Check if the process is a Python process
            if process.info["name"] in ["python", "python3"]:
                # Check if the process command line matches the script name and is not the current process
                if (
                    len(process.info["cmdline"]) > 1
                    and script_name == os.path.basename(process.info["cmdline"][1])
                    and process.info["pid"] != current_pid
                ):
                    logger.info(
                        f"Terminating duplicate script with PID: {process.info['pid']}"
                    )
                    process.terminate()
                    try:
                        process.wait(timeout=2)  # Wait for the process to terminate
                        logger.info(
                            f"Successfully terminated script with PID: {process.info['pid']}"
                        )
                    except psutil.TimeoutExpired:
                        logger.warning(
                            f"Process with PID: {process.info['pid']} did not terminate in time, killing it"
                        )
                        process.kill()
                    found_duplicates = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.error(
                f"Error terminating process with PID: {process.info['pid']}. Reason: {e}"
            )

    if found_duplicates:
        logger.info(
            f"Duplicate script(s) with name '{script_name}' were found and terminated."
        )
    else:
        logger.info(f"No duplicate scripts with name '{script_name}' were found.")


async def log_processes():
    # Set up the logger
    logger = additionals.funcs.setup_logger("resource_usage.log")
    logger.info("Logging resource usage!!")

    while True:
        try:
            # Log overall CPU and memory usage
            total_cpu_usage = psutil.cpu_percent(
                interval=1
            )  # Total CPU usage across all cores
            total_memory_usage = (
                psutil.virtual_memory().percent
            )  # Total memory usage percentage
            logger.info(f"Total CPU Usage: {total_cpu_usage}%")
            logger.info(f"Total Memory Usage: {total_memory_usage}%")

            logger.info("Getting processes!")
            # Get all running processes
            processes = []
            for proc in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "cpu_percent",
                    "memory_percent",
                    "username",
                    "status",
                    "create_time",
                ]
            ):
                try:
                    # Get additional process info
                    process_info = proc.info
                    process_info["create_time"] = datetime.fromtimestamp(
                        process_info["create_time"]
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    process_info["open_files"] = len(proc.open_files())
                    process_info["connections"] = len(proc.connections())
                    processes.append(process_info)
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    # Skip processes that are no longer running or access is denied
                    continue

            # Sort processes by memory usage, and by CPU usage in cases of similar memory usage
            processes = sorted(
                processes,
                key=lambda x: (x["memory_percent"], x["cpu_percent"]),
                reverse=True,
            )

            # Log process details
            logger.info(
                f"{'PID':>6} {'Process Name':<30} {'CPU %':>6} {'Memory %':>8} {'User':<15} {'Status':<10} {'Start Time':<20} {'Open Files':>10} {'Connections':>12}"
            )
            logger.info("-" * 120)
            for process in processes:
                logger.info(
                    f"{process['pid']:>6} {process['name']:<30} {process['cpu_percent']:>6.2f} {process['memory_percent']:>8.2f} "
                    f"{process['username']:<15} {process['status']:<10} {process['create_time']:<20} {process['open_files']:>10} {process['connections']:>12}"
                )

        except Exception as e:
            logger.error(f"Error while logging processes: {e}")

        # Wait for 5 minutes before running again
        await asyncio.sleep(5 * 60)


async def run_updates_daily(time_interval):
    logger = additionals.funcs.setup_logger("daily_update_interval.log")
    while True:
        try:
            env_dict = additionals.funcs.read_env_file(logger)
            connection = await async_setup_mysql_connection(env_dict, logger)

            config_data = json.loads(
                (
                    await async_execute_query(
                        connection, "SELECT config FROM configjson LIMIT 1", logger
                    )
                )[0][0]
            )
            time_to_sleep = (
                config_data.get("General", {})
                .get("IntervalConfigurations", {})
                .get("ModulesUpdates", {})
                .get("TimeIntervalInHours", 24)
            )
            artifact_list = (
                config_data.get("General", {})
                .get("IntervalConfigurations", {})
                .get("ModulesUpdates", {})
                .get("UpdateVelociraptorModules", [])
            )
            logger.info("Creating client_id/hostname json dict!")
            velociraptor_client_dict = (
                modules.Velociraptor.VelociraptorScript.get_clients(logger)
            )
            with open(
                os.path.join("response_folder", "velociraptor_clients.json"), "w"
            ) as f:
                json.dump(velociraptor_client_dict, f)
            logger.info("Modules Update Time To Sleep:" + str(time_to_sleep) + " hours")
            logger.info("Update modules:" + str(artifact_list))
            logger.info("Running daily task!")
            for artifact_name in artifact_list:
                await async_run_server_artifact(artifact_name, logger)
                await asyncio.sleep(2)

            connection.close()
        except Exception as e:
            logger.error(f"Failed in daily task!\nError Message: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        await asyncio.sleep(time_interval)


async def run_velociraptor_result_collection(time_interval, logger):
    logger.info("Start interval!")

    env_dict = additionals.funcs.read_env_file(logger)

    while True:
        try:
            logger.info("Start interval loop!")
            logger.info("Creating connection!")
            logger.info("Connecting MySQL!")
            connection = await async_setup_mysql_connection(env_dict, logger)
            config_json = json.loads(
                (
                    await async_execute_query(
                        connection, "SELECT config FROM configjson LIMIT 1", logger
                    )
                )[0][0]
            )
            previous_config_date = (
                await async_execute_query(
                    connection, "SELECT lastupdated FROM configjson LIMIT 1", logger
                )
            )[0][0]
            requests_object = config_json.get("RequestStatus", {})

            logger.info("Connecting TimeSketchAPI")
            timesketch_api = await async_connect_timesketch_api(config_json, logger)
            for request in requests_object:
                try:
                    if request["Status"] == "Hunting":
                        current_datetime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                        if (
                            additionals.funcs.calculate_seconds_difference(
                                current_datetime, request["LastIntervalDate"]
                            )
                            < 0
                        ):
                            if request["ModuleName"] == "Velociraptor":
                                if request["SubModuleName"] == "BestPractice":
                                    for module in request["Arguments"]["Modules"]:
                                        try:
                                            logger.info(
                                                "Module: "
                                                + str(module["SubModuleName"])
                                            )
                                            collection_data = (
                                                await async_collect_hunt_data(
                                                    module, logger
                                                )
                                            )
                                            if type(collection_data["table"]) != str:
                                                collection_data[
                                                    "table"
                                                ] = collection_data["table"].to_json(
                                                    orient="records",
                                                    lines=False,
                                                    indent=4,
                                                )
                                            additionals.funcs.write_json(
                                                collection_data, module["ResponsePath"]
                                            )
                                        except Exception as e:
                                            logger.error(
                                                "Module: "
                                                + str(module["SubModuleName"])
                                                + " didn't work!"
                                            )
                                            logger.error(
                                                f"Traceback:\n{traceback.format_exc()}"
                                            )
                                else:
                                    collection_data = await async_collect_hunt_data(
                                        request, logger
                                    )
                                    logger.info("Collection data: ")
                                    logger.info(str(collection_data))
                                    if collection_data["error"] != "No data collected.":
                                        logger.info("Creating macro table!")
                                        modules.Velociraptor.VelociraptorScript.create_modules_macro_json(
                                            request["SubModuleName"],
                                            collection_data["table"],
                                            request["ResponsePath"],
                                            logger,
                                        )
                                        collection_data["table"] = collection_data[
                                            "table"
                                        ].to_json(
                                            orient="records", lines=False, indent=4
                                        )
                                    additionals.funcs.write_json(
                                        collection_data, request["ResponsePath"]
                                    )
                            elif request["ModuleName"] == "TimeSketch":
                                logger.info("TimeSketch request: " + str(request))
                                try:
                                    if (
                                        await async_get_timeline_status(
                                            timesketch_api,
                                            request["UniqueID"]["SketchID"],
                                            request["UniqueID"]["TimelineID"],
                                            logger,
                                        )
                                        == "ready"
                                    ):
                                        logger.info("TimeSketch status is ready!")
                                        request["Status"] = "Complete"
                                except Exception as e:
                                    logger.error("Error in timesketch status:" + str(e))
                                    request["Status"] = "Failed"
                                    request["Error"] = (
                                        "There most likely an error in the timesketch run. check the main.log to see what happens.\n"
                                        + str(e)
                                    )
                            request["LastIntervalDate"] = current_datetime

                        if (
                            additionals.funcs.calculate_seconds_difference(
                                current_datetime, request["ExpireDate"]
                            )
                            < 0
                            and request["ModuleName"] != "TimeSketch"
                        ):
                            request["Status"] = "Complete"
                except Exception as e:
                    logger.error(f"Failed in inner loop!\nError Message: {str(e)}")
                    logger.error(f"Traceback:\n{traceback.format_exc()}")
            previous_config_date = previous_config_date.strftime("%d-%m-%Y-%H-%M-%S")
            await async_update_json(
                connection, config_json, previous_config_date, True, logger
            )
            logger.info("Finish interval!")
            connection.close()
        except Exception as e:
            logger.error(f"Failed in main loop!\nError Message: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        await asyncio.sleep(time_interval)


async def load_alerts_if_exists(logger):
    # Define the path to the JSON file
    file_path = os.path.join("response_folder", "alerts.json")

    # Ensure the file path is valid (e.g., no directory traversal attacks)
    file_path = os.path.abspath(file_path)

    # Check if the file exists and is accessible
    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} does not exist.")
        return None, 1

    try:
        # Ensure the file is readable and handle exceptions
        with open(file_path, "r") as file:
            existing_data = json.load(file)

            # Validate that existing_data is a list and contains elements
            if not isinstance(existing_data, list) or len(existing_data) == 0:
                logger.error("Invalid data format or empty list in JSON file.")
                return None, 1

            # Ensure the last element contains a '_ts' key
            last_entry = existing_data[0]
            if "_ts" not in last_entry:
                logger.error("Missing '_ts' key in the last entry of the JSON data.")
                return None, 1

            # Get the last _ts value and increment it
            last_ts = last_entry["_ts"]
            return existing_data, last_ts + 1
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {file_path}: {e}")
        return None, 1
    except Exception as e:
        logger.error(f"Unexpected error while loading alerts: {e}")
        return None, 1


async def sort_alerts(previous_collection_data, collection_data, logger):
    try:
        logger.info("Sorting alerts!")

        # Flatten the incoming collection_data if it contains nested lists
        combined_list = (
            [item for sublist in collection_data for item in sublist]
            if isinstance(collection_data[0], list)
            else collection_data
        )

        # Sort the combined list by the '_ts' timestamp key in descending order
        sorted_list = sorted(combined_list, key=lambda x: x["_ts"], reverse=True)

        # Get the last _ts value from the sorted list (largest _ts value in this case)
        last_ts = sorted_list[0]["_ts"] if sorted_list else None
        logger.info(str(last_ts) + " First Timestamp")
        # If there is previous collection data, merge it with the new sorted data
        if previous_collection_data:
            if isinstance(previous_collection_data, list):
                # Ensure the previous data is also not nested and merge both lists
                if isinstance(previous_collection_data[0], list):
                    previous_collection_data = [
                        item for sublist in previous_collection_data for item in sublist
                    ]

                sorted_list = (
                    sorted_list + previous_collection_data
                )  # Append new data to previous data
            else:
                logger.warning(
                    "Previous collection data is not a list. Overwriting with new data."
                )
        else:
            logger.info("No previous collection data found. Creating a new collection.")

        # Write the combined data back to the file
        # logger.info(str(sorted_list) + " First sorted_list sorted_list sorted_list sorted_list sorted_list sorted_list sorted_list sorted_list sorted_list sorted_listsorted_listsorted_listsorted_listsorted_listsorted_list")
        file_path = os.path.join("response_folder", "alerts.json")
        additionals.funcs.write_json(sorted_list, file_path)

        logger.info("Data saved successfully.")
        return sorted_list, last_ts

    except Exception as e:
        logger.error(f"An error occurred during processing: {e}")
        return None, None


async def run_velociraptor_alerts(time_interval):
    logger = additionals.funcs.setup_logger("alerts_interval.log")
    logger.info("Entered alerts function!")
    while True:
        try:
            logger.info("Start alerts loop!")
            env_dict = additionals.funcs.read_env_file(logger)
            connection = await async_setup_mysql_connection(env_dict, logger)
            logger.info("Loading config file!")
            config_data = json.loads(
                (
                    await async_execute_query(
                        connection, "SELECT config FROM configjson LIMIT 1", logger
                    )
                )[0][0]
            )
            logger.info("Loading clients dictionary!")
            clients_dict = modules.Velociraptor.VelociraptorScript.get_clients(logger)
            logger.info("Clients dictionary:" + str(clients_dict))
            previous_collection, previous_timestamp = await load_alerts_if_exists(
                logger
            )
            collection_data = []
            alerts_with_show_false = '","'.join([alert for alert, details in config_data["General"]["AlertDictionary"].items() if not details.get("Log", True)])

            for client_name, client_id in clients_dict.items():
                logger.info("Getting alerts from: " + str(client_name))
                query = f"""
        LET x <= get_client_monitoring().artifacts 
        SELECT * FROM foreach(row=x.artifacts,query={{
        SELECT _value AS Artifact, *
        FROM monitoring(artifact=_value, client_id="{client_id}") WHERE _ts > {previous_timestamp} 
        and not Artifact in ("AlonBerg.Best.Designer","{alerts_with_show_false}")
        ORDER BY _ts DESC 
        limit {config_data["General"]["IntervalConfigurations"]["AlertsConfiguration"]["AlertResultPerArtifactLimit"]}
        }})
        """
                logger.info("query query query queryqueryquery query query queryquery query query query query query query query query : " + query)
                response = await async_run_generic_vql(query, logger)
                logger.info("Has response, response length:" + str(len(response)))
                # Add the new structure
                for response_element in response:
                    # logger.info("Response element loop!")
                    response_element.update(
                        {
                            "AlertID": str(random.randint(1, 9999999999999)),
                            "ClientName": client_name,
                            "UserInput": {
                                "UserId": "",
                                "Status": "New",
                                "ChangedAt": "",
                            },
                        }
                    )
                logger.info("Adding response!")
                collection_data.append(response)
            logger.info("Alerts succeeded. Saving alerts.json file!")
            await sort_alerts(previous_collection, collection_data, logger)
            connection.close()
        except Exception as e:
            logger.error(f"Failed in daily task!\nError Message: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        await asyncio.sleep(time_interval)


async def main():
    logger = additionals.funcs.setup_logger("interval.log")
    # run_velociraptor_alerts()
    logger.info("Closing previous script if running!")
    time_to_sleep_for_all_modules = {}
    try:
        env_dict = additionals.funcs.read_env_file(logger)
        connection = await async_setup_mysql_connection(env_dict, logger)
        config_data = json.loads(
            (
                await async_execute_query(
                    connection, "SELECT config FROM configjson LIMIT 1", logger
                )
            )[0][0]
        )
        time_to_sleep_for_all_modules = (
            config_data.get("General", {})
            .get("IntervalConfigurations", {})
            .get("IntervalTimes", {})
        )

        # Convert each time value from minutes to seconds
        if time_to_sleep_for_all_modules == {}:
            logger.error("Fatal error no interval times found!")
            quit()
        for module, time_in_minutes in time_to_sleep_for_all_modules.items():
            time_to_sleep_for_all_modules[module] = time_in_minutes * 60
        # connection.close()

    except Exception as e:
        logger.error("That error killed the Interval!\n" + str(e))
        quit()
    while True:
        try:
            script_name = os.path.basename(__file__)  # Get the current script name
            terminate_duplicate_scripts(script_name, logger)

            await asyncio.gather(
                run_velociraptor_alerts(
                    time_to_sleep_for_all_modules["GetAlertsDataInMinutes"]
                ),
                run_velociraptor_result_collection(
                    time_to_sleep_for_all_modules["GetResultsDataInMinutes"], logger
                ),
                run_updates_daily(
                    time_to_sleep_for_all_modules["GetModulesUpdatesInMinutes"]
                ),
                modules.Dashboard.Dashboards.run_dashboard(
                    time_to_sleep_for_all_modules["GetDashboardsDataInMinutes"]
                ),
                log_processes(),
            )
        except Exception as e:
            logger.error("That error killed the Interval!\n" + str(e))
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())