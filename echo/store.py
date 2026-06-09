import threading
from apps.core.services import worklist_scp, storage_scp

if __name__ == "__main__":
    t_wl = threading.Thread(target=worklist_scp.run_server, daemon=True, name='worklist')
    t_wl.start()
    storage_scp.run_server()
