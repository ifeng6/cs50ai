from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Each character is either a knight or a knave
A_Knight_Knave = And(Or(AKnight, AKnave), Not(And(AKnight, AKnave)))
B_Knight_Knave = And(Or(BKnight, BKnave), Not(And(BKnight, BKnave)))
C_Knight_Knave = And(Or(CKnight, CKnave), Not(And(CKnight, CKnave)))

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    A_Knight_Knave,
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(AKnave, Not(And(AKnight, AKnave))),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    A_Knight_Knave,
    B_Knight_Knave,
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave))),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
same_kind = Or(Biconditional(AKnight, BKnight), Biconditional(AKnave, BKnave))
different_kind = Not(same_kind)

knowledge2 = And(
    A_Knight_Knave,
    B_Knight_Knave,
    Implication(AKnight, same_kind),
    Implication(AKnave, different_kind),
    Implication(BKnight, different_kind),
    Implication(BKnave, same_kind),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    A_Knight_Knave,
    B_Knight_Knave,
    C_Knight_Knave,
    Implication(BKnight, And(Implication(AKnight, AKnave), Implication(AKnave, AKnight), CKnave)),
    Implication(BKnave, And(Implication(AKnight, AKnight), Implication(AKnave, AKnave), CKnight)),
    Implication(CKnight, AKnight),
    Implication(CKnave, AKnave),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
