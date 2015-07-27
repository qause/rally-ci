# Copyright 2015: Mirantis Inc.
# All Rights Reserved.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import importlib
import logging
import logging.config
import yaml

LOG = logging.getLogger(__name__)


class Config:
    def __init__(self, root, filename):
        self.root = root
        self.filename = filename
        self._modules = {}
        self.data = {}
        with open(filename, "rb") as cf:
            self.raw_data = yaml.safe_load(cf)

        for item in self.raw_data:
            if len(item.keys()) > 1:
                raise ValueError("Invalid config entry %s" % item)
            key = list(item.keys())[0]
            value = list(item.values())[0]
            name = value.get("name")
            if key == "logging":
                self.configure_logging(value)
            if name:
                self.data.setdefault(key, {})
                if name in self.data[key]:
                    raise ValueError("Duplicate name %s" % name)
                self.data[key][name] = value
            else:
                self.data.setdefault(key, [])
                self.data[key].append(value)

    def get_instance(self, cfg):
        return self._get_module(cfg["module"]).Class(cfg)

    def iter_instances(self, section):
        section = self.data.get(section, {})
        for config in section.values():
            cls = self._get_module(config["module"]).Class
            yield cls(**config)

    def iter_providers(self):
        for cfg in self.data.get("provider", {}).values():
            yield self._get_module(cfg["module"]).Provider(self.root, cfg)

    def _get_module(self, name):
        """Get module by name.

        Import module if it is not imported.
        """
        module = self._modules.get(name)
        if not module:
            module = importlib.import_module(name)
            self._modules[name] = module
        return module

    def configure_logging(self, section):
        def _get_handler(key, value):
            return {'level': key.upper(), 'filename': value}

        default_log = {
            'debug': _get_handler,
            'error': _get_handler,
            'info': _get_handler,
        }

        if section:
            for key in section.keys():
                if key in default_log.keys():
                    LOGGING["handlers"][key].update(default_log[key](key, section[key]))
                else:
                    raise ValueError("Unknown logging level")

        logging.config.dictConfig(LOGGING)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(name)s:"
                      "%(levelname)s: %(message)s "
                      "(%(filename)s:%(lineno)d)",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        "debug": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "debug.log"
        },
        "info": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "info.log"
        },
        "error": {
            "level": "ERROR",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "error.log"
        },
    },
    "loggers": {
        "": {
            "handlers": ["info", "debug", "error"],
            'level': 'DEBUG'
        }
    }
}
