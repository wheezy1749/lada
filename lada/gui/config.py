from gi.repository import GLib
from pathlib import Path
import json
import os

from lada import MODEL_WEIGHTS_DIR

MODEL_FILES_TO_NAMES = {
    os.path.join(MODEL_WEIGHTS_DIR, 'lada_mosaic_restoration_model_generic.pth'): 'basicvsrpp-generic-1.0',
    os.path.join(MODEL_WEIGHTS_DIR, 'lada_mosaic_restoration_model_generic_v1.1.pth'): 'basicvsrpp-generic-1.1',
    os.path.join(MODEL_WEIGHTS_DIR, 'lada_mosaic_restoration_model_bj_pov.pth'): 'basicvsrpp-bj-pov-1.0',
    os.path.join(MODEL_WEIGHTS_DIR, '3rd_party', 'clean_youknow_video.pth'): 'deepmosaics-clean-youknow',
}

MODEL_NAMES_TO_FILES = {v: k for k, v in MODEL_FILES_TO_NAMES.items()}


class Config:
    def __init__(self):
        self.preview_mode = None
        self.preview_mode = None
        self.mosaic_restoration_model = None
        self.export_codec = None
        self.export_crf = None
        self.preview_buffer_duration = None
        self.max_clip_duration = None
        self.device = None
        self.mosaic_pre_cleaning = None

        self.set_defaults()

    def set_defaults(self):
        self.preview_mode = 'mosaic-removal'
        self.mosaic_restoration_model = self.get_default_restoration_model()
        self.export_codec = 'h264'
        self.export_crf = 22
        self.preview_buffer_duration = 0
        self.max_clip_duration = 180
        self.device = 'cuda:0'
        self.mosaic_pre_cleaning = False

    def get_default_restoration_model(self):
        return 'basicvsrpp-generic-1.1'

    def save(self):
        config_file_path = get_config_file_path()
        if not config_file_path.parent.exists():
            config_file_path.parent.mkdir()
        with open(config_file_path, 'w') as f:
            config_dict = self._as_dict()
            json.dump(config_dict, f)
            print("saved config file", config_file_path, config_dict)

    def load_config(self):
        config_file_path = get_config_file_path()
        success = False
        if not config_file_path.exists():
            print("config file doesnt exist at", config_file_path)
        else:
            try:
                with open(config_file_path, 'r') as f:
                    config_dict = json.load(f)
                    self._from_dict(config_dict)
                    print("loaded config file", config_file_path, config_dict)
                    success = True
            except Exception as e:
                print("error loading config file, fall back to defaults", e)
                self.set_defaults()
        if not success:
            self.save()

    def _as_dict(self) -> dict:
        return dict(
            preview_mode=self.preview_mode,
            mosaic_restoration_model=self.mosaic_restoration_model,
            export_codec=self.export_codec,
            export_crf=self.export_crf,
            preview_buffer_duration=self.preview_buffer_duration,
            max_clip_duration=self.max_clip_duration,
            device=self.device,
            mosaic_pre_cleaning=self.mosaic_pre_cleaning
        )

    def _from_dict(self, dict):
        def update_prop(key):
            if key in dict and dict[key] is not None:
                setattr(self, key, dict[key])

        update_prop('preview_mode')
        update_prop('mosaic_restoration_model')
        update_prop('export_codec')
        update_prop('export_crf')
        update_prop('preview_buffer_duration')
        update_prop('max_clip_duration')
        update_prop('device')
        update_prop('mosaic_pre_cleaning')


def get_config_file_path() -> Path:
    base_config_dir = GLib.get_user_config_dir()
    return Path(base_config_dir).joinpath('lada').joinpath('lada.conf')