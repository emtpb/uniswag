import csv
import os

from PySide6 import QtCore


# noinspection PyCallingNonCallable
class GenProperties(QtCore.QObject):

    # signals that indicate a device property access has been completed,
    # contain device id and current/new property value
    isRunning = QtCore.Signal('QVariantMap', bool)
    reset = QtCore.Signal('QVariantMap', bool)
    trigSrcAvail = QtCore.Signal('QVariantMap', list)
    trigSrc = QtCore.Signal('QVariantMap', str)
    trigTime = QtCore.Signal('QVariantMap', float)

    # signals that indicate a channel property access has been completed,
    # contain device id, channel number and current/new property value
    isOutInv = QtCore.Signal('QVariantMap', int, bool)
    sigTypesAvail = QtCore.Signal('QVariantMap', int, list)
    sigType = QtCore.Signal('QVariantMap', int, str)
    amp = QtCore.Signal('QVariantMap', int, float)
    isAmpAutoRange = QtCore.Signal('QVariantMap', int, bool)
    offset = QtCore.Signal('QVariantMap', int, float)
    period = QtCore.Signal('QVariantMap', int, float)
    freq = QtCore.Signal('QVariantMap', int, float)
    freqModesAvail = QtCore.Signal('QVariantMap', int, list)
    freqMode = QtCore.Signal('QVariantMap', int, str)
    phase = QtCore.Signal('QVariantMap', int, float)
    symmetry = QtCore.Signal('QVariantMap', int, float)
    pulseDelay = QtCore.Signal('QVariantMap', int, float)
    pulseHold = QtCore.Signal('QVariantMap', int, float)
    pulseTransLead = QtCore.Signal('QVariantMap', int, float)
    pulseTransTrail = QtCore.Signal('QVariantMap', int, float)
    pulseWidth = QtCore.Signal('QVariantMap', int, float)
    dutyCycle = QtCore.Signal('QVariantMap', int, float)
    impedance = QtCore.Signal('QVariantMap', int, float)
    modesAvail = QtCore.Signal('QVariantMap', int, list)
    mode = QtCore.Signal('QVariantMap', int, str)
    burstModesAvail = QtCore.Signal('QVariantMap', int, list)
    burstMode = QtCore.Signal('QVariantMap', int, str)
    isBurstOn = QtCore.Signal('QVariantMap', int, bool)
    burstCnt = QtCore.Signal('QVariantMap', int, int)
    burstSampleCnt = QtCore.Signal('QVariantMap', int, int)
    burstSegCnt = QtCore.Signal('QVariantMap', int, int)
    burstDelay = QtCore.Signal('QVariantMap', int, float)

    def __init__(self, front_to_back_connector):
        """
        A supplementary interface between frontend & backend
        specifically dedicated to getting & setting signal generator properties.
        Inherits from QtCore.QObject.

        Frontend can call its methods to display and change the currently selected device's (channel) settings.
        In order to determine that device, the main interface connecting front- & backend is consulted.

        Args:
            front_to_back_connector (uniswag.front_to_back_connector.FrontToBackConnector):
                The main interface connecting front- to backend.

        Returns:
            GenProperties:
                A GenProperties object.
        """
        super(GenProperties, self).__init__()

        # the main interface connecting front- to backend,
        # provides information about the currently selected signal generator (and signal generator channel)
        self.front_to_back_connector = front_to_back_connector

    # GENERATOR FUNCTIONS ##############################################################################################

    @QtCore.Slot()
    def _is_running(self):
        self.front_to_back_connector.access_gen_property(self._is_running_thread)

    def _is_running_thread(self, device):
        result = device.is_running
        self.isRunning.emit(device.id, result)

    @QtCore.Slot()
    def _start_n_stop(self):
        self.front_to_back_connector.access_gen_property(self._start_n_stop_thread)

    def _start_n_stop_thread(self, device):
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        # start the signal generator if it is not already running
        if not device.is_running:
            success = device.start()
            if success:
                print(dev_id + ' started')
            else:
                print('Could not start ' + dev_id)

        # stop the signal generator if it is currently running
        else:
            success = device.stop()
            if success:
                print(dev_id + ' stopped')
            else:
                print('Could not stop ' + dev_id)

        result = device.is_running
        self.isRunning.emit(device.id, result)

    @QtCore.Slot()
    def _reset(self):
        self.front_to_back_connector.access_gen_property(self._reset_thread)

    def _reset_thread(self, device):
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        # reset the device
        device.reset()
        print(dev_id + ' was manually reset')
        self.reset.emit(device.id, True)

        # update signal preview graph after device (and thereby channel) reset
        for channel in device.ch:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot()
    def _force_trig(self):
        self.front_to_back_connector.access_gen_property(self._force_trig_thread)

    @staticmethod
    def _force_trig_thread(device):
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        # force the trigger
        success = device.force_trig()
        if success:
            print(dev_id + ' triggered manually')
        else:
            print('Could not manually trigger ' + dev_id)

    @QtCore.Slot()
    def _trig_src_avail(self):
        self.front_to_back_connector.access_gen_property(self._trig_src_avail_thread)

    def _trig_src_avail_thread(self, device):
        result = device.trig_src_avail()
        self.trigSrcAvail.emit(device.id, result)
        self._trig_src_thread(device, None)

    @QtCore.Slot(str)
    def _trig_src(self, value):
        self.front_to_back_connector.access_gen_property(self._trig_src_thread, value)

    def _trig_src_thread(self, device, value):
        if value is not None:
            device.trig_src = value
        result = device.trig_src
        self.trigSrc.emit(device.id, result)

    @QtCore.Slot(str)
    def _trig_time(self, value):
        self.front_to_back_connector.access_gen_property(self._trig_time_thread, value)

    def _trig_time_thread(self, device, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.trig_time = value
        result = device.trig_time
        self.trigTime.emit(device.id, result)

    # GENERATOR CHANNEL FUNCTIONS ######################################################################################
    @QtCore.Slot(str)
    def _arb_data(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._arb_data_thread, value)

    def _arb_data_thread(self, device, channel, value):
        graph_update = False

        # convert filename to os-path
        raw_path = os.path.normpath(value)
        raw_path = raw_path.split(sep=':\\', maxsplit=1)
        if len(raw_path) < 2:
            raw_path = raw_path[0].split(sep=':', maxsplit=1)
            if len(raw_path) >= 2:
                file = raw_path[1]
            else:
                file = raw_path[0]
        else:
            file = raw_path[1]

        # open the file pointed to by the os-path if it exists and is of type CSV
        if os.path.exists(file) and file[-4:] == '.csv':
            opened_file = open(file, 'r')
            csv_r = csv.reader(opened_file)

            # initially assume the data to be stored in a single row (rather than column)
            row_major = True

            # convert the CVS file contents into a Python list
            input_data = []
            for row in csv_r:
                if row_major:

                    # check if the data is actually stored in a single row
                    if len(row) > 1:

                        for entry in row:
                            try:
                                data = float(entry)
                            except ValueError:
                                data = 0.0
                            input_data.append(data)

                        # stop after one row
                        break

                    else:
                        row_major = False

                # only if the data is stored in a column:
                try:
                    data = float(row[0])
                except (ValueError, IndexError):
                    data = 0.0
                input_data.append(data)

            opened_file.close()

            # remove CSV header if the data was read as column
            if not row_major:
                input_data.pop(0)

            graph_update = channel.arb_data(input_data)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _is_out_inv(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._is_out_inv_thread, value)

    def _is_out_inv_thread(self, device, channel, value):
        if value is not None:

            # String comparison necessary due to passed parameter being of type String, not Bool
            if value == 'true':
                channel.is_out_inv = True
            else:
                channel.is_out_inv = False

        result = channel.is_out_inv
        self.isOutInv.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _sig_types_avail(self):
        self.front_to_back_connector.access_gen_ch_property(self._sig_types_avail_thread)

    def _sig_types_avail_thread(self, device, channel):
        result = channel.sig_types_avail
        self.sigTypesAvail.emit(device.id, channel.id['No'], result)
        self._sig_type_thread(device, channel, None)

    @QtCore.Slot(str)
    def _sig_type(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._sig_type_thread, value)

    def _sig_type_thread(self, device, channel, value):
        graph_update = False

        if value is not None:
            channel.sig_type = value
            graph_update = True

        result = channel.sig_type
        self.sigType.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _amp(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._amp_thread, value)

    def _amp_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.amp = value
            graph_update = True

        result = channel.amp
        self.amp.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _is_amp_auto_range(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._is_amp_auto_range_thread, value)

    def _is_amp_auto_range_thread(self, device, channel, value):
        if value is not None:

            # String comparison necessary due to passed parameter being of type String, not Bool
            if value == 'true':
                channel.is_amp_auto_range = True
            else:
                channel.is_amp_auto_range = False

        result = channel.is_amp_auto_range
        self.isAmpAutoRange.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _offset(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._offset_thread, value)

    def _offset_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.offset = value
            graph_update = True

        result = channel.offset
        self.offset.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _period(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._period_thread, value)

    def _period_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.period = value
            graph_update = True

        result = channel.period
        self.period.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _freq(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._freq_thread, value)

    def _freq_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.freq = value
            graph_update = True

        result = channel.freq
        self.freq.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot()
    def _freq_modes_avail(self):
        self.front_to_back_connector.access_gen_ch_property(self._freq_modes_avail_thread)

    def _freq_modes_avail_thread(self, device, channel):
        result = channel.freq_modes_avail
        self.freqModesAvail.emit(device.id, channel.id['No'], result)
        self._freq_mode_thread(device, channel, None)

    @QtCore.Slot(str)
    def _freq_mode(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._freq_mode_thread, value)

    def _freq_mode_thread(self, device, channel, value):
        graph_update = False

        if value is not None:
            channel.freq_mode = value
            graph_update = True

        result = channel.freq_mode
        self.freqMode.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _phase(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._phase_thread, value)

    def _phase_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.phase = value
            graph_update = True

        result = channel.phase
        self.phase.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _symmetry(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._symmetry_thread, value)

    def _symmetry_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.symmetry = value
            graph_update = True

        result = channel.symmetry
        self.symmetry.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _pulse_delay(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._pulse_delay_thread, value)

    def _pulse_delay_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.pulse_delay = value

        result = channel.pulse_delay
        self.pulseDelay.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _pulse_hold(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._pulse_hold_thread, value)

    def _pulse_hold_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.pulse_hold = value

        result = channel.pulse_hold
        self.pulseHold.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _pulse_trans_lead(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._pulse_trans_lead_thread, value)

    def _pulse_trans_lead_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.pulse_trans_lead = value

        result = channel.pulse_trans_lead
        self.pulseTransLead.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _pulse_trans_trail(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._pulse_trans_trail_thread, value)

    def _pulse_trans_trail_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.pulse_trans_trail = value

        result = channel.pulse_trans_trail
        self.pulseTransLead.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _pulse_width(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._pulse_width_thread, value)

    def _pulse_width_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.pulse_width = value
            graph_update = True

        result = channel.pulse_width
        self.pulseWidth.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _duty_cycle(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._duty_cycle_thread, value)

    def _duty_cycle_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.duty_cycle = value
            graph_update = True

        result = channel.duty_cycle
        self.dutyCycle.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot(str)
    def _impedance(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._impedance_thread, value)

    def _impedance_thread(self, device, channel, value):
        graph_update = False

        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.impedance = value
            graph_update = True

        result = channel.impedance
        self.impedance.emit(device.id, channel.id['No'], result)

        # update signal preview graph if a new value was assigned to property
        if graph_update:
            self.front_to_back_connector.update_signal_preview(device.id, channel)

    @QtCore.Slot()
    def _modes_avail(self):
        self.front_to_back_connector.access_gen_ch_property(self._modes_avail_thread)

    def _modes_avail_thread(self, device, channel):
        result = channel.modes_avail
        self.modesAvail.emit(device.id, channel.id['No'], result)
        self._mode_thread(device, channel, None)

    @QtCore.Slot(str)
    def _mode(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._mode_thread, value)

    def _mode_thread(self, device, channel, value):
        if value is not None:
            channel.mode = value
        result = channel.mode
        self.mode.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _burst_modes_avail(self):
        self.front_to_back_connector.access_gen_ch_property(self._burst_modes_avail_thread)

    def _burst_modes_avail_thread(self, device, channel):
        result = channel.burst_modes_avail()
        self.burstModesAvail.emit(device.id, channel.id['No'], result)
        self._burst_mode_thread(device, channel, None)

    @QtCore.Slot(str)
    def _burst_mode(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._burst_mode_thread, value)

    def _burst_mode_thread(self, device, channel, value):
        if value is not None:
            channel.burst_mode = value
        result = channel.burst_mode
        self.burstMode.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _is_burst_on(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._is_burst_on_thread, value)

    def _is_burst_on_thread(self, device, channel, value):
        if value is not None:

            # String comparison necessary due to passed parameter being of type String, not Bool
            if value == 'true':
                channel.is_burst_on = True
            else:
                channel.is_burst_on = False

        result = channel.is_burst_on
        self.isBurstOn.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _burst_cnt(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._burst_cnt_thread, value)

    def _burst_cnt_thread(self, device, channel, value):
        # filter out empty or non-Int-like input
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.burst_cnt = value
        result = channel.burst_cnt
        self.burstCnt.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _burst_sample_cnt(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._burst_sample_cnt_thread, value)

    def _burst_sample_cnt_thread(self, device, channel, value):
        # filter out empty or non-Int-like input
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.burst_sample_cnt = value
        result = channel.burst_sample_cnt
        self.burstSampleCnt.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _burst_seg_cnt_cnt(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._burst_seg_cnt_thread, value)

    def _burst_seg_cnt_thread(self, device, channel, value):
        # filter out empty or non-Int-like input
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.burst_seg_cnt = value
        result = channel.burst_seg_cnt
        self.burstSegCnt.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _burst_delay(self, value):
        self.front_to_back_connector.access_gen_ch_property(self._burst_delay_thread, value)

    def _burst_delay_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.burst_delay = value

        result = channel.burst_delay
        self.burstDelay.emit(device.id, channel.id['No'], result)
