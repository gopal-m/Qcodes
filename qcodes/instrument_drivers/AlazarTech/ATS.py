import ctypes
import logging
import numpy as np
import os

from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import Parameter

# TODO logging

# these items are important for generalizing this code to multiple alazar cards
# TODO remove 8 bits per sample requirement
# TODO some alazar cards have a different number of channels :(


class AlazarTech_ATS(Instrument):

    def __init__(self, name):
        super().__init__(name)
        # Make sure the dll is located at "C:\\WINDOWS\\System32\\ATSApi"
        self._ATS9870_dll = ctypes.cdll.LoadLibrary('C:\\WINDOWS\\System32\\ATSApi')

        # TODO make the board id more general such that more than one card per system configurations are supported
        self._handle = self._ATS9870_dll.AlazarGetBoardBySystemID(1, 1)
        if not self._handle:
            raise Exception("AlazarTech_ATS not found")

        # TODO do something with board kind here

        # TODO is the succes code always 512 (for any board)?
        self._succes = 512

    def config(self, clock_source=None, sample_rate=None, clock_edge=None, decimation=None, coupling=None,
               channel_range=None, impedence=None, bwlimit=None, trigger_operation=None,
               trigger_engine1=None, trigger_source1=None, trigger_slope1=None, trigger_level1=None,
               trigger_engine2=None, trigger_source2=None, trigger_slope2=None, trigger_level2=None,
               external_trigger_coupling=None, trigger_range=None, trigger_delay=None, timeout_ticks=None):

        # region set parameters from args

        if clock_source is not None:
            self.parameters['clock_source']._set(clock_source)
        if sample_rate is not None:
            self.parameters['sample_rate']._set(sample_rate)
        if clock_edge is not None:
            self.parameters['clock_edge']._set(clock_edge)
        if decimation is not None:
            self.parameters['decimation']._set(decimation)

        if coupling is not None:
            for i, v in enumerate(coupling):
                self.parameters['coupling'+str(i)]._set(v)
        if channel_range is not None:
            for i, v in enumerate(channel_range):
                self.parameters['range'+str(i)]._set(v)
        if impedence is not None:
            for i, v in enumerate(impedence):
                self.parameters['impedence'+str(i)]._set(v)
        if bwlimit is not None:
            for i, v in enumerate(bwlimit):
                self.parameters['bwlimit'+str(i)]._set(v)

        if trigger_operation is not None:
            self.parameters['trigger_operation']._set(trigger_operation)
        if trigger_engine1 is not None:
            self.parameters['trigger_engine1']._set(trigger_engine1)
        if trigger_source1 is not None:
            self.parameters['trigger_source1']._set(trigger_source1)
        if trigger_slope1 is not None:
            self.parameters['trigger_slope1']._set(trigger_slope1)
        if trigger_level1 is not None:
            self.parameters['trigger_level1']._set(trigger_level1)

        if trigger_engine2 is not None:
            self.parameters['trigger_engine2']._set(trigger_engine2)
        if trigger_source2 is not None:
            self.parameters['trigger_source2']._set(trigger_source2)
        if trigger_slope2 is not None:
            self.parameters['trigger_slope2']._set(trigger_slope2)
        if trigger_level2 is not None:
            self.parameters['trigger_level2']._set(trigger_level2)

        if external_trigger_coupling is not None:
            self.parameters['external_trigger_coupling']._set(external_trigger_coupling)
        if trigger_range is not None:
            self.parameters['trigger_range']._set(trigger_range)
        if trigger_delay is not None:
            self.parameters['trigger_delay']._set(trigger_delay)
        if timeout_ticks is not None:
            self.parameters['timeout_ticks']._set(timeout_ticks)
        # endregion

        return_code = self._ATS9870_dll.AlazarSetCaptureClock(self._handle,
                                                              self.parameters['clock_source']._get_byte(),
                                                              self.parameters['sample_rate']._get_byte(),
                                                              self.parameters['clock_edge']._get_byte(),
                                                              self.parameters['decimation']._get_byte())
        self._result_handler(error_code=return_code, error_source="AlazarSetCaptureClock")
        self.parameters['clock_source']._set_updated()
        self.parameters['sample_rate']._set_updated()
        self.parameters['clock_edge']._set_updated()
        self.parameters['decimation']._set_updated()

        for i in [1, 2]:
            return_code = self._ATS9870_dll.AlazarInputControl(self._handle,
                                                               i,
                                                               self.parameters['coupling'+str(i)]._get_byte(),
                                                               self.parameters['range'+str(i)]._get_byte(),
                                                               self.parameters['impedence'+str(i)]._get_byte())
            self._result_handler(error_code=return_code, error_source="AlazarInputControl " + str(i))
            self.parameters['coupling'+str(i)]._set_updated()
            self.parameters['range'+str(i)]._set_updated()
            self.parameters['impedence'+str(i)]._set_updated()

            return_code = self._ATS9870_dll.AlazarSetBWLimit(self._handle,
                                                             i,
                                                             self.parameters['bwlimit'+str(i)]._get_byte())
            self._result_handler(error_code=return_code, error_source="AlazarSetBWLimit " + str(i))
            self.parameters['bwlimit'+str(i)]._set_updated()

        return_code = self._ATS9870_dll.AlazarSetTriggerOperation(self._handle,
                                                                  self.parameters['trigger_operation']._get_byte(),
                                                                  self.parameters['trigger_engine1']._get_byte(),
                                                                  self.parameters['trigger_source1']._get_byte(),
                                                                  self.parameters['trigger_slope1']._get_byte(),
                                                                  self.parameters['trigger_level1']._get_byte(),
                                                                  self.parameters['trigger_engine2']._get_byte(),
                                                                  self.parameters['trigger_source2']._get_byte(),
                                                                  self.parameters['trigger_slope2']._get_byte(),
                                                                  self.parameters['trigger_level2']._get_byte())
        self._result_handler(error_code=return_code, error_source="AlazarSetTriggerOperation")
        self.parameters['trigger_operation']._set_updated()
        self.parameters['trigger_engine1']._set_updated()
        self.parameters['trigger_source1']._set_updated()
        self.parameters['trigger_slope1']._set_updated()
        self.parameters['trigger_level1']._set_updated()
        self.parameters['trigger_engine2']._set_updated()
        self.parameters['trigger_source2']._set_updated()
        self.parameters['trigger_slope2']._set_updated()
        self.parameters['trigger_level2']._set_updated()

        return_code = self._ATS9870_dll.AlazarSetExternalTrigger(self._handle,
                                                                 self.parameters['external_trigger_coupling']._get_byte(),
                                                                 self.parameters['trigger_range']._get_byte())
        self._result_handler(error_code=return_code, error_source="AlazarSetExternalTrigger")
        self.parameters['external_trigger_coupling']._set_updated()
        self.parameters['trigger_range']._set_updated()

        return_code = self._ATS9870_dll.AlazarSetTriggerDelay(self._handle,
                                                              self.parameters['trigger_delay']._get_byte())
        self._result_handler(error_code=return_code, error_source="AlazarSetTriggerDelay")
        self.parameters['trigger_delay']._set_updated()

        return_code = self._ATS9870_dll.AlazarSetTriggerTimeOut(self._handle,
                                                                self.parameters['timeout_ticks']._get_byte())
        self._result_handler(error_code=return_code, error_source="AlazarSetTriggerTimeOut")
        self.parameters['timeout_ticks']._set_updated()

        # TODO config AUXIO

    def acquire(self, mode=None, samples_per_record=None, records_per_buffer=None, buffers_per_acquisition=None,
                channel_selection=None, transfer_offset=None, external_startcapture=None, enable_record_headers=None,
                alloc_buffers=None, fifo_only_streaming=None, interleave_samples=None, get_processed_data=None):
        # region set parameters from args
        if mode is not None:
            self.parameters['mode']._set(mode)
        if samples_per_record is not None:
            self.parameters['samples_per_record']._set(samples_per_record)
        if records_per_buffer is not None:
            self.parameters['records_per_buffer']._set(records_per_buffer)
        if buffers_per_acquisition is not None:
            self.parameters['buffers_per_acquisition']._set(buffers_per_acquisition)
        if channel_selection is not None:
            self.parameters['channel_selection']._set(channel_selection)
        if transfer_offset is not None:
            self.parameters['transfer_offset']._set(transfer_offset)
        if external_startcapture is not None:
            self.parameters['external_starcapture']._set(external_startcapture)
        if enable_record_headers is not None:
            self.parameters['enable_record_headers']._set(enable_record_headers)
        if alloc_buffers is not None:
            self.parameters['alloc_buffers']._set(alloc_buffers)
        if fifo_only_streaming is not None:
            self.parameters['fifo_only_streaming']._set(fifo_only_streaming)
        if interleave_samples is not None:
            self.parameters['interleave_samples']._set(interleave_samples)
        if get_processed_data is not None:
            self.parameters['get_processed_data']._set(get_processed_data)

        # endregion

        if not (self.parameters['mode'].get() == 'TS' or self.parameters['mode'].get() == 'NPT'):
            raise Exception("Only the 'TS' and 'NPT' modes are implemented at this point")

        return_code = self._ATS9870_dll.AlazarAbortAsyncRead(self._handle)
        self._result_handler(error_code=return_code, error_source="AlazarAbortAsyncRead")

        # get channel info
        bps = np.array([0], dtype=np.uint8)  # bps bits per sample
        max_s = np.array([0], dtype=np.uint32)  # max_s memory size in samples
        return_code = self._ATS9870_dll.AlazarGetChannelInfo(self._handle, max_s.ctypes.data, bps.ctypes.data)
        self._result_handler(error_code=return_code, error_source="AlazarGetChannelInfo")
        bps = bps[0]
        max_s = max_s[0]
        if not bps == 8:
            raise Exception("Only 8 bits per sample supported at this moment")

        if self.parameters['mode'].get() == 'NPT':
            pretriggersize = 0  # pretriggersize is 0 for NPT always
            post_trigger_size = self.parameters['samples_per_record']._get_byte()
            return_code = self._ATS9870_dll.AlazarSetRecordSize(self._handle, pretriggersize, post_trigger_size)
            self._result_handler(error_code=return_code, error_source="AlazarSetRecordSize")

        if self.parameters['channel_selection']._get_byte() == 3:
            number_of_channels = 2
        else:
            number_of_channels = 1
        samples_per_buffer = 0
        acquire_flags = self.parameters['mode']._get_byte() | \
                        self.parameters['external_startcapture']._get_byte() | \
                        self.parameters['enable_record_headers']._get_byte() | \
                        self.parameters['alloc_buffers']._get_byte() | \
                        self.parameters['fifo_only_streaming']._get_byte() | \
                        self.parameters['interleave_samples']._get_byte() | \
                        self.parameters['get_processed_data']._get_byte()
        if self.parameters['mode'].get() == 'NPT':
            samples_per_record = self.parameters['samples_per_record']._get_byte()
            records_per_buffer = self.parameters['records_per_buffer']._get_byte()
            records_per_acquisition = records_per_buffer * self.parameters['buffers_per_acquisition']._get_byte()
            samples_per_buffer = samples_per_record * records_per_buffer
            return_code = self._ATS9870_dll.AlazarBeforeAsyncRead(self._handle,
                                                                  self.parameters['channel_selection']._get_byte(),
                                                                  self.parameters['transfer_offset']._get_byte(),
                                                                  samples_per_record,
                                                                  records_per_buffer,
                                                                  records_per_acquisition,
                                                                  acquire_flags)
            self._result_handler(error_code=return_code, error_source="AlazarBeforeAsyncRead")
        elif self.parameters['mode'].get() == 'TS':
            if not self.parameters['samples_per_record']._get_byte() % self.parameters['buffers_per_acquisition'] == 0:
                logging.warning("buffers_per_acquisition is not a divisor of samples per record which it should be in"
                                " TS mode, rounding down in samples per buffer calculation")
            samples_per_buffer = int(self.parameters['samples_per_record']._get_byte() / self.parameters['buffers_per_acquisition'])
            buffers_per_acquisition = self.parameters['buffers_per_acquisition']._get_byte()
            if not self.parameters['records_per_buffer']._get_byte() == 1:
                logging.warning('records_per_buffer should be 1 in TS mode, defauling to 1')
                self.parameters['records_per_buffer']._set(1)
            records_per_buffer = self.parameters['records_per_buffer']._get_byte()
            return_code = self._ATS9870_dll.AlazarBeforeAsyncRead(self._handle,
                                                                  self.parameters['channel_selection']._get_byte(),
                                                                  self.parameters['transfer_offset']._get_byte(),
                                                                  samples_per_buffer,
                                                                  records_per_buffer,
                                                                  buffers_per_acquisition,
                                                                  acquire_flags)
            self._result_handler(error_code=return_code, error_source="AlazarBeforeAsyncRead")
        self.parameters['samples_per_record']._set_updated()
        self.parameters['records_per_buffer']._set_updated()
        self.parameters['buffers_per_acquisition']._set_updated()
        self.parameters['channel_selection']._set_updated()
        self.parameters['transfer_offset']._set_updated()
        self.parameters['mode']._set_updated()
        self.parameters['external_starcapture']._set_updated()
        self.parameters['enable_record_headers']._set_updated()
        self.parameters['alloc_buffers']._set_updated()
        self.parameters['fifo_only_streaming']._set_updated()
        self.parameters['interleave_samples']._set_updated()
        self.parameters['get_processed_data']._set_updated()

        for buf in self.buflist:
            return_code = self._ATS9870_dll.AlazarPostAsyncBuffer(self._handle, buf.addr, buf.size_bytes)
            self._result_handler(error_code=return_code, error_source="AlazarPostAsyncBuffer")

        return_code = self._ATS9870_dll.AlazarStartCapture(self._handle)
        self._result_handler(error_code=return_code, error_source="AlazarStartCapture")

        while BuffersCompleted < BuffersPerAcquisition:
            return_code = self._ATS9870_dll.AlazarWaitAsyncBufferComplete(self._handle, buf.addr, self.waittimeout)
            self._result_handler(error_code=return_code, error_source="AlazarWaitAsyncBufferComplete")

            return_code = self._ATS9870_dll.AlazarPostAsyncBuffer(self._handle, buf.addr, buf.size_bytes)
            self._result_handler(error_code=return_code, error_source="AlazarPostAsyncBuffer")

        return_code = self._ATS9870_dll.AlazarAbortAsyncRead(self._handle)
        self._result_handler(error_code=return_code, error_source="AlazarAbortAsyncRead")

    def _result_handler(self, error_code=0, error_source=""):
        # region error codes
        error_codes = {513: 'ApiFailed', 514: 'ApiAccessDenied', 515: 'ApiDmaChannelUnavailable',
                       516: 'ApiDmaChannelInvalid', 517: 'ApiDmaChannelTypeError', 518: 'ApiDmaInProgress',
                       519: 'ApiDmaDone', 520: 'ApiDmaPaused', 521: 'ApiDmaNotPaused',
                       522: 'ApiDmaCommandInvalid', 523: 'ApiDmaManReady', 524: 'ApiDmaManNotReady',
                       525: 'ApiDmaInvalidChannelPriority', 526: 'ApiDmaManCorrupted',
                       527: 'ApiDmaInvalidElementIndex', 528: 'ApiDmaNoMoreElements',
                       529: 'ApiDmaSglInvalid',
                       530: 'ApiDmaSglQueueFull', 531: 'ApiNullParam', 532: 'ApiInvalidBusIndex',
                       533: 'ApiUnsupportedFunction', 534: 'ApiInvalidPciSpace', 535: 'ApiInvalidIopSpace',
                       536: 'ApiInvalidSize', 537: 'ApiInvalidAddress', 538: 'ApiInvalidAccessType',
                       539: 'ApiInvalidIndex', 540: 'ApiMuNotReady', 541: 'ApiMuFifoEmpty',
                       542: 'ApiMuFifoFull',
                       543: 'ApiInvalidRegister', 544: 'ApiDoorbellClearFailed', 545: 'ApiInvalidUserPin',
                       546: 'ApiInvalidUserState', 547: 'ApiEepromNotPresent',
                       548: 'ApiEepromTypeNotSupported',
                       549: 'ApiEepromBlank', 550: 'ApiConfigAccessFailed', 551: 'ApiInvalidDeviceInfo',
                       552: 'ApiNoActiveDriver', 553: 'ApiInsufficientResources',
                       554: 'ApiObjectAlreadyAllocated',
                       555: 'ApiAlreadyInitialized', 556: 'ApiNotInitialized',
                       557: 'ApiBadConfigRegEndianMode', 558: 'ApiInvalidPowerState', 559: 'ApiPowerDown',
                       560: 'ApiFlybyNotSupported',
                       561: 'ApiNotSupportThisChannel', 562: 'ApiNoAction', 563: 'ApiHSNotSupported',
                       564: 'ApiVPDNotSupported', 565: 'ApiVpdNotEnabled', 566: 'ApiNoMoreCap',
                       567: 'ApiInvalidOffset',
                       568: 'ApiBadPinDirection', 569: 'ApiPciTimeout', 570: 'ApiDmaChannelClosed',
                       571: 'ApiDmaChannelError', 572: 'ApiInvalidHandle', 573: 'ApiBufferNotReady',
                       574: 'ApiInvalidData',
                       575: 'ApiDoNothing', 576: 'ApiDmaSglBuildFailed', 577: 'ApiPMNotSupported',
                       578: 'ApiInvalidDriverVersion',
                       579: 'ApiWaitTimeout: operation did not finish during timeout interval. Check your trigger.',
                       580: 'ApiWaitCanceled', 581: 'ApiBufferTooSmall',
                       582: 'ApiBufferOverflow:rate of acquiring data > rate of transferring data to local memory. Try reducing sample rate, reducing number of enabled channels, increasing size of each DMA buffer or increase number of DMA buffers.',
                       583: 'ApiInvalidBuffer', 584: 'ApiInvalidRecordsPerBuffer',
                       585: 'ApiDmaPending:Async I/O operation was succesfully started, it will be completed when sufficient trigger events are supplied to fill the buffer.',
                       586: 'ApiLockAndProbePagesFailed:Driver or operating system was unable to prepare the specified buffer for DMA transfer. Try reducing buffer size or total number of buffers.',
                       587: 'ApiWaitAbandoned', 588: 'ApiWaitFailed',
                       589: 'ApiTransferComplete:This buffer is last in the current acquisition.',
                       590: 'ApiPllNotLocked:hardware error, contact AlazarTech',
                       591: 'ApiNotSupportedInDualChannelMode:Requested number of samples per channel is too large to fit in on-board memory. Try reducing number of samples per channel, or switch to single channel mode.'}
        # endregion
        if error_code == self._succes:
            return None
        else:
            # TODO log error

            if error_code not in error_codes:
                raise KeyError(error_source+" raised unknown error "+str(error_code))
            raise Exception(error_source+" raised "+str(error_code)+": "+error_codes[error_code])


