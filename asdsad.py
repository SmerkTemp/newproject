#!/usr/bin/env python3
import random

"""
Simple European Roulette CLI
- Wheel: numbers 0-36 (0 is green)
- Bets supported:
    - number <0-36> <amount>         -> pays 35:1
    - color <red|black> <amount>     -> pays 1:1
    - parity <even|odd> <amount>     -> pays 1:1 (0 loses)
    - range <1-18|19-36> <amount>    -> pays 1:1
    - dozen <1|2|3> <amount>         -> pays 2:1 (1=>1-12,2=>13-24,3=>25-36)
    - column <1|2|3> <amount>        -> pays 2:1 (columns of roulette table)
Commands:
    bet ...     place a bet (can place many before spin)
    spin        spin the wheel and resolve bets
    balance     show current balance
    work [easy|medium|hard]   do simple tasks to increase balance (reward scales with current balance)
    invest <amount>    move money to savings (earns interest)
    withdraw <amount>  move money from savings back to balance
    savings            show savings balance and interest rate
    shop               show purchasable items
    buy <item>         buy an item to boost investments or work
    donate <amount>    donate money to charity
    help        show help
    quit        exit
"""

RED = {
    1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
}
COLUMNS = {
    1: {1,4,7,10,13,16,19,22,25,28,31,34},
    2: {2,5,8,11,14,17,20,23,26,29,32,35},
    3: {3,6,9,12,15,18,21,24,27,30,33,36},
}

PAYOUTS = {
    "number": 35,
    "color": 1,
    "parity": 1,
    "range": 1,
    "dozen": 2,
    "column": 2,
}

SHOP_ITEMS = {
    # item: (price, description, effect_key, effect_value)
    "safe": (500, "Increases savings interest rate by 0.5%", "savings_rate", 0.005),
    "course": (300, "Improves work payouts by 20%", "work_multiplier", 0.2),
    "portfolio": (1000, "Increases savings interest rate by 1.5%", "savings_rate", 0.015),
}

def parse_bet(parts):
    if not parts:
        return None
    t = parts[0].lower()
    try:
        if t == "number" and len(parts) == 3:
            n = int(parts[1])
            amt = int(parts[2])
            if 0 <= n <= 36 and amt > 0:
                return ("number", n, amt)
        if t == "color" and len(parts) == 3:
            c = parts[1].lower()
            if c in ("red","black"):
                amt = int(parts[2])
                if amt > 0:
                    return ("color", c, amt)
        if t == "parity" and len(parts) == 3:
            p = parts[1].lower()
            if p in ("even","odd"):
                amt = int(parts[2])
                if amt > 0:
                    return ("parity", p, amt)
        if t == "range" and len(parts) == 3:
            r = parts[1]
            if r in ("1-18","19-36"):
                amt = int(parts[2])
                if amt > 0:
                    return ("range", r, amt)
        if t == "dozen" and len(parts) == 3:
            d = int(parts[1])
            if d in (1,2,3):
                amt = int(parts[2])
                if amt > 0:
                    return ("dozen", d, amt)
        if t == "column" and len(parts) == 3:
            c = int(parts[1])
            if c in (1,2,3):
                amt = int(parts[2])
                if amt > 0:
                    return ("column", c, amt)
    except ValueError:
        return None
    return None

