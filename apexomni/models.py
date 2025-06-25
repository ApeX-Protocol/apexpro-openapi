from collections import namedtuple


def configDecoder(configs):
    return namedtuple('X', configs.keys())(*configs.values())

class CreateOrderModel:
    def __init__(self, symbol,
                 side,
                 type,
                 size,
                 subAccountId=None,
                 takerFeeRate=None,
                 makerFeeRate=None,
                 price=None,
                 accountId=None,
                 timeInForce="GOOD_TIL_CANCEL",
                 reduceOnly=False,
                 triggerPrice=None,
                 triggerPriceType=None,
                 trailingPercent=None,
                 clientId=None,
                 timestampSeconds=None,
                 isPositionTpsl = False,
                 signature=None,
                 isOpenTpslOrder=False,
                 isSetOpenSl=False,
                 isSetOpenTp=False,
                 slClientId=None,
                 slPrice=None,
                 slSide=None,
                 slSize=None,
                 slTriggerPrice=None,
                 tpClientId=None,
                 tpPrice=None,
                 tpSide=None,
                 tpSize=None,
                 tpTriggerPrice=None,
                 sourceFlag=None,
                 brokerId=None,):
        self.symbol = symbol
        self.side = side
        self.type = type
        self.size = size
        self.subAccountId = subAccountId
        self.takerFeeRate = takerFeeRate
        self.makerFeeRate = makerFeeRate
        self.price = price
        self.accountId = accountId
        self.timeInForce = timeInForce
        self.reduceOnly = reduceOnly
        self.triggerPrice = triggerPrice
        self.triggerPriceType = triggerPriceType
        self.trailingPercent = trailingPercent
        self.clientId = clientId
        self.timestampSeconds = timestampSeconds
        self.isPositionTpsl = isPositionTpsl
        self.signature = signature
        self.isOpenTpslOrder = isOpenTpslOrder
        self.isSetOpenSl = isSetOpenSl
        self.isSetOpenTp = isSetOpenTp
        self.slClientId = slClientId
        self.slPrice = slPrice
        self.slSide = slSide
        self.slSize = slSize
        self.slTriggerPrice = slTriggerPrice
        self.tpClientId = tpClientId
        self.tpPrice = tpPrice
        self.tpSide = tpSide
        self.tpSize = tpSize
        self.tpTriggerPrice = tpTriggerPrice
        self.slTriggerPrice = slTriggerPrice
        self.sourceFlag = sourceFlag
        self.brokerId = brokerId