class AlazarParameter(Parameter):
    def __init__(self, name=None, label=None, unit=None, value=None, byte_to_value_dict=None):
        # TODO implement trivial dictionary
        # TODO implement restrictions for trivial dictionary case
        super().__init__(name=name, label=label, unit=unit)
        self._byte = None
        self._uptodate_flag = True
        self._byte_to_value_dict = byte_to_value_dict
        # TODO check this line
        self._value_to_byte_dict = {v: k for k, v in self._byte_to_value_dict}

        self._set(value)

    def get(self):
        """
        This method returns the name of the value set for this parameter
        :return: value
        """
        # TODO test this exception
        if self._uptodate_flag is False:
            raise Exception('The value of this parameter is not up to date with the actual value in the instrument.'
                            '\n Most probable cause is illegal usage of ._set() method of this parameter.'
                            '\n Don\'t use private methods if you do not know what you are doing!')
        return self._byte_to_value_dict[self._byte]

    def _get_byte(self):
        """
        this method gets the byte representation of the value of the parameter
        :return: byte representation
        """
        return self._byte

    def _set(self, value):
        """
        This method sets the value of this parameter
        This method is private to ensure that all values in the instruments are up to date always
        :param value: the new value (e.g. 'NPT', 0.5, ...)
        :return: None
        """

        # TODO test this exception handling
        if value not in self._value_to_byte_dict:
            raise KeyError('Value "'+str(value)+'" unknown setting in parameter "'+str(self.name)+'"')
        self._byte = self._value_to_byte_dict[value]
        self._uptodate_flag = False
        return None

    def _set_updated(self):
        self._uptodate_flag = True


