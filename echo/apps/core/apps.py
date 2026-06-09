import logging
import os
import threading

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class EchoConfig(AppConfig):
    name = 'apps.core'
    verbose_name = 'core'

    def ready(self):
        print('initializing core app')
        import apps.core.signals  # noqa

        # Auto-start DICOM servers in background threads.
        # RUN_MAIN guard prevents double-start under Django's auto-reloader.
        # DISABLE_DICOM / DISABLE_DICOM_AUTO prevents auto-start.
        # Under gunicorn, DICOM servers must run as a separate process (store.py),
        # not inside workers — gunicorn workers share ports and only one can bind.
        _under_gunicorn = os.environ.get('SERVER_SOFTWARE', '').startswith('gunicorn')
        if _under_gunicorn:
            logger.info("Running under gunicorn — skipping DICOM auto-start (use store.py separately)")
        if (os.environ.get('RUN_MAIN') != 'true'
                and os.environ.get('DISABLE_DICOM') != '1'
                and os.environ.get('DISABLE_DICOM_AUTO') != '1'
                and not _under_gunicorn):
            self._start_dicom_servers()

    def _start_dicom_servers(self):
        try:
            from apps.core.services.worklist_scp import run_server as run_worklist
            t_wl = threading.Thread(target=run_worklist, daemon=True, name='dicom-worklist')
            t_wl.start()
            logger.info("DICOM Worklist/MPPS server started (port 11112)")
        except Exception as e:
            logger.error(f"Failed to start DICOM Worklist server: {e}")

        try:
            from apps.core.services.storage_scp import run_server as run_storage
            t_st = threading.Thread(target=run_storage, daemon=True, name='dicom-storage')
            t_st.start()
            logger.info("DICOM Storage server started (port 11113)")
        except Exception as e:
            logger.error(f"Failed to start DICOM Storage server: {e}")
