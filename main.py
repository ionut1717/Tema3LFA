import random
from collections import defaultdict
import re

counter = 0

class CFG:
    def __init__(self, non_terminals, terminals, production_rules, start_symbol):
        self.non_terminals = set(non_terminals)
        self.terminals = set(terminals)
        self.production_rules = production_rules
        self.start_symbol = start_symbol
        self.sorted_non_terminals = sorted(list(self.non_terminals), key=len, reverse=True)
        self.sorted_terminals = sorted(list(self.terminals), key=len, reverse=True)

    def verify_CFG(self):
        if not self.non_terminals or not self.terminals or not self.start_symbol or not self.production_rules:
            print(f"Error: Invalid CFG Definition for Grammar #{counter}. CFG definition is incomplete.")
            return False

        if self.start_symbol not in self.non_terminals:
            print(f"Error: Invalid CFG Definition for Grammar #{counter}. The specified start symbol is not found within the set of non-terminal symbols.")
            return False

        if not self.non_terminals.isdisjoint(self.terminals):
            print(f"Error: Invalid CFG Definition for Grammar #{counter}. Non terminal symbols and terminal symbols are not disjoint")
            return False

        for key in self.production_rules:
            if key not in self.non_terminals:
                print(f"Error: Invalid CFG Definition for Grammar #{counter}. Production rules have an invalid left side symbol")
                return False
            else:
                for production in self.production_rules[key]:
                    if not self.verify_string(production):
                        print(f"Error: Invalid CFG Definition for Grammar #{counter}. Production rules have an invalid right side symbol")
                        return False
        return True

    def verify_string(self, string):
        all_valid_symbols = self.non_terminals.union(self.terminals)
        sorted_symbols = sorted(list(all_valid_symbols), key=len, reverse=True)

        while string:
            found_match = False
            for symbol in sorted_symbols:
                if string.startswith(symbol):
                    string = string[len(symbol):]
                    found_match = True
                    break
            if not found_match:
                print(f"Error: Invalid CFG Definition for Grammar #{counter}. Right side contains invalid symbols.", string)
                return False
        return True

    def print_CFG(self):
        print("Terminals:", self.terminals)
        print("Non terminals:", self.non_terminals)
        print("Start Symbol:", self.start_symbol)
        print("Production Rules")
        for key in self.production_rules:
            rhs = ["ε" if prod == "" else prod for prod in self.production_rules[key]]
            print(key, " -> ", " | ".join(rhs))

    def generate_string(self, max_length=10):
        max_tries = 100
        def generate_recursive(current_form, current_depth):
            if current_depth > (max_length * 2) + 10:
                return None
            
            terminal_len = 0
            temp = current_form
            while True:
                found_leading_terminal = False
                matched_len = 0
                for t_symbol in self.sorted_terminals:
                    if temp.startswith(t_symbol):
                        matched_len = len(t_symbol)
                        found_leading_terminal = True
                        break
                if found_leading_terminal:
                    terminal_len += matched_len
                    temp = temp[matched_len:]
                else:
                    break
            if terminal_len > max_length:
                return None
            if len(temp)==0:
                if len(current_form) <= max_length:
                    return current_form
                else:
                    return None

            first_found_nt = None
            nt_start_index = terminal_len
            nt_end_index = -1

            for nt_symbol in self.sorted_non_terminals:
                if temp.startswith(nt_symbol):
                    first_found_nt = nt_symbol 
                    nt_end_index = nt_start_index + len(nt_symbol)
                    break
            productions = self.production_rules.get(first_found_nt, [])
            if not productions:
                return None

            random.shuffle(productions)

            for production_rhs in productions:
                new_form = (
                    current_form[:nt_start_index] +
                    production_rhs +
                    current_form[nt_end_index:]
                )

                result = generate_recursive(new_form, current_depth + 1)
                if result is not None:
                    return result
            return None

        for _ in range(max_tries):
            generated_str = generate_recursive(self.start_symbol, 0)
            if generated_str is not None:
                return generated_str
        print(f"Warning: Could not generate a string of max_length {max_length} after {max_tries} attempts.")
        return None

    def leftmost_deviation(self, target_string, max_recursion_depth=200):
        if target_string == "":
            if "" in self.production_rules.get(self.start_symbol, []):
                return f"{self.start_symbol}=>ε"
            else:
                return f"No leftmost derivation found for '{target_string}'."

        def _derivation_recursive(current_form, current_depth):
            if current_form == target_string:
                return [target_string]
            
            if current_depth > max_recursion_depth:
                return None
            
            nt_to_expand = None
            nt_start_index = -1

            for nt_symbol in self.sorted_non_terminals:
                index = current_form.find(nt_symbol)
                if index != -1:
                    if nt_start_index == -1 or index < nt_start_index:
                        nt_start_index = index
                        nt_to_expand = nt_symbol

            if nt_to_expand is None:
                return None

            nt_end_index = nt_start_index + len(nt_to_expand)

            current_terminal_prefix = current_form[:nt_start_index]
            if not target_string.startswith(current_terminal_prefix):
                return None

            productions = self.production_rules.get(nt_to_expand, [])

            for rhs in productions:
                new_form = (
                    current_form[:nt_start_index] +
                    rhs +
                    current_form[nt_end_index:]
                )


                if len(new_form) > len(target_string) + len(self.sorted_non_terminals[0]):
                    return None

                path = _derivation_recursive(new_form, current_depth + 1)

                if path is not None:
                    return [current_form] + path
            return None

        derivation_steps = _derivation_recursive(self.start_symbol, 0)

        if derivation_steps:
            derivation_string = []
            for step in derivation_steps:
                if step == "":
                    derivation_string.append("ε")
                else:
                    derivation_string.append(step)
            return "=>".join(derivation_string)
        else:
            return f"No leftmost derivation found for '{target_string}'."
        
    def recognize_string(self, target_string, max_recursion_depth=2000):
        if self.leftmost_deviation(target_string,max_recursion_depth):
            print("True")
        else:
            print("False")

