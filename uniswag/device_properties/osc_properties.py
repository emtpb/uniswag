import re

from PySide6 import QtCore


# noinspection PyCallingNonCallable
class OscProperties(QtCore.QObject):

    # signals that indicate a device property access has been completed,
    # contain device id and current/new property value
    isRunning = QtCore.Signal('QVariantMap', bool)
    reset = QtCore.Signal('QVariantMap', bool)
    measureModesAvail = QtCore.Signal('QVariantMap', list)
    measureMode = QtCore.Signal('QVariantMap', str)
    autoResAvail = QtCore.Signal('QVariantMap', list)
    autoRes = QtCore.Signal('QVariantMap', str)
    resAvail = QtCore.Signal('QVariantMap', list)
    res = QtCore.Signal('QVariantMap', int)
    sampleFreq = QtCore.Signal('QVariantMap', float)
    recLen = QtCore.Signal('QVariantMap', int)
    clockSrcAvail = QtCore.Signal('QVariantMap', list)
    clockSrc = QtCore.Signal('QVariantMap', str)
    clockOutsAvail = QtCore.Signal('QVariantMap', list)
    clockOut = QtCore.Signal('QVariantMap', str)
    preSampleRatio = QtCore.Signal('QVariantMap', float)
    segCnt = QtCore.Signal('QVariantMap', int)
    trigTimeout = QtCore.Signal('QVariantMap', float)
    trigDelay = QtCore.Signal('QVariantMap', float)
    trigHoldoff = QtCore.Signal('QVariantMap', float)
    trigModesAvail = QtCore.Signal('QVariantMap', list)
    trigMode = QtCore.Signal('QVariantMap', str)
    trigSweepsAvail = QtCore.Signal('QVariantMap', list)
    trigSweep = QtCore.Signal('QVariantMap', str)
    trigSlopesAvail = QtCore.Signal('QVariantMap', list)
    trigSlope = QtCore.Signal('QVariantMap', str)
    timeBase = QtCore.Signal('QVariantMap', float)

    # signals that indicate a channel property access has been completed,
    # contain device id, channel number and current/new property value
    operandsAvail = QtCore.Signal('QVariantMap', int, list)
    operand1 = QtCore.Signal('QVariantMap', int, str)
    operand2 = QtCore.Signal('QVariantMap', int, str)
    operatorsAvail = QtCore.Signal('QVariantMap', int, list)
    operator = QtCore.Signal('QVariantMap', int, str)
    shift = QtCore.Signal('QVariantMap', int, float)
    couplingsAvail = QtCore.Signal('QVariantMap', int, list)
    coupling = QtCore.Signal('QVariantMap', int, str)
    probeGain = QtCore.Signal('QVariantMap', int, float)
    probeOffset = QtCore.Signal('QVariantMap', int, float)
    isAutoRange = QtCore.Signal('QVariantMap', int, bool)
    rangesAvail = QtCore.Signal('QVariantMap', int, list)
    range = QtCore.Signal('QVariantMap', int, float)
    isTrigAvail = QtCore.Signal('QVariantMap', int, bool)
    isTrigEnabled = QtCore.Signal('QVariantMap', int, bool)
    trigKindsAvail = QtCore.Signal('QVariantMap', int, list)
    trigKind = QtCore.Signal('QVariantMap', int, str)
    trigLvl = QtCore.Signal('QVariantMap', int, list)
    trigHyst = QtCore.Signal('QVariantMap', int, list)
    trigCondAvail = QtCore.Signal('QVariantMap', int, list)
    trigCond = QtCore.Signal('QVariantMap', int, str)
    trigTime = QtCore.Signal('QVariantMap', int, list)

    def __init__(self, front_to_back_connector):
        """
        A supplementary interface between frontend & backend
        specifically dedicated to getting & setting oscilloscope properties.
        Inherits from QtCore.QObject.

        Frontend can call its methods to display and change the currently selected device's (channel) settings.
        In order to determine that device, the main interface connecting front- & backend is consulted.

        Args:
            front_to_back_connector (uniswag.front_to_back_connector.FrontToBackConnector):
                The main interface connecting front- to backend.

        Returns:
            OscProperties:
                An OscProperties object.
        """
        super(OscProperties, self).__init__()

        # the main interface connecting front- to backend,
        # provides information about the currently selected oscilloscope (and oscilloscope channel)
        self.front_to_back_connector = front_to_back_connector

        # a regular expression used to split an input string that is formatted as a list into an actual Python list
        self._re_list_filter = '[][\'\", ]'

    # OSCILLOSCOPE FUNCTIONS ###########################################################################################

    @QtCore.Slot()
    def _add_ch(self):
        self.front_to_back_connector.access_osc_property(self._add_ch_thread)

    def _add_ch_thread(self, device):
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        # add one channel
        added_ch = device.add_ch()
        print('Added one channel to ' + dev_id)

        self.front_to_back_connector.channel_list_update('add', device, added_ch)

    @QtCore.Slot()
    def _remove_ch(self):
        self.front_to_back_connector.access_osc_property(self._remove_ch_thread)

    def _remove_ch_thread(self, device):
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        # remove latest added channel
        removed_ch = device.remove_ch()
        if removed_ch is None:
            print(dev_id + ' is currently running or has only one channel left; could not remove a channel')
        else:
            print('Removed one channel from ' + dev_id)
            self.front_to_back_connector.remove_visible_ch(device.id, removed_ch['No'])
            self.front_to_back_connector.channel_list_update('remove', device, removed_ch)

    @QtCore.Slot()
    def _is_running(self):
        self.front_to_back_connector.access_osc_property(self._is_running_thread)

    def _is_running_thread(self, device):
        result = device.is_running
        self.isRunning.emit(device.id, result)

    @QtCore.Slot()
    def _start_n_stop(self):
        self.front_to_back_connector.access_osc_property(self._start_n_stop_thread)

    def _start_n_stop_thread(self, device):
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        # start the measurement if it is not already running
        if not device.is_running:
            success = device.start()
            if success:
                print(dev_id + ' started')
            else:
                print('Could not start ' + dev_id)

        # stop the measurement if it is currently running
        else:
            success = device.stop()
            if success:
                print(dev_id + ' stopped')
            else:
                print('Could not stop ' + dev_id)

        result = device.is_running
        self.isRunning.emit(device.id, result)

    @QtCore.Slot()
    def _force_trig(self):
        self.front_to_back_connector.access_osc_property(self._force_trig_thread)

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
    def _reset(self):
        self.front_to_back_connector.access_osc_property(self._reset_thread)

    def _reset_thread(self, device):
        dev_id = device.id['Vendor'] + ' ' + device.id['Name'] + ' (' + device.id['SerNo'] + ')'

        # reset the device
        device.reset()
        print(dev_id + ' was manually reset')
        self.reset.emit(device.id, True)

    @QtCore.Slot()
    def _measure_modes_avail(self):
        self.front_to_back_connector.access_osc_property(self._measure_modes_avail_thread)

    def _measure_modes_avail_thread(self, device):
        result = device.measure_modes_avail
        self.measureModesAvail.emit(device.id, result)
        self._measure_mode_thread(device, None)

    @QtCore.Slot(str)
    def _measure_mode(self, value):
        self.front_to_back_connector.access_osc_property(self._measure_mode_thread, value)

    def _measure_mode_thread(self, device, value):
        if value is not None:
            device.measure_mode = value
        result = device.measure_mode
        self.measureMode.emit(device.id, result)

    @QtCore.Slot()
    def _auto_res_avail(self):
        self.front_to_back_connector.access_osc_property(self._auto_res_avail_thread)

    def _auto_res_avail_thread(self, device):
        result = device.auto_res_avail
        self.autoResAvail.emit(device.id, result)
        self._auto_res_thread(device, None)

    @QtCore.Slot(str)
    def _auto_res(self, value):
        self.front_to_back_connector.access_osc_property(self._auto_res_thread, value)

    def _auto_res_thread(self, device, value):
        if value is not None:
            device.auto_res = value
        result = device.auto_res
        self.autoRes.emit(device.id, result)

    @QtCore.Slot()
    def _res_avail(self):
        self.front_to_back_connector.access_osc_property(self._res_avail_thread)

    def _res_avail_thread(self, device):
        result = device.res_avail
        self.resAvail.emit(device.id, result)
        self._res_thread(device, None)

    @QtCore.Slot(str)
    def _res(self, value):
        self.front_to_back_connector.access_osc_property(self._res_thread, value)

    def _res_thread(self, device, value):
        if value is not None:
            device.res = int(value)
        result = device.res
        self.res.emit(device.id, result)

    @QtCore.Slot(str)
    def _sample_freq(self, value):
        self.front_to_back_connector.access_osc_property(self._sample_freq_thread, value)

    def _sample_freq_thread(self, device, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.sample_freq = value
        result = device.sample_freq
        self.sampleFreq.emit(device.id, result)

    @QtCore.Slot(str)
    def _rec_len(self, value):
        self.front_to_back_connector.access_osc_property(self._rec_len_thread, value)

    def _rec_len_thread(self, device, value):
        # filter out empty or non-Int-like input
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.rec_len = value
        result = device.rec_len
        self.recLen.emit(device.id, result)

    @QtCore.Slot()
    def _clock_src_avail(self):
        self.front_to_back_connector.access_osc_property(self._clock_src_avail_thread)

    def _clock_src_avail_thread(self, device):
        result = device.clock_src_avail
        self.clockSrcAvail.emit(device.id, result)
        self._clock_src_thread(device, None)

    @QtCore.Slot(str)
    def _clock_src(self, value):
        self.front_to_back_connector.access_osc_property(self._clock_src_thread, value)

    def _clock_src_thread(self, device, value):
        if value is not None:
            device.clock_src = value
        result = device.clock_src
        self.clockSrc.emit(device.id, result)

    @QtCore.Slot()
    def _clock_outs_avail(self):
        self.front_to_back_connector.access_osc_property(self._clock_outs_avail_thread)

    def _clock_outs_avail_thread(self, device):
        result = device.clock_outs_avail
        self.clockOutsAvail.emit(device.id, result)
        self._clock_out_thread(device, None)

    @QtCore.Slot(str)
    def _clock_out(self, value):
        self.front_to_back_connector.access_osc_property(self._clock_out_thread, value)

    def _clock_out_thread(self, device, value):
        if value is not None:
            device.clock_out = value
        result = device.clock_out
        self.clockOut.emit(device.id, result)

    @QtCore.Slot(str)
    def _pre_sample_ratio(self, value):
        self.front_to_back_connector.access_osc_property(self._pre_sample_ratio_thread, value)

    def _pre_sample_ratio_thread(self, device, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.pre_sample_ratio = value
        result = device.pre_sample_ratio
        self.preSampleRatio.emit(device.id, result)

    @QtCore.Slot(str)
    def _seg_cnt(self, value):
        self.front_to_back_connector.access_osc_property(self._seg_cnt_thread, value)

    def _seg_cnt_thread(self, device, value):
        # filter out empty or non-Int-like input
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.seg_cnt = value
        result = device.seg_cnt
        self.segCnt.emit(device.id, result)

    @QtCore.Slot(str)
    def _trig_timeout(self, value):
        self.front_to_back_connector.access_osc_property(self._trig_timeout_thread, value)

    def _trig_timeout_thread(self, device, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.trig_timeout = value
        result = device.trig_timeout
        self.trigTimeout.emit(device.id, result)

    @QtCore.Slot(str)
    def _trig_delay(self, value):
        self.front_to_back_connector.access_osc_property(self._trig_delay_thread, value)

    def _trig_delay_thread(self, device, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.trig_delay = value
        result = device.trig_delay
        self.trigDelay.emit(device.id, result)

    @QtCore.Slot(str)
    def _trig_holdoff(self, value):
        self.front_to_back_connector.access_osc_property(self._trig_holdoff_thread, value)

    def _trig_holdoff_thread(self, device, value):
        # filter out empty or non-Int-like input
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            device.trig_holdoff = value
        result = device.trig_holdoff
        self.trigHoldoff.emit(device.id, result)

    @QtCore.Slot()
    def _trig_modes_avail(self):
        self.front_to_back_connector.access_osc_property(self._trig_modes_avail_thread)

    def _trig_modes_avail_thread(self, device):
        result = device.trig_modes_avail
        self.trigModesAvail.emit(device.id, result)
        self._trig_mode_thread(device, None)

    @QtCore.Slot(str)
    def _trig_mode(self, value):
        self.front_to_back_connector.access_osc_property(self._trig_mode_thread, value)

    def _trig_mode_thread(self, device, value):
        if value is not None:
            device.trig_mode = value
        result = device.trig_mode
        self.trigMode.emit(device.id, result)

    @QtCore.Slot()
    def _trig_sweeps_avail(self):
        self.front_to_back_connector.access_osc_property(self._trig_sweeps_avail_thread)

    def _trig_sweeps_avail_thread(self, device):
        result = device.trig_sweeps_avail
        self.trigSweepsAvail.emit(device.id, result)
        self._trig_sweep_thread(device, None)

    @QtCore.Slot(str)
    def _trig_sweep(self, value):
        self.front_to_back_connector.access_osc_property(self._trig_sweep_thread, value)

    def _trig_sweep_thread(self, device, value):
        if value is not None:
            device.trig_sweep = value
        result = device.trig_sweep
        self.trigSweep.emit(device.id, result)

    @QtCore.Slot()
    def _trig_slopes_avail(self):
        self.front_to_back_connector.access_osc_property(self._trig_slopes_avail_thread)

    def _trig_slopes_avail_thread(self, device):
        result = device.trig_slopes_avail
        self.trigSlopesAvail.emit(device.id, result)
        self._trig_slope_thread(device, None)

    @QtCore.Slot(str)
    def _trig_slope(self, value):
        self.front_to_back_connector.access_osc_property(self._trig_slope_thread, value)

    def _trig_slope_thread(self, device, value):
        if value is not None:
            device.trig_slope = value
        result = device.trig_slope
        self.trigSlope.emit(device.id, result)

    @QtCore.Slot(str)
    def _time_base(self, value):
        self.front_to_back_connector.access_osc_property(self._time_base_thread, value)

    def _time_base_thread(self, device, value):
        if value is not None:
            device.time_base = float(value)
        result = device.time_base
        self.timeBase.emit(device.id, result)

    # OSCILLOSCOPE CHANNEL FUNCTIONS ###################################################################################

    @QtCore.Slot()
    def _operands_avail(self):
        self.front_to_back_connector.access_osc_ch_property(self._operands_avail_thread)

    def _operands_avail_thread(self, device, channel):
        # get the keys from a dictionary that maps tuples of oscilloscope and channel objects to descriptive strings
        result = list(channel.operands_avail.keys())

        self.operandsAvail.emit(device.id, channel.id['No'], result)
        self._operand1_thread(device, channel, None)
        self._operand2_thread(device, channel, None)

    @QtCore.Slot(str)
    def _operand1(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._operand1_thread, value)

    def _operand1_thread(self, device, channel, value):
        if value is not None:
            channel.operand1 = value
        result = channel.operand1
        self.operand1.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _operand2(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._operand2_thread, value)

    def _operand2_thread(self, device, channel, value):
        if value is not None:
            channel.operand2 = value
        result = channel.operand2
        self.operand2.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _operators_avail(self):
        self.front_to_back_connector.access_osc_ch_property(self._operators_avail_thread)

    def _operators_avail_thread(self, device, channel):
        result = channel.operators_avail
        self.operatorsAvail.emit(device.id, channel.id['No'], result)
        self._operator_thread(device, channel, None)

    @QtCore.Slot(str)
    def _operator(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._operator_thread, value)

    def _operator_thread(self, device, channel, value):
        if value is not None:
            channel.operator = value
        result = channel.operator
        self.operator.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _shift(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._shift_thread, value)

    def _shift_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.shift = value
        result = channel.shift
        self.shift.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _couplings_avail(self):
        self.front_to_back_connector.access_osc_ch_property(self._couplings_avail_thread)

    def _couplings_avail_thread(self, device, channel):
        result = channel.couplings_avail
        self.couplingsAvail.emit(device.id, channel.id['No'], result)
        self._coupling_thread(device, channel, None)

    @QtCore.Slot(str)
    def _coupling(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._coupling_thread, value)

    def _coupling_thread(self, device, channel, value):
        if value is not None:
            channel.coupling = value
        result = channel.coupling
        self.coupling.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _probe_gain(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._probe_gain_thread, value)

    def _probe_gain_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.probe_gain = value
        result = channel.probe_gain
        self.probeGain.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _probe_offset(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._probe_offset_thread, value)

    def _probe_offset_thread(self, device, channel, value):
        # filter out empty or non-Float-like input
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = None

        if value is not None:
            channel.probe_offset = value
        result = channel.probe_offset
        self.probeOffset.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _is_auto_range(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._is_auto_range_thread, value)

    def _is_auto_range_thread(self, device, channel, value):
        if value is not None:

            # String comparison necessary due to passed parameter being of type String, not Bool
            if value == 'true':
                channel.is_auto_range = True
            else:
                channel.is_auto_range = False

        result = channel.is_auto_range
        self.isAutoRange.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _ranges_avail(self):
        self.front_to_back_connector.access_osc_ch_property(self._ranges_avail_thread)

    def _ranges_avail_thread(self, device, channel):
        result = channel.ranges_avail
        self.rangesAvail.emit(device.id, channel.id['No'], result)
        self._range_thread(device, channel, None)

    @QtCore.Slot(str)
    def _range(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._range_thread, value)

    def _range_thread(self, device, channel, value):
        if value is not None:
            channel.range = float(value)
        result = channel.range
        self.range.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _is_trig_avail(self):
        self.front_to_back_connector.access_osc_ch_property(self._is_trig_avail_thread)

    def _is_trig_avail_thread(self, device, channel):
        result = channel.is_trig_avail
        self.isTrigAvail.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _is_trig_enabled(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._is_trig_enabled_thread, value)

    def _is_trig_enabled_thread(self, device, channel, value):
        if value is not None:

            # String comparison necessary due to passed parameter being of type String, not Bool
            if value == 'true':
                channel.is_trig_enabled = True
            else:
                channel.is_trig_enabled = False

        result = channel.is_trig_enabled
        self.isTrigEnabled.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _trig_kinds_avail(self):
        self.front_to_back_connector.access_osc_ch_property(self._trig_kinds_avail_thread)

    def _trig_kinds_avail_thread(self, device, channel):
        result = channel.trig_kinds_avail
        self.trigKindsAvail.emit(device.id, channel.id['No'], result)
        self._trig_kind_thread(device, channel, None)

    @QtCore.Slot(str)
    def _trig_kind(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._trig_kind_thread, value)

    def _trig_kind_thread(self, device, channel, value):
        if value is not None:
            channel.trig_kind = value
        result = channel.trig_kind
        self.trigKind.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _trig_lvl(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._trig_lvl_thread, value)

    def _trig_lvl_thread(self, device, channel, value):
        if value is not None:

            # split input by using the regular expression list filter
            val_list = re.split(self._re_list_filter, value)

            # remove empty list elements
            val_list = list(filter(None, val_list))

            valid = False

            # check whether the list still contains at least one element
            if val_list:
                valid = True

                # try to convert each list element into Float, abort if not possible
                for i in range(len(val_list)):
                    try:
                        val_list[i] = float(val_list[i])
                    except ValueError:
                        valid = False
                        break

            # set the channel's trigger levels (if all list elements are valid Float values)
            if valid:
                channel.trig_lvl = val_list

        result = channel.trig_lvl
        self.trigLvl.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _trig_hyst(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._trig_hyst_thread, value)

    def _trig_hyst_thread(self, device, channel, value):
        if value is not None:

            # split input by using the regular expression list filter
            val_list = re.split(self._re_list_filter, value)

            # remove empty list elements
            val_list = list(filter(None, val_list))

            valid = False

            # check whether the list still contains at least one element
            if val_list:
                valid = True

                # try to convert each list element into Float, abort if not possible
                for i in range(len(val_list)):
                    try:
                        val_list[i] = float(val_list[i])
                    except ValueError:
                        valid = False
                        break

            # set the channel's trigger hysteresises (if all list elements are valid Float values)
            if valid:
                channel.trig_hyst = val_list

        result = channel.trig_hyst
        self.trigHyst.emit(device.id, channel.id['No'], result)

    @QtCore.Slot()
    def _trig_cond_avail(self):
        self.front_to_back_connector.access_osc_ch_property(self._trig_cond_avail_thread)

    def _trig_cond_avail_thread(self, device, channel):
        result = channel.trig_cond_avail
        self.trigCondAvail.emit(device.id, channel.id['No'], result)
        self._trig_cond_thread(device, channel, None)

    @QtCore.Slot(str)
    def _trig_cond(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._trig_cond_thread, value)

    def _trig_cond_thread(self, device, channel, value):
        if value is not None:
            channel.trig_cond = value
        result = channel.trig_cond
        self.trigCond.emit(device.id, channel.id['No'], result)

    @QtCore.Slot(str)
    def _trig_time(self, value):
        self.front_to_back_connector.access_osc_ch_property(self._trig_time_thread, value)

    def _trig_time_thread(self, device, channel, value):
        if value is not None:

            # split input by using the regular expression list filter
            val_list = re.split(self._re_list_filter, value)

            # remove empty list elements
            val_list = list(filter(None, val_list))

            valid = False

            # check whether the list still contains at least one element
            if val_list:
                valid = True

                # try to convert each list element into Float, abort if not possible
                for i in range(len(val_list)):
                    try:
                        val_list[i] = float(val_list[i])
                    except ValueError:
                        valid = False
                        break

            # set the channel's trigger times (if all list elements are valid Float values)
            if valid:
                channel.trig_time = val_list

        result = channel.trig_time
        self.trigTime.emit(device.id, channel.id['No'], result)