def eval_bet(bet, outcome):
    typ = bet[0]
    if typ == "number":
        n, amt = bet[1], bet[2]
        if outcome == n:
            return amt * (PAYOUTS["number"] + 1)
        return 0
    if typ == "color":
        c, amt = bet[1], bet[2]
        if outcome == 0:
            return 0
        win = ("red" if outcome in RED else "black")
        if win == c:
            return amt * (PAYOUTS["color"] + 1)
        return 0
    if typ == "parity":
        p, amt = bet[1], bet[2]
        if outcome == 0:
            return 0
        is_even = (outcome % 2 == 0)
        if (is_even and p == "even") or (not is_even and p == "odd"):
            return amt * (PAYOUTS["parity"] + 1)
        return 0
    if typ == "range":
        r, amt = bet[1], bet[2]
        if outcome == 0:
            return 0
        low = range(1,19)
        high = range(19,37)
        if (r == "1-18" and outcome in low) or (r == "19-36" and outcome in high):
            return amt * (PAYOUTS["range"] + 1)
        return 0
    if typ == "dozen":
        d, amt = bet[1], bet[2]
        if outcome == 0:
            return 0
        if d == 1 and 1 <= outcome <= 12: return amt * (PAYOUTS["dozen"] + 1)
        if d == 2 and 13 <= outcome <= 24: return amt * (PAYOUTS["dozen"] + 1)
        if d == 3 and 25 <= outcome <= 36: return amt * (PAYOUTS["dozen"] + 1)
        return 0
    if typ == "column":
        c, amt = bet[1], bet[2]
        if outcome == 0:
            return 0
        if outcome in COLUMNS[c]:
            return amt * (PAYOUTS["column"] + 1)
        return 0
    return 0

def print_help():
    print(__doc__)

def do_work(balance, difficulty):
    if balance <= 0:
        return 0, "You have no money to leverage for work."
    # Choose problem complexity based on difficulty
    if difficulty == "easy":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        ops = ["+" , "-"]
        pct_low, pct_high = 0.01, 0.03
    elif difficulty == "medium":
        a = random.randint(5, 50)
        b = random.randint(1, 12)
        ops = ["+", "-", "*"]
        pct_low, pct_high = 0.03, 0.07
    else:  # hard
        a = random.randint(2, 20)
        b = random.randint(1, 20)
        exp = random.choice([2, 3])
        ops = ["+", "-", "*", "pow"]
        pct_low, pct_high = 0.05, 0.15

    op = random.choice(ops)
    if op == "+":
        question = f"{a} + {b}"
        answer = a + b
    elif op == "-":
        question = f"{a} - {b}"
        answer = a - b
    elif op == "*":
        question = f"{a} * {b}"
        answer = a * b
    else:  # pow
        question = f"{a} ^ {exp}"
        answer = a ** exp

    try:
        user_in = input(f"Solve: {question} = ").strip()
    except (EOFError, KeyboardInterrupt):
        return 0, "Work cancelled."

    try:
        user_ans = int(user_in)
    except ValueError:
        return 0, f"Invalid answer. Correct answer was {answer}."

    if user_ans == answer:
        pct = random.uniform(pct_low, pct_high)
        reward = max(1, int(balance * pct))
        # small chance of bonus
        if random.random() < 0.05:
            bonus = max(1, int(reward * random.uniform(0.5, 1.5)))
            reward += bonus
            return reward, f"Correct! Bonus task (+{bonus}). Total gain: {reward}."
        return reward, f"Correct! You solved the problem and earned {reward}."
    else:
        return 0, f"Incorrect. The correct answer was {answer}."