working_CFG = None
bonus_CFG= CFG(['S'], ['a','b','c'], {'S': ['abcS','']}, 'S')
with open("input.txt", 'r') as file:
    for line in file:
        line = line.strip()
        task_match = re.match(r'task([1-5])', line)
        if task_match:
            task_number = int(task_match.group(1))
            if task_number == 1:
                non_terminals = set()
                terminals = set()
                start_symbol = None
                production_rules = defaultdict(list)
                while True:
                    line = next(file).strip()
                    if line == "END":
                        break
                    if line == '':
                        continue
                    if line.startswith("NON_TERMINALS:"):
                        line = line.split("NON_TERMINALS:", 1)
                        non_terminals.update([ch.strip() for ch in line[1].strip().split(",")])
                    elif line.startswith("TERMINALS:"):
                        line = line.split("TERMINALS:", 1)
                        terminals.update([ch.strip() for ch in line[1].strip().split(",")])
                    elif line.startswith("START_SYMBOL:"):
                        line = line.split("START_SYMBOL:", 1)
                        start_symbol = line[1].strip()
                    elif line.startswith("PRODUCTION_RULES:"):
                        while True:
                            line = next(file).strip()
                            if line == '':
                                continue
                            if line == "END_PRODUCTION_RULES":
                                break
                            line = line.strip().split("->")
                            productions = [p.strip() for p in line[1].split("|")]
                            production_rules[line[0].strip()].extend(productions)
                current_CFG = CFG(non_terminals, terminals, production_rules, start_symbol)
                if current_CFG.verify_CFG():
                    working_CFG = current_CFG
                    working_CFG.print_CFG()
                else:
                    print("Invalid CFG, continuing with the latest valid CFG")
            elif task_number==2:
                line=next(file).strip()
                number_of_strings=int(line)
                if number_of_strings>10:
                    number_of_strings=10
                if number_of_strings<1:
                    number_of_strings=1
                line=next(file).strip()
                max_length=int(line)
                if max_length>10:
                    max_length=10
                if max_length<1:
                    max_length=1
                line=next(file)
                if working_CFG!=None:
                    for i in range (number_of_strings):
                        print(working_CFG.generate_string(max_length))
                else: 
                    print("No valid CFG provided")
            elif task_number==3:
                line=next(file).strip()
                target_string=line
                print(working_CFG.leftmost_deviation(target_string))
            elif task_number==4:
                line=next(file).strip()
                number_of_strings=int(line)
                for i in range(number_of_strings):
                    line=next(file).strip()
                    target_string=line
                    working_CFG.recognize_string(target_string)
            elif task_number==5:
                bonus_CFG.print_CFG()
                print(bonus_CFG.generate_string(10))
                bonus_CFG.recognize_string('abcabcabcabcabcabcabcabcabcabcabcabc')
