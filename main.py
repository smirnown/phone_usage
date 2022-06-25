import datetime
from decimal import Decimal
import math


def run_billing(file):
    with open(file, "r") as f:
        lines = f.readlines()

    call_infos = []
    rows = lines[1:]
    for row in rows:
        values = row.split(",")
        call_infos.append(CallInfo(
            account_number=values[0],
            origination_number=values[1],
            termination_number=values[2],
            call_start=values[3],
            call_stop=values[4].strip(),  # strip newline character off end of row
        ))

    bills = calculate_bills(call_infos)

    with open("output.csv", "w") as f:
        headers = "account_number,minutes_international,number_international,minutes_domestic,number_domestic,minutes_local,number_local,charge\n"
        f.write(headers)
        for bill in bills:
            f.write(str(bill) + "\n")


def calculate_bills(call_infos):
    account_number_to_customer_bill_map = dict()

    for info in call_infos:
        bill = CustomerBill(info)
        if account_number_to_customer_bill_map.get(info.account_number) is None:
            account_number_to_customer_bill_map[info.account_number] = bill
        else:
            account_number_to_customer_bill_map[info.account_number].update(bill)

    return list(account_number_to_customer_bill_map.values())


class PhoneNumber:

    def __init__(self, phone_number):
        phone_number = phone_number.strip("+")
        self.country_code = phone_number[0]
        self.area_code = phone_number[1:4]
        self.number = phone_number[4:]


class CustomerBill:

    def __init__(self, call_info):
        self.account_number = call_info.account_number
        self.minutes_international = 0
        self.num_international = 0
        self.minutes_domestic = 0
        self.num_domestic = 0
        self.minutes_local = 0
        self.num_local = 0
        self.set_call_metrics(call_info)
        self.charge = call_info.calculate_charge_for_call()

    def set_call_metrics(self, call_info):
        duration = call_info.get_call_duration()
        call_type = call_info.get_call_type()
        if call_type == "international":
            self.minutes_international += duration
            self.num_international += 1
        elif call_type == "domestic":
            self.minutes_domestic += duration
            self.num_domestic += 1
        elif call_type == "local":
            self.minutes_local += duration
            self.num_local += 1
        else:
            raise NotImplementedError(f"Unhandled call_type encountered: {call_type}")

    def update(self, new_call_info):
        """Aggregate billing metrics from two CustomerBill objects into one"""
        msg = f"Cannot combine bills for different accounts! " \
              f"This account: {self.account_number}, Other account: {new_call_info.account_number}"
        assert self.account_number == new_call_info.account_number, msg

        self.minutes_international += new_call_info.minutes_international
        self.minutes_domestic += new_call_info.minutes_domestic
        self.minutes_local += new_call_info.minutes_local
        self.num_international += new_call_info.num_international
        self.num_domestic += new_call_info.num_domestic
        self.num_local += new_call_info.num_local
        self.charge += new_call_info.charge.quantize(Decimal('1.00'))

    def __repr__(self):
        return f"{self.account_number},{self.minutes_international},{self.num_international},{self.minutes_domestic}," \
               f"{self.num_domestic},{self.minutes_local},{self.num_local},{self.charge.quantize(Decimal('1.00'))}"


class CallInfo:

    def __init__(self, account_number, origination_number, termination_number, call_start, call_stop):
        self.account_number = account_number
        self.origination_number = origination_number
        self.termination_number = termination_number
        self.call_start = call_start
        self.call_stop = call_stop

    def get_call_duration(self):
        start = datetime.datetime.fromisoformat(self.call_start)
        stop = datetime.datetime.fromisoformat(self.call_stop)
        difference = stop - start
        return math.ceil(difference.seconds / 60)

    def get_call_type(self):
        origin_number = PhoneNumber(self.origination_number)
        termination_number = PhoneNumber(self.termination_number)
        if origin_number.country_code != termination_number.country_code:
            return "international"
        elif origin_number.area_code != termination_number.area_code:
            return "domestic"
        else:
            return "local"

    def calculate_charge_for_call(self):
        duration = self.get_call_duration()
        call_type = self.get_call_type()
        if call_type == "international":
            base = 1
            rate = .2
        elif call_type == "domestic":
            base = 0
            rate = .1
        elif call_type == "local":
            base = 0
            rate = .02
        else:
            raise NotImplementedError(f"Unhandled call_type encountered: {call_type}")
        return Decimal(base + rate * duration).quantize(Decimal('1.00'))


if __name__ == "__main__":
    run_billing("usage.csv")
