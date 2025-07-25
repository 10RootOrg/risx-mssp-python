import os
import sys
import re

# Wrappers for async:
# Wrapper for setup_mysql_connection
import signal

import traceback
import additionals.logger
import additionals.elastic_api

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


def get_clients(logger, onlineFlag):
    modules.Velociraptor.VelociraptorScript.get_clients(logger, onlineFlag)


async def async_get_clients(logger, onlineFlag):
    # Run the get_clients function asynchronously in a separate thread
    return await asyncio.to_thread(get_clients, logger, onlineFlag)


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


# Wrapper for run_generic_vql
def get_online_clients(logger):
    return modules.Velociraptor.VelociraptorScript.get_online_clients(logger)


async def async_get_online_clients(logger):
    return await asyncio.to_thread(get_online_clients, logger)


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
from datetime import datetime, timedelta
import asyncio
import string


def timestamp_to_Elastic(timestamp):
    if timestamp > 4102444800:
        timestamp_seconds = timestamp / 1000
        microseconds = int(timestamp % 1000) * 1000
    else:
        timestamp_seconds = timestamp
        microseconds = 0

    dt = datetime.fromtimestamp(timestamp_seconds)
    dt = dt.replace(microsecond=microseconds)

    return dt.isoformat() + "Z"  # Add Z for UTC


