import time

from os.path import isfile
from PyQt5.QtCore import QObject, pyqtSlot

from instr.instrumentfactory import SemiconductorAnalyzerFactory, mock_enabled
from measureresult import MeasureResult


class InstrumentController(QObject):
    states = {
        i * 0.25: i for i in range(64)
    }

    main_states = [0, 1, 2, 4, 8, 16, 32, 63]

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.requiredInstruments = {
            'Анализатор п/п приборов': SemiconductorAnalyzerFactory('GPIB1::10::INSTR'),
        }

        self.deviceParams = {
            'Варикап': {
                'F': [1.15, 1.35, 1.75, 1.92, 2.25, 2.54, 2.7, 3, 3.47, 3.86, 4.25],
                'mul': 2,
                'P1': 15,
                'P2': 21,
                'Istat': [None, None, None],
                'Idyn': [None, None, None]
            },
        }

        if isfile('./params.ini'):
            import ast
            with open('./params.ini', 'rt', encoding='utf-8') as f:
                raw = ''.join(f.readlines())
                self.deviceParams = ast.literal_eval(raw)

        self.secondaryParams = {
            'Pin': -10,
            'F1': 4,
            'F2': 8,
            'kp': 0,
            'Fborder1': 4,
            'Fborder2': 8
        }

        self.sweep_points = 201
        self.cal_set = '-20db_pyatkin_6G'

        self._instruments = dict()
        self.found = False
        self.present = False
        self.hasResult = False
        self.only_main_states = False

        self.result = MeasureResult()

        self._freqs = list()

    def __str__(self):
        return f'{self._instruments}'

    def connect(self, addrs):
        print(f'searching for {addrs}')
        for k, v in addrs.items():
            self.requiredInstruments[k].addr = v
        self.found = self._find()

    def _find(self):
        self._instruments = {
            k: v.find() for k, v in self.requiredInstruments.items()
        }
        return all(self._instruments.values())

    def check(self, params):
        print(f'call check with {params}')
        device, secondary = params
        self.present = self._check(device, secondary)
        print('sample pass')

    def _check(self, device, secondary):
        print(f'launch check with {self.deviceParams[device]} {self.secondaryParams}')
        return self._runCheck(self.deviceParams[device], self.secondaryParams)

    def _runCheck(self, param, secondary):
        print(f'run check with {param}, {secondary}')
        return True

    def measure(self, params):
        print(f'call measure with {params}')
        device, _ = params
        self.result.raw_data = self._measure(device), self.secondaryParams
        print('>>>>>>>>>>>> here')
        self.hasResult = bool(self.result)

    def _measure(self, device):
        param = self.deviceParams[device]
        secondary = self.secondaryParams
        print(f'launch measure with {param} {secondary}')

        self._clear()
        self._init()

        return self._measure_s_params()

    def _clear(self):
        pass

    def _init(self):
        sda = self._instruments['Анализатор п/п приборов']

        res = sda.query('*IDN?')
        print(res)

    def _measure_s_params(self):
        sda = self._instruments['Анализатор п/п приборов']

        i = 0
        j = 0
        nop1 = 21
        nop2 = 1
        data = []
        value ="Vg (V), Cp (pF), C_st, G (uS), G_st, OSC (mV), Osc_st, DC (V), Dc_st, Time (s)"
        fname = "ex15.txt"
        title = "CV Sweep Measurement Result"
        msg = "No error."
        err = "0"
        freq = 1000000
        ref_cp = 0
        ref_g = 0
        osc_level = 0.03
        vg1 = 0
        vg2 = 10
        hold = 0
        delay = 0
        s_delay = 0
        _range = 0
        rep = nop1
        sc = [0] * nop1
        md = [0] * nop1 * 2
        st = [0] * nop1 * 2
        mon = [0] * nop1 * 2
        st_mon = [0] * nop1 * 2
        tm = [0] * nop1
        ret_val = ''

        sda.send("FMT 1,1")
        sda.send("TSC 1")
        sda.send("DV 5,0,0,0.1,0")

        ch = 5   # slot number in which MFCMU device is set (B1520A)
        sda.send(f"CN {ch}")
        sda.send("SSP {ch],4")
        sda.send("ACT 0, 2")
        sda.send("WTDCV 0,0,0")
        sda.send(f"WDCV {ch},1,{vg1},{vg2},{nop1}")
        sda.send(f"MM 18,{ch}")
        sda.send("IMP 100")
        sda.send("LMN 1")
        sda.send(f"RC {ch},{_range}")

        time.sleep(3)
        sda.send("TSR")
        sda.send("XE")   # trigger measure

        time.sleep(3)
        rdy = sda.query('*OPC?')

        res = sda.query('NUB?')

        time.sleep(3)

        res = sda._inst.read()
        # NET+5.25600E-02,NEC+1.46373E-09,NEY-2.56441E-05,NEV+00.0007E-03,NEV+0.00674E+00,WEV+000.000E+00,NET+2.87550E-01,NEC-8.40749E-11,NEY-4.55479E-06,NEV+00.0002E-03,NEV+0.50602E+00,WEV+000.500E+00,NET+5.86190E-01,NEC+4.89616E-10,NEY+2.22992E-06,NEV+00.0008E-03,NEV+1.00644E+00,WEV+001.000E+00,NET+7.23700E-01,NEC-7.75500E-10,NEY-4.04134E-06,NEV+00.0023E-03,NEV+1.50706E+00,WEV+001.500E+00,NET+8.61820E-01,NEC+8.18367E-10,NEY+7.85093E-07,NEV+00.0007E-03,NEV+2.00756E+00,WEV+002.000E+00,NET+1.15919E+00,NEC-2.23096E-11,NEY+2.45527E-06,NEV+00.0006E-03,NEV+2.50768E+00,WEV+002.500E+00,NET+1.29663E+00,NEC+9.87095E-10,NEY-2.47513E-07,NEV+00.0013E-03,NEV+3.00716E+00,WEV+003.000E+00,NET+1.61019E+00,NEC+5.99652E-09,NEY+3.06692E-05,NEV+00.0007E-03,NEV+3.50795E+00,WEV+003.500E+00,NET+1.82818E+00,NEC+1.52073E-09,NEY+6.52340E-06,NEV+00.0016E-03,NEV+4.00837E+00,WEV+004.000E+00,NET+1.96565E+00,NEC+3.39565E-09,NEY-2.62115E-05,NEV+00.0006E-03,NEV+4.50830E+00,WEV+004.500E+00,NET+2.10267E+00,NEC-7.58325E-10,NEY+1.37186E-05,NEV+00.0002E-03,NEV+5.00864E+00,WEV+005.000E+00,NET+2.24135E+00,NEC-4.48145E-10,NEY-1.91574E-05,NEV+00.0012E-03,NEV+5.50842E+00,WEV+005.500E+00,NET+2.37881E+00,NEC-1.89574E-09,NEY+2.54290E-05,NEV+00.0008E-03,NEV+6.00883E+00,WEV+006.000E+00,NET+2.51680E+00,NEC+2.24535E-09,NEY+1.07565E-05,NEV+00.0015E-03,NEV+6.50913E+00,WEV+006.500E+00,NET+2.73518E+00,NEC+2.59057E-09,NEY+3.69362E-05,NEV+00.0004E-03,NEV+7.00953E+00,WEV+007.000E+00,NET+2.87272E+00,NEC-5.18365E-09,NEY+3.15577E-05,NEV+00.0005E-03,NEV+7.51013E+00,WEV+007.500E+00,NET+3.00966E+00,NEC-3.20750E-09,NEY-6.50247E-05,NEV+00.0001E-03,NEV+8.00962E+00,WEV+008.000E+00,NET+3.14822E+00,NEC-5.86164E-09,NEY-9.81667E-06,NEV+00.0005E-03,NEV+08.5099E+00,WEV+008.500E+00,NET+3.44520E+00,NEC-7.77032E-09,NEY-2.17607E-06,NEV+00.0005E-03,NEV+09.0103E+00,WEV+009.000E+00,NET+3.74320E+00,NEC-1.45949E-09,NEY+5.10958E-06,NEV+00.0008E-03,NEV+09.5108E+00,WEV+009.500E+00,NET+4.15281E+00,NEC+2.52192E-09,NEY+2.62095E-05,NEV+00.0013E-03,NEV+10.0112E+00,EEV+010.000E+00

        print('>>> result', res)
        return res

    def pow_sweep(self):
        print('pow sweep')
        return [4, 5, 6], [4, 5, 6]

    @pyqtSlot(dict)
    def on_secondary_changed(self, params):
        self.secondaryParams = params

    @property
    def status(self):
        return [i.status for i in self._instruments.values()]


def parse_float_list(lst):
    return [float(x) for x in lst.split(',')]
