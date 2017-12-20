"""
Miscellanea routines that depend on other pyfant modules.

Rule: only 'gui/' modules can import util!!!

"""
import os
import glob
import shutil
import pyfant
import a99
import f311
import sqlite3
import unicodedata

__all__ = ["run_parallel", "setup_inputs", "copy_star", "link_to_data",
           "create_or_replace_or_skip_links", "copy_or_skip_files", "insert_states_from_nist",
           "insert_fcfs", "insert_molecule_from_nist", "run_traprb", ]

# ##################################################################################################
# Terminal-based interface


def run_parallel(rr, max_simultaneous=None, flag_console=False, runnable_manager=None,
                 flag_verbose=False, flag_exit_if_fail=False):
    """
    Args:
        rr: list of Runnable instances
        max_simultaneous: (defaults to RunnableManager.max_simultaneous)
            maximum number of simultaneous processes. **Note** ineffective if runnable_manager is passed
        flag_console: if True, will display menu with options, otherwise will exit when all runnables finish
        runnable_manager: if passed, will use passed; if not, will create new.
        flag_verbose: whether of not to log any messages (besides console) **Note** if runnable_manager is passed, it will keep its own
        flag_exit_if_fail: exit as soon as possible if any runnable fails? **Note** ineffective if runnable_manager is passed

    Returns: the RunnableManager object
    """
    import pyfant

    # Adds to pool
    logger = a99.get_python_logger()
    if runnable_manager:
        assert isinstance(runnable_manager, pyfant.RunnableManager)
        rm = runnable_manager
    else:
        rm = pyfant.RunnableManager(max_simultaneous=max_simultaneous, flag_verbose=flag_verbose,
                                flag_exit_if_fail=flag_exit_if_fail)
    flag_had_to_start = False
    if not rm.flag_start_called:
        rm.start()
        flag_had_to_start = True

    rm.add_runnables(rr)

    # Primitive thread monitor
    if flag_console:
        while True:
            print(("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" + (
            " ALIVE" if rm.is_alive() else " DEAD")))
            print(rm)
            print(("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" + (
            " ALIVE" if rm.is_alive() else " DEAD")))
            s = input("[Enter] -- [e]xit & keep in loop -- [q]uit -- [k]ill running >>> ")
            if s.lower() == "q":
                if rm.is_alive():
                    try:
                        rm.exit()
                    except:
                        logger.exception("Error trying to exit")
                break
            if s.lower() == "e":
                try:
                    rm.exit()
                except:
                    logger.exception("Error trying to exit")
            if s.lower() == "k":
                rm.kill_runnables()
    else:
        rm.wait_until_finished()
        if flag_had_to_start:
            rm.exit()

    if flag_verbose:
        a99.get_python_logger().info(
            ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" + (" ALIVE" if rm.is_alive() else " DEAD")))
        a99.get_python_logger().info("test-tm2 [SUPPOSED TO HAVE] EXITED")
        a99.get_python_logger().info(rm)

    return rm


def setup_inputs(dest_dir='.', star='sun-asplund-2009', common='common', h=True, atoms=True,
                 molecules=True, opa=True):
    """
    Sets up input data for spectral synthesis.

    Args:
      dest_dir='.': directory where files and links will be created
      star='sun-asplund-2009': directory (relative to PFANT/data) for stellar data
      common='common': directory (relative to PFANT/data) for star-independent data files
      h=True: whether to look for hmap.dat
      atoms=True: whether to look for atoms.dat
      molecules=True: whether to look for molecules.dat
      opa=True: whether to look for grid.moo
    """
    import pyfant as pf

    logger = a99.get_python_logger()
    dd = pyfant.get_pfant_path("data")

    # Functions that return full path, given a filename, to ...
    fd = lambda filename: os.path.join(dest_dir, filename)  # ... Destination directory
    fs = lambda filename: os.path.join(dd, star, filename)  # ... Stellar data directory
    fc = lambda filename: os.path.join(dd, common, filename)  # ... Common data directory

    # ## main.dat not present
    if not os.path.isfile(fd("main.dat")):
        zz_mnbp = ["main.dat", "abonds.dat",
                   "modeles.mod"]  # files that must not be present if main.dat is not present

        for z in zz_mnbp:
            if os.path.isfile(fd(z)):
                raise RuntimeError("Found file '%s' in local directory."
                                   "If 'main.dat' is not present, files %s must also not exist." %
                                   (z, zz_mnbp[1:]))

    # ## Stellar data...
    zz = ["main.dat", "abonds.dat"]
    copy_or_skip_files([fs(z) for z in zz], dest_dir=dest_dir)

    # ## Common data...
    zz = ["absoru2.dat", "partit.dat", "grid.mod"]
    if opa: zz.append("grid.moo")
    if h: zz.append("hmap.dat")
    if atoms: zz.append("atoms.dat")
    if molecules: zz.append("molecules.dat")
    create_or_replace_or_skip_links([fc(z) for z in zz], dest_dir=dest_dir)


def copy_star(src_dir=None, starname=None):
    """
    Copies files such as main.dat and abonds.dat from PFANT/data/some_directory into local directory

    Args:
        src_dir: absolute path to directory containing PFANT star data files FileMain and FileAbonds
                 (and optionally FileDissoc files, which will be also copied if present)
        starname: if passed, will ignore src_dir and make it from starname instead, considering
                  starname as a subdirectory of PFANT/data/
    """
    star_classes = [pyfant.FileMain, pyfant.FileDissoc, pyfant.FileAbonds]

    if starname is not None:
        src_dir = os.path.join(pyfant.get_pfant_data_path(), starname)

    if src_dir is None and starname is None:
        raise ValueError("Supply either src_dir or starname")

    if not os.path.isdir(src_dir):
        raise ValueError("'{}' is not a valid directory".format(src_dir))

    a99.get_python_logger().debug("Will look inside directory %s" % src_dir)

    # makes list of files to analyse
    types = ('*.dat', '*.mod')
    ff = []
    for type_ in types:
        ff.extend(glob.glob(os.path.join(src_dir, type_)))

    copy_or_skip_files(ff)


def link_to_data(src_dir=None):
    """Creates symbolic links to files '*.dat', '*.mod', '*.moo' within src_dir, skipping certain types

    Args:
        src_dir: directory containing files to be linked to. If omitted, it defaults to
                 PFANT/data/common
    """

    if src_dir is None:
        src_dir = pyfant.get_pfant_path('data', 'common')

    a99.get_python_logger().debug("Will look inside directory %s" % src_dir)

    # makes list of files to analyse
    types = ('*.dat', '*.mod', '*.moo')
    ff = []
    for type_ in types:
        ff.extend(glob.glob(os.path.join(src_dir, type_)))

    create_or_replace_or_skip_links(ff)


def create_or_replace_or_skip_links(ff, dest_dir="."):
    """Creates a series of links given a list of target filepaths.

    Args:
        ff: list of full path to files
        dest_dir: destination directory

    It skips files of types FileMain, FileAbonds, FileDissoc, FileToH
    """
    for f in ff:
        name = os.path.split(f)[1]
        ptd = os.path.join(dest_dir, name)  # path to destination

        flag_skip = False
        a99.get_python_logger().info(("Considering file '%s' ..." % name))
        if os.path.isfile(ptd) and not os.path.islink(ptd):
            _print_skipped("file exists in local directory")
            flag_skip = True
        else:
            obj = f311.load_with_classes(f, [pyfant.FileMain, pyfant.FileAbonds, pyfant.FileDissoc, pyfant.FileToH])
            if obj is not None:
                _print_skipped("detected type %s" % obj.__class__.__name__)
                flag_skip = True
            else:
                obj = f311.load_with_classes(f, [pyfant.FileModBin])
                if obj is not None:
                    if len(obj) == 1:
                        _print_skipped("%s of only one record" % obj.__class__.__name__)
                        flag_skip = True

        if not flag_skip:
            try:
                if os.path.islink(ptd):
                    os.remove(ptd)
                    s_action = "replaced existing"
                else:
                    s_action = "created"
                a99.create_symlink(f, ptd)
                a99.get_python_logger().info("   ... %s link" % s_action)
            except Exception as e:
                a99.print_error("Error creating link: %s" % str(e))


def copy_or_skip_files(ff, dest_dir="."):
    """Copies a series of files, skipping those which already exist.

    Args:
      ff: list of full paths to files to be copied
      dest_dir: destination directory
    """

    for f in ff:
        name = os.path.split(f)[1]

        flag_skip = False
        a99.get_python_logger().info("Considering file '%s' ..." % name)
        if os.path.isfile(name):
            _print_skipped("file exists in local directory")
            flag_skip = True
        else:
            obj = f311.load_with_classes(f, [pyfant.FileMain, pyfant.FileAbonds, pyfant.FileDissoc])
            if obj is not None:
                pass
            else:
                _print_skipped("neither main, abonds, nor dissoc file")
                flag_skip = True

        if not flag_skip:
            try:
                shutil.copy(f, dest_dir)
                a99.get_python_logger().info("   ... file copied")
            except Exception as e:
                a99.print_error("Error copying file: %s" % str(e))


def _print_skipped(reason):
    """Standardized printing for when a file was skipped."""
    a99.get_python_logger().info("   ... SKIPPED ({0!s}).".format(reason))


def insert_fcfs(moldb, id_system, fcfs, flag_replace=False):
    """
    Inserts Franck-Condon Factors for given system

    :param moldb: FileMolDB
    :param id_system: int, system ID in 'system' table
    :param fcfs: {(vl, v2l): fcf, ...}, as stored in a FileTRAPRBOutput object
    :param flag_replace: if FCFs for system identified by 'id_system' already exists,
        I may either raise (flag_replace==False) or replace these FCFs
    :return: None
    """
    conn = moldb.get_conn()
    cursor = conn.cursor()
    assert isinstance(conn, sqlite3.Connection)
    assert isinstance(cursor, sqlite3.Cursor)

    n = cursor.execute("select count(*) from fcf where id_system = ?",
                       (id_system,)).fetchone()["count(*)"]
    if n > 0:
        if flag_replace:
            cursor.execute("delete from fcf where id_system = ?", (id_system,))
        else:
            raise RuntimeError("FCFs exist for system #{}".format(id_system))

    for (vl, v2l), fcf in fcfs.items():
        conn.execute("insert into fcf (id_system, vl, v2l, value) values (?,?,?,?)",
                     (id_system, vl, v2l, fcf))

    conn.commit()


def insert_molecule_from_nist(moldb, formula, flag_replace=False, flag_do_what_i_can=True):
    """
    Retrieves NIST data and inserts new molecule into DB, or updates states if molecule exists

    :param moldb: FileMolDB object
    :param formula: str, e.g., "OH"
    :param flag_replace: applies to states (not molecule entry); passed on to insert_states_from_nist()
    :param flag_do_what_i_can: if set, will insert molecule even if cannot
        download molecular constants from NIST
    :return: None
    """
    conn = moldb.get_conn()
    cursor = conn.cursor()
    assert isinstance(conn, sqlite3.Connection)
    assert isinstance(cursor, sqlite3.Cursor)

    id_molecule = None
    data = None
    name = "?name?"
    n = conn.execute("select count(*) from molecule where formula = ?", (formula,)).fetchone()["count(*)"]
    if n > 0:
        id_molecule = conn.execute("select id from molecule where formula = ?", (formula,))
    else:
        try:
            data, header, name = pyfant.get_nist_webbook_constants(formula, flag_unicode=True,
                                                                   flag_parse_state=True)
        except:
            if flag_do_what_i_can:
                a99.get_python_logger().exception("Could not get NIST constants for formula '{}'".format(formula))
            else:
                raise

    if id_molecule is None:
        cursor.execute("insert into molecule (formula, name) values (?, ?)", (formula, name))
        id_molecule = cursor.lastrowid
        conn.commit()

    if data is not None:
        insert_states_from_nist(moldb, id_molecule, data, flag_replace)

    conn.commit()


def insert_states_from_nist(moldb, id_molecule, nist_data, flag_replace=False):
    """
    Inserts downloaded NIST data into table 'state'

    :param moldb: FileMolDB
    :param id_molecule: int, molecule ID in 'molecule' table
    :param nist_data: list of lists as returned by
                      get_nist_webbook_constants(..., flag_parse_state=True)
    :param flag_replace: if states for molecule identified by 'id_molecule' already exists,
        I may either raise (flag_replace==False) or replace these states
    :return: None
    """

    conn = moldb.get_conn()
    cursor = conn.cursor()
    assert isinstance(conn, sqlite3.Connection)
    assert isinstance(cursor, sqlite3.Cursor)

    n = cursor.execute("select count(*) from state where id_molecule = ?",
                       (id_molecule,)).fetchone()["count(*)"]
    if n > 0:
        if flag_replace:
            cursor.execute("delete from state where id_molecule = ?", (id_molecule,))
        else:
            formula = cursor.execute("select formula from molecule where id = ?",
                                     (id_molecule,)).fetchone()["formula"]
            raise RuntimeError("States exist for formula '{}'".format(formula))


    for state in nist_data:
        # **Note** assumes that the columns in data match the
        # (number of columns in the state table - 3) and their order
        conn.execute("insert into state values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     [None, id_molecule] + state + [""])

    conn.commit()


def run_traprb(molconsts, fn_input=None, fn_output=None, maxv=None,
               ni=None, ns=None, igraph=None, ienerg=None, istate=None,
               rmin=None, rmax=None, delr=None):
    """
    Runs TRAPRB and returns a the TRAPRB object

    :param molconsts: MolConsts object
    :param fn_input: input filename (will be created with this name). If not passed, will make up a
                     filename as 'temp-in-*'
    :param fn_output: output filename (will be created with this name). If not passed, will make up
                     a filename as 'temp-out-*'
    :return: TRAPRB object

    For meanings of parameters and their default values, see filetraprb.py::TRAPRBInputState class

    **This routine creates files 'temp-traprb*' and leaves then**

    **Not multiprocessing-safe**, unless fn_input and fn_output are controlled externally.
    """

    if fn_input is None:
        fn_input = a99.new_filename("temp-in-")
    if fn_output is None:
        fn_output = a99.new_filename("temp-out-")

    fin = pyfant.FileTRAPRBInput()
    fin.from_molconsts(molconsts, maxv, ni, ns, igraph, ienerg, istate, rmin, rmax, delr, )
    fin.save_as(fn_input)

    r = pyfant.TRAPRB()
    r.fn_input = fn_input
    r.fn_output = fn_output
    r.run()

    return r

