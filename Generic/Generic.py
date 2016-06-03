from __future__ import with_statement

import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from SpecialMixerComponent import SpecialMixerComponent
from SpecialTransportComponent import SpecialTransportComponent
from SpecialSessionComponent import SpecialSessionComponent
from SpecialZoomingComponent import SpecialZoomingComponent
from SpecialViewControllerComponent import DetailViewControllerComponent
from MIDI_Map import *

class Generic(ControlSurface):
    __doc__ = " Script for FCB1010 in APC emulation mode "

    _active_instances = []
    def _combine_active_instances():
        track_offset = 0
        scene_offset = 0
        for instance in Generic._active_instances:
            instance._activate_combination_mode(track_offset, scene_offset)
            track_offset += instance._session.width()
    _combine_active_instances = staticmethod(_combine_active_instances)

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self._note_map_scenes = []
            self._note_map_buttons = []
            self._ctrl_map_sliders = []
            self._note_map_trk_stop_buttons = []
            self._note_map_trk_sel_buttons = []
            self._note_map_trk_mute_buttons = []
            self._note_map_trk_solo_buttons = []
            self._note_map_trk_rec_buttons = []
            self._ctrl_map_trk_volume = []
            self._ctrl_map_trk_pan = []
            self._ctrl_map_senda = []
            self._ctrl_map_sendb = []
            self._ctrl_map_sendc = []
            self._note_map_bank_buttons = []
            self._ctrl_map_parameter = []
            self._load_MIDI_map()
            self._session = None
            self._session_zoom = None
            self._mixer = None
            self._setup_session_control()
            self._setup_mixer_control()
            self._session.set_mixer(self._mixer)
            self._setup_device_and_transport_control()
            self.set_highlighting_session_component(self._session)
        self._pads = []
        self._load_pad_translations()
        self._do_combine()


    def disconnect(self):
        self._note_map_scenes = None
        self._note_map_buttons = None
        self._ctrl_map_sliders = None
        self._note_map_trk_stop_buttons = None
        self._note_map_trk_sel_buttons = None
        self._note_map_trk_mute_buttons = None
        self._note_map_trk_solo_buttons = None
        self._note_map_trk_rec_buttons = None
        self._ctrl_map_trk_volume = None
        self._ctrl_map_trk_pan = None
        self._ctrl_map_senda = None
        self._ctrl_map_sendb = None
        self._ctrl_map_sendc = None
        self._note_map_bank_buttons = None
        self._ctrl_map_parameter = None
        self._pads = None
        self._do_uncombine()
        self._shift_button = None
        self._session = None
        self._session_zoom = None
        self._mixer = None
        ControlSurface.disconnect(self)


    def _do_combine(self):
        if self not in Generic._active_instances:
            Generic._active_instances.append(self)
            Generic._combine_active_instances()


    def _do_uncombine(self):
        if ((self in Generic._active_instances) and Generic._active_instances.remove(self)):
            self._session.unlink()
            Generic._combine_active_instances()


    def _activate_combination_mode(self, track_offset, scene_offset):
        if TRACK_OFFSET != -1:
            track_offset = TRACK_OFFSET
        if SCENE_OFFSET != -1:
            scene_offset = SCENE_OFFSET
        self._session.link_with_track_offset(track_offset, scene_offset)


    def _setup_session_control(self):
        is_momentary = True
        self._session = SpecialSessionComponent(TRACK_NUMBER, MATRIX_DEPTH)
        self._session.name = 'Session_Control'
        self._session.set_track_bank_buttons(self._note_map_buttons[25], self._note_map_buttons[24])
        self._session.set_scene_bank_buttons(self._note_map_buttons[27], self._note_map_buttons[26])
        self._session.set_select_buttons(self._note_map_buttons[34], self._note_map_buttons[35])
        self._scene_launch_buttons = [self._note_map_scenes[index] for index in range(MATRIX_DEPTH) ]
        self._track_stop_buttons = [self._note_map_trk_stop_buttons[index] for index in range(TRACK_NUMBER) ]
        self._session.set_stop_all_clips_button(self._note_map_buttons[38])
        self._session.set_stop_track_clip_buttons(tuple(self._track_stop_buttons))
        self._session.selected_scene().name = 'Selected_Scene'
        self._session.selected_scene().set_launch_button(self._note_map_buttons[36])
        self._session.set_slot_launch_button(self._note_map_buttons[37])
        for scene_index in range(MATRIX_DEPTH):
            scene = self._session.scene(scene_index)
            scene.name = 'Scene_' + str(scene_index)
            button_row = []
            scene.set_launch_button(self._scene_launch_buttons[scene_index])
            scene.set_triggered_value(2)
            for track_index in range(TRACK_NUMBER):
                if (CLIPNOTEMAP[scene_index][track_index] == -1):
                    button = None
                else:
                    button = ButtonElement(is_momentary, CLIPNOTEMAP_TYPE[scene_index][track_index], CLIPNOTEMAP_CH[scene_index][track_index], CLIPNOTEMAP[scene_index][track_index])
                button_row.append(button)
                clip_slot = scene.clip_slot(track_index)
                clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
                clip_slot.set_launch_button(button)
        self._session_zoom = SpecialZoomingComponent(self._session)
        self._session_zoom.name = 'Session_Overview'
        self._session_zoom.set_nav_buttons(self._note_map_buttons[28], self._note_map_buttons[29], self._note_map_buttons[30], self._note_map_buttons[31])

    def _setup_mixer_control(self):
        is_momentary = True
        self._mixer = SpecialMixerComponent(TRACK_NUMBER)
        self._mixer.name = 'Mixer'
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer.master_strip().set_select_button(self._note_map_buttons[39])
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        self._mixer.set_select_buttons(self._note_map_buttons[33], self._note_map_buttons[32])
        self._mixer.set_crossfader_control(self._ctrl_map_sliders[2])
        self._mixer.set_prehear_volume_control(self._ctrl_map_sliders[1])
        self._mixer.master_strip().set_volume_control(self._ctrl_map_sliders[0])
        for track in range(TRACK_NUMBER):
            strip = self._mixer.channel_strip(track)
            strip.name = 'Channel_Strip_' + str(track)
            strip.set_arm_button(self._note_map_trk_rec_buttons[track])
            strip.set_solo_button(self._note_map_trk_solo_buttons[track])
            strip.set_mute_button(self._note_map_trk_mute_buttons[track])
            strip.set_select_button(self._note_map_trk_sel_buttons[track])
            strip.set_volume_control(self._ctrl_map_trk_volume[track])
            strip.set_pan_control(self._ctrl_map_trk_pan[track])
            strip.set_send_controls((self._ctrl_map_senda[track], self._ctrl_map_sendb[track], self._ctrl_map_sendc[track]))
            strip.set_invert_mute_feedback(True)


    def _setup_device_and_transport_control(self):
        is_momentary = True
        self._device = DeviceComponent()
        self._device.name = 'Device_Component'
        device_bank_buttons = []
        device_param_controls = []
        for index in range(PARAMS_NUMBER):
            device_param_controls.append(self._ctrl_map_parameter[index])
        for index in range(BANKS_NUMBER):
            device_bank_buttons.append(self._note_map_bank_buttons[index])
        if None not in device_bank_buttons:
            self._device.set_bank_buttons(tuple(device_bank_buttons))
        if None not in device_param_controls:
            self._device.set_parameter_controls(tuple(device_param_controls))
        self._device.set_on_off_button(self._note_map_buttons[17])
        self._device.set_bank_nav_buttons(self._note_map_buttons[20], self._note_map_buttons[21])
        self._device.set_lock_button(self._note_map_buttons[16])
        self.set_device_component(self._device)

        detail_view_toggler = DetailViewControllerComponent()
        detail_view_toggler.name = 'Detail_View_Control'
        detail_view_toggler.set_device_clip_toggle_button(self._note_map_buttons[15])
        detail_view_toggler.set_detail_toggle_button(self._note_map_buttons[14])
        detail_view_toggler.set_device_nav_buttons(self._note_map_buttons[18], self._note_map_buttons[19] )

        transport = SpecialTransportComponent()
        transport.name = 'Transport'
        transport.set_play_button(self._note_map_buttons[0])
        transport.set_stop_button(self._note_map_buttons[1])
        transport.set_record_button(self._note_map_buttons[2])
        transport.set_nudge_buttons(self._note_map_buttons[4], self._note_map_buttons[5])
        transport.set_undo_button(self._note_map_buttons[6])
        transport.set_redo_button(self._note_map_buttons[7])
        transport.set_tap_tempo_button(self._note_map_buttons[3])
        transport.set_quant_toggle_button(self._note_map_buttons[13])
        transport.set_overdub_button(self._note_map_buttons[11])
        transport.set_metronome_button(self._note_map_buttons[12])
        transport.set_tempo_control(self._ctrl_map_sliders[3])
        transport.set_loop_button(self._note_map_buttons[8])
        transport.set_seek_buttons(self._note_map_buttons[22], self._note_map_buttons[23])
        transport.set_punch_buttons(self._note_map_buttons[9], self._note_map_buttons[10])


    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        track = self.song().view.selected_track
        device_to_select = track.view.selected_device
        if device_to_select == None and len(track.devices) > 0:
            device_to_select = track.devices[0]
        if device_to_select != None:
            self.song().view.select_device(device_to_select)
        self._device_component.set_device(device_to_select)


    def _load_pad_translations(self):
        if -1 not in DRUM_PADS:
            pad = []
            for row in range(PAD_Y_NUMBER):
                for col in range(PAD_X_NUMBER):
                    pad = (col, row, DRUM_PADS[row*4 + col], PADCHANNEL,)
                    self._pads.append(pad)
            self.set_pad_translations(tuple(self._pads))


    def _load_MIDI_map(self):
        is_momentary = True
        # SCENELAUNCH Buttons
        for scene_id in range(MATRIX_DEPTH):
            if (SCENELAUNCH[scene_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, SCENELAUNCH_TYPE[scene_id], SCENELAUNCH_CH[scene_id], SCENELAUNCH[scene_id])
                button.name = 'Scene_' + str(scene_id)
            self._note_map_scenes.append(button)
        # BUTTON_VECTOR Buttons
        for button_id in range(NUMBER_BUTTONS):
            if (BUTTON_VECTOR[button_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, BUTTON_VECTOR_TYPE[button_id], BUTTON_VECTOR_CH[button_id], BUTTON_VECTOR[button_id])
                button.name = 'Global_Button_' + str(button_id)
            self._note_map_buttons.append(button)
        # SLIDER_VECTOR Sliders
        for slider_id in range(NUMBER_SLIDERS):
            if (SLIDER_VECTOR[slider_id] == -1) :
                control = None
            else:
                control = SliderElement(MIDI_CC_TYPE, SLIDER_VECTOR_CH[slider_id], SLIDER_VECTOR[slider_id])
                control.name = 'Global_Slider_' + str(slider_id)
            self._ctrl_map_sliders.append(control)
        # TRACKSTOP Buttons
        for track_id in range(TRACK_NUMBER):
            if (TRACKSTOP[track_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, TRACKSTOP_TYPE[track_id], TRACKSTOP_CH[track_id], TRACKSTOP[track_id])
                button.name = 'Trk_Stop_Button_' + str(track_id)
            self._note_map_trk_stop_buttons.append(button)
        # TRACKSEL Buttons
        for track_id in range(TRACK_NUMBER):
            if (TRACKSEL[track_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, TRACKSEL_TYPE[track_id], TRACKSEL_CH[track_id], TRACKSEL[track_id])
                button.name = 'Trk_Sel_Button_' + str(track_id)
            self._note_map_trk_sel_buttons.append(button)
        # TRACKMUTE Buttons
        for track_id in range(TRACK_NUMBER):
            if (TRACKMUTE[track_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, TRACKMUTE_TYPE[track_id], TRACKMUTE_CH[track_id], TRACKMUTE[track_id])
                button.name = 'Trk_Mute_Button_' + str(track_id)
            self._note_map_trk_mute_buttons.append(button)			
        # TRACKSOLO Buttons
        for track_id in range(TRACK_NUMBER):
            if (TRACKSOLO[track_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, TRACKSOLO_TYPE[track_id], TRACKSOLO_CH[track_id], TRACKSOLO[track_id])
                button.name = 'Trk_Solo_Button_' + str(track_id)
            self._note_map_trk_solo_buttons.append(button)	
        # TRACKREC Buttons
        for track_id in range(TRACK_NUMBER):
            if (TRACKREC[track_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, TRACKREC_TYPE[track_id], TRACKREC_CH[track_id], TRACKREC[track_id])
                button.name = 'Trk_Rec_Button_' + str(track_id)
            self._note_map_trk_rec_buttons.append(button)	
        # TRACKVOL Sliders
        for track_id in range(TRACK_NUMBER):
            if (TRACKVOL[track_id] == -1) :
                control = None
            else:
                control = SliderElement(MIDI_CC_TYPE, TRACKVOL_CH[track_id], TRACKVOL[track_id])
                control.name = 'Trk_Vol_Slider_' + str(track_id)
            self._ctrl_map_trk_volume.append(control)
        # TRACKPAN Sliders
        for track_id in range(TRACK_NUMBER):
            if (TRACKPAN[track_id] == -1) :
                control = None
            else:
                control = SliderElement(MIDI_CC_TYPE, TRACKPAN_CH[track_id], TRACKPAN[track_id])
                control.name = 'Trk_Pan_Slider_' + str(track_id)
            self._ctrl_map_trk_pan.append(control)
        # TRACKSENDA Sliders
        for track_id in range(TRACK_NUMBER):
            if (TRACKSENDA[track_id] == -1) :
                control = None
            else:
                control = SliderElement(MIDI_CC_TYPE, TRACKSENDA_CH[track_id], TRACKSENDA[track_id])
                control.name = 'Trk_SendA_Slider_' + str(track_id)
            self._ctrl_map_senda.append(control)
        # TRACKSENDB Sliders
        for track_id in range(TRACK_NUMBER):
            if (TRACKSENDB[track_id] == -1) :
                control = None
            else:
                control = SliderElement(MIDI_CC_TYPE, TRACKSENDB_CH[track_id], TRACKSENDB[track_id])
                control.name = 'Trk_SendB_Slider_' + str(track_id)
            self._ctrl_map_sendb.append(control)
        # TRACKSENDC Sliders
        for track_id in range(TRACK_NUMBER):
            if (TRACKSENDC[track_id] == -1) :
                control = None
            else:
                control = SliderElement(MIDI_CC_TYPE, TRACKSENDC_CH[track_id], TRACKSENDC[track_id])
                control.name = 'Trk_SendC_Slider_' + str(track_id)
            self._ctrl_map_sendc.append(control)
        # DEVICEBANK Buttons
        for bank_id in range(BANKS_NUMBER):
            if (DEVICEBANK[bank_id] == -1) :
                button = None
            else:
                button = ButtonElement(is_momentary, DEVICEBANK_TYPE[bank_id], DEVICEBANK_CH[bank_id], DEVICEBANK[bank_id])
                button.name = 'Bank_Button_' + str(bank_id)
            self._note_map_bank_buttons.append(button)
        # PARAMCONTROL Sliders
        for param_id in range(PARAMS_NUMBER):
            if (PARAMCONTROL[param_id] == -1) :
                control = None
            else:
                control = SliderElement(MIDI_CC_TYPE, PARAMCONTROL_CH[param_id], PARAMCONTROL[param_id])
                control.name = 'Slider_Param_' + str(param_id)
            self._ctrl_map_parameter.append(control)
