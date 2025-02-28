# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: steammessages_twofactor.steamclient.proto
# plugin: python-betterproto
# Last updated 27/02/2022

from dataclasses import dataclass

import betterproto

from .msg import UnifiedMessage


class RegisterCDKeyRequest(UnifiedMessage, um_name="Store.RegisterCDKey"):
    activation_code: str = betterproto.string_field(1)
    purchase_platform: int = betterproto.int32_field(2)
    is_request_from_client: bool = betterproto.bool_field(3)


class RegisterCDKeyResponse(UnifiedMessage, um_name="Store.RegisterCDKey"):
    purchase_result_details: int = betterproto.int32_field(1)
    purchase_receipt_info: "PurchaseReceiptInfo" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class PurchaseReceiptInfo(betterproto.Message):
    transactionid: int = betterproto.uint64_field(1)
    packageid: int = betterproto.uint32_field(2)
    purchase_status: int = betterproto.uint32_field(3)
    result_detail: int = betterproto.uint32_field(4)
    transaction_time: int = betterproto.uint32_field(5)
    payment_method: int = betterproto.uint32_field(6)
    base_price: int = betterproto.uint64_field(7)
    total_discount: int = betterproto.uint64_field(8)
    tax: int = betterproto.uint64_field(9)
    shipping: int = betterproto.uint64_field(10)
    currency_code: int = betterproto.uint32_field(11)
    country_code: str = betterproto.string_field(12)
    error_headline: str = betterproto.string_field(13)
    error_string: str = betterproto.string_field(14)
    error_link_text: str = betterproto.string_field(15)
    error_link_url: str = betterproto.string_field(16)
    error_appid: int = betterproto.uint32_field(17)
    line_items: "list[PurchaseReceiptInfoLineItem]" = betterproto.message_field(18)


@dataclass(eq=False, repr=False)
class PurchaseReceiptInfoLineItem(betterproto.Message):
    packageid: int = betterproto.uint32_field(1)
    appid: int = betterproto.uint32_field(2)
    line_item_description: str = betterproto.string_field(3)
