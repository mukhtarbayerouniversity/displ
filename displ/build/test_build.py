import unittest
import os
import json
from ase import Atoms
import ase.db
from displ.pwscf.build import build_qe
from displ.build.cell import make_cell
from displ.build.build import (_extract_syms, get_c_sep, get_wann_valence,
        get_num_bands, make_qe_config, get_pseudo_dir)
from displ.build.util import _base_dir

def check_qe_config(testcase, qe_config, qe_config_expected, soc, xc, pp):
    testcase.assertEqual(sorted(qe_config.keys()), sorted(qe_config_expected.keys()))

    for k, v in qe_config.items():
        v_expected = qe_config_expected[k]

        # pseudo_dir value is system-dependent.
        if k == 'pseudo_dir':
            pseudo_dir_expected = get_pseudo_dir(soc, xc, pp)
            testcase.assertEqual(v, pseudo_dir_expected)
            continue

        # Remaining values are not.
        testcase.assertEqual(v, v_expected)

def check_qe_input(testcase, qe_input, qe_input_expected, soc, xc, pp):
    for line, line_expected in zip(qe_input.split('\n'), qe_input_expected.split('\n')):
        # pseudo_dir value is system-dependent.
        if line.split('=')[0] == 'pseudo_dir':
            pseudo_dir_expected = get_pseudo_dir(soc, xc, pp)
            testcase.assertEqual(line.split('=')[1].strip(), pseudo_dir_expected)
            continue

        # Remaining values are not.
        testcase.assertEqual(line, line_expected)

class TestQE(unittest.TestCase):
    def test_qe_config(self):
        syms = ["WSe2", "WSe2", "WSe2"]
        soc = True
        vacuum_dist = 20.0 # Angstrom
        D = 0.5 # V/nm
        AB_stacking = True
        xc = 'lda'
        pp = 'nc'

        db_path = os.path.join(_base_dir(), "c2dm.db")
        db = ase.db.connect(db_path)
        c_sep = get_c_sep(db, syms[0])

        latvecs, at_syms, cartpos = make_cell(db, syms, c_sep, vacuum_dist, AB_stacking)
        system = Atoms(symbols=at_syms, positions=cartpos, cell=latvecs, pbc=True)
        system.center(axis=2)

        wann_valence, num_wann = get_wann_valence(system.get_chemical_symbols(), soc)
        num_bands = get_num_bands(num_wann)

        qe_config = make_qe_config(system, D, soc, num_bands, xc, pp)
        #with open('test_build_qe_config_new.json', 'w') as fp:
        #    json.dump(qe_config, fp)

        with open('test_build_qe_config.json', 'r') as fp:
            qe_config_expected = json.load(fp)

        check_qe_config(self, qe_config, qe_config_expected, soc, xc, pp)

        prefix = 'test'
        qe_input = build_qe(system, prefix, 'scf', qe_config)
        #with open('test_build_qe_input_new', 'w') as fp:
        #    fp.write(qe_input)

        with open('test_build_qe_input', 'r') as fp:
            qe_input_expected = fp.read()

        check_qe_input(self, qe_input, qe_input_expected, soc, xc, pp)

if __name__ == "__main__":
    unittest.main()