class Buffer:
    def __init__(self, bits_per_sample, samples_per_buffer, number_of_channels):
        if not bits_per_sample == 8:
            raise Exception("Buffer: only 8 bit per sample supported")
        if not os.name == 'nt':
            raise Exception("Buffer: only Windows supported at this moment")
        self._allocated = True

        # try to allocate memory
        mem_commit = 0x1000
        page_readwrite = 0x4

        size_bytes = samples_per_buffer * number_of_channels

        # please see https://msdn.microsoft.com/en-us/library/windows/desktop/aa366887(v=vs.85).aspx for documentation
        ctypes.windll.kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_long, ctypes.c_long, ctypes.c_long]
        ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_void_p
        self.addr = ctypes.windll.kernel32.VirtualAlloc(0, ctypes.c_long(size_bytes), mem_commit, page_readwrite)
        if self.addr is None:
            self._allocated = False
            e = ctypes.windll.kernel32.GetLastError()
            raise Exception("Memory allocation error: " + str(e))

        ctypes_array = (ctypes.c_uint8 * size_bytes).from_address(self.addr)
        self.buffer = np.frombuffer(ctypes_array, dtype=np.uint8)
        pointer, read_only_flag = self.buffer.__array_interface__['data']

    def free_mem(self):
        mem_release = 0x8000

        # see https://msdn.microsoft.com/en-us/library/windows/desktop/aa366892(v=vs.85).aspx
        ctypes.windll.kernel32.VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_long, ctypes.c_long]
        ctypes.windll.kernel32.VirtualFree.restype = ctypes.c_int
        ctypes.windll.kernel32.VirtualFree(ctypes.c_void_p(self.addr), 0, mem_release)
        self._allocated = False

    def __del__(self):
        if self._allocated:
            self.free_mem()
            logging.warning("Buffer prevented memory leak; Memory released to Windows.\n"
                            "Memory should have been released before buffer was deleted.")