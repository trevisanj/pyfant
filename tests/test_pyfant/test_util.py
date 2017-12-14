import pyfant
import os
import glob


# Note: requires PFANT installed


def test_copy_star(tmpdir):
    os.chdir(str(tmpdir))

    dir_ = os.path.join(pyfant.get_pfant_data_path(), 'arcturus')
    pyfant.copy_star(dir_)

    assert glob.glob("*") == ['abonds.dat', 'main.dat']


def test_link_to_data(tmpdir):
    os.chdir(str(tmpdir))
    pyfant.link_to_data(pyfant.get_pfant_data_path("common"))
    d = glob.glob("*")
    d.sort()
    assert d == ['absoru2.dat', 'atoms.dat', 'grid.mod', 'grid.moo', 'hmap.dat', 'molecules.dat', 'partit.dat']


def test_run_combo(tmpdir):
    os.chdir(str(tmpdir))
    pyfant.copy_star(pyfant.get_pfant_data_path('arcturus'))
    pyfant.link_to_data(pyfant.get_pfant_data_path("common"))
    c = pyfant.Combo()
    c.run()


def test_run_parallel(tmpdir):
    os.chdir(str(tmpdir))

    pyfant.copy_star(pyfant.get_pfant_data_path('arcturus'))
    pyfant.link_to_data(pyfant.get_pfant_data_path("common"))

    cc = []

    c = pyfant.Combo()
    c.conf.flag_output_to_dir = True
    cc.append(c)
    c = pyfant.Combo()
    c.conf.flag_output_to_dir = True
    cc.append(c)

    pyfant.run_parallel(cc, flag_console=False)


def test_setup_inputs(tmpdir):
    os.chdir(str(tmpdir))

    pyfant.setup_inputs()

    d = glob.glob("*")
    d.sort()

    assert d == ['abonds.dat', 'absoru2.dat', 'atoms.dat', 'grid.mod', 'grid.moo', 'hmap.dat',
                 'main.dat', 'molecules.dat', 'partit.dat']

