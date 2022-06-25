import pytest
import main
from decimal import Decimal


@pytest.fixture(scope="session")
def international_call_info():
    yield main.CallInfo(
        account_number=1,
        origination_number="+15555555555",
        termination_number="+26666666666",
        call_start="2022-06-24 15:31:11.696409",
        call_stop="2022-06-24 15:33:11.696409"
    )


@pytest.fixture(scope="session")
def domestic_call_info():
    yield main.CallInfo(
        account_number=1,
        origination_number="+15555555555",
        termination_number="+16666666666",
        call_start="2022-06-24 15:31:11.696409",
        call_stop="2022-06-24 15:33:11.696409"
    )


@pytest.fixture(scope="session")
def local_call_info():
    yield main.CallInfo(
        account_number=1,
        origination_number="+15555555555",
        termination_number="+15556666666",
        call_start="2022-06-24 15:31:11.696409",
        call_stop="2022-06-24 15:33:11.696409"
    )


def test_get_call_duration_no_rounding(international_call_info):
    assert international_call_info.get_call_duration() == 2


def test_get_call_duration_round_up():
    call_info = main.CallInfo(
        account_number=1,
        origination_number="+15555555555",
        termination_number="+16666666666",
        call_start="2022-06-24 15:31:11.696409",
        call_stop="2022-06-24 15:33:12.696409"
    )
    assert call_info.get_call_duration() == 3


def test_get_call_type_international(international_call_info):
    assert international_call_info.get_call_type() == "international"


def test_get_call_type_domestic(domestic_call_info):
    assert domestic_call_info.get_call_type() == "domestic"


def test_get_call_type_local(local_call_info):
    assert local_call_info.get_call_type() == "local"


def test_calculate_international_charge(international_call_info):
    assert international_call_info.calculate_charge_for_call() == Decimal(1.4).quantize(Decimal('1.00'))


def test_calculate_domestic_charge(domestic_call_info):
    assert domestic_call_info.calculate_charge_for_call() == Decimal(.2).quantize(Decimal('1.00'))


def test_calculate_local_charge(local_call_info):
    assert local_call_info.calculate_charge_for_call() == Decimal(.04).quantize(Decimal('1.00'))


def test_phone_number(local_call_info):
    number = main.PhoneNumber(local_call_info.termination_number)
    assert number.country_code == "1"
    assert number.area_code == "555"
    assert number.number == "6666666"


def test_international_customer_bill(international_call_info):
    bill = main.CustomerBill(international_call_info)
    assert bill.minutes_international == 2
    assert bill.num_international == 1
    assert bill.minutes_domestic == 0
    assert bill.num_domestic == 0
    assert bill.minutes_local == 0
    assert bill.num_local == 0
    assert bill.charge == Decimal(1.4).quantize(Decimal('1.00'))


def test_domestic_customer_bill(domestic_call_info):
    bill = main.CustomerBill(domestic_call_info)
    assert bill.minutes_international == 0
    assert bill.num_international == 0
    assert bill.minutes_domestic == 2
    assert bill.num_domestic == 1
    assert bill.minutes_local == 0
    assert bill.num_local == 0
    assert bill.charge == Decimal(.2).quantize(Decimal('1.00'))


def test_local_customer_bill(local_call_info):
    bill = main.CustomerBill(local_call_info)
    assert bill.minutes_international == 0
    assert bill.num_international == 0
    assert bill.minutes_domestic == 0
    assert bill.num_domestic == 0
    assert bill.minutes_local == 2
    assert bill.num_local == 1
    assert bill.charge == Decimal(.04).quantize(Decimal('1.00'))


def test_update_customer_bill(international_call_info, domestic_call_info):
    bill = main.CustomerBill(international_call_info)
    domestic_bill = main.CustomerBill(domestic_call_info)

    bill.update(domestic_bill)

    assert bill.minutes_international == 2
    assert bill.num_international == 1
    assert bill.minutes_domestic == 2
    assert bill.num_domestic == 1
    assert bill.minutes_local == 0
    assert bill.num_local == 0
    assert bill.charge.quantize(Decimal('1.00')) == Decimal(1.6).quantize(Decimal('1.00'))


def test_update_customer_bill_with_different_account_number(international_call_info):
    bill = main.CustomerBill(international_call_info)
    call_info = main.CallInfo(
        account_number=2,
        origination_number="+15555555555",
        termination_number="+16666666666",
        call_start="2022-06-24 15:31:11.696409",
        call_stop="2022-06-24 15:33:12.696409"
    )
    other_bill = main.CustomerBill(call_info)
    with pytest.raises(AssertionError):
        bill.update(other_bill)


def test_calculate_single_bill(international_call_info):
    bills = main.calculate_bills([international_call_info])
    assert len(bills) == 1

    bill = bills[0]
    assert bill.minutes_international == 2
    assert bill.num_international == 1
    assert bill.minutes_domestic == 0
    assert bill.num_domestic == 0
    assert bill.minutes_local == 0
    assert bill.num_local == 0
    assert bill.charge == Decimal(1.4).quantize(Decimal('1.00'))


def test_calculate_multiple_bills_for_one_account(international_call_info, domestic_call_info):
    bills = main.calculate_bills([international_call_info, domestic_call_info])
    assert len(bills) == 1

    bill = bills[0]
    assert bill.minutes_international == 2
    assert bill.num_international == 1
    assert bill.minutes_domestic == 2
    assert bill.num_domestic == 1
    assert bill.minutes_local == 0
    assert bill.num_local == 0
    assert bill.charge == Decimal(1.6).quantize(Decimal('1.00'))


def test_calculate_multiple_bills_for_multiple_accounts(international_call_info, domestic_call_info):
    other_account_call_info = main.CallInfo(
        account_number=2,
        origination_number="+15555555555",
        termination_number="+16666666666",
        call_start="2022-06-24 15:31:11.696409",
        call_stop="2022-06-24 15:33:11.696409"
    )
    bills = main.calculate_bills([international_call_info, domestic_call_info, other_account_call_info])
    assert len(bills) == 2

    account_1_bill = bills[0]
    assert account_1_bill.minutes_international == 2
    assert account_1_bill.num_international == 1
    assert account_1_bill.minutes_domestic == 2
    assert account_1_bill.num_domestic == 1
    assert account_1_bill.minutes_local == 0
    assert account_1_bill.num_local == 0
    assert account_1_bill.charge == Decimal(1.6).quantize(Decimal('1.00'))

    account_2_bill = bills[1]
    assert account_2_bill.minutes_international == 0
    assert account_2_bill.num_international == 0
    assert account_2_bill.minutes_domestic == 2
    assert account_2_bill.num_domestic == 1
    assert account_2_bill.minutes_local == 0
    assert account_2_bill.num_local == 0
    assert account_2_bill.charge == Decimal(.2).quantize(Decimal('1.00'))
