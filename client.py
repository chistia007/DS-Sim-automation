#!/usr/bin/env python3
import socket
import sys
import time

HOST, PORT, USER = "127.0.0.1", 50000, "chist"

def send(sock, msg):
    sock.sendall(msg.encode("ascii"))

def recv_response(sock, timeout=2):
    sock.settimeout(timeout)
    try:
        data = sock.recv(8192)
        decoded = data.decode("ascii", errors="ignore").strip()
        return decoded
    except socket.timeout:
        return ""
    except Exception as e:
        return ""

def wait_for_response(sock, expected=None, timeout=2):
    response = recv_response(sock, timeout)
    return response

def get_best_server(servers_response, job_cores, job_memory, job_disk):
    best_server = None
    best_score = float('inf')
    lines = servers_response.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('.'):
            parts = line.split()
            if len(parts) >= 8:
                server_type, server_id, state = parts[0], parts[1], parts[2]
                cores, memory, disk = int(parts[4]), int(parts[5]), int(parts[6])
                waiting_jobs = int(parts[7])

                if cores >= job_cores and memory >= job_memory and disk >= job_disk:
                    resource_waste = (cores - job_cores) + (memory - job_memory) / 1000 + (disk - job_disk) / 1000
                    wait_penalty = waiting_jobs * 100
                    state_penalty = 0
                    if state == "inactive":
                        state_penalty = 50
                    elif state == "booting":
                        state_penalty = 20
                    immediate_bonus = 0
                    if waiting_jobs == 0 and state in ["idle", "active"]:
                        immediate_bonus = -100

                    total_score = resource_waste + wait_penalty + state_penalty + immediate_bonus
                    if total_score < best_score:
                        best_score = total_score
                        best_server = (server_type, server_id)
    return best_server

def main():
    try:
        sock = socket.create_connection((HOST, PORT), timeout=00.5)
    except Exception as e:
        return

    try:
        send(sock, "HELO")
        response = wait_for_response(sock, "OK", 3)
        if response != "OK":
            return

        send(sock, f"AUTH {USER}")
        response = wait_for_response(sock, "OK", 3)
        if response != "OK":
            return

        job_count = 0

        # Main scheduling loop
        while True:
            time.sleep(0.0002)
            send(sock, "REDY")
            response = wait_for_response(sock, timeout=3)

            if not response:
                break

            if response == "NONE":
                send(sock, "QUIT")
                _ = wait_for_response(sock, timeout=3)  
                break

            if response.startswith("JOBN") or response.startswith("JOBP"):
                job_count += 1
                parts = response.split()
                if len(parts) >= 7:
                    job_id, cores, memory, disk = parts[1], parts[3], parts[4], parts[5]

                    send(sock, f"GETS Capable {cores} {memory} {disk}")

                    data_response = wait_for_response(sock, timeout=3)
                    if data_response and data_response.startswith("DATA"):
                        try:
                            n = int(data_response.split()[1])
                        except Exception:
                            n = 0

                        # 1. First OK to receive server list
                        send(sock, "OK")

                        # 2. Read exactly n server lines (responses may come chunked or bundled)
                        server_lines = []
                        while len(server_lines) < n:
                            chunk = wait_for_response(sock, timeout=3)
                            if not chunk:
                                break
                            for ln in chunk.split('\n'):
                                s = ln.strip()
                                if s:
                                    server_lines.append(s)
                                    if len(server_lines) == n:
                                        break

                        servers_response = "\n".join(server_lines[:n])

                        # 3) Second OK to acknowledge receipt of n lines
                        send(sock, "OK")

                        # 4) Read until we see a standalone dot line "."
                        #    (chunk may include multiple lines; look for a line equal to ".")
                        got_dot = False
                        while not got_dot:
                            dot_chunk = wait_for_response(sock, timeout=3)
                            if not dot_chunk:
                                break
                            for ln in dot_chunk.split('\n'):
                                if ln.strip() == ".":
                                    got_dot = True
                                    break

                        best_server = get_best_server(servers_response, int(cores), int(memory), int(disk))

                        if best_server:
                            server_type, server_id = best_server
                            send(sock, f"SCHD {job_id} {server_type} {server_id}")
                            # time.sleep(0.001)
                            schd_response = wait_for_response(sock, timeout=3)
                        else:
                            if servers_response:
                                lines = servers_response.split('\n')
                                for line in lines:
                                    if line.strip() and not line.startswith('.'):
                                        server_parts = line.split()
                                        if len(server_parts) >= 2:
                                            server_type, server_id = server_parts[0], server_parts[1]
                                            send(sock, f"SCHD {job_id} {server_type} {server_id}")
                                            schd_response = wait_for_response(sock, timeout=3)
                                            break

            elif response.startswith("CHKQ"):
                send(sock, "OK")
                wait_for_response(sock, timeout=2)
                send(sock, "QUIT")
        wait_for_response(sock, timeout=3)

    except Exception as e:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    main()
