#!/usr/bin/env python3

module_name = "Cortex Mailer Responder"
module_description = "Integrate with Cortex Mailer responder. Responder must be enabled within Cortex."
interface_version = 1.2
module_version = 1.0
pipeline_support = False
pipeline_info = {}
module_configuration = [
    {
        "param_name": "cortexresponder_url",
        "param_human_name": "Cortex URL",
        "param_description": "Cortex URL",
        "default": None,
        "mandatory": True,
        "type": "string",
    },
    {
        "param_name": "cortexresponder_key",
        "param_human_name": "Cortex API Key",
        "param_description": "Cortex API key allowed to run responders",
        "default": None,
        "mandatory": True,
        "type": "sensitive_string",
    },
    {
        "param_name": "mailer_responder_name",
        "param_human_name": "Cortex Responder Name",
        "param_description": "Exact Cortex responder name to run",
        "default": "Wailer_1_1",
        "mandatory": True,
        "type": "string",
    },
    {
        "param_name": "mailer_manual_note_hook_enabled",
        "param_human_name": "Manual trigger on notification note",
        "param_description": "Allow manual sending from the note processor",
        "default": True,
        "mandatory": True,
        "type": "bool",
        "section": "Config",
    },
    {
        "param_name": "mailer_notification_note_title",
        "param_human_name": "Notification note title",
        "param_description": "Only notes with this exact title are processed",
        "default": "Mailer Notification",
        "mandatory": True,
        "type": "string",
        "section": "Config",
    },
    {
        "param_name": "mailer_poll_seconds",
        "param_human_name": "Cortex poll interval seconds",
        "param_description": "Seconds between Cortex job status checks",
        "default": "5",
        "mandatory": True,
        "type": "string",
        "section": "Advanced",
    },
    {
        "param_name": "mailer_timeout_seconds",
        "param_human_name": "Cortex responder timeout seconds",
        "param_description": "Maximum time to wait for the responder job",
        "default": "120",
        "mandatory": True,
        "type": "string",
        "section": "Advanced",
    },
]