def id_generator(size=15, chars=string.ascii_letters + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def adjust_datetime(date_string, seconds, logger, operation="subtract"):
    """Adjust the datetime by adding or subtracting a specified number of seconds.

    Args:
    date_string (str): The datetime string in ISO 8601 format ending with 'Z'.
    seconds (int): The number of seconds to adjust.
    operation (str): 'add' to add the seconds, 'subtract' to subtract the seconds.

    Returns:
    str: The adjusted datetime in ISO 8601 format ending with 'Z'.
    """
    try:
        # Prepare the date string by replacing 'Z' with '+00:00' and truncating fractional seconds to six places
        if "." in date_string:
            base, frac = date_string.replace("Z", "").split(".")
            frac = frac[:6]  # Keep only up to microseconds
            date_string = f"{base}.{frac}+00:00"
        else:
            date_string = date_string.replace("Z", "+00:00")

        # Convert the date string to a datetime object
        dt = datetime.fromisoformat(date_string)

        # Determine the operation to perform
        if operation == "add":
            new_dt = dt + timedelta(seconds=seconds)
        elif operation == "subtract":
            new_dt = dt - timedelta(seconds=seconds)
        else:
            logger.error(
                f"Invalid operation specified: {operation}. Use 'add' or 'subtract'."
            )
            raise ValueError(
                f"Invalid operation specified: {operation}. Use 'add' or 'subtract'."
            )

        # Convert back to the same string format with 'Z' to indicate UTC
        new_date_string = (
            new_dt.isoformat()[:26] + "Z"
        )  # Ensure to cut any excess if any
        return new_date_string

    except Exception as e:
        logger.error(f"Error adjusting datetime: {e}")
        raise  # Reraising the exception to notify callers of the function failure


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
    """
    Runs scheduled tasks in a continuous loop. This version uses asyncio.gather
    to run all artifact updates concurrently and correctly waits for them
    to complete before proceeding.
    """
    logger = additionals.funcs.setup_logger("daily_update_interval.log")
    
    while True:
        connection = None # Ensure connection is defined in the outer scope
        time_to_sleep_hours = 24 # Default sleep time
        sleep_seconds = int(time_to_sleep_hours) * 3600
        try:
            logger.info("Starting daily update cycle...")
            
            env_dict = additionals.funcs.read_env_file(logger)
            connection = await async_setup_mysql_connection(env_dict, logger)
            config_data_raw = await async_execute_query(
                connection, "SELECT config FROM configjson LIMIT 1", logger
            )
            config_data = json.loads(config_data_raw[0][0])
            modules_updates_config = config_data.get("General", {}).get("IntervalConfigurations", {}).get("ModulesUpdates", {})
            time_to_sleep_hours = modules_updates_config.get("TimeIntervalInHours", 24)
            artifact_list = modules_updates_config.get("UpdateVelociraptorModules", [])
        
            if not artifact_list:
                logger.info("No artifacts scheduled for update in this cycle.")
            else:
                logger.info(f"Starting {len(artifact_list)} artifact updates concurrently: {artifact_list}")

                # --- THIS IS THE FIX ---
                # 1. Prepare a list of all the tasks (coroutines) to run.
                tasks = [
                    async_run_server_artifact(artifact_name, logger)
                    for artifact_name in artifact_list
                ]

                # 2. asyncio.gather runs all tasks concurrently.
                # The 'await' here is crucial. It pauses this function
                # until ALL the background tasks in the list have completed.
                # This prevents the 'finally' block from running too early.
                if tasks:
                    await asyncio.gather(*tasks)
                
                logger.info("All artifact update tasks for this cycle have finished.")

        except Exception as e:
            logger.error(f"An error occurred in the daily update cycle: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            sleep_seconds = 360
        
        finally:
            # This block will now correctly run only AFTER all tasks are done.
            if connection:
                connection.close()
                logger.info("Database connection closed.")

        logger.info(f"Update cycle finished. Sleeping for {time_to_sleep_hours} hours.")
        
        await asyncio.sleep(sleep_seconds)


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


import re


def create_golang_regex(data):
    """
    Filters out entries where 'Filename' contains '$' and generates a Golang regex pattern
    matching all unique 'OSPath' values with proper escaping.

    :param data: List of dictionaries containing file metadata
    :return: Golang regex pattern string
    """
    # Use a set to store unique paths
    unique_os_paths = {
        entry["OSPath"]
        for entry in data
        if "$" not in entry["Filename"]
        and "ConsoleHost_history.txt" not in entry["Filename"]
    }

    # Correct escaping: replace single '\' with '\\\' and ensure correct regex structure
    regex_pattern = "|".join(
        re.escape(path).replace("\\\\", "\\\\\\\\") for path in unique_os_paths
    )

    return regex_pattern


# Function to format timestamps in seconds
def format_timestamp(timestamp):
    if timestamp:
        try:
            return datetime.strptime(
                timestamp.split(".")[0][:-1], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            return timestamp  # Return original if formatting fails
    return None


# Function to format timestamps in miliseconds
"""
def format_timestamp(timestamp):
    if timestamp:
        try:
            return datetime.strptime(timestamp.split('.')[0][:-1], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
        except ValueError:
            return timestamp  # Return original if formatting fails
    return None
"""


async def malware_func(
    config_data,
    response_element,
    uniqueListAlert,
    client_name,
    filteredResponse,
    fqdn,
    logger,
):
    try:
        logger.info("Entering malware_func")

        logger.info(
            f"response_element keys: {list(response_element.keys()) if isinstance(response_element, dict) else 'Not a dictionary'}"
        )
        logger.info(
            f"config_data keys: {list(config_data.keys()) if isinstance(config_data, dict) else 'Not a dictionary'}"
        )

        # Check if we've already processed this alert
        try:
            logger.info("About to access Filename and Timestamp")
            filename = response_element.get("Filename")
            timestamp = response_element.get("Timestamp")
            if filename is None or timestamp is None:
                logger.error(
                    f"Missing required keys in response_element - Filename: {filename is not None}, Timestamp: {timestamp is not None}"
                )
                return response_element

            alert_timestamp = timestamp.split(".")[0]
            alert_key = f"{filename}{alert_timestamp}"
            logger.info(f"Generated alert_key: {alert_key}")

            if alert_key not in uniqueListAlert:
                logger.info(f"Suspicious Alert detected: {response_element}")
                uniqueListAlert.append(alert_key)

                try:
                    # Get time range for the USN check based on when the suspicious file was detected
                    alert_time = timestamp
                    logger.info(f"Using alert_time: {alert_time}")

                    # Check config data structure
                    seconds_check_path = (
                        config_data.get("General", {})
                        .get("IntervalConfigurations", {})
                        .get("AlertsConfiguration", {})
                        .get("SuspiciousFileSecondsCheck")
                    )
                    logger.info(
                        f"SuspiciousFileSecondsCheck value: {seconds_check_path}"
                    )

                    if seconds_check_path is None:
                        logger.error("Missing SuspiciousFileSecondsCheck configuration")
                        return response_element

                    time_back = adjust_datetime(
                        alert_time, seconds_check_path, logger, "subtract"
                    )
                    time_ahead = adjust_datetime(
                        alert_time, seconds_check_path, logger, "add"
                    )

                    logger.info(
                        f"Time range calculated - back: {time_back}, ahead: {time_ahead}"
                    )

                    # Check for client_id
                    client_id = response_element.get("ClientId")
                    if not client_id:
                        logger.error("Missing ClientId in response_element")
                        return response_element

                    # Query to find all changed files during this time period using Windows.Forensics.Usn
                    usn_query = f"""  
                        LET collection <= collect_client(
                            client_id='{client_id}',
                            artifacts='Windows.Forensics.Usn', 
                            env=dict(DateAfter='{time_back}',DateBefore='{time_ahead}',FileNameRegex='.*(txt|csv)$'))
                        LET _ <= SELECT * FROM watch_monitoring(artifact='System.Flow.Completion')
                            WHERE FlowId = collection.flow_id
                            LIMIT 1
                        SELECT * FROM source(
                            client_id=collection.request.client_id,
                            flow_id=collection.flow_id,
                            artifact='Windows.Forensics.Usn')
                    """
                    # to add this to after test:
                    #
                    logger.info(
                        f"Running USN query to find changed text/CSV files: {usn_query}"
                    )

                    try:

                        usn_results = await async_run_generic_vql(usn_query, logger)
                        if len(usn_results) < 1:
                            logger.info("No csv/txt detected!")
                            response_element.update(
                                {
                                    "AlertID": id_generator(),
                                    "Client FQDN": fqdn,
                                    "UserInput": {
                                        "UserId": "",
                                        "Status": "New",
                                        "ChangedAt": "",
                                    },
                                }
                            )
                            filteredResponse.append(response_element)
                            return
                        logger.info(f"USN query returned {len(usn_results)} files.")
                        logger.info(f"USN values:" + str(usn_results))
                        path_regex = create_golang_regex(usn_results)
                        logger.info("Path regex:" + str(path_regex))
                        # For each text/CSV file found, check MFT fors timestamp discrepancies
                        if path_regex.strip() != "":
                            try:
                                # Query to check timestamp correlation using MFT
                                mft_query = f"""  
                                    LET collection <= collect_client(
                                        client_id='{client_id}',
                                        artifacts='Windows.NTFS.MFT', 
                                        env=dict(PathRegex='{path_regex}'))
                                    LET _ <= SELECT * FROM watch_monitoring(artifact='System.Flow.Completion')
                                        WHERE FlowId = collection.flow_id
                                        LIMIT 1
                                    SELECT OSPath,FileName,Created0x10,Created0x30,LastModified0x10,LastModified0x30,
                                            LastRecordChange0x10,LastRecordChange0x30,LastAccess0x10,LastAccess0x30 
                                    FROM source(
                                        client_id=collection.request.client_id,
                                        flow_id=collection.flow_id,
                                        artifact='Windows.NTFS.MFT')
                                """

                                try:
                                    mft_response = await async_run_generic_vql(
                                        mft_query, logger
                                    )
                                    # Check for timestamp discrepancies
                                    for file_entry in mft_response:
                                        try:
                                            logger.info(
                                                "File entry type:"
                                                + str(type(file_entry))
                                            )
                                            logger.info("file entry:" + str(file_entry))

                                            # Dictionary to store timestamp differences
                                            timestamp_diffs = {}

                                            # Check and format Created timestamps
                                            if file_entry.get(
                                                "Created0x10"
                                            ) != file_entry.get("Created0x30"):
                                                timestamp_diffs["Created ($FN)"] = (
                                                    format_timestamp(
                                                        file_entry.get("Created0x30")
                                                    )
                                                )
                                                timestamp_diffs["Created ($STD)"] = (
                                                    format_timestamp(
                                                        file_entry.get("Created0x10")
                                                    )
                                                )

                                            # Check and format LastModified timestamps
                                            if file_entry.get(
                                                "LastModified0x10"
                                            ) != file_entry.get("LastModified0x30"):
                                                timestamp_diffs[
                                                    "Last Modified ($FN)"
                                                ] = format_timestamp(
                                                    file_entry.get("LastModified0x30")
                                                )
                                                timestamp_diffs[
                                                    "Last Modified ($STD)"
                                                ] = format_timestamp(
                                                    file_entry.get("LastModified0x10")
                                                )

                                            # Check and format LastRecordChange timestamps
                                            if file_entry.get(
                                                "LastRecordChange0x10"
                                            ) != file_entry.get("LastRecordChange0x30"):
                                                timestamp_diffs[
                                                    "Last Record Change ($FN)"
                                                ] = format_timestamp(
                                                    file_entry.get(
                                                        "LastRecordChange0x30"
                                                    )
                                                )
                                                timestamp_diffs[
                                                    "Last Record Change ($STD)"
                                                ] = format_timestamp(
                                                    file_entry.get(
                                                        "LastRecordChange0x10"
                                                    )
                                                )

                                            # Check and format LastAccess timestamps
                                            if file_entry.get(
                                                "LastAccess0x10"
                                            ) != file_entry.get("LastAccess0x30"):
                                                timestamp_diffs["Last Access ($FN)"] = (
                                                    format_timestamp(
                                                        file_entry.get("LastAccess0x30")
                                                    )
                                                )
                                                timestamp_diffs[
                                                    "Last Access ($STD)"
                                                ] = format_timestamp(
                                                    file_entry.get("LastAccess0x10")
                                                )

                                            # If we found any timestamp discrepancies
                                            if timestamp_diffs:
                                                logger.info(
                                                    f"Timestamp discrepancy detected in file: {file_entry.get('OSPath', 'Unknown')}"
                                                )
                                                suspicious_file_path = file_entry.get(
                                                    "OSPath", "Unknown"
                                                )
                                                logger.info(
                                                    f"Found {len(suspicious_file_path)} files with timestamp discrepancies: {suspicious_file_path}"
                                                )
                                                try:
                                                    logger.info(
                                                        f"file_entry.get sanfloksdjgfpodsjfsxflksdf :{timestamp_diffs}  {file_entry.get('FileName', 'Unknown')} {response_element.get('_ts', 'Unknown')}"
                                                    )
                                                except Exception as e:
                                                    logger.error(
                                                        f"Error IN MID timestamp_diffs: {str(e)}"
                                                    )

                                                process = response_element.get(
                                                    "Filename", "Unknown"
                                                )  # .split("-")[0]
                                                tempObjTime = {
                                                    "AlertID": id_generator(),
                                                    "Artifact": "Python.Suspicious.File.Found",  # Not needed but fked up the UI
                                                    "_ts": response_element.get(
                                                        "_ts", "Unknown"
                                                    ),
                                                    "Process": process,
                                                    "Client FQDN": fqdn,
                                                    "Pf File Path": response_element.get(
                                                        "OSPath", "Unknown"
                                                    ),
                                                    f"Pf {'Create' if 'FILE_CREATE' in response_element.get('OSPath', 'Unknown') else 'Modified'} Time": response_element.get(
                                                        "Timestamp", "Unknown"
                                                    ),
                                                    "Suspicious File": suspicious_file_path,
                                                    "UserInput": {
                                                        "UserId": "",
                                                        "Status": "New",
                                                        "ChangedAt": "",
                                                    },
                                                }

                                                tempObjTime = {
                                                    **{
                                                        k: tempObjTime[k]
                                                        for k in tempObjTime
                                                        if k != "UserInput"
                                                    },  # Keep everything except "UserInput"
                                                    **timestamp_diffs,  # Insert timestamp_diffs values here
                                                    "UserInput": tempObjTime[
                                                        "UserInput"
                                                    ],  # Add "UserInput" at the end
                                                }

                                                """
                                                tempObjTime = {
                                                    "AlertID": id_generator(),
                                                    "_ts":response_element.get('_ts', 'Unknown'),
                                                    "Process":response_element.get('Filename', 'Unknown'),
                                                    "Artifact": "Python.Suspicious.File.Found",
                                                    "Client Name": client_name,
                                                    "Suspicious File": suspicious_file_path,
                                                    "UserInput": {
                                                        "UserId": "",
                                                        "Status": "New",
                                                        "ChangedAt": "",
                                                    }
                                                }
                                                """
                                                tempObjTime.update(timestamp_diffs)
                                                filteredResponse.append(tempObjTime)
                                            else:
                                                response_element.update(
                                                    {
                                                        "AlertID": id_generator(),
                                                        "Client FQDN": fqdn,
                                                        "UserInput": {
                                                            "UserId": "",
                                                            "Status": "New",
                                                            "ChangedAt": "",
                                                        },
                                                    }
                                                )
                                                filteredResponse.append(
                                                    response_element
                                                )
                                        except Exception as e:
                                            logger.error(
                                                f"Error checking timestamps for file entry: {str(e)}"
                                            )
                                except Exception as e:
                                    logger.error(f"Error in MFT query: {str(e)}")
                            except Exception as e:
                                logger.error(f"Error processing file data: {str(e)}")

                        # Remove the pf file if wanted
                        # temp bool for the removal
                        removePF = False
                        if removePF:
                            delete_file_query = f"""  
    LET delete_cmd = 'cmd /c del "{response_element.get('OSPath')}"'
    
    LET collection <= collect_client(
        client_id='{client_id}',
        artifacts='Artifact.Generic.OSCommand', 
        env=dict(Command=delete_cmd))
    
    LET _ <= SELECT * FROM watch_monitoring(artifact='System.Flow.Completion')
        WHERE FlowId = collection.flow_id
        LIMIT 1
    
    SELECT * FROM source(
        client_id=collection.request.client_id,
        flow_id=collection.flow_id,
        artifact='Artifact.Generic.OSCommand')
"""
                    except Exception as e:
                        logger.error(f"Error in USN query: {str(e)}")
                except Exception as e:
                    logger.error(f"Error calculating time range: {str(e)}")
            else:
                logger.info("This alert has already been processed")
        except Exception as e:
            logger.error(f"Error checking alert key: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Global error in malware_func: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())

    logger.info("Exiting malware_func")
    return response_element  # Return the potentially updated response_element


async def run_velociraptor_alerts(time_interval, elasticIP):
    logger = additionals.funcs.setup_logger("alerts_interval.log")
    path = "response_folder/alerts.json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)
            logger.info("Created empty alerts.json")
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
            logger.info("Creating client_id/hostname json dict!")
            velociraptor_client_dict = (
                modules.Velociraptor.VelociraptorScript.get_clients(logger, False)
            )
            with open(
                os.path.join("response_folder", "velociraptor_clients.json"), "w" 
            ) as f:
                json.dump(velociraptor_client_dict, f)
            logger.info("Loading clients dictionary!")
            clients_dict = modules.Velociraptor.VelociraptorScript.get_clients(
                logger, False
            )
            logger.info("Clients dictionary:" + str(clients_dict))
            previous_collection, previous_timestamp = await load_alerts_if_exists(
                logger
            )
            collection_data = []
            alerts_with_show_false = '","'.join(
                [
                    alert
                    for alert, details in config_data["General"][
                        "AlertDictionary"
                    ].items()
                    if not details.get("Log", True)
                ]
            )

            for client_name, client_id in clients_dict.items():
                logger.info("Getting alerts from: " + str(client_name))
                query = f"""
        LET x <= get_client_monitoring().artifacts 
        SELECT * FROM foreach(row=x.artifacts,query={{
        SELECT _value AS Artifact, *
        FROM monitoring(artifact=_value, client_id="{client_id}") WHERE _ts > {previous_timestamp} 
        and not Artifact in ("Example.Alert.To.Not.Run","{alerts_with_show_false}")
        ORDER BY _ts DESC 
        limit {config_data["General"]["IntervalConfigurations"]["AlertsConfiguration"]["AlertResultPerArtifactLimit"]}
        }})
        """
                response = await async_run_generic_vql(query, logger)
                logger.info("Has response, response length:" + str(len(response)))
                # Add the new structure
                uniqueListAlert = []
                filteredResponse = []

                for response_element in response:
                    logger.info(
                        "Has response,response_element:\n"
                        + str(
                            response_element["Artifact"]
                            == "Custom.Windows.Detection.Usn.malwareTest"
                            and not str(response_element["Filename"])
                            + str(response_element["Timestamp"])
                            in uniqueListAlert
                        )
                    )
                    clients = modules.Velociraptor.VelociraptorScript.get_clients(
                        logger, True
                    )
                    fqdn = clients[client_id][1]
                    if (
                        response_element["Artifact"]
                        == "Custom.Windows.Detection.Usn.malwareTest"
                    ):
                        # Remove the client id from the if
                        logger.info("Client id:" + client_id)
                        logger.info("Client name:" + client_name)
                        logger.info("Get into malware_function")
                        # online_clients = await async_get_online_clients(logger)

                        from datetime import datetime, timezone
                        import time

                        # Get current UTC time in seconds
                        current_utc_time = datetime.now(timezone.utc).timestamp()
                        threshold_seconds = 120  # in secs

                        logger.info(f"Current UTC Unix Time: {current_utc_time}")
                        logger.info(
                            f"Threshold (last seen after this time is online): {current_utc_time - threshold_seconds}"
                        )

                        # Debugging: Log timestamps before filtering
                        """
                        for cid, ts in clients.items():
                            converted_time = float(ts / 1e6)  # Convert microseconds to seconds
                            human_readable = datetime.fromtimestamp(converted_time, tz=timezone.utc).isoformat()

                            logger.info(f"Client: {cid} | Raw last_seen_at: {ts} | Converted: {converted_time} | Human Readable: {human_readable}")
                            logger.info(f"Comparison: {converted_time} >= {current_utc_time - threshold_seconds}")
                        """
                        # Apply online filter
                        online_clients = {
                            cid: datetime.fromtimestamp(
                                float(ts[0] / 1e6), tz=timezone.utc
                            ).isoformat()
                            for cid, ts in clients.items()
                            if float(ts[0] / 1e6)
                            >= (current_utc_time - threshold_seconds)
                        }

                        logger.info(
                            "\n=== Online Clients (Forced UTC, Corrected Microsecond Conversion) ==="
                        )
                        logger.info(online_clients)

                        if client_id in online_clients:
                            logger.info("Client is online keeping the progress!")

                            logger.info("current fqdn:" + str(fqdn))
                            response_element = await malware_func(
                                config_data,
                                response_element,
                                uniqueListAlert,
                                client_name,
                                filteredResponse,
                                fqdn,
                                logger,
                            )
                        else:
                            logger.info("Client is offline skipping to the next one!")
                        logger.info("Get out of malware_function")
                    else:
                        response_element.update(
                            {
                                "AlertID": id_generator(),
                                "Detection Time": timestamp_to_Elastic(
                                    response_element["_ts"]
                                ),
                                "Client FQDN": fqdn,
                                "UserInput": {
                                    "UserId": "",
                                    "Status": "New",
                                    "ChangedAt": "",
                                },
                            }
                        )
                        if response_element:
                            filteredResponse.append(response_element)
                logger.info("Adding response!")

                collection_data.append(filteredResponse)
                logger.info("Adding alerts to elastic!")
                for elastic_response in filteredResponse:
                    additionals.elastic_api.enter_data(
                        elastic_response, "mssp_alerts", elasticIP, logger
                    )

            logger.info("Alerts succeeded. Saving alerts.json file!")
            await sort_alerts(previous_collection, collection_data, logger)
            connection.close()
        except Exception as e:
            logger.error(f"Failed in daily task!\nError Message: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        await asyncio.sleep(time_interval)


async def main():
    logger = additionals.funcs.setup_logger("interval.log")
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
        logger.info(
            f"time_to_sleep_for_all_modules {str(time_to_sleep_for_all_modules)}"
        )
        elasticIP = config_data["ClientData"]["API"]["Elastic"]["Ip"]
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
                    time_to_sleep_for_all_modules["GetAlertsDataInMinutes"], elasticIP
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