def main():
    balance = 1000
    bets = []
    savings = 0
    savings_rate = 0.01  # 1% per loop tick (simple demo)
    work_multiplier = 1.0
    owned = set()
    charity_total = 0

    def accrue_savings():
        nonlocal savings
        if savings <= 0:
            return 0
        interest = int(savings * savings_rate)
        if interest > 0:
            savings += interest
            return interest
        return 0

    print("Roulette CLI — starting balance:", balance)
    print("Type 'help' for commands.")
    while True:
        # accrue a little interest each loop tick (keeps things simple)
        interest = accrue_savings()
        if interest > 0:
            print(f"Savings earned interest: {interest} (savings now {savings})")

        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd:
            continue
        parts = cmd.split()
        if parts[0].lower() == "quit":
            break
        if parts[0].lower() == "help":
            print_help()
            continue
        if parts[0].lower() == "balance":
            print("Balance:", balance)
            print("Savings:", savings, f"(rate {savings_rate*100:.2f}%)")
            print("Owned items:", ", ".join(sorted(owned)) if owned else "none")
            continue
        if parts[0].lower() == "savings":
            print("Savings balance:", savings)
            print("Interest rate:", f"{savings_rate*100:.2f}%")
            continue
        if parts[0].lower() == "invest":
            if len(parts) != 2:
                print("Usage: invest <amount>")
                continue
            try:
                amt = int(parts[1])
            except ValueError:
                print("Invalid amount.")
                continue
            if amt <= 0:
                print("Amount must be positive.")
                continue
            if amt > balance:
                print("Insufficient funds.")
                continue
            balance -= amt
            savings += amt
            print(f"Invested {amt}. Savings: {savings}")
            continue
        if parts[0].lower() == "withdraw":
            if len(parts) != 2:
                print("Usage: withdraw <amount>")
                continue
            try:
                amt = int(parts[1])
            except ValueError:
                print("Invalid amount.")
                continue
            if amt <= 0:
                print("Amount must be positive.")
                continue
            if amt > savings:
                print("Insufficient savings.")
                continue
            savings -= amt
            balance += amt
            print(f"Withdrew {amt}. Savings: {savings}. Balance: {balance}")
            continue
        if parts[0].lower() == "shop" or parts[0].lower() == "store":
            print("Items available:")
            for k, v in SHOP_ITEMS.items():
                print(f"  {k}: price {v[0]} - {v[1]}")
            continue
        if parts[0].lower() == "buy":
            if len(parts) != 2:
                print("Usage: buy <item>")
                continue
            item = parts[1].lower()
            if item not in SHOP_ITEMS:
                print("Unknown item.")
                continue
            if item in owned:
                print("You already own that item.")
                continue
            price, desc, effect_key, effect_val = SHOP_ITEMS[item]
            if price > balance:
                print("Insufficient funds.")
                continue
            balance -= price
            owned.add(item)
            # apply effect
            if effect_key == "savings_rate":
                savings_rate += effect_val
            elif effect_key == "work_multiplier":
                work_multiplier += effect_val
            print(f"Bought {item} for {price}.")
            continue
        if parts[0].lower() == "donate":
            if len(parts) != 2:
                print("Usage: donate <amount>")
                continue
            try:
                amt = int(parts[1])
            except ValueError:
                print("Invalid amount.")
                continue
            if amt <= 0:
                print("Amount must be positive.")
                continue
            if amt > balance:
                print("Insufficient funds.")
                continue
            balance -= amt
            charity_total += amt
            print(f"Donated {amt}. Thanks! Total donated: {charity_total}")
            continue
        if parts[0].lower() == "bet":
            b = parse_bet(parts[1:])
            if not b:
                print("Invalid bet. See 'help'.")
                continue
            amt = b[-1]
            if amt > balance:
                print("Insufficient funds.")
                continue
            balance -= amt
            bets.append(b)
            print("Placed:", b)
            continue
        if parts[0].lower() == "work":
            difficulty = "easy"
            if len(parts) >= 2 and parts[1].lower() in ("easy","medium","hard"):
                difficulty = parts[1].lower()
            reward, msg = do_work(balance, difficulty)
            if reward == 0:
                print(msg)
                continue
            # apply shop multiplier
            reward = int(reward * work_multiplier)
            balance += reward
            print(msg)
            print("Balance:", balance)
            continue
        if parts[0].lower() == "spin":
            if not bets:
                print("No bets placed.")
                continue
            outcome = random.randint(0,36)
            color = "green" if outcome==0 else ("red" if outcome in RED else "black")
            print(f"Wheel spins... {outcome} ({color})")
            total_return = 0
            for b in bets:
                ret = eval_bet(b, outcome)
                stake = b[-1]
                total_return += ret
                if ret > 0:
                    win_amount = ret - stake
                    print(f"Bet {b}: WIN {win_amount} (return {ret})")
                else:
                    print(f"Bet {b}: lose ({-stake})")
            balance += total_return
            print("Balance:", balance)
            bets.clear()
            if balance <= 0:
                print("Bankrupt. Game over.")
                break
            continue
        print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()