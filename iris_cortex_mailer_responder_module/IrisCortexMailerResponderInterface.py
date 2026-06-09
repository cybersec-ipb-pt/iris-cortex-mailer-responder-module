#!/usr/bin/env python3
import iris_interface.IrisInterfaceStatus as InterfaceStatus
from iris_interface.IrisModuleInterface import IrisModuleInterface, IrisModuleTypes
import iris_cortex_mailer_responder_module.IrisCortexMailerResponderConfig as interface_conf
from iris_cortex_mailer_responder_module.cortex_mailer_responder_handler.cortex_mailer_responder_handler import MailerHandler

class IrisCortexMailerResponderInterface(IrisModuleInterface):
    name = "IrisCortexMailerResponderInterface"
    _module_name = interface_conf.module_name
    _module_description = interface_conf.module_description
    _interface_version = interface_conf.interface_version
    _module_version = interface_conf.module_version
    _pipeline_support = interface_conf.pipeline_support
    _pipeline_info = interface_conf.pipeline_info
    _module_configuration = interface_conf.module_configuration
    _module_type = IrisModuleTypes.module_processor

    def register_hooks(self, module_id: int):
        self.module_id = module_id
        module_conf = self.module_dict_conf
        self.deregister_from_hook(module_id=self.module_id, iris_hook_name="on_manual_trigger_case")

        if module_conf.get("mailer_manual_note_hook_enabled"):
            status = self.register_to_hook(
                module_id,
                iris_hook_name="on_manual_trigger_note",
                manual_hook_name="Send Mailer notification",
            )

            if status.is_failure():
                self.log.error(status.get_message())
                self.log.error(status.get_data())
            else:
                self.log.info("Successfully registered on_manual_trigger_note hook")
        else:
            self.deregister_from_hook(module_id=self.module_id, iris_hook_name="on_manual_trigger_note")

    def hooks_handler(self, hook_name: str, hook_ui_name: str, data: any):
        self.log.info(f"Received hook {hook_name}")
        status = self._handle_notes(data=data)

        if status.is_failure():
            self.log.error(f"Encountered error processing hook {hook_name}")

            return InterfaceStatus.I2Error(data=data, logs=list(self.message_queue))

        self.log.info(f"Successfully processed hook {hook_name}")

        return InterfaceStatus.I2Success(data=data, logs=list(self.message_queue))

    def _handle_notes(self, data) -> InterfaceStatus.IIStatus:
        handler = MailerHandler(
            mod_config=self.module_dict_conf,
            server_config=self.server_dict_conf,
            logger=self.log,
        )

        in_status = InterfaceStatus.IIStatus(code=InterfaceStatus.I2CodeNoError)
        items = data if isinstance(data, list) else [data]

        for note in items:
            status = handler.handle_note(note=note)
            in_status = InterfaceStatus.merge_status(in_status, status)

        return in_status(data=data)