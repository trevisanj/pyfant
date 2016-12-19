__all__ = ["branch_to_Jl", "global_quanta_to_branch"]

_J2L_MAP = {"P": -1, "Q": 0, "R": 1}


def branch_to_Jl(Br, J2l):
    """Returns J superior given J inferior and the branch"""
    return J2l + _J2L_MAP[Br]


# TODO there is more ask BLB. "pois ha os dubletos que teem 6 ramos e tripletos teem 9 ramos"
def global_quanta_to_branch(Jl, J2l):
    """

    Args:
        Jl: J upper or J'
        J2l: J lower or  J''

    Returns: branch letter: "P"/"Q"/"R"
    """
    if Jl > J2l:
        return "R"
    if Jl == J2l:
        return "Q"
    return "P"
