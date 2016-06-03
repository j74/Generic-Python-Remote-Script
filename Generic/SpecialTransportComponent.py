import Live
from _Framework.TransportComponent import TransportComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement 
from _Framework.SubjectSlot import subject_slot 

from MIDI_Map import TEMPO_TOP
from MIDI_Map import TEMPO_BOTTOM
class SpecialTransportComponent(TransportComponent):
    __doc__ = ' TransportComponent that only uses certain buttons if a shift button is pressed '
    def __init__(self):
        TransportComponent.__init__(self)
        self._quant_toggle_button = None
        self._last_quant_value = Live.Song.RecordingQuantization.rec_q_eight
        self.song().add_midi_recording_quantization_listener(self._on_quantisation_changed)
        self._on_quantisation_changed()
        self._undo_button = None
        self._redo_button = None
        self._tempo_encoder_control = None
        return None

    def disconnect(self):
        TransportComponent.disconnect(self)
        if self._quant_toggle_button != None:
            self._quant_toggle_button.remove_value_listener(self._quant_toggle_value)
            self._quant_toggle_button = None
        self.song().remove_midi_recording_quantization_listener(self._on_quantisation_changed)
        if (self._undo_button != None): 
            self._undo_button.remove_value_listener(self._undo_value)
            self._undo_button = None
        if (self._redo_button != None): 
            self._redo_button.remove_value_listener(self._redo_value)
            self._redo_button = None
        if (self._tempo_encoder_control != None):
            self._tempo_encoder_control.remove_value_listener(self._tempo_encoder_value)
            self._tempo_encoder_control = None
        return None

    def set_quant_toggle_button(self, button):
        if not(button == None or isinstance(button, ButtonElement) and button.is_momentary()):
            isinstance(button, ButtonElement)
            raise AssertionError
        if self._quant_toggle_button != button:
            if self._quant_toggle_button != None:
                self._quant_toggle_button.remove_value_listener(self._quant_toggle_value)
            self._quant_toggle_button = button
            if self._quant_toggle_button != None:
                self._quant_toggle_button.add_value_listener(self._quant_toggle_value)

            self.update()
        return None

    def _quant_toggle_value(self, value):
        assert (self._quant_toggle_button != None)
        assert (value in range(128))
        assert (self._last_quant_value != Live.Song.RecordingQuantization.rec_q_no_q)
        if self.is_enabled():
            if ((value != 0) or (not self._quant_toggle_button.is_momentary())):
                quant_value = self.song().midi_recording_quantization
                if (quant_value != Live.Song.RecordingQuantization.rec_q_no_q):
                    self._last_quant_value = quant_value
                    self.song().midi_recording_quantization = Live.Song.RecordingQuantization.rec_q_no_q
                else:
                    self.song().midi_recording_quantization = self._last_quant_value

    def _on_quantisation_changed(self):
        if self.is_enabled():
            quant_value = self.song().midi_recording_quantization
            quant_on = (quant_value != Live.Song.RecordingQuantization.rec_q_no_q)
            if quant_on:
                self._last_quant_value = quant_value
            if self._quant_toggle_button != None:
                if quant_on:
                    self._quant_toggle_button.turn_on()
                else:
                    self._quant_toggle_button.turn_off()

    def set_undo_button(self, undo_button):
        assert isinstance(undo_button, (ButtonElement,
                                        type(None)))
        if (undo_button != self._undo_button):
            if (self._undo_button != None):
                self._undo_button.remove_value_listener(self._undo_value)
            self._undo_button = undo_button
            if (self._undo_button != None):
                self._undo_button.add_value_listener(self._undo_value)
            self.update()


    def set_redo_button(self, redo_button):
        assert isinstance(redo_button, (ButtonElement,
                                        type(None)))
        if (redo_button != self._redo_button):
            if (self._redo_button != None):
                self._redo_button.remove_value_listener(self._redo_value)
            self._redo_button = redo_button
            if (self._redo_button != None):
                self._redo_button.add_value_listener(self._redo_value)
            self.update()


    def _undo_value(self, value):
        assert (self._undo_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if ((value != 0) or (not self._undo_button.is_momentary())):
                if self.song().can_undo:
                    self.song().undo()


    def _redo_value(self, value):
        assert (self._redo_button != None)
        assert (value in range(128))
        if self.is_enabled():
            if ((value != 0) or (not self._redo_button.is_momentary())):
                if self.song().can_redo:
                    self.song().redo()


    def _tempo_encoder_value(self, value):
        assert (self._tempo_encoder_control != None)
        assert (value in range(128))
        backwards = (value >= 64)
        step = 0.1
        if backwards:
            amount = (value - 128)
        else:
            amount = value
        tempo = max(20, min(999, (self.song().tempo + (amount * step))))
        self.song().tempo = tempo


    def set_tempo_encoder(self, control):
        assert ((control == None) or (isinstance(control, EncoderElement) and (control.message_map_mode() is Live.MidiMap.MapMode.relative_two_compliment)))
        if (self._tempo_encoder_control != None):
            self._tempo_encoder_control.remove_value_listener(self._tempo_encoder_value)
        self._tempo_encoder_control = control
        if (self._tempo_encoder_control != None):
            self._tempo_encoder_control.add_value_listener(self._tempo_encoder_value)
        self.update()

    @subject_slot('value')
    def _tempo_value(self, value):
        assert (self._tempo_control != None)
        assert (value in range(128))
        if self.is_enabled():
            fraction = ((TEMPO_TOP - TEMPO_BOTTOM) / 127.0)
            self.song().tempo = ((fraction * value) + TEMPO_BOTTOM)

