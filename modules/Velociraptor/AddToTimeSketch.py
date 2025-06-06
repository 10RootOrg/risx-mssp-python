import grpc
import json
from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc
import yaml
import time
import argparse
import os
import sys
import subprocess
import modules.Velociraptor.VelociraptorScript
from datetime import datetime, timedelta
import additionals.funcs
import requests
import traceback
import os
import ssl
import warnings
from timesketch_api_client import client
import urllib3


# Disable SSL warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Modify SSL context globally
ssl._create_default_https_context = ssl._create_unverified_context
def connect_timesketch_api(config, logger):
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Extract Timesketch credentials from the configuration
    try:
        logger.info("Connecting timesketch api")
        timesketch_config = config['ClientData']['API']['Timesketch']
        host_uri = f"https://{timesketch_config['IP']}"  # Ensure the URL is correctly formatted
        username = timesketch_config['Username']
        password = timesketch_config['Password']

        # Initialize the Timesketch API client with SSL verification disabled
        api = client.TimesketchApi(
            host_uri=host_uri,
            username=username,
            password=password,
            verify=False  # Disable SSL certificate verification
        )
        logger.info("TimeSketch api connected!")
        return api
    except Exception as e:
        logger.error(traceback.format_exc())
        return None

def is_plaso_running(logger):
    try:
        logger.info("In plaso_running function!")
        # Run the docker ps command
        result = subprocess.run(['sudo','docker', 'ps'], capture_output=True, text=True, check=True)
        logger.info("Twwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        # Check if log2timeline/plaso is in the output
        return 'log2timeline/plaso' in result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run docker ps command: {e.stderr}")
        return False

def run_kape_artifact(stub, client_id, kape_collection, timeout, cpu_limit,  logger):
    flow_id = ""
    artifact_name =  'Windows.KapeFiles.Targets'
    max_bytes = "9000000000000000"
    #query = f"LET collection <= collect_client(client_id='{client_id}', artifacts='Windows.KapeFiles.Targets', timeout=60000, env=dict(Device='C:', VSSAnalysis='Y', {kape_collection}='Y'))SELECT * FROM collection"
    query = f"LET collection <= collect_client(client_id='{client_id}', artifacts='Windows.KapeFiles.Targets', timeout={timeout}, cpu_limit={cpu_limit}, max_bytes={max_bytes}, env=dict(Device='C:', VSSAnalysis='Y', {kape_collection}='Y')) SELECT * FROM collection"

    logger.info("Running KAPE artifact query.")
    logger.info("Query:" + query)
    request = api_pb2.VQLCollectorArgs(
        max_wait=10,
        max_row=100,
        Query=[api_pb2.VQLRequest(
            Name=artifact_name,
            VQL=query,
        )]
    )
    for response in stub.Query(request):
        if response.Response:
            
            #print("Response:" + response.Response)
            logger.info("Response:" + str(response))
            response = json.loads(str(response.Response))
            flow_id = response[0]["flow_id"]

        #elif response.log:
            # Query execution logs are sent in their own messages.
            #print ("%s: %s" % (time.ctime(response.timestamp / 1000000), response.log))
    if(flow_id != ""):
        logger.info("Flow id:" + str(flow_id))
        return flow_id
    logger.error("Failed to run KAPE artifact.")
    return ""


def get_timeline_status(api, sketch_id, timeline_id, logger):
    try:
        # Fetch the sketch
        sketch = api.get_sketch(sketch_id)
        if not sketch:
            logger.error(f"Sketch with ID {sketch_id} not found.")
            return None

        # Fetch the timeline directly using its ID
        timeline = sketch.get_timeline(timeline_id)
        if timeline:
            logger.info(f"Found timeline. Status: {timeline.status}")
            return timeline.status
        else:
            logger.warning(f"Timeline with ID {timeline_id} not found in sketch {sketch_id}.")
            return None

    except Exception as e:
        logger.error(f"Error fetching timeline status: {str(e)}")
        return None

def get_flow_state(stub, client_id, flow_id, timeout, logger):
    query = f"LET collection <= get_flow(client_id='{client_id}', flow_id='{flow_id}') SELECT * FROM collection"
    request = api_pb2.VQLCollectorArgs(
        Query=[api_pb2.VQLRequest(VQL=query)],
    )

    all_rows = []  # Initialize an empty list to accumulate all rows
    try:
        timeout_seconds = timeout  # Timeout after 10 seconds
        for response in stub.Query(request, timeout=timeout_seconds):
            if response.Response:
                rows = json.loads(response.Response)
                if rows:
                    all_rows.extend(rows)  # Append the rows from this response to the list
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            logger.error("The call timed out.")
        else:
            logger.error(f"An RPC error occurred: {e}")

    # Extract the state from the response
    if all_rows:
        state = all_rows[0].get('state', 'UNKNOWN')
        return state

    return 'UNKNOWN'

def run_artifact_on_client(channel, client_id, kape_collection, timeout, cpu_limit, logger):
    logger.info("Running artifact on client!")
    flow_id = ""
    # Here, you would add the logic to perform some action on the client
    # For example, querying data, sending commands, etc.

    stub = api_pb2_grpc.APIStub(channel)
    flow_id = run_kape_artifact(stub, client_id, kape_collection, timeout, cpu_limit, logger)
    if(flow_id == ""):
        logger.error("Failed to run kape artifact!")
        return
    start_time = time.time()
    #timeout = 9999999999  # Run loop for 30 seconds
    state = ""
    while True:
        state = get_flow_state(stub, client_id, flow_id, timeout, logger)
        if state == "FINISHED":
            logger.info("Artifact is done!")
            return flow_id
        if state == "FAILED":
            logger.error("The flow has been failed!")
            return

        # Check if 30 seconds have passed
        if time.time() - start_time > timeout:
            logger.warning("Timeout reached. Exiting the loop.")
            break
    return

def get_command2(config, api, row, host_name, user_name, client_name, logger):
    formatted_datetime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    #formatted_datetime = datetime.now().strftime("%Y-%d-%m_%H:%M")
    username = config['ClientData']['API']['Timesketch']['Username']
    password = config['ClientData']['API']['Timesketch']['Password']
    formatted_future_datetime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    timeline_name =  client_name + "_" + formatted_datetime
    sketch_name = row["Arguments"]["SketchName"]

    sketch_id = get_sketch_id(api, sketch_name, logger)
    row["LastIntervalDate"] = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    row["ExpireDate"] = formatted_future_datetime
    logger.info("Checking if sketch exists or not [Need timesketch importer connection!]")
    ip = config['ClientData']['API']['Timesketch']["IP"]
    timesketch_importer_path = ""
    PathToPlaso = ""
    # When the shell is inside a container the user name will always be node else its dev version
    if(user_name == "node"):
        timesketch_importer_path = f"/usr/local/bin/timesketch_importer"
        PathToPlaso = f"/plaso/{client_name}Artifacts.plaso"
    else:
        timesketch_importer_path = f"/home/{user_name}/.local/bin/timesketch_importer"
        PathToPlaso = f"/home/tenroot/setup_platform/workdir/risx-mssp/backend/plaso/{client_name}Artifacts.plaso"

    # Add a check for sketch_id and construct command
    if sketch_id is not None:
        logger.info(f"Sketch with the same name found. Sketchid: {sketch_id}")
        row["UniqueID"] = {"SketchID": sketch_id, "TimelineID": timeline_name}
        return row, f"{timesketch_importer_path} -u {username} -p {password} --host http://{ip}:5666 --timeline_name {timeline_name} --sketch_id {sketch_id} {PathToPlaso} --quick"
    else:
        logger.info(f"Sketch with the same name not found. Creating new Sketch: {sketch_name}")
        row["UniqueID"] = {"SketchID": sketch_name, "TimelineID": timeline_name}
        return row, f"{timesketch_importer_path} -u {username} -p {password} --host http://{ip}:5666 --timeline_name {timeline_name} --sketch_name {sketch_name} {PathToPlaso} --quick"


def get_sketch_id(api, sketch_name, logger):
    # Get the list of sketches and search for the given sketch name
    logger.info("Getting list of sketches!")
    sketches = api.list_sketches()
    logger.info("List of sketches:" + str(sketches))
    for sketch in sketches:
        if sketch.name == sketch_name:
            return sketch.id
    return None

def get_timeline_id(api, sketch_id, timeline_name, logger):
    try:
        # Get the sketch
        logger.info(f"Fetching sketch with ID: {sketch_id}")
        sketch = api.get_sketch(sketch_id)
        # Test make it public
        #sketch.grant_permission(permission='read', user='public')
        logger.info(f"Sketch Name [Check if its not empty]: {sketch.name}")
        logger.info(f"Sketch Labels: {sketch.labels}")
        if not sketch:
            logger.error(f"Sketch with ID {sketch_id} not found.")
            return None

        # Get the list of timelines for the given sketch
        logger.info(f"Getting list of timelines for sketch ID: {sketch_id}")
        timelines = sketch.list_timelines()
        logger.info("Pre timelines loop!")
        for timeline in timelines:
            logger.info("Timeline loop:" + str(timeline.id))
            if timeline.name == timeline_name:
                logger.info(f"Found timeline '{timeline_name}' with ID: {timeline.id}")
                return timeline.id

        logger.warning(f"Timeline '{timeline_name}' not found in sketch ID: {sketch_id}")
        return None

    except AttributeError as e:
        logger.error(f"API method error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def make_sketches_public(api, logger):
    sketches = list(api.list_sketches())
            
    if sketches:   
        total_sketches = len(sketches)
        logger.info(f"Found {total_sketches} sketches")
        
        for sketch in sketches:
            logger.info(f"Making sketch '{sketch.name}' (ID: {sketch.id}) public")
            # First attempt - use set_acl if available (newer API)
            sketch.set_acl(user_list=[], group_list=[], make_public=True)
def start_timesketch(row, general_config, logger):
    # Here, based on the parsed arguments, you can call different functions
    # For example:
    try:
        logger.info("WhoAmI:" + str(subprocess.run(['whoami'], stdout=subprocess.PIPE, text=True).stdout.strip()))
        if(is_plaso_running(logger)):
            logger.error("Timesketch plaso is already running. Let it finish and run again later")
            row["Status"] = "Failed"
            row["Error"] = "Timesketch plaso is already running. Let it finish and run again later"
            return row
    
        logger.info("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
        config_path = os.path.join("modules", "Velociraptor", "dependencies", "api.config.yaml")
        velociraptor_config = ""
        with open(config_path, 'r') as f:
            velociraptor_config = yaml.safe_load(f)

        creds = grpc.ssl_channel_credentials(
        root_certificates=velociraptor_config["ca_certificate"].encode("utf8"),
        private_key=velociraptor_config["client_private_key"].encode("utf8"),
        certificate_chain=velociraptor_config["client_cert"].encode("utf8"))
        options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

        # Establish a secure channel
        with grpc.secure_channel(velociraptor_config["api_connection_string"], creds, options) as channel:
            host_client_id_dict = modules.Velociraptor.VelociraptorScript.get_clients(logger, False)
            logger.info("Current host_client_id_dict:" + str(host_client_id_dict))
            logger.info("Running artifact")
            logger.info("TimeSketchPopulation:" + str(row["Population"]))
            for client in row["Population"]:
                try:
                    client_name = client["asset_string"]
                    if(client_name in host_client_id_dict):
                        logger.info("Client name:" + client_name)
                        client_id = host_client_id_dict[client_name]
                        logger.info(f"Timeout is {row['ArtifactTimeOutInMinutes']} seconds!")
                        logger.info(f"Kape CPU limit: 50")
                        cpu_limit = 50
                        # Return after loading file
                        flow_id = run_artifact_on_client(channel=channel, client_id=client_id, kape_collection=row["Arguments"]["KapeCollection"], timeout = int(row["ArtifactTimeOutInMinutes"]), cpu_limit = cpu_limit, logger=logger)
                        logger.info(f"flowid: {flow_id}")
                        # Get the username
                        user_name = subprocess.run(['whoami'], stdout=subprocess.PIPE, text=True).stdout.strip()
                        # user_name="tenroot"

                        

                        # Get the hostname
                        host_name = subprocess.run(['uname', '-n'], stdout=subprocess.PIPE, text=True).stdout.strip()
                        
                        # collect_path = os.path.join("home", user_name, "setup_platform", "workdir", "velociraptor", "velociraptor", "clients", client_id, "collections", flow_id, "uploads")
                        # logger.info(f"Collect path: {collect_path}")
                        cpus = additionals.funcs.closest_cpu_percentage(int(row['Arguments']['CPUThrottling']))
                        ram = additionals.funcs.closest_memory_percentage(int(row['Arguments']['MemoryThrottling'])) + "g"
                        logger.info("Number of CPUs:" + cpus)
                        logger.info("Number of Memory:" + ram)
 
                        command1 = f"sudo docker run -v /home/tenroot/setup_platform/workdir/risx-mssp/backend/plaso/:/data -v /home/tenroot/setup_platform/workdir/velociraptor/velociraptor:/velociraptor --cpus='{cpus}' --memory='{ram}' log2timeline/plaso log2timeline --workers {cpus} --status_view window --status_view_interval 60 --storage-file /data/{client_name}Artifacts.plaso /velociraptor/clients/{client_id}/collections/{flow_id}/uploads"
                        api = connect_timesketch_api(general_config, logger)
                        #Check if there existing sketch or not
                        row, command2 = get_command2(general_config, api, row, host_name, user_name, client_name, logger)
                        logger.info("Removing previous artifacts.plaso")
                        # Return after loading file
                        # additionals.funcs.run_subprocess(f"sudo docker run --rm -v /home/tenroot/setup_platform/workdir/risx-mssp/backend/plaso/:/data alpine sh -c 'rm -f /data/{client_name}Artifacts.plaso'", "", logger)
                        # additionals.funcs.run_subprocess(f"sudo docker run --rm -v /home/tenroot/setup_platform/workdir/risx-mssp/backend/plaso/:/data/ alpine sh -c 'rm -f /data/.timesketchrc'", "", logger)
                        # additionals.funcs.run_subprocess(f"sudo docker run --rm -v /home/tenroot/setup_platform/workdir/risx-mssp/backend/plaso/:/data/ alpine sh -c 'rm -f /data/.timesketch.token'", "", logger)
                        additionals.funcs.run_subprocess(f"sudo rm -f /home/node/.timesketch.token", "", logger)
                        additionals.funcs.run_subprocess(f"sudo rm -f /home/node/.timesketchrc", "", logger)
                        additionals.funcs.run_subprocess(f"sudo rm -f /data/{client_name}Artifacts.plaso", "", logger)
                        logger.info("Running plaso!")
                        # Return after loading file
                        additionals.funcs.run_subprocess(command1,"Processing completed", logger)
                        #Wait for plaso
                        logger.info("Waiting for plaso to finish!")
                        #while is_plaso_running(logger):
                         #   logger.info("log2timeline/plaso is still running. Checking again in 15 seconds...")
                          #  time.sleep(15)
                        # Run the second command
                        logger.info("Running timesketech importer!")
                        additionals.funcs.run_subprocess(command2, "", logger)

                        #additionals.funcs.run_subprocess(f"docker run --rm -v /home/{user_name}/:/data alpine sh -c 'rm -f /data/{client_name}Artifacts.plaso'", "", logger)
                        # time.sleep(120)
                        time.sleep(30)
                        logger.info("SketchID:" + str(row["UniqueID"]["SketchID"]))
                        logger.info("SketchName:" + str(row["Arguments"]["SketchName"]))
                        logger.info("TimeLine ID:" + row["UniqueID"]["TimelineID"])
                        if(row["UniqueID"]["SketchID"] == row["Arguments"]["SketchName"]):
                            row["UniqueID"]["SketchID"] = get_sketch_id(api, row["Arguments"]["SketchName"], logger)
                        row["UniqueID"]["TimelineID"] = get_timeline_id(api, row["UniqueID"]["SketchID"], row["UniqueID"]["TimelineID"], logger)
                        logger.info(row["UniqueID"]["TimelineID"])
                        #make_sketches_public(api, logger)
                        api.session.close()
                except Exception as e:
                    logger.error("Mid run timesketch error:" + str(e))
                    logger.error(traceback.format_exc())
                    #make_sketches_public(api, logger)
                    api.session.close()

            #row["Status"] = "Hunting"
            row["Status"] = "Complete"
            logger.info("Removing plaso containers!")
            additionals.funcs.run_subprocess('sudo docker ps -a -q --filter "ancestor=log2timeline/plaso" | sudo xargs -r docker rm -f',"", logger)
            return row
    except Exception as e:
        logger.error("TimeSketch unknown error:" + str(e))
        row["Status"] = "Failed"
        row["Error"] = "Unknown error:" + str(e)
        logger.info("Removing plaso containers!")
        additionals.funcs.run_subprocess('sudo docker ps -a -q --filter "ancestor=log2timeline/plaso" | sudo xargs -r docker rm -f',"", logger)
        return row


def start_kape_collection(row, general_config, logger):
    # Here, based on the parsed arguments, you can call different functions
    try:
        logger.info("WhoAmI:" + str(subprocess.run(['whoami'], stdout=subprocess.PIPE, text=True).stdout.strip()))
        if(is_plaso_running(logger)):
            logger.error("Kape collection is already running. Let it finish and run again later")
            row["Status"] = "Failed"
            row["Error"] = "Kape collection is already running. Let it finish and run again later"
            return row
    
        logger.info("Twwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        logger.info("Starting Kape collection for multiple clients")
        config_path = os.path.join("modules", "Velociraptor", "dependencies", "api.config.yaml")
        velociraptor_config = ""
        with open(config_path, 'r') as f:
            velociraptor_config = yaml.safe_load(f)

        creds = grpc.ssl_channel_credentials(
        root_certificates=velociraptor_config["ca_certificate"].encode("utf8"),
        private_key=velociraptor_config["client_private_key"].encode("utf8"),
        certificate_chain=velociraptor_config["client_cert"].encode("utf8"))
        options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

        # Establish a secure channel
        with grpc.secure_channel(velociraptor_config["api_connection_string"], creds, options) as channel:
            host_client_id_dict = modules.Velociraptor.VelociraptorScript.get_clients(logger, False)
            logger.info("Current host_client_id_dict:" + str(host_client_id_dict))
            logger.info("Running artifact")
            logger.info("KapePopulation:" + str(row["Population"]))
            
            # Start running on all clients concurrently
            collection_results = []
            client_flows = []
            
            # First launch all the artifacts in parallel
            for client in row["Population"]:
                try:
                    client_name = client["asset_string"]
                    if(client_name in host_client_id_dict):
                        logger.info("Client name:" + client_name)
                        client_id = host_client_id_dict[client_name]
                        logger.info(f"Timeout is {row['ArtifactTimeOutInMinutes']} minutes!")
                        logger.info(f"Kape CPU limit: 50")
                        cpu_limit = 50
                        
                        # Launch the artifact collection but don't wait for completion
                        # Just get the flow ID
                        stub = api_pb2_grpc.APIStub(channel)
                        flow_id = run_kape_artifact(stub, client_id, row["Arguments"]["KapeCollection"], 
                                           int(row["ArtifactTimeOutInMinutes"]), cpu_limit, logger)
                        
                        if flow_id:
                            logger.info(f"Started flow for {client_name} with flowid: {flow_id}")
                            
                            # Track this client and flow
                            client_flows.append({
                                "client_name": client_name,
                                "client_id": client_id,
                                "flow_id": flow_id,
                                "stub": stub,
                                "status": "running"
                            })
                        else:
                            logger.error(f"Failed to start artifact for {client_name}")
                            collection_results.append({
                                "client_name": client_name,
                                "status": "error",
                                "message": "Failed to start artifact collection"
                            })
                except Exception as e:
                    logger.error(f"Error starting Kape collection for client {client_name}: {str(e)}")
                    logger.error(traceback.format_exc())
                    collection_results.append({
                        "client_name": client_name,
                        "status": "error",
                        "message": f"Error: {str(e)}"
                    })
            
            # Now wait for all the flows to complete - this is the monitoring phase
            logger.info("All artifact collections started, now monitoring completion...")
            
            # Use the same start_time for all flows to enforce a global timeout
            start_time = time.time()
            global_timeout = int(row["ArtifactTimeOutInMinutes"]) * 60  # Convert minutes to seconds
            
            # Track which clients still need monitoring
            pending_clients = list(client_flows)
            
            # Loop until all clients are done or timeout is reached
            while pending_clients and (time.time() - start_time < global_timeout):
                # Process each pending client
                still_pending = []
                
                for client_flow in pending_clients:
                    try:
                        # Check flow state using the existing get_flow_state function
                        state = get_flow_state(
                            client_flow["stub"], 
                            client_flow["client_id"], 
                            client_flow["flow_id"], 
                            global_timeout,
                            logger
                        )
                        
                        if state == "FINISHED":
                            logger.info(f"Artifact for {client_flow['client_name']} completed successfully")
                            collection_results.append({
                                "client_name": client_flow["client_name"],
                                "status": "complete",
                                "flow_id": client_flow["flow_id"],
                                "message": "Collection successful"
                            })
                            client_flow["status"] = "complete"
                            # Don't add to still_pending
                        elif state == "FAILED" or state == "ERROR":
                            logger.error(f"Artifact for {client_flow['client_name']} failed")
                            collection_results.append({
                                "client_name": client_flow["client_name"],
                                "status": "error",
                                "flow_id": client_flow["flow_id"],
                                "message": f"Collection failed with state: {state}"
                            })
                            client_flow["status"] = "error"
                            # Don't add to still_pending
                        else:
                            # Still running or unknown state, keep monitoring
                            logger.info(f"Artifact for {client_flow['client_name']} is still running (state: {state})")
                            still_pending.append(client_flow)
                    except Exception as e:
                        logger.error(f"Error checking status for {client_flow['client_name']}: {str(e)}")
                        # Keep checking on error
                        still_pending.append(client_flow)
                
                # Update pending clients
                pending_clients = still_pending
                
                # If we still have pending clients, wait before checking again
                if pending_clients:
                    logger.info(f"Waiting for {len(pending_clients)} clients to complete. Checking again in 30 seconds...")
                    time.sleep(30)
            
            # Handle any clients that are still pending after the loop exits
            for client_flow in pending_clients:
                logger.warning(f"Artifact collection for {client_flow['client_name']} did not complete within the timeout")
                collection_results.append({
                    "client_name": client_flow["client_name"],
                    "status": "timeout",
                    "flow_id": client_flow["flow_id"],
                    "message": "Collection timed out"
                })
            
            # Update row with results
            row["KapeResults"] = collection_results
            success_count = sum(1 for result in collection_results if result["status"] == "complete")
            error_count = len(collection_results) - success_count
            
            if error_count > 0:
                row["Status"] = "Partial Success" if success_count > 0 else "Failed"
                row["Error"] = f"{error_count} client(s) failed or timed out during collection"
            else:
                row["Status"] = "Complete"
            
            return row
    except Exception as e:
        logger.error("Kape collection unknown error:" + str(e))
        logger.error(traceback.format_exc())
        row["Status"] = "Failed"
        row["Error"] = "Unknown error:" + str(e)
        return row