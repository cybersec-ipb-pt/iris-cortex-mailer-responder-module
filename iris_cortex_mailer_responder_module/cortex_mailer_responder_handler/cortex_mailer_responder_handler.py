#!/usr/bin/env python3

import json
import time
import traceback
import requests
from typing import Any, Dict
from cortex4py.api import Api
import iris_interface.IrisInterfaceStatus as InterfaceStatus

class MailerHandler(object):
    def __init__(self, mod_config, server_config, logger):
        self.mod_config = mod_config or {}
        self.server_config = server_config or {}
        self.log = logger

    def _extract_note_info(self, text: str) -> str:
        subject = ""
        recipient = ""
        lines = []

        for line in str(text or "").splitlines():
            stripped = line.strip()

            if not stripped:
                lines.append("")
                continue

            if stripped.lower().startswith("**subject:**"):
                subject = stripped.split(":** ")[1]
                continue

            if stripped.lower().startswith("**notification recipient:**"):
                recipient = stripped.split(":** ")[1]
                continue

            lines.append(line)

        if recipient == "":
            raise RuntimeError("Missing Recipient")

        if subject == "":
            raise RuntimeError("Missing Email Subject")

        body = "\n".join(lines).strip()

        return subject, recipient, body

    def _call_cortex_responder(self, subject: str, recipient: str, message_body: str, case_id: str = "") -> Dict[str, Any]:
        cortex_url = str(self.mod_config.get("cortexresponder_url")).strip().rstrip("/")
        cortex_key = str(self.mod_config.get("cortexresponder_key")).strip()
        responder_name = str(self.mod_config.get("mailer_responder_name")).strip()
        poll_seconds = int(self.mod_config.get("mailer_poll_seconds"))
        timeout_seconds = int(self.mod_config.get("mailer_timeout_seconds"))

        api = Api(cortex_url, cortex_key, verify_cert=False)
        headers = {"Authorization": f"Bearer {cortex_key}"}
        r = requests.get(f"{cortex_url}/api/user/current", headers=headers, verify=False)
        cortex_info = r.json()

        payload = {
            "dataType": f"dfir-iris-case:{case_id}",
            "tlp": 2,
            "pap": 2,
            "parameters": {
                "organisation": cortex_info.get("organization"),
                "user": cortex_info.get("id")
            },
            "data": {
                "title": subject,
                "description": message_body,
                "recipient": recipient,
                "caseId": str(case_id) if case_id else "",
                "tags": [
                    f"mail={recipient}",
                ],
            },
        }

        self.log.info("Running Cortex responder %s recipient=%s", responder_name, recipient)
        job = api.responders.run_by_name(responder_name, payload, force=1)
        job_json = job.json() if hasattr(job, "json") else job
        job_id = job_json.get("id")
        status = job_json.get("status")

        if not job_id:
            raise RuntimeError(f"Cortex responder did not return a job id: {job_json}")

        start = time.time()
        last_json = job_json

        while status not in ("Success", "Failure"):
            if time.time() - start > timeout_seconds:
                raise RuntimeError(
                    f"Cortex responder timeout after {timeout_seconds}s. Last status={status} job_id={job_id}"
                )

            time.sleep(poll_seconds)
            followup = api.jobs.get_by_id(job_id)
            last_json = followup.json() if hasattr(followup, "json") else followup
            status = last_json.get("status")
            self.log.info("Mailer responder job %s status=%s", job_id, status)

        if status == "Failure":
            try:
                report = api.jobs.get_report(job_id).report
            except Exception:
                report = {}
            raise RuntimeError(
                "Cortex responder failed. job_id={} report={}".format(
                    job_id,
                    json.dumps(report, ensure_ascii=False),
                )
            )

        return {
            "job_id": job_id,
            "status": status,
            "response": last_json,
        }

    def handle_note(self, note):
        title = str(note.note_title)
        content = str(note.note_content)
        case_id = str(note.note_case_id)
        wanted_title = str(self.mod_config.get("mailer_notification_note_title")).strip()

        if "|" in wanted_title:
            wanted_title = wanted_title.split("|")
        else:
            wanted_title = [wanted_title]

        if title not in wanted_title:
            self.log.info("Skipping note title=%r; expected %r", title, wanted_title)

            return InterfaceStatus.I2Success(data={"skipped": True, "reason": "not_thephish_notification_note"})

        subject, recipient, message_body = self._extract_note_info(content)

        if not recipient:
            msg = f"Could not extract notification recipient from note {title}"
            self.log.error(msg)

            return InterfaceStatus.I2Error(msg)

        try:
            result = self._call_cortex_responder(
                subject=subject,
                recipient=recipient,
                message_body=message_body,
                case_id=case_id,
            )
            self.log.info("Mailer responder completed: %s", json.dumps(result, ensure_ascii=False))

            return InterfaceStatus.I2Success(data=result)

        except Exception as exc:
            self.log.error(traceback.format_exc())

            return InterfaceStatus.I2Error(str(exc))