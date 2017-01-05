"""
Hönl-London factors for doublets, formulas from Kovacs 1969 p130
"""

def UPLUSL(J, LBIG):
    return 2. * (J - LBIG + 0.5)


def UMINUSL(J, LBIG):
    return 2. * (J + LBIG + 0.5)


def CPLUSL(J, LBIG):
    return 4. * (J + 0.5) * (J - LBIG + 0.5)


def CMINUSL(J, LBIG):
    return 4. * (J + 0.5) * (J + LBIG + 0.5)


def UPLUS2L(J, LSMALL):
    return 2.*(J-LSMALL+0.5)


def UMINUS2L(J, LSMALL):
    return 2.*(J+LSMALL+0.5)


def CPLUS2L(J, LSMALL):
    return 4.*(J+0.5)*(J-LSMALL+0.5)


def CMINUS2L(J, LSMALL):
    return 4.*(J+0.5)*(J+LSMALL+0.5)


def formula0(J, LBIG, LSMALL):
    """Formula for P1(J) or R1(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/(8*J*CMINUSL(J-1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UMINUSL(J-1, LBIG)*UMINUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)

def formula1(J, LBIG, LSMALL):
    """Formula for Q1(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CMINUSL(J, LBIG)*CMINUS2L(J, LSMALL)))*((UMINUSL(J, LBIG)*UMINUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula2(J, LBIG, LSMALL):
    """Formula for R1(J) or P1(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CMINUSL(J+1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UMINUSL(J+1, LBIG)*UMINUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula3(J, LBIG, LSMALL):
    """Formula for P21(J) or R12(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/(8*J*CPLUSL(J-1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UPLUSL(J-1, LBIG)*UMINUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula4(J, LBIG, LSMALL):
    """Formula for Q21(J) or Q12(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CPLUSL(J, LBIG)*CMINUS2L(J, LSMALL)))*((UPLUSL(J, LBIG)*UMINUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)

def formula5(J, LBIG, LSMALL):
    """Formula for R21(J) or P12(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CPLUSL(J+1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UPLUSL(J+1, LBIG)*UMINUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula6(J, LBIG, LSMALL):
    """Formula for P21(J) or R21(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/(8*J*CMINUSL(J-1, LBIG)*
    CPLUS2L(J, LSMALL)))*((UMINUSL(J-1, LBIG)*UPLUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula7(J, LBIG, LSMALL):
    """Formula for Q12(J) or Q21(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CMINUSL(J, LBIG)*CPLUS2L(J, LSMALL)))*((UMINUSL(J, LBIG)*UPLUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula8(J, LBIG, LSMALL):
    """Formula for R12(J) or P21(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CMINUSL(J+1, LBIG)*
    CPLUS2L(J, LSMALL)))*((UMINUSL(J+1, LBIG)*UPLUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula9(J, LBIG, LSMALL):
    """Formula for P2(J) or R2(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/(8*J*CPLUSL(J-1, LBIG)*
    CPLUS2L(J, LSMALL)))*((UPLUSL(J-1, LBIG)*UPLUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula10(J, LBIG, LSMALL):
    """Formula for Q2(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CPLUSL(J, LBIG)*CPLUS2L(J, LSMALL)))*((UPLUSL(J, LBIG)*UPLUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula11(J, LBIG, LSMALL):
    """Formula for R2(J) or P2(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CPLUSL(J+1, LBIG)*
    CPLUS2L(J, LSMALL)))*((UPLUSL(J+1, LBIG)*UPLUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def get_formulas(LAML, LAM2L):
    """Function factory: returns (P1(J), Q1(J), ...)

    Args:
        LAML: Lambda sup:
          0 for Sigma
          1 for Pi
          2 for Delta
          3 for Phi
        LAM2L: Lambda inf (0/1/2/3 as above)

    Returns:
        (P1, Q1, R1, P21, Q21, R21, P12, Q12, R12, P2, Q2, R2)

    all functions are functions of J, i.e., P1 = P1(J) (they are adjusted for specific LAML, LAM2L)

    Order as in Kovacs 1969, p130, 1st column


    >>> P1, Q1, R1, P21, Q21, R21, P12, Q12, R12, P2, Q2, R2 = get_formulas(1, 0)

    >>> P1, Q1, R1, P21, Q21, R21, P12, Q12, R12, P2, Q2, R2 = get_formulas(0, 1)

    >>> J = 10.5
    >>> formulas = get_formulas(1, 0)  # delta Lambda = +1
    >>> p1, q1, r1, p21, q21, r21, p12, q12, r12, p2, q2, r2 = [f(J) for f in formulas]

    >>> J = 10.5
    >>> formulas = get_formulas(1, 0)  # delta Lambda = +1
    >>> [f(J) for f in formulas]
    [4.714285714285714, 10.952380952380953, 6.260869565217392, 0.047619047619047616, 0.02484472049689441, 0.0, 0.0, 0.020703933747412008, 0.043478260869565216, 4.761904761904762, 10.956521739130435, 6.217391304347826]

    >>> S, DELTAK = 0.5, 0  # spin, delta Kronecker
    >>> J = 10.5
    >>> factor = 2/((2*J+1)*(2*S+1)*(2-DELTAK))
    >>> normalized = [f(J)*factor for f in get_formulas(1, 0)]
    >>> normalized
    [0.10714285714285715, 0.24891774891774893, 0.1422924901185771, 0.0010822510822510823, 0.0005646527385657821, 0.0, 0.0, 0.0004705439488048184, 0.0009881422924901185, 0.10822510822510822, 0.24901185770750991, 0.14130434782608697]
    >>> sum(normalized)
    1.0

    >>> S, DELTAK = 0.5, 0  # spin, delta Kronecker
    >>> J = 32
    >>> factor = 2/((2*J+1)*(2*S+1)*(2-DELTAK))
    >>> normalized = [f(J)*factor for f in get_formulas(0, 1)]
    >>> sum(normalized)
    1.0
    """

    if LAML > LAM2L:
        P1 = lambda J: formula0(J, LAML, LAM2L)
        Q1 = lambda J: formula1(J, LAML, LAM2L)
        R1 = lambda J: formula2(J, LAML, LAM2L)
        P21 = lambda J: formula3(J, LAML, LAM2L)
        Q21 = lambda J: formula4(J, LAML, LAM2L)
        R21 = lambda J: formula5(J, LAML, LAM2L)
        P12 = lambda J: formula6(J, LAML, LAM2L)
        Q12 = lambda J: formula7(J, LAML, LAM2L)
        R12 = lambda J: formula8(J, LAML, LAM2L)
        P2 = lambda J: formula9(J, LAML, LAM2L)
        Q2 = lambda J: formula10(J, LAML, LAM2L)
        R2 = lambda J: formula11(J, LAML, LAM2L)
    elif LAML < LAM2L:
        P1 = lambda J: formula2(J-1, LAM2L, LAML)
        Q1 = lambda J: formula1(J, LAM2L, LAML)
        R1 = lambda J: formula0(J+1, LAM2L, LAML)
        P21 = lambda J: formula8(J-1, LAM2L, LAML)
        Q21 = lambda J: formula7(J, LAM2L, LAML)
        R21 = lambda J: formula6(J+1, LAM2L, LAML)
        P12 = lambda J: formula5(J-1, LAM2L, LAML)
        Q12 = lambda J: formula4(J, LAM2L, LAML)
        R12 = lambda J: formula3(J+1, LAM2L, LAML)
        P2 = lambda J: formula11(J-1, LAM2L, LAML)
        Q2 = lambda J: formula10(J, LAM2L, LAML)
        R2 = lambda J: formula9(J+1, LAM2L, LAML)
    else:
        raise ValueError("Invalid delta Lambda")

    return P1, Q1, R1, P21, Q21, R21, P12, Q12, R12, P2, Q2, R2